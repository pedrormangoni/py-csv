SELECT
  id,
  source_file_name,
  row_number,
  purchase_date,
  installment_raw,
  installment_number,
  installment_total
FROM stg_credit_card_transactions
WHERE
  (installment_total IS NOT NULL AND installment_total <= 0)
  OR (installment_number IS NOT NULL AND installment_number <= 0)
  OR (installment_number IS NOT NULL AND installment_total IS NOT NULL AND installment_number > installment_total)
  OR (
    LOWER(BTRIM(installment_raw)) IN ('única', 'unica')
    AND (installment_number IS NOT NULL OR installment_total IS NOT NULL)
  )
ORDER BY purchase_date DESC, source_file_name, row_number;