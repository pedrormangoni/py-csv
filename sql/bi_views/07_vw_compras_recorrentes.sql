-- Arquivo: 07_vw_compras_recorrentes.sql
-- Objetivo: Sinalizar padrões de compras recorrentes por descrição, categoria, cartão e valor.
-- Dependência: View `vw_base_transacoes`.
-- Saída: View `vw_compras_recorrentes` com quantidade de ocorrências e periodicidade média.

CREATE OR REPLACE VIEW vw_compras_recorrentes AS
WITH recorrencia AS (
    SELECT
        recurring_signature,
        MIN(description) AS descricao_base,
        MIN(category) AS categoria,
        MIN(cardholder_name) AS nome_cartao,
        MIN(card_last4) AS final_cartao,
        ROUND(AVG(amount_brl), 2) AS valor_medio_brl,
        COUNT(*) AS quantidade_ocorrencias,
        MIN(purchase_date) AS primeira_compra,
        MAX(purchase_date) AS ultima_compra,
        SUM(amount_brl) AS total_gasto_brl
    FROM vw_base_transacoes
    GROUP BY recurring_signature
    HAVING COUNT(*) > 1
)
SELECT
    recurring_signature,
    descricao_base,
    categoria,
    nome_cartao,
    final_cartao,
    valor_medio_brl,
    quantidade_ocorrencias,
    primeira_compra,
    ultima_compra,
    CASE
        WHEN quantidade_ocorrencias > 1 THEN ROUND(
            ((ultima_compra - primeira_compra)::NUMERIC / (quantidade_ocorrencias - 1)),
            1
        )
        ELSE NULL
    END AS media_dias_entre_compras,
    total_gasto_brl
FROM recorrencia
ORDER BY quantidade_ocorrencias DESC, total_gasto_brl DESC;
