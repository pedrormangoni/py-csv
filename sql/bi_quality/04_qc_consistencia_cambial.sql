SELECT
  id,
  source_file_name,
  row_number,
  purchase_date,
  amount_usd,
  fx_rate_brl,
  amount_brl,
  ROUND((amount_usd * fx_rate_brl)::numeric, 2) AS amount_brl_calculado,
  ROUND((amount_brl - (amount_usd * fx_rate_brl))::numeric, 2) AS diferenca_brl
FROM stg_credit_card_transactions
WHERE ABS(amount_brl - (amount_usd * fx_rate_brl)) > 0.05
ORDER BY ABS(amount_brl - (amount_usd * fx_rate_brl)) DESC, purchase_date DESC;