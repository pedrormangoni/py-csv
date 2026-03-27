WITH totais AS (
  SELECT SUM(amount_brl) AS total_geral_brl
  FROM vw_base_transacoes
  WHERE amount_brl > 0
)
SELECT
  t.category,
  SUM(t.amount_brl) AS total_gasto_brl,
  COUNT(*) AS quantidade_compras,
  ROUND((SUM(t.amount_brl) / NULLIF(MAX(totais.total_geral_brl), 0)) * 100, 2) AS percentual_total
FROM vw_base_transacoes t
CROSS JOIN totais
WHERE t.amount_brl > 0
GROUP BY t.category
ORDER BY total_gasto_brl DESC;