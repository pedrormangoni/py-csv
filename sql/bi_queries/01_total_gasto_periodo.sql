-- Arquivo: 01_total_gasto_periodo.sql
-- Objetivo: Resumir gasto total e quantidade de compras no período disponível.
-- Dependência: View `vw_base_transacoes`.
-- Saída: Uma linha com datas limite, totais BRL/USD e total de compras.

SELECT
  MIN(purchase_date) AS data_inicial,
  MAX(purchase_date) AS data_final,
  SUM(amount_brl) AS total_gasto_brl,
  SUM(amount_usd) AS total_gasto_usd,
  COUNT(*) AS total_compras
FROM vw_base_transacoes
WHERE amount_brl > 0;