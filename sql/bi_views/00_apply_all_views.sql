-- Arquivo: 00_apply_all_views.sql
-- Objetivo: Executar a criação/atualização de todas as views analíticas da camada BI.
-- Dependência: Scripts `00` a `05` da pasta `bi_views` e tabela de staging.
-- Saída: Views prontas para consumo por KPIs, quality checks e dashboard.

\i 00_vw_base_transacoes.sql
\i 01_vw_gastos_mensais.sql
\i 02_vw_gastos_categoria.sql
\i 03_vw_parcelamento.sql
\i 04_vw_fx_impacto_mensal.sql
\i 05_vw_frequencia_categoria_mensal.sql
\i 06_vw_gastos_semanais_mes.sql
\i 07_vw_compras_recorrentes.sql