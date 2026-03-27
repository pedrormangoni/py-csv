WITH base AS (
  SELECT
    COUNT(*) AS qtd_compras,
    COALESCE(SUM(amount_brl), 0) AS total_brl,
    COALESCE(SUM(amount_usd), 0) AS total_usd,
    ROUND(COALESCE(AVG(amount_brl), 0), 2) AS ticket_medio_brl,
    ROUND(
      COALESCE(
        100.0 * SUM(CASE WHEN COALESCE(installment_total, 1) > 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        0
      ),
      2
    ) AS percentual_parcelado
  FROM vw_base_transacoes
  WHERE amount_brl > 0
),
mes_top AS (
  SELECT
    DATE_TRUNC('month', purchase_date)::date AS mes,
    SUM(amount_brl) AS valor
  FROM vw_base_transacoes
  WHERE amount_brl > 0
  GROUP BY 1
  ORDER BY valor DESC, mes ASC
  LIMIT 1
),
categoria_top AS (
  SELECT
    category,
    SUM(amount_brl) AS valor
  FROM vw_base_transacoes
  WHERE amount_brl > 0
  GROUP BY 1
  ORDER BY valor DESC, category ASC
  LIMIT 1
)
SELECT
  base.qtd_compras AS kpi_quantidade_compras,
  base.total_brl AS kpi_total_gasto_brl,
  base.total_usd AS kpi_total_gasto_usd,
  base.ticket_medio_brl AS kpi_ticket_medio_brl,
  base.percentual_parcelado AS kpi_percentual_compras_parceladas,
  mes_top.mes AS kpi_mes_maior_gasto,
  mes_top.valor AS kpi_valor_mes_maior_gasto_brl,
  categoria_top.category AS kpi_categoria_lider,
  categoria_top.valor AS kpi_valor_categoria_lider_brl
FROM base
LEFT JOIN mes_top ON TRUE
LEFT JOIN categoria_top ON TRUE;