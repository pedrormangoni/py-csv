SELECT ROUND(COALESCE(AVG(amount_brl), 0), 2) AS kpi_ticket_medio_brl
FROM stg_credit_card_transactions;