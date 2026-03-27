import os

THEME_NAME = os.getenv("DW_THEME_NAME", "credit_card")
STAGING_TRANSACTIONS_TABLE = os.getenv("DW_STAGING_TRANSACTIONS_TABLE", "stg_credit_card_transactions")
SQL_BASE_VIEW_NAME = os.getenv("DW_SQL_BASE_VIEW_NAME", "vw_base_transacoes")

EXPECTED_COLUMNS = [
    "Data de Compra",
    "Nome no Cartão",
    "Final do Cartão",
    "Categoria",
    "Descrição",
    "Parcela",
    "Valor (em US$)",
    "Cotação (em R$)",
    "Valor (em R$)",
]

FILE_DELIMITER = ";"