SELECT COALESCE(SUM(amount_usd), 0) AS kpi_total_gasto_usd
FROM vw_base_transacoes
WHERE amount_brl > 0;