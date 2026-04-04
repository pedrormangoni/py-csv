-- Arquivo: 06_kpi_categoria_lider.sql
-- Objetivo: Encontrar a categoria com maior gasto total em BRL.
-- Dependência: View `vw_base_transacoes` e coluna `category`.
-- Saída: Uma linha com `kpi_categoria_lider` e `kpi_valor_categoria_lider_brl`.

SELECT
  category AS kpi_categoria_lider,
  total_gasto_brl AS kpi_valor_categoria_lider_brl
FROM (
  SELECT
    category,
    SUM(amount_brl) AS total_gasto_brl
  FROM vw_base_transacoes
  WHERE amount_brl > 0
  GROUP BY 1
) base
ORDER BY total_gasto_brl DESC, category ASC
LIMIT 1;