SELECT 'purchase_date' AS campo, COUNT(*) AS qtde_invalidos
FROM vw_base_transacoes
WHERE purchase_date IS NULL
UNION ALL
SELECT 'cardholder_name', COUNT(*)
FROM vw_base_transacoes
WHERE cardholder_name IS NULL OR BTRIM(cardholder_name) = ''
UNION ALL
SELECT 'card_last4', COUNT(*)
FROM vw_base_transacoes
WHERE card_last4 IS NULL OR BTRIM(card_last4) = ''
UNION ALL
SELECT 'category', COUNT(*)
FROM vw_base_transacoes
WHERE category IS NULL OR BTRIM(category) = ''
UNION ALL
SELECT 'description', COUNT(*)
FROM vw_base_transacoes
WHERE description IS NULL OR BTRIM(description) = ''
UNION ALL
SELECT 'installment_raw', COUNT(*)
FROM vw_base_transacoes
WHERE installment_raw IS NULL OR BTRIM(installment_raw) = ''
UNION ALL
SELECT 'amount_usd', COUNT(*)
FROM vw_base_transacoes
WHERE amount_usd IS NULL
UNION ALL
SELECT 'fx_rate_brl', COUNT(*)
FROM vw_base_transacoes
WHERE fx_rate_brl IS NULL
UNION ALL
SELECT 'amount_brl', COUNT(*)
FROM vw_base_transacoes
WHERE amount_brl IS NULL
ORDER BY campo;