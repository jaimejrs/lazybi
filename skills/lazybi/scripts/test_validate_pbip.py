"""Temporary fixtures only; these tests do not edit an existing PBIP project."""

import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
from validate_pbip import Validator, main


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def fixture(self, legacy=False, connection=False, bim=False):
        project = self.root / "Example.pbip"
        report = self.root / "Example.Report"
        model = self.root / "Example.SemanticModel"
        self.write(project, {"artifacts": [{"report": {"path": report.name}}]})
        reference = {"byConnection": {}} if connection else {"byPath": {"path": "../" + model.name}}
        self.write(report / "definition.pbir", {"version": "4.0", "datasetReference": reference})
        if legacy:
            self.write(report / "report.json", {})
        else:
            self.write(report / "definition" / "report.json", {})
            self.write(report / "definition" / "version.json", {"version": "2.0.0"})
        if not connection:
            self.write(model / "definition.pbism", {"version": "4.2"})
            if bim:
                self.write(model / "model.bim", {"model": {}})
            else:
                definition = model / "definition"
                definition.mkdir()
                (definition / "model.tmdl").write_text("model Model\n", encoding="utf-8")
        return project, report, model

    def validate(self, project):
        validator = Validator()
        validator.validate(project)
        return validator

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def test_pbir_sibling_tmdl_is_read_only(self):
        project, _, model = self.fixture()
        before = self.snapshot()
        validator = self.validate(project)
        self.assertEqual(validator.errors, [])
        self.assertEqual(validator.formats, ["PBIR"])
        self.assertEqual(validator.models, {model})
        self.assertEqual(self.snapshot(), before)

    def test_legacy_tmsl(self):
        project, _, _ = self.fixture(legacy=True, bim=True)
        validator = self.validate(project)
        self.assertEqual(validator.errors, [])
        self.assertEqual(validator.formats, ["PBIR-Legacy"])

    def test_connection_does_not_require_local_model(self):
        project, _, model = self.fixture(connection=True)
        self.assertFalse(model.exists())
        validator = self.validate(project)
        self.assertEqual(validator.errors, [])
        self.assertEqual(validator.models, set())

    def test_missing_descriptor_and_pbir_version_fail(self):
        project, report, model = self.fixture()
        (model / "definition.pbism").unlink()
        (report / "definition" / "version.json").unlink()
        validator = self.validate(project)
        self.assertEqual(len(validator.errors), 2)
        self.assertTrue(any("definition.pbism" in error for error in validator.errors))

    def test_duplicate_key_in_editable_json_fails(self):
        project, report, _ = self.fixture()
        (report / "definition" / "theme.json").write_text('{"x": 1, "x": 2}', encoding="utf-8")
        self.assertTrue(any("duplicate JSON key" in error for error in self.validate(project).errors))

    def test_nan_in_bim_fails(self):
        project, _, model = self.fixture(bim=True)
        (model / "model.bim").write_text('{"value": NaN}', encoding="utf-8")
        self.assertTrue(any("non-finite JSON" in error for error in self.validate(project).errors))

    def test_broken_json_and_ignored_cache(self):
        project, report, _ = self.fixture()
        for directory in (".pbi", ".git"):
            ignored = report / directory
            ignored.mkdir()
            (ignored / "cache.json").write_text("not json", encoding="utf-8")
        self.assertEqual(self.validate(project).errors, [])
        (report / "definition" / "report.json").write_text('{"x":', encoding="utf-8")
        self.assertTrue(any("invalid JSON at line" in error for error in self.validate(project).errors))

    def test_absolute_reference_and_null_project_fail(self):
        project, _, _ = self.fixture()
        self.write(project, {"artifacts": [{"report": {"path": "C:\\Elsewhere\\Report"}}]})
        self.assertTrue(any("must be relative" in error for error in self.validate(project).errors))
        project.write_text("null", encoding="utf-8")
        self.assertTrue(self.validate(project).errors)

    def test_linked_directory_is_not_scanned(self):
        project, report, _ = self.fixture()
        external = self.root / "External"
        external.mkdir()
        (external / "bad.json").write_text("not json", encoding="utf-8")
        try:
            os.symlink(external, report / "Linked", target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symlink creation unavailable: {exc.strerror}")
        validator = self.validate(project)
        self.assertEqual(validator.errors, [])
        self.assertEqual(validator.skipped_links, 1)

    def test_cli_exit_and_scope(self):
        project, report, _ = self.fixture()
        for expected in (0, 1):
            if expected:
                (report / "definition.pbir").unlink()
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                result = main([str(project)])
            self.assertEqual(result, expected)
            self.assertIn("no schema, TMDL/DAX, execution or rendering validation", output.getvalue())


if __name__ == "__main__":
    unittest.main()
