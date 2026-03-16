SELECT
  DATE_TRUNC('month', purchase_date)::date AS mes,
  category,
  COUNT(*) AS frequencia_compras,
  SUM(amount_brl) AS total_gasto_brl
FROM stg_credit_card_transactions
GROUP BY 1, 2
ORDER BY 1, frequencia_compras DESC, total_gasto_brl DESC;