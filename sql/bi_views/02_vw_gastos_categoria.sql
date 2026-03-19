CREATE OR REPLACE VIEW vw_gastos_categoria AS
WITH total AS (
  SELECT SUM(amount_brl) AS total_geral_brl
  FROM stg_credit_card_transactions
)
SELECT
  t.category,
  COUNT(*) AS quantidade_compras,
  SUM(t.amount_brl) AS total_gasto_brl,
  SUM(t.amount_usd) AS total_gasto_usd,
  ROUND((SUM(t.amount_brl) / NULLIF(MAX(total.total_geral_brl), 0)) * 100, 2) AS percentual_total_brl
FROM stg_credit_card_transactions t
CROSS JOIN total
GROUP BY t.category
ORDER BY total_gasto_brl DESC;