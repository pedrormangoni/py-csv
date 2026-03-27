WITH stats AS (
  SELECT
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY amount_brl) AS q1,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY amount_brl) AS q3
  FROM vw_base_transacoes
),
limites AS (
  SELECT
    q1,
    q3,
    (q3 - q1) AS iqr,
    (q1 - 1.5 * (q3 - q1)) AS limite_inferior,
    (q3 + 1.5 * (q3 - q1)) AS limite_superior
  FROM stats
)
SELECT
  t.id,
  t.source_file_name,
  t.row_number,
  t.purchase_date,
  t.category,
  t.description,
  t.amount_brl,
  l.limite_inferior,
  l.limite_superior
FROM vw_base_transacoes t
CROSS JOIN limites l
WHERE t.amount_brl < l.limite_inferior OR t.amount_brl > l.limite_superior
ORDER BY t.amount_brl DESC, t.purchase_date DESC;