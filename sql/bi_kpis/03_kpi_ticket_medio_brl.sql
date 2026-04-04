-- Arquivo: 03_kpi_ticket_medio_brl.sql
-- Objetivo: Calcular o ticket médio das compras em BRL.
-- Dependência: View `vw_base_transacoes`.
-- Saída: Uma linha com a coluna `kpi_ticket_medio_brl` arredondada em 2 casas.

SELECT ROUND(COALESCE(AVG(amount_brl), 0), 2) AS kpi_ticket_medio_brl
FROM vw_base_transacoes
WHERE amount_brl > 0;