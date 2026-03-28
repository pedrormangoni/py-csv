-- Arquivo: 01_qc_contagem_geral.sql
-- Objetivo: Gerar visão geral do volume carregado (linhas, arquivos e intervalo de datas).
-- Dependência: View `vw_base_transacoes`.
-- Saída: Uma linha com métricas macro de cobertura dos dados.

SELECT
  COUNT(*) AS total_linhas,
  COUNT(DISTINCT source_file_name) AS total_arquivos,
  MIN(purchase_date) AS data_minima,
  MAX(purchase_date) AS data_maxima
FROM vw_base_transacoes;