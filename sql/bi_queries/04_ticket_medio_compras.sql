-- Arquivo: 04_ticket_medio_compras.sql
-- Objetivo: Calcular ticket médio das compras em BRL e USD.
-- Dependência: View `vw_base_transacoes`.
-- Saída: Uma linha com tickets médios e total de compras.

SELECT
  ROUND(AVG(amount_brl), 2) AS ticket_medio_brl,
  ROUND(AVG(amount_usd), 2) AS ticket_medio_usd,
  COUNT(*) AS total_compras
FROM vw_base_transacoes
WHERE amount_brl > 0;