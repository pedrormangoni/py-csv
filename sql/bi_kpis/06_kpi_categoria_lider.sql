SELECT
  category AS kpi_categoria_lider,
  total_gasto_brl AS kpi_valor_categoria_lider_brl
FROM (
  SELECT
    category,
    SUM(amount_brl) AS total_gasto_brl
  FROM stg_credit_card_transactions
  GROUP BY 1
) base
ORDER BY total_gasto_brl DESC, category ASC
LIMIT 1;