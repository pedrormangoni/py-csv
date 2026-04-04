-- Arquivo: 02_kpi_total_gasto_usd.sql
-- Objetivo: Calcular o total gasto em USD para transações com valor positivo em BRL.
-- Dependência: View `vw_base_transacoes`.
-- Saída: Uma linha com a coluna `kpi_total_gasto_usd`.

SELECT COALESCE(SUM(amount_usd), 0) AS kpi_total_gasto_usd
FROM vw_base_transacoes
WHERE amount_brl > 0;