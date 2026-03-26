SELECT
  ROUND(AVG(amount_brl), 2) AS ticket_medio_brl,
  ROUND(AVG(amount_usd), 2) AS ticket_medio_usd,
  COUNT(*) AS total_compras
FROM stg_credit_card_transactions
WHERE amount_brl > 0;