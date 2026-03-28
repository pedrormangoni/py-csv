-- Arquivo: 04_vw_fx_impacto_mensal.sql
-- Objetivo: Disponibilizar visão mensal do impacto cambial nas compras internacionais.
-- Dependência: View `vw_base_transacoes` e campos de câmbio.
-- Saída: View `vw_fx_impacto_mensal` com USD, cotação, BRL real/calculado e diferença.

CREATE OR REPLACE VIEW vw_fx_impacto_mensal AS
SELECT
  DATE_TRUNC('month', purchase_date)::date AS mes,
  SUM(amount_usd) AS total_usd,
  ROUND(AVG(fx_rate_brl), 4) AS cotacao_media,
  SUM(amount_brl) AS total_brl_real,
  ROUND(SUM(amount_usd * fx_rate_brl), 2) AS total_brl_calculado,
  ROUND(SUM(amount_brl - (amount_usd * fx_rate_brl)), 2) AS diferenca_brl
FROM vw_base_transacoes
WHERE amount_usd > 0
  AND amount_brl > 0
GROUP BY 1
ORDER BY 1;