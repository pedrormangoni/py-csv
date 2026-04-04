-- Arquivo: 05_compras_parceladas_impacto.sql
-- Objetivo: Comparar impacto financeiro entre compras parceladas e à vista.
-- Dependência: View `vw_base_transacoes` e campo `installment_total`.
-- Saída: Métricas por `tipo_compra` (quantidade, total e ticket médio).

SELECT
  CASE
    WHEN COALESCE(installment_total, 1) > 1 THEN 'parcelada'
    ELSE 'a_vista'
  END AS tipo_compra,
  COUNT(*) AS quantidade_compras,
  SUM(amount_brl) AS total_gasto_brl,
  ROUND(AVG(amount_brl), 2) AS ticket_medio_brl
FROM vw_base_transacoes
WHERE amount_brl > 0
GROUP BY 1
ORDER BY total_gasto_brl DESC;