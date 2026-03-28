-- Arquivo: 00_vw_base_transacoes.sql
-- Objetivo: Definir a view base de transações a partir da staging consolidada.
-- Dependência: Tabela `stg_credit_card_transactions`.
-- Saída: View `vw_base_transacoes` com os campos originais de transação.

CREATE OR REPLACE VIEW vw_base_transacoes AS
SELECT *
FROM stg_credit_card_transactions;
