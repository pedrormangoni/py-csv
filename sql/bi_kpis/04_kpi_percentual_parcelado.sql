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