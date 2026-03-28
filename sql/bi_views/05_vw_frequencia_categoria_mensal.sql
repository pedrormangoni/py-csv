-- Arquivo: 05_vw_frequencia_categoria_mensal.sql
-- Objetivo: Criar visão mensal da frequência de compras por categoria.
-- Dependência: View `vw_base_transacoes` e colunas de tempo/categoria.
-- Saída: View `vw_frequencia_categoria_mensal` com frequência, total e ticket por mês/categoria.

CREATE OR REPLACE VIEW vw_frequencia_categoria_mensal AS
SELECT
  DATE_TRUNC('month', purchase_date)::date AS mes,
  category,
  COUNT(*) AS frequencia_compras,
  SUM(amount_brl) AS total_gasto_brl,
  ROUND(AVG(amount_brl), 2) AS ticket_medio_brl
FROM vw_base_transacoes
WHERE amount_brl > 0
GROUP BY 1, 2
ORDER BY 1, frequencia_compras DESC, total_gasto_brl DESC;