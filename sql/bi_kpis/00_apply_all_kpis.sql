-- Arquivo: 00_apply_all_kpis.sql
-- Objetivo: Executar, em sequência, todos os scripts de KPI da camada BI.
-- Dependência: Scripts `01` a `08` da pasta `bi_kpis` e a view `vw_base_transacoes`.
-- Saída: Resultado individual de cada KPI executado no contexto do cliente SQL (psql).

\i 01_kpi_total_gasto_brl.sql
\i 02_kpi_total_gasto_usd.sql
\i 03_kpi_ticket_medio_brl.sql
\i 04_kpi_percentual_parcelado.sql
\i 05_kpi_mes_maior_gasto.sql
\i 06_kpi_categoria_lider.sql
\i 07_kpi_quantidade_compras.sql
\i 08_kpi_resumo_geral.sql