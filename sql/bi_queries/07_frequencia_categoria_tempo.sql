-- Arquivo: 07_frequencia_categoria_tempo.sql
-- Objetivo: Medir a frequência de compras por categoria ao longo do tempo.
-- Dependência: View `vw_base_transacoes`, `purchase_date` e `category`.
-- Saída: Série mensal por categoria com frequência e total gasto em BRL.

SELECT
  DATE_TRUNC('month', purchase_date)::date AS mes,
  category,
  COUNT(*) AS frequencia_compras,
  SUM(amount_brl) AS total_gasto_brl
FROM vw_base_transacoes
WHERE amount_brl > 0
GROUP BY 1, 2
ORDER BY 1, frequencia_compras DESC, total_gasto_brl DESC;