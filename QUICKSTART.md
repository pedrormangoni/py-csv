QUICKSTART (Linux)

Este guia traz apenas os comandos essenciais para rodar no Linux.

## 1) Preparar ambiente Python

Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r csv-ingestion/requirements.txt
```

## 2) Subir PostgreSQL com Docker

Na raiz do projeto:

```bash
docker compose up -d db
docker compose ps
```

## 3) Configurar variáveis de ambiente (Linux)

```bash
export POSTGRES_HOST=localhost
export POSTGRES_DB=credit-card
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_PORT=5433
```

Observação: no `docker-compose.yml`, o Postgres do container é exposto na porta `5433` do host.

## 4) Executar ETL

```bash
python csv-ingestion/main.py
```

## 5) Comandos úteis

Listar consultas disponíveis:

```bash
cd csv-ingestion
python -c "from app.pipeline.queries import listar_consultas; listar_consultas()"
cd ..
```

Executar consulta (gasto por categoria):

```bash
cd csv-ingestion
python -c "
import os
import psycopg2
from app.pipeline.queries import CONSULTAS

conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'credit-card'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
        port=os.getenv('POSTGRES_PORT', '5433')
)
cur = conn.cursor()
cur.execute(CONSULTAS['gasto_categoria']['query'])
for row in cur.fetchall():
        print(row)
conn.close()
"
cd ..
```

Conectar ao banco diretamente:

```bash
psql -h localhost -p 5433 -U postgres -d credit-card
```

## 6) Verificações rápidas

Verificar versão do Postgres:

```bash
psql -h localhost -p 5433 -U postgres -d credit-card -c "SELECT version();"
```

Contar registros carregados:

```bash
psql -h localhost -p 5433 -U postgres -d credit-card -c "
SELECT
        (SELECT COUNT(*) FROM fato_transacoes) AS transacoes,
        (SELECT COUNT(*) FROM dim_data) AS datas,
        (SELECT COUNT(*) FROM dim_cartao) AS cartoes;
"
```

Gasto total:

```bash
psql -h localhost -p 5433 -U postgres -d credit-card -c "
SELECT ROUND(SUM(valor_brl), 2) AS total_brl
FROM fato_transacoes;
"
```

## 7) Troubleshooting rápido (Linux)

- Erro `could not connect to server`:
    - Verifique containers: `docker compose ps`
    - Suba o banco: `docker compose up -d db`
- Erro `database "credit-card" does not exist`:
    - Crie no container: `docker exec -it postgres_db psql -U postgres -c 'CREATE DATABASE "credit-card";'`
- Erro `No module named psycopg2`:
    - Reative venv e reinstale dependências: `python -m pip install -r csv-ingestion/requirements.txt`



