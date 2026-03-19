# KPIs de BI

Consultas SQL para cards de dashboard (modelo 1 KPI por query).

## Arquivos

- `01_kpi_total_gasto_brl.sql`: total gasto em BRL.
- `02_kpi_total_gasto_usd.sql`: total gasto em USD.
- `03_kpi_ticket_medio_brl.sql`: ticket médio em BRL.
- `04_kpi_percentual_parcelado.sql`: percentual de compras parceladas.
- `05_kpi_mes_maior_gasto.sql`: mês com maior gasto e respectivo valor.
- `06_kpi_categoria_lider.sql`: categoria com maior gasto e respectivo valor.
- `07_kpi_quantidade_compras.sql`: quantidade total de compras.
- `08_kpi_resumo_geral.sql`: visão consolidada com os principais KPIs em uma única linha.

## Como executar

### pgAdmin
Execute os arquivos individualmente no Query Tool do banco `credit-card`.

### psql (terminal)
Na pasta `sql/bi_kpis`, execute:

```bash
psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_kpis.sql
```

> Observação: `00_apply_all_kpis.sql` usa `\\i` (comando do `psql`).
