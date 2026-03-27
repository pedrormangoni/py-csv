CREATE OR REPLACE VIEW vw_gastos_categoria AS
WITH total AS (
  SELECT SUM(amount_brl) AS total_geral_brl
  FROM vw_base_transacoes
  WHERE amount_brl > 0
)
SELECT
  t.category,
  COUNT(*) AS quantidade_compras,
  SUM(t.amount_brl) AS total_gasto_brl,
  SUM(t.amount_usd) AS total_gasto_usd,
  ROUND((SUM(t.amount_brl) / NULLIF(MAX(total.total_geral_brl), 0)) * 100, 2) AS percentual_total_brl
FROM vw_base_transacoes t
CROSS JOIN total
WHERE t.amount_brl > 0
GROUP BY t.category
ORDER BY total_gasto_brl DESC;