-- Arquivo: 08_qc_resumo_status.sql
-- Objetivo: Consolidar indicadores de qualidade em um status único de monitoramento.
-- Dependência: View `vw_base_transacoes` e CTEs de validação de nulidade, câmbio e parcelamento.
-- Saída: Uma linha com totais e flags de criticidade para data quality.

WITH total AS (
  SELECT COUNT(*) AS total_linhas
  FROM vw_base_transacoes
),
invalidos AS (
  SELECT COUNT(*) AS total_invalidos
  FROM vw_base_transacoes
  WHERE
    purchase_date IS NULL
    OR cardholder_name IS NULL OR BTRIM(cardholder_name) = ''
    OR card_last4 IS NULL OR BTRIM(card_last4) = ''
    OR category IS NULL OR BTRIM(category) = ''
    OR description IS NULL OR BTRIM(description) = ''
    OR installment_raw IS NULL OR BTRIM(installment_raw) = ''
    OR amount_usd IS NULL
    OR fx_rate_brl IS NULL
    OR amount_brl IS NULL
),
fx_inconsistente AS (
  SELECT COUNT(*) AS total_fx_inconsistente
  FROM vw_base_transacoes
  WHERE ABS(amount_brl - (amount_usd * fx_rate_brl)) > 0.05
),
parcela_inconsistente AS (
  SELECT COUNT(*) AS total_parcela_inconsistente
  FROM vw_base_transacoes
  WHERE
    (installment_total IS NOT NULL AND installment_total <= 0)
    OR (installment_number IS NOT NULL AND installment_number <= 0)
    OR (installment_number IS NOT NULL AND installment_total IS NOT NULL AND installment_number > installment_total)
    OR (
      LOWER(BTRIM(installment_raw)) IN ('única', 'unica')
      AND (installment_number IS NOT NULL OR installment_total IS NOT NULL)
    )
)
SELECT
  total.total_linhas,
  invalidos.total_invalidos,
  fx_inconsistente.total_fx_inconsistente,
  parcela_inconsistente.total_parcela_inconsistente,
  ROUND(
    COALESCE(100.0 * invalidos.total_invalidos / NULLIF(total.total_linhas, 0), 0),
    2
  ) AS percentual_invalidos
FROM total
CROSS JOIN invalidos
CROSS JOIN fx_inconsistente
CROSS JOIN parcela_inconsistente;