# PBIP: arquivos e verificação

Consulte ao criar projetos ou alterar sua estrutura. Referências oficiais
conferidas em 05/10/2026; confira novamente versões, propriedades e recursos de
preview quando o caso depender deles. Não atualize versões de schema em massa.

## Identifique o projeto real

Um arranjo comum, com modelo local em TMDL, é:

```text
Painel.pbip
Painel.Report/
  definition.pbir
  definition/
    version.json
    report.json
    pages/
      <page-id>/
        page.json
        visuals/<visual-id>/visual.json
Painel.SemanticModel/
  definition.pbism
  definition/
    database.tmdl
    model.tmdl
    tables/<tabela>.tmdl
    relationships.tmdl
```

É um exemplo, não uma lista universal para scaffolding. O `.pbip` aponta para
o relatório; `definition.pbir` aponta para o modelo. Resolva cada caminho a
partir do arquivo que o contém. `byPath` é relativo, usa `/` e pode apontar a
`../Painel.SemanticModel`. `byConnection` referencia um modelo remoto: não crie
uma cópia local nem mude a conexão apenas para satisfazer um validador.
Confira detalhes no [formato do relatório](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report).

| Camada | Formato | Decisão |
| --- | --- | --- |
| Relatório | PBIR: pasta `definition/` | JSON público, editável conforme schemas. |
| Relatório | PBIR-Legacy: `report.json` na raiz do `.Report` | Não edite externamente esse JSON sem suporte; use Desktop. |
| Modelo | TMDL: pasta `definition/` no modelo | Texto com gramática própria e indentação estrutural. |
| Modelo | TMSL: `model.bim` | Preserve o formato encontrado. |

`definition.pbir` versão `4.0` pode acompanhar PBIR ou legado. Não infira o
formato só pela versão. Não confunda `Report/report.json` legado com o JSON
editável `Report/definition/report.json`.

## Novo projeto

Escolha um exemplo oficial ou template autorizado compatível com o Desktop
alvo. Derive os arquivos necessários de seus schemas, acrescente só os objetos
do pedido e ligue os campos existentes. Copiar um visual exige conferir também
aliases, entidades, medidas, filtros, recursos e IDs. Para objetos novos, gere
IDs distintos; para objetos existentes, mantenha a identidade.

Páginas, visuais e bookmarks têm dependências: ao copiar ou renomear, ajuste
referências, ordem de páginas quando presente e seleções de navegação. Tema e
imagens devem estar corretamente registrados como recursos do relatório.
Não use um projeto vazio com links quebrados como entrega concluída.

Schemas oficiais, escolhidos pelo `$schema` do arquivo, não por "última versão":

- [PBIP](https://github.com/microsoft/json-schemas/tree/main/fabric/pbip/pbipProperties)
- [Ponteiro do relatório](https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definitionProperties)
- [Definição PBIR](https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition)
- [Definição do modelo](https://github.com/microsoft/json-schemas/tree/main/fabric/item/semanticModel/definitionProperties)

## Estado do Desktop e edição externa

Antes de editar um projeto aberto, confira se há mudanças não salvas; salve-as
ou coordene sua preservação. Não descarte esse trabalho para aplicar os seus
arquivos. Confira `.pbi/unappliedChanges.json` antes de editar expressões M: uma
aplicação posterior de pendências pode sobrescrever a edição externa. Preserve
o arquivo e resolva o conflito antes dessa edição. Veja [arquivos do modelo](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset).

PBIP e PBIR já são GA. A detecção/reload externo e o Desktop Bridge ainda estão
em preview na data acima. Detecte a capacidade e versão instaladas: recarregue
com suporte disponível, ou feche/reabra com o trabalho salvo. Algumas mudanças,
inclusive em `definition.pbir`, não entram no reload atual. Não prometa que um
reload aplica qualquer arquivo. Veja [edição externa](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-external-editing).

Se o Bridge já estiver disponível, consulte `manifest`/status e
`hasUnsavedChanges` antes de usar abertura, reload ou capturas. Use apenas as
operações suportadas pela instalação. É uma opção, não pré-requisito nem motivo
para instalar CLI/MCP automaticamente. Veja [Desktop Bridge](https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-desktop-bridge-overview).

Salve arquivos externos em UTF-8 sem BOM e preserve finais de linha existentes.
Não edite `cache.abf`, diagramas internos ou tabelas automáticas de data. Preserve
o `.gitignore` existente e acrescente exclusões para `**/.pbi/localSettings.json`
e `**/.pbi/cache.abf` se faltarem. Sem cache, o projeto pode exigir atualização
para exibir valores; não preencha o cache com dados inventados. Veja [projetos PBIP](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview).

## TMDL e camadas de validação

Mantenha indentação, aspas de nomes e escaping TMDL; não normalize arquivos
inteiros ao inserir uma medida. Use `TmdlSerializer.DeserializeDatabaseFromFolder`
quando TOM estiver disponível para verificar a representação. Isso não executa
consultas nem prova os resultados de DAX/M. Consulte [TMDL](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview).

O helper `scripts/validate_pbip.py` lê o projeto e os diretórios vinculados sem
seguir links/reparse points, sem rede e sem alterar arquivos. Seu sucesso diz
apenas que as verificações locais implementadas passaram. Schemas, referências
de campos/IDs, TMDL e engine exigem verificações próprias. A [skill oficial de
autoria](https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-report-authoring-skill-overview)
é uma referência complementar para validar PBIR e conferir renderização com
ferramentas já disponíveis; não precisa ser instalada para usar esta skill.

Pedidos de "dashboard" em `.pbip` normalmente significam relatório interativo.
Um dashboard com tiles no Service é outra entrega. Criar ou editar arquivos
locais não implica publicar, alterar gateway ou configurar atualização remota.
