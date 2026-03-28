-- Arquivo: 00_apply_all_quality_checks.sql
-- Objetivo: Executar, em sequência, todas as consultas de verificação de qualidade de dados.
-- Dependência: Scripts `01` a `08` da pasta `bi_quality` e a view `vw_base_transacoes`.
-- Saída: Resultados de checagens de qualidade para diagnóstico operacional.

\i 01_qc_contagem_geral.sql
\i 02_qc_nulos_vazios.sql
\i 03_qc_duplicidade_potencial.sql
\i 04_qc_consistencia_cambial.sql
\i 05_qc_parcelamento_inconsistente.sql
\i 06_qc_categorias_semelhantes.sql
\i 07_qc_outliers_valor.sql
\i 08_qc_resumo_status.sql