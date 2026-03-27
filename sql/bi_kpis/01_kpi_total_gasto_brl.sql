SELECT COALESCE(SUM(amount_brl), 0) AS kpi_total_gasto_brl
FROM vw_base_transacoes
WHERE amount_brl > 0;