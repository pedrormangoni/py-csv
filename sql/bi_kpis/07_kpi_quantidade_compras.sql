SELECT COUNT(*) AS kpi_quantidade_compras
FROM stg_credit_card_transactions
WHERE amount_brl > 0;