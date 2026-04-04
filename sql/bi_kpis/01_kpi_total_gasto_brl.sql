-- Arquivo: 01_kpi_total_gasto_brl.sql
-- Objetivo: Calcular o total gasto em BRL considerando somente compras válidas (> 0).
-- Dependência: View `vw_base_transacoes`.
-- Saída: Uma linha com a coluna `kpi_total_gasto_brl`.

SELECT COALESCE(SUM(amount_brl), 0) AS kpi_total_gasto_brl
FROM vw_base_transacoes
WHERE amount_brl > 0;