-- Arquivo: 02_evolucao_mensal_gastos.sql
-- Objetivo: Exibir a evolução mensal de gastos e volume de compras.
-- Dependência: View `vw_base_transacoes` e coluna `purchase_date`.
-- Saída: Série temporal mensal com totais BRL/USD e quantidade de compras.

SELECT
  DATE_TRUNC('month', purchase_date)::date AS mes,
  SUM(amount_brl) AS total_gasto_brl,
  SUM(amount_usd) AS total_gasto_usd,
  COUNT(*) AS quantidade_compras
FROM vw_base_transacoes
WHERE amount_brl > 0
GROUP BY 1
ORDER BY 1;