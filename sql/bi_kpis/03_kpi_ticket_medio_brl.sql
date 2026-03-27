SELECT ROUND(COALESCE(AVG(amount_brl), 0), 2) AS kpi_ticket_medio_brl
FROM vw_base_transacoes
WHERE amount_brl > 0;