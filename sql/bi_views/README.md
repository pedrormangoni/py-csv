# Camada Analítica (Views BI)

Este diretório contém views para consumo em pgAdmin e ferramentas de BI.

## Views disponíveis

- `vw_base_transacoes`: camada base com atributos derivados de tempo, parcelamento, cartão, câmbio e recorrência.
- `vw_gastos_mensais`: total, volume e ticket médio por mês.
- `vw_gastos_categoria`: distribuição de gastos por categoria com percentual.
- `vw_parcelamento`: comparação entre compras parceladas e à vista.
- `vw_fx_impacto_mensal`: impacto mensal da cotação sobre compras em USD.
- `vw_frequencia_categoria_mensal`: frequência e valor por categoria ao longo do tempo.
- `vw_gastos_semanais_mes`: ranking das semanas com maior gasto em cada mês.
- `vw_compras_recorrentes`: agrupamento de compras recorrentes por descrição, categoria, cartão e valor.

## Modelo semântico sugerido para BI

- Fato principal: `vw_base_transacoes`
- Dimensão de tempo: `purchase_date`, `purchase_month`, `purchase_week`, `purchase_year`, `purchase_year_month`
- Dimensão de cartão: `cardholder_name`, `card_last4`, `card_key`
- Dimensão de categoria: `category`, `category_key`
- Dimensão de parcelamento: `purchase_type`, `installment_number`, `installment_total`, `is_installment`
- Métricas centrais: `amount_brl`, `amount_usd`, `fx_rate_brl`, `fx_impact_brl`, `recurring_occurrences`

## Padronização para troca de tema/fonte

Todos os SQLs analíticos (queries, KPIs, views e quality checks) passam a ler de `vw_base_transacoes`.
Para trocar facilmente a fonte de dados, ajuste apenas a definição em `00_vw_base_transacoes.sql`.

## Como aplicar

### Opção 1: executar arquivo por arquivo
No Query Tool (banco `credit-card`), execute os arquivos `01` a `05`.

### Opção 2: aplicar tudo via psql
Dentro da pasta `sql/bi_views`, execute:

```bash
psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_views.sql
```

> Observação: o arquivo `00_apply_all_views.sql` usa comandos `\\i` (psql). No pgAdmin, execute os arquivos individualmente.
