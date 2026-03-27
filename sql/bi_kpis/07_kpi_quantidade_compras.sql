SELECT COUNT(*) AS kpi_quantidade_compras
FROM vw_base_transacoes
WHERE amount_brl > 0;