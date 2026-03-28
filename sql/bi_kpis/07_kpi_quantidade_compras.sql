-- Arquivo: 07_kpi_quantidade_compras.sql
-- Objetivo: Contar a quantidade total de compras com valor positivo.
-- Dependência: View `vw_base_transacoes`.
-- Saída: Uma linha com a coluna `kpi_quantidade_compras`.

SELECT COUNT(*) AS kpi_quantidade_compras
FROM vw_base_transacoes
WHERE amount_brl > 0;