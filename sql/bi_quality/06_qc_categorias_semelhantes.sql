SELECT
  LOWER(BTRIM(category)) AS categoria_normalizada,
  COUNT(DISTINCT category) AS variacoes_texto,
  STRING_AGG(DISTINCT category, ' | ' ORDER BY category) AS exemplos_categoria,
  COUNT(*) AS total_registros
FROM vw_base_transacoes
GROUP BY LOWER(BTRIM(category))
HAVING COUNT(DISTINCT category) > 1
ORDER BY variacoes_texto DESC, total_registros DESC;