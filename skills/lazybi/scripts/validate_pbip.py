#!/usr/bin/env python3
"""Read-only local PBIP structure check; no schema, TMDL, DAX or render validation."""

import argparse
import json
import os
from pathlib import Path, PureWindowsPath
import sys


IGNORED_DIRS = {".pbi", ".git"}
REPARSE_POINT = 0x400  # Windows junctions, symlinks and other linked entries.
LIMITS = "Limits: no schema, TMDL/DAX, execution or rendering validation."
FAILED = object()


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("non-finite JSON number: " + value)


def linked(path):
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) & REPARSE_POINT)


class Validator:
    def __init__(self):
        self.errors = []
        self.seen = set()
        self.documents = {}
        self.models = set()
        self.formats = []
        self.skipped_links = 0

    def error(self, path, message):
        self.errors.append(f"ERROR: {path}: {message}")

    def safe(self, path):
        # Do not resolve links before inspecting them; sibling references are legal.
        try:
            for entry in [*reversed(path.parents), path]:
                if linked(entry):
                    self.error(path, "linked/reparse path is not scanned")
                    return False
            return True
        except OSError as exc:
            self.error(path, f"cannot access path ({exc.strerror or type(exc).__name__})")
            return False

    def required(self, path, directory=False):
        if not self.safe(path):
            return False
        if (path.is_dir() if directory else path.is_file()):
            return True
        self.error(path, "directory required" if directory else "file required")
        return False

    def read_json(self, path):
        if path in self.seen:
            return self.documents.get(path, FAILED)
        self.seen.add(path)
        if not self.required(path):
            return FAILED
        try:
            value = json.loads(
                path.read_text(encoding="utf-8-sig"),
                object_pairs_hook=strict_object,
                parse_constant=reject_constant,
            )
            self.documents[path] = value
            return value
        except json.JSONDecodeError as exc:
            self.error(path, f"invalid JSON at line {exc.lineno}, column {exc.colno}")
        except UnicodeError:
            self.error(path, "invalid UTF-8")
        except ValueError as exc:
            self.error(path, str(exc))
        except OSError as exc:
            self.error(path, f"cannot read file ({exc.strerror or type(exc).__name__})")
        return FAILED

    def relative(self, base, value, owner):
        if not isinstance(value, str) or not value.strip() or "\x00" in value:
            self.error(owner, "reference path must be a nonempty relative string")
            return None
        windows = PureWindowsPath(value)
        if Path(value).is_absolute() or windows.drive or windows.root:
            self.error(owner, "reference path must be relative")
            return None
        return Path(os.path.abspath(base / value.replace("\\", os.sep)))

    def files(self, root):
        def failed(exc):
            self.error(root, f"cannot scan directory ({exc.strerror or type(exc).__name__})")

        for current, dirs, names in os.walk(root, followlinks=False, onerror=failed):
            current = Path(current)
            kept = []
            for name in sorted(dirs):
                if name.lower() in IGNORED_DIRS:
                    continue
                try:
                    if linked(current / name):
                        self.skipped_links += 1
                    else:
                        kept.append(name)
                except OSError as exc:
                    failed(exc)
            dirs[:] = kept
            for name in sorted(names):
                path = current / name
                try:
                    if linked(path):
                        self.skipped_links += 1
                        continue
                except OSError as exc:
                    failed(exc)
                    continue
                yield path

    def scan_json(self, root):
        for path in self.files(root):
            if path.suffix.lower() == ".json":
                self.read_json(path)

    def model(self, root):
        if root in self.models:
            return
        self.models.add(root)
        if not self.required(root, directory=True):
            return
        self.read_json(root / "definition.pbism")
        bim = root / "model.bim"
        definition = root / "definition"
        if bim.exists() or bim.is_symlink():
            self.read_json(bim)
        elif not self.required(definition, directory=True):
            self.error(root, "expected model.bim or a TMDL definition directory")
        elif not any(path.suffix.lower() == ".tmdl" for path in self.files(definition)):
            self.error(definition, "no TMDL file found")
        self.scan_json(root)

    def report(self, root):
        if not self.required(root, directory=True):
            return
        pbir_path = root / "definition.pbir"
        pbir = self.read_json(pbir_path)
        definition = root / "definition"
        pbir_report = definition / "report.json"
        legacy_report = root / "report.json"
        if pbir_report.exists() or pbir_report.is_symlink():
            self.formats.append("PBIR")
            self.read_json(pbir_report)
            self.read_json(definition / "version.json")
        elif legacy_report.exists() or legacy_report.is_symlink():
            self.formats.append("PBIR-Legacy")
            self.read_json(legacy_report)
        else:
            self.error(root, "expected definition/report.json (PBIR) or report.json (PBIR-Legacy)")
        if pbir is not FAILED:
            reference = pbir.get("datasetReference") if isinstance(pbir, dict) else None
            if not isinstance(reference, dict):
                self.error(pbir_path, "datasetReference object required")
            elif "byPath" in reference and "byConnection" in reference:
                self.error(pbir_path, "datasetReference must choose byPath or byConnection")
            elif "byPath" in reference:
                entry = reference["byPath"]
                model_path = self.relative(root, entry.get("path") if isinstance(entry, dict) else None, pbir_path)
                if model_path is not None:
                    self.model(model_path)
            elif "byConnection" in reference:
                if not isinstance(reference["byConnection"], dict):
                    self.error(pbir_path, "byConnection must be an object")
            else:
                self.error(pbir_path, "datasetReference needs byPath or byConnection")
        self.scan_json(root)

    def validate(self, path):
        document = self.read_json(path)
        if document is FAILED:
            return
        artifacts = document.get("artifacts") if isinstance(document, dict) else None
        if not isinstance(artifacts, list) or not artifacts:
            self.error(path, "nonempty artifacts list required")
            return
        reports = 0
        for artifact in artifacts:
            if not isinstance(artifact, dict) or "report" not in artifact:
                continue
            reports += 1
            report = artifact["report"]
            root = self.relative(path.parent, report.get("path") if isinstance(report, dict) else None, path)
            if root is not None:
                self.report(root)
        if not reports:
            self.error(path, "no report artifact found")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pbip", type=Path, help="path to the .pbip project file")
    args = parser.parse_args(argv)
    path = Path(os.path.abspath(args.pbip))
    validator = Validator()
    if path.suffix.lower() != ".pbip":
        validator.error(path, "expected a .pbip file")
    else:
        validator.validate(path)
    for message in validator.errors:
        print(message, file=sys.stderr)
    if validator.errors:
        print(f"FAILED: {len(validator.errors)} structural/JSON error(s).")
    else:
        print(f"OK: {', '.join(validator.formats)}; {len(validator.models)} local model(s); {len(validator.seen)} JSON file(s).")
    if validator.skipped_links:
        print(f"Skipped: {validator.skipped_links} linked/reparse entry/entries.")
    print(LIMITS)
    return 1 if validator.errors else 0


if __name__ == "__main__":
    sys.exit(main())
