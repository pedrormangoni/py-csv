-- Arquivo: 06_vw_gastos_semanais_mes.sql
-- Objetivo: Identificar as semanas com maior volume e valor de gastos em cada mês.
-- Dependência: View `vw_base_transacoes`.
-- Saída: View `vw_gastos_semanais_mes` com ranking semanal por mês.

CREATE OR REPLACE VIEW vw_gastos_semanais_mes AS
WITH semanal AS (
    SELECT
        purchase_year,
        purchase_month_number,
        purchase_month,
        purchase_week,
        purchase_year_week,
        COUNT(*) AS quantidade_compras,
        SUM(amount_brl) AS total_gasto_brl,
        ROUND(AVG(amount_brl), 2) AS ticket_medio_brl
    FROM vw_base_transacoes
    GROUP BY 1, 2, 3, 4, 5
)
SELECT
    purchase_year,
    purchase_month_number,
    purchase_month,
    purchase_week,
    purchase_year_week,
    quantidade_compras,
    total_gasto_brl,
    ticket_medio_brl,
    RANK() OVER (
        PARTITION BY purchase_year, purchase_month_number
        ORDER BY total_gasto_brl DESC, quantidade_compras DESC, purchase_week ASC
    ) AS ranking_semana_no_mes
FROM semanal
ORDER BY purchase_week;
