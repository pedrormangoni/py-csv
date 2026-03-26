CREATE OR REPLACE VIEW vw_gastos_mensais AS
SELECT
  DATE_TRUNC('month', purchase_date)::date AS mes,
  COUNT(*) AS quantidade_compras,
  SUM(amount_brl) AS total_gasto_brl,
  SUM(amount_usd) AS total_gasto_usd,
  ROUND(AVG(amount_brl), 2) AS ticket_medio_brl
FROM stg_credit_card_transactions
WHERE amount_brl > 0
GROUP BY 1
ORDER BY 1;