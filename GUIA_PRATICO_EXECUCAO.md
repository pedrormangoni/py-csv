# Guia Prático de Execução

Guia único para rodar ETL, camada SQL e dashboard com a arquitetura atual do projeto.

## 1) Preparação

Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r csv-ingestion/requirements.txt
```

## 2) Banco PostgreSQL

Subir apenas o banco:

```bash
docker compose up -d db
docker compose ps
```

Conexão esperada no host:
- Host: `localhost`
- Porta: `5433`
- Database: `credit-card`
- User: `postgres`

## 3) Variáveis de ambiente

### Padrão Docker (`.env`)

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=credit-card
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Execução local (terminal do host)

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5433
export POSTGRES_DB=credit-card
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
```

## 4) Executar ETL

```bash
python csv-ingestion/main.py
```

O ETL:
- valida cabeçalho,
- normaliza campos,
- ignora linhas de pagamento/valores negativos,
- carrega em `stg_credit_card_transactions`.

## 5) Aplicar SQL analítico

```bash
cd sql/bi_views
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_views.sql

cd ../bi_kpis
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_kpis.sql
```

## 6) Executar Dashboard (Streamlit)

```bash
streamlit run dashboard/streamlit_app.py
```

Acesse:

```text
http://localhost:8501
```

## 7) Verificações úteis

### Banco acessível

```bash
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -c "SELECT version();"
```

### Linhas carregadas no staging

```bash
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -c "
SELECT COUNT(*) AS total_linhas
FROM stg_credit_card_transactions;
"
```

### Views principais criadas

```bash
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -c "
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public'
  AND table_name IN (
    'vw_base_transacoes',
    'vw_gastos_mensais',
    'vw_gastos_categoria',
    'vw_parcelamento',
    'vw_fx_impacto_mensal',
    'vw_frequencia_categoria_mensal'
  )
ORDER BY table_name;
"
```

## 8) Padronização para troca de tema/fonte

### ETL (config central)

Arquivo: `csv-ingestion/app/api/config.py`

- `DW_THEME_NAME`
- `DW_STAGING_TRANSACTIONS_TABLE`
- `DW_SQL_BASE_VIEW_NAME`

### SQL (desacoplamento da tabela física)

Todos os SQLs analíticos usam `vw_base_transacoes`.

Para trocar a fonte dos dashboards, altere apenas:

- `sql/bi_views/00_vw_base_transacoes.sql`

## 9) Troubleshooting

### Erro: `could not translate host name "db"`

Causa: app rodando no host com host de Docker interno.

Solução:

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5433
```

### Erro: `streamlit run yourscript.py` falha

Causa: script inexistente.

Solução:

```bash
streamlit run dashboard/streamlit_app.py
```

### Erro: `relation "vw_*" does not exist`

Solução:

```bash
cd sql/bi_views
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_views.sql

cd ../bi_kpis
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_kpis.sql
```

---

**Última atualização:** Março 2026
