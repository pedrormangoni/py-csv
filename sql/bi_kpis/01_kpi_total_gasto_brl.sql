SELECT COALESCE(SUM(amount_brl), 0) AS kpi_total_gasto_brl
FROM stg_credit_card_transactions;