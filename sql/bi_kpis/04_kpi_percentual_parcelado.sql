-- Arquivo: 04_kpi_percentual_parcelado.sql
-- Objetivo: Medir o percentual de compras parceladas sobre o total de compras.
-- Dependência: View `vw_base_transacoes` e campos de parcelamento.
-- Saída: Uma linha com a coluna `kpi_percentual_compras_parceladas` em percentual.

SELECT
  ROUND(
    COALESCE(
      100.0 * SUM(CASE WHEN COALESCE(installment_total, 1) > 1 THEN 1 ELSE 0 END)
      / NULLIF(COUNT(*), 0),
      0
    ),
    2
  ) AS kpi_percentual_compras_parceladas
FROM vw_base_transacoes
WHERE amount_brl > 0;