# Modelo, medidas e desenho mínimo correto

Consulte apenas quando a tarefa envolver dados, cálculos, aparência ou
interações. O objetivo é tirar complexidade de manutenção sem reduzir clareza.

## Camada certa

| Necessidade | Primeiro caminho a considerar |
| --- | --- |
| Limpar tipos, chaves, duplicidade ou granularidade | Fonte/Power Query; preservar query folding quando aplicável. |
| Total, razão ou comparação sob filtros | Medida DAX reutilizável. |
| Atributo usado em eixo, agrupamento ou relacionamento | Coluna existente; transformação M ou coluna calculada só quando necessária. |
| Categoria ou entidade compartilhada por fatos | Dimensão e relacionamento compatíveis com o grão. |
| Cor, unidade, rótulo, ordenação ou interação | Propriedade nativa/tema antes de expressão auxiliar. |

Não mova transformações para DAX só porque a expressão é menor. Não crie tabelas
ou relações que o caso simples não exige. Quando houver múltiplas entidades ou
fatos, use modelagem dimensional para filtrar corretamente, começando por grão,
unicidade de chaves e relações `1:*` de dimensões para fatos. Não conserte uma
chave duplicada com muitos-para-muitos ou filtro bidirecional indiscriminado.
Veja [esquema estrela](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
e [filtros bidirecionais](https://learn.microsoft.com/en-us/power-bi/guidance/relationships-bidirectional-filtering).

Preserve modos de armazenamento e fontes quando não fizerem parte do pedido.
Mantenha privacidade de dados e credenciais fora de arquivos compartilhados.

## DAX pequeno, significado completo

- Reutilize medidas existentes e confirme a agregação. Contagem de linhas, contagem distinta, soma e última aferição respondem perguntas diferentes.
- Uma taxa total geralmente depende dos numeradores/denominadores agregados; não some percentuais nem troque média ponderada por média simples sem a regra de negócio.
- Use `DIVIDE` quando o denominador puder ser zero/BLANK. Zero como resultado alternativo só quando o negócio definir zero nesse caso. Veja [DIVIDE](https://learn.microsoft.com/en-us/dax/best-practices/dax-divide-function-operator).
- Preserve `BLANK()` quando ausência for significativa. Converter tudo em zero pode criar categorias e esconder falta de dados. Veja [BLANK](https://learn.microsoft.com/en-us/dax/best-practices/dax-avoid-converting-blank).
- Prefira predicados booleanos em `CALCULATE` quando equivalentes; use `KEEPFILTERS` se for necessário intersectar o filtro. Mantenha `FILTER` quando a condição exigir expressão mais complexa ou medida. Veja [filtros DAX](https://learn.microsoft.com/en-us/power-bi/guidance/dax-avoid-avoid-filter-as-filter-argument).
- `ALL`/`REMOVEFILTERS` precisam corresponder ao denominador desejado; não apague segmentações por conveniência.
- Mantenha medidas numéricas. Use formato da medida/visual para moeda e percentual; `FORMAT` muda o valor para texto quando usado como resultado.
- Reutilize o calendário se a análise temporal o exigir. Confirme datas válidas, grão, calendário fiscal e relacionamento ativo; não crie calendário extra para um cartão isolado. Veja [tabelas de datas](https://learn.microsoft.com/en-us/power-bi/guidance/model-date-tables).

Exemplo: para "percentual de indicadores concluídos por eixo", determine primeiro
o identificador do indicador, o que conta como concluído, a última aferição e o
universo elegível. Um `COUNTROWS` pequeno sobre histórico pode duplicar o mesmo
indicador. Escreva a expressão depois de esclarecer essa definição.

## Layout que ajuda a decidir

Para um painel novo sem briefing visual, comece com uma visão geral suficiente
para a decisão: título e período claros, indicadores prioritários, comparação
adequada e filtros úteis. Uma página é um ponto de partida quando ela acomoda o
pedido, não um limite. Reaproveite marca, dimensões e tema fornecidos; capriche no
alinhamento, espaçamento, contraste e hierarquia sem acrescentar decoração.

Escolha visuais pela pergunta: cartão para valor, barras para comparar
categorias, linha para evolução, tabela/matriz para detalhar. Evite dois visuais
que repetem a mesma informação. Use unidades e casas decimais consistentes,
ordenação coerente e nomes de negócio. Cor deve ter significado estável, com
rótulos ou ícones quando necessário para não depender só dela. Preserve
acessibilidade e requisitos móveis existentes.

Confira quais visuais cada segmentação filtra; não desabilite interações para
disfarçar cálculo errado. Tooltips, drill-through e bookmarks entram quando
resolvem uma necessidade concreta. Um visual customizado pedido ou indispensável
continua válido, com compatibilidade verificada.

## Confira o efeito da mudança

Para cálculos, compare total e recorte com fonte/consulta confiável e verifique
o caso de filtro vazio, denominador zero ou múltiplas seleções quando relevantes.
Não invente valores esperados; derive-os dos dados e da regra acordada. Para
layout, capture as páginas alteradas no Desktop e procure visuais quebrados,
cortes, sobreposições, rótulos ilegíveis e interação incorreta.

Desempenho deve ser medido no cenário afetado. Use o [Performance Analyzer](https://learn.microsoft.com/en-us/power-bi/create-reports/performance-analyzer)
disponível para localizar custo de visual/consulta antes de reescrever medidas,
criar agregações ou mudar armazenamento. Não anuncie ganho sem medição.
