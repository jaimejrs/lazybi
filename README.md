# LazyBI

Skill para criar, editar e simplificar dashboards e relatórios Power BI em
projetos `.pbip`. Reutilize o que funciona, prefira recursos nativos e escreva
somente o DAX, Power Query e a modelagem necessários.

Inspirada no [ponytail](https://github.com/dietrichgebert/ponytail), com uma
escada de decisões e três intensidades. Eficiência sem sacrificar a definição
dos indicadores, a integridade do projeto ou a legibilidade do painel.

## Instalação no Codex

Com acesso a este repositório privado, peça ao Codex:

```text
Use $skill-installer para instalar a skill de https://github.com/jaimejrs/lazybi/tree/main/skills/lazybi
```

Alternativamente, clone o repositório e copie a pasta `skills/lazybi` para
`~/.codex/skills/lazybi`. Preserve suas subpastas. Se esse destino já existir,
confira as mudanças antes de substituí-lo.

## Uso

```text
Use $lazybi full para criar um dashboard Power BI em .pbip com os dados e indicadores deste projeto.
```

| Nível | Comportamento |
| --- | --- |
| `lite` | Atende ao pedido e aponta uma alternativa mais simples quando útil. |
| `full` | Reutiliza primeiro e acrescenta somente o necessário. Padrão. |
| `ultra` | Questiona extras e elimina duplicações dispensáveis no escopo. |

Para desativar o estilo nesta conversa, diga `lazybi off` ou `modo normal`.
Requisitos explícitos continuam sendo atendidos em qualquer nível.

## O que está incluído

- [Skill principal](skills/lazybi/SKILL.md): escada, modos, fluxo e critérios de entrega.
- [PBIP/PBIR/TMDL](skills/lazybi/references/pbip.md): formatos, vínculos, edição externa e validação.
- [Modelo e design](skills/lazybi/references/modelo-e-design.md): medidas, relacionamentos, layout e interações.
- [Validador local](skills/lazybi/scripts/validate_pbip.py): sintaxe JSON e vínculos básicos, somente leitura e sem dependências externas.

## Verificação local

Com Python 3.9 ou posterior, na raiz do repositório:

```powershell
python -B skills/lazybi/scripts/test_validate_pbip.py
python -B skills/lazybi/scripts/validate_pbip.py "C:/Projetos/Painel/Painel.pbip"
```

O validador não verifica schemas, gramática TMDL, DAX/M, atualização, dados ou
renderização. Essas verificações exigem ferramentas específicas e, quando
disponível, o Power BI Desktop. O teste de links simbólicos pode ser pulado
quando o sistema não permitir criá-los.

## Licença e origem

[MIT](LICENSE). A arquitetura é inspirada no ponytail de DietrichGebert;
a atribuição e a licença original são preservadas. LazyBI é uma adaptação
independente para Power BI.
