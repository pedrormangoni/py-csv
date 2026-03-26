SELECT COALESCE(SUM(amount_usd), 0) AS kpi_total_gasto_usd
FROM stg_credit_card_transactions
WHERE amount_brl > 0;