SELECT
  DATE_TRUNC('month', purchase_date)::date AS mes,
  SUM(amount_brl) AS total_gasto_brl,
  SUM(amount_usd) AS total_gasto_usd,
  COUNT(*) AS quantidade_compras
FROM stg_credit_card_transactions
WHERE amount_brl > 0
GROUP BY 1
ORDER BY 1;