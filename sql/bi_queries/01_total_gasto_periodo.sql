SELECT
  MIN(purchase_date) AS data_inicial,
  MAX(purchase_date) AS data_final,
  SUM(amount_brl) AS total_gasto_brl,
  SUM(amount_usd) AS total_gasto_usd,
  COUNT(*) AS total_compras
FROM stg_credit_card_transactions
WHERE amount_brl > 0;