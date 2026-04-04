QUICKSTART (Linux)

Comandos essenciais para rodar ETL + SQL analítico + dashboard.

## 1) Preparar ambiente Python

Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r csv-ingestion/requirements.txt
```

## 2) Subir PostgreSQL com Docker

```bash
docker compose up -d db
docker compose ps
```

## 3) Variáveis de ambiente (execução local)

```bash
export POSTGRES_HOST=localhost
export POSTGRES_DB=credit-card
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_PORT=5433
```

Observação:
- `db:5432` funciona para processos dentro do Docker.
- `localhost:5433` é o acesso do host (seu terminal local).

## 4) Executar ETL

```bash
python csv-ingestion/main.py
```

## 5) Aplicar camada SQL de BI

```bash
cd sql/bi_views
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_views.sql

cd ../bi_kpis
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_kpis.sql
```

## 6) Subir dashboard

```bash
streamlit run dashboard/streamlit_app.py
```

Acesse em: `http://localhost:8501`

## 7) Verificações rápidas

Contagem da base carregada:

```bash
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -c "
SELECT COUNT(*) AS total_linhas
FROM stg_credit_card_transactions;
"
```

Verificar se views foram aplicadas:

```bash
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -c "
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public'
  AND table_name IN ('vw_base_transacoes', 'vw_gastos_mensais', 'vw_parcelamento');
"
```

## 8) Troubleshooting rápido

- Erro `could not translate host name "db"` no Streamlit:
  - rode no host com `POSTGRES_HOST=localhost` e `POSTGRES_PORT=5433`.
- Erro `streamlit run yourscript.py`:
  - use o script correto: `streamlit run dashboard/streamlit_app.py`.
- Erro `relation "vw_*" does not exist`:
  - reaplique `00_apply_all_views.sql` e `00_apply_all_kpis.sql`.
