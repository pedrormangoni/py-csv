CREATE OR REPLACE VIEW vw_frequencia_categoria_mensal AS
SELECT
  DATE_TRUNC('month', purchase_date)::date AS mes,
  category,
  COUNT(*) AS frequencia_compras,
  SUM(amount_brl) AS total_gasto_brl,
  ROUND(AVG(amount_brl), 2) AS ticket_medio_brl
FROM stg_credit_card_transactions
WHERE amount_brl > 0
GROUP BY 1, 2
ORDER BY 1, frequencia_compras DESC, total_gasto_brl DESC;