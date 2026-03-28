-- Arquivo: 05_kpi_mes_maior_gasto.sql
-- Objetivo: Identificar o mês com maior gasto agregado em BRL.
-- Dependência: View `vw_base_transacoes` e coluna `purchase_date`.
-- Saída: Uma linha com `kpi_mes_maior_gasto` e `kpi_valor_mes_maior_gasto_brl`.

SELECT
  mes AS kpi_mes_maior_gasto,
  total_gasto_brl AS kpi_valor_mes_maior_gasto_brl
FROM (
  SELECT
    DATE_TRUNC('month', purchase_date)::date AS mes,
    SUM(amount_brl) AS total_gasto_brl
  FROM vw_base_transacoes
  WHERE amount_brl > 0
  GROUP BY 1
) base
ORDER BY total_gasto_brl DESC, mes ASC
LIMIT 1;