SELECT
  purchase_date,
  cardholder_name,
  card_last4,
  category,
  description,
  installment_raw,
  amount_usd,
  fx_rate_brl,
  amount_brl,
  COUNT(*) AS repeticoes
FROM vw_base_transacoes
GROUP BY
  purchase_date,
  cardholder_name,
  card_last4,
  category,
  description,
  installment_raw,
  amount_usd,
  fx_rate_brl,
  amount_brl
HAVING COUNT(*) > 1
ORDER BY repeticoes DESC, purchase_date DESC;