SELECT
  DATE_TRUNC('month', purchase_date)::date AS mes,
  category,
  COUNT(*) AS frequencia_compras,
  SUM(amount_brl) AS total_gasto_brl
FROM vw_base_transacoes
WHERE amount_brl > 0
GROUP BY 1, 2
ORDER BY 1, frequencia_compras DESC, total_gasto_brl DESC;