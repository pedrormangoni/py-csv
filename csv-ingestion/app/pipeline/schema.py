"""
Modelo analítico para responder as perguntas do escopo de BI.

O projeto já carrega os dados normalizados na staging
`stg_credit_card_transactions`. A partir dela, este módulo define uma camada
semântica em formato estrela baseada em views:

- `vw_dim_tempo`
- `vw_dim_cartao`
- `vw_dim_categoria`
- `vw_dim_parcelamento`
- `vw_fato_transacoes`

Essa abordagem mantém o ETL simples e prepara o banco para Power BI, SQL e
análises exploratórias sem duplicar dados físicos.
"""

from __future__ import annotations

import os


CREATE_ANALYTICAL_MODEL_SQL = """
CREATE OR REPLACE VIEW vw_dim_tempo AS
SELECT DISTINCT
    purchase_date AS data,
    EXTRACT(YEAR FROM purchase_date)::INTEGER AS ano,
    EXTRACT(MONTH FROM purchase_date)::INTEGER AS mes,
    TO_CHAR(purchase_date, 'YYYY-MM') AS ano_mes,
    DATE_TRUNC('month', purchase_date)::DATE AS inicio_mes,
    DATE_TRUNC('week', purchase_date)::DATE AS inicio_semana,
    EXTRACT(WEEK FROM purchase_date)::INTEGER AS semana_ano,
    EXTRACT(ISODOW FROM purchase_date)::INTEGER AS dia_semana_numero,
    TO_CHAR(purchase_date, 'TMDay') AS dia_semana_nome,
    EXTRACT(QUARTER FROM purchase_date)::INTEGER AS trimestre,
    CASE
        WHEN EXTRACT(ISODOW FROM purchase_date) IN (6, 7) THEN TRUE
        ELSE FALSE
    END AS eh_fim_semana
FROM vw_base_transacoes;

CREATE OR REPLACE VIEW vw_dim_cartao AS
SELECT DISTINCT
    CONCAT(cardholder_name, ' • ', card_last4) AS cartao_sk,
    cardholder_name,
    card_last4
FROM vw_base_transacoes;

CREATE OR REPLACE VIEW vw_dim_categoria AS
SELECT DISTINCT
    LOWER(REGEXP_REPLACE(TRIM(category), '\\s+', ' ', 'g')) AS categoria_sk,
    category AS categoria,
    INITCAP(category) AS categoria_apresentacao
FROM vw_base_transacoes;

CREATE OR REPLACE VIEW vw_dim_parcelamento AS
SELECT DISTINCT
    CASE
        WHEN COALESCE(installment_total, 1) > 1 THEN 'parcelada'
        ELSE 'a_vista'
    END AS tipo_compra,
    COALESCE(installment_total, 1) AS total_parcelas,
    CASE
        WHEN COALESCE(installment_total, 1) > 1 THEN TRUE
        ELSE FALSE
    END AS eh_parcelada
FROM vw_base_transacoes;

CREATE OR REPLACE VIEW vw_fato_transacoes AS
SELECT
    id AS transacao_id,
    purchase_date AS data,
    TO_CHAR(purchase_date, 'YYYY-MM') AS ano_mes,
    DATE_TRUNC('week', purchase_date)::DATE AS inicio_semana,
    CONCAT(cardholder_name, ' • ', card_last4) AS cartao_sk,
    LOWER(REGEXP_REPLACE(TRIM(category), '\\s+', ' ', 'g')) AS categoria_sk,
    category AS categoria,
    description AS descricao,
    installment_raw,
    COALESCE(installment_number, 1) AS numero_parcela,
    COALESCE(installment_total, 1) AS total_parcelas,
    CASE
        WHEN COALESCE(installment_total, 1) > 1 THEN 'parcelada'
        ELSE 'a_vista'
    END AS tipo_compra,
    amount_usd,
    fx_rate_brl,
    amount_brl,
    CASE
        WHEN amount_usd > 0 THEN ROUND(amount_brl - (amount_usd * fx_rate_brl), 2)
        ELSE 0
    END AS impacto_cambial_brl,
    source_file_name,
    loaded_at
FROM vw_base_transacoes;
"""


def create_analytical_model(conn) -> None:
    """Cria a camada semântica analítica baseada em views."""
    cur = conn.cursor()
    try:
        for statement in CREATE_ANALYTICAL_MODEL_SQL.split(";"):
            sql = statement.strip()
            if sql:
                cur.execute(sql)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


if __name__ == "__main__":
    import psycopg2

    connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "credit-card"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )
    try:
        create_analytical_model(connection)
        print("Modelo analítico criado com sucesso.")
    finally:
        connection.close()
