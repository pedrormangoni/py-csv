SELECT
  COUNT(*) AS total_linhas,
  COUNT(DISTINCT source_file_name) AS total_arquivos,
  MIN(purchase_date) AS data_minima,
  MAX(purchase_date) AS data_maxima
FROM vw_base_transacoes;