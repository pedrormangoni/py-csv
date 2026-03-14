import os
import psycopg2
from app.api.upload import transfer_csv_files

# conn = psycopg2.connect(
#     host=os.getenv("POSTGRES_HOST"),
#     database=os.getenv("POSTGRES_DB"),
#     user=os.getenv("POSTGRES_USER"),
#     password=os.getenv("POSTGRES_PASSWORD"),
#     port=os.getenv("POSTGRES_PORT")
# )

# print("Conectado ao PostgreSQL!")

# cur = conn.cursor()
# cur.execute("SELECT version();")

# version = cur.fetchone()
# print("Versão do Postgres:", version)

# cur.close()
# conn.close()

# Executa a transferência dos arquivos CSV
transfer_csv_files()