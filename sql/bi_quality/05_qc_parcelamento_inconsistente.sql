-- Arquivo: 05_qc_parcelamento_inconsistente.sql
-- Objetivo: Identificar inconsistências em informações de parcelamento e compra única.
-- Dependência: View `vw_base_transacoes` e campos de parcela (`installment_*`).
-- Saída: Registros com regras de parcelamento inválidas.

SELECT
  id,
  source_file_name,
  row_number,
  purchase_date,
  installment_raw,
  installment_number,
  installment_total
FROM vw_base_transacoes
WHERE
  (installment_total IS NOT NULL AND installment_total <= 0)
  OR (installment_number IS NOT NULL AND installment_number <= 0)
  OR (installment_number IS NOT NULL AND installment_total IS NOT NULL AND installment_number > installment_total)
  OR (
    LOWER(BTRIM(installment_raw)) IN ('única', 'unica')
    AND (installment_number IS NOT NULL OR installment_total IS NOT NULL)
  )
ORDER BY purchase_date DESC, source_file_name, row_number;