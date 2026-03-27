# ETL de CSV + Camada Analítica SQL + Dashboard

Projeto para ingestão de faturas CSV de cartão, tratamento de dados e consumo analítico via SQL e Streamlit.

## Arquitetura (resumo)

1. Entrada de CSVs em `csv-ingestion/app/datas/unread/`.
2. ETL valida, normaliza, remove pagamentos e carrega `stg_credit_card_transactions`.
3. Camada SQL cria uma base desacoplada (`vw_base_transacoes`) e views analíticas.
4. KPIs e dashboard consomem as views.

## Padronização de tema/fonte

A troca da fonte analítica foi centralizada:

- ETL usa configurações em `csv-ingestion/app/api/config.py`:
  - `DW_THEME_NAME`
  - `DW_STAGING_TRANSACTIONS_TABLE`
  - `DW_SQL_BASE_VIEW_NAME`
- SQL analítico usa `vw_base_transacoes`.
- Para trocar a origem dos SQLs, altere apenas `sql/bi_views/00_vw_base_transacoes.sql`.

## Pré-requisitos

- Docker + Docker Compose
- Python 3.11+

## Variáveis de ambiente

Arquivo `.env` na raiz (padrão para Docker):

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=credit-card
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Para execução local (host), use:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

## Execução rápida

### 1) Instalar dependências

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r csv-ingestion/requirements.txt
```

### 2) Subir banco

```bash
docker compose up -d db
```

### 3) Rodar ETL

```bash
python csv-ingestion/main.py
```

### 4) Aplicar SQL de BI

```bash
cd sql/bi_views
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_views.sql

cd ../bi_kpis
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_kpis.sql
```

### 5) Subir dashboard

```bash
streamlit run dashboard/streamlit_app.py
```

Acesse: `http://localhost:8501`

## Estrutura SQL

- `sql/bi_views`: views para consumo analítico (inclui `vw_base_transacoes`).
- `sql/bi_kpis`: consultas de KPI para cards.
- `sql/bi_queries`: consultas de negócio.
- `sql/bi_quality`: checks de qualidade.

## Testes

```bash
cd csv-ingestion
/home/pedro/Documents/py-csv/.venv/bin/python -m pytest -q
```
