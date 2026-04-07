# Guia Prático de Execução (Docker PostgreSQL + Metabase)

Guia para rodar ETL, camada SQL analítica e dashboard Metabase com **PostgreSQL no Docker**.

## 1) Pré-requisitos

- **Docker Desktop** instalado
- **Python 3.9+** instalado
- `docker compose` disponível no terminal

## 2) Preparação do Ambiente Python

Na raiz do projeto, crie e ative o ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou: source .venv/bin/activate  # macOS/Linux

python -m pip install --upgrade pip
python -m pip install -r csv-ingestion/requirements.txt
```

## 3) Configurar PostgreSQL (Docker Compose)

### 3.1) Subir o banco Docker

Na raiz do projeto:

```bash
docker compose up -d db
docker compose ps
```

Conforme [docker-compose.yml](docker-compose.yml):
- Container: `postgres_db`
- Host local: `localhost`
- Porta no host: `5433`
- Porta interna do container: `5432`

### 3.2) Configurar credenciais (`.env`)

Na raiz do projeto, crie/atualize `.env`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=credit-card
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

**Importante:** esses valores são para containers (rede Docker).

Para comandos executados no host (PowerShell), use:
- Host: `localhost`
- Port: `5433`

## 4) Executar ETL (Carregar CSV)

No terminal com `.venv` ativo:

```powershell
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5433"
$env:POSTGRES_DB="credit-card"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="postgres"
```

```bash
python csv-ingestion/main.py
```

**Saída esperada:**
```
Resumo ETL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Arquivos carregados: 11
Linhas carregadas: 1758
```

O ETL:
- Valida cabeçalho CSV
- Normaliza campos (datas, moedas)
- Remove pagamentos (valores negativos)
- Carrega em `stg_credit_card_transactions`

## 5) Aplicar Camada SQL Analítica

Execute os scripts SQL para criar views e KPIs:

```bash
cd sql/bi_views
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_views.sql

cd ../bi_kpis
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_kpis.sql
```

Em seguida, crie a camada semântica (dimensões + fato):

```bash
cd ../../csv-ingestion
python -m app.pipeline.schema
```

Se você já estiver dentro de `sql/bi_kpis`, use:

```bash
cd ../bi_views
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_views.sql

cd ../bi_kpis
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_kpis.sql
```

**Resultado:** views criadas:
- `vw_base_transacoes` - Base enriquecida com dimensões
- `vw_dim_tempo` - Dimensão temporal
- `vw_dim_cartao` - Dimensão cartões
- `vw_dim_categoria` - Dimensão categorias
- `vw_dim_parcelamento` - Dimensão parcelamento
- `vw_fato_transacoes` - Fatos das transações
- `vw_gastos_semanais_mes` - Gastos semanais por mês
- `vw_compras_recorrentes` - Padrões de compra recorrente

## 6) Conectar Metabase

### 6.1) Iniciar Metabase (Docker)

```bash
docker run -d -p 3000:3000 --name metabase metabase/metabase:latest
```

Acesse: `http://localhost:3000`

**⏱️ Aguarde 1-2 minutos** para o Metabase inicializar completamente.

### 6.2) Setup Inicial do Metabase

1. **Welcome Screen:** Preencha email, senha e nome
2. **Database Connection:**
   - **Database type:** PostgreSQL
   - **Display name:** `credit-card`
  - **Host:** `host.docker.internal` (Windows/macOS) ou `172.17.0.1` (Linux)
  - **Port:** `5433`
   - **Database name:** `credit-card`
   - **Username:** `postgres`
  - **Password:** `postgres` (ou valor do seu `.env`)
  - **Use a secure connection (SSL):** `No`
   - Clique **Save**

**Espere a sincronização** do banco com o Metabase (visível no canto inferior direito).

### 6.3) Explorar Dados

1. **+ New** → **Question** → **Simple question**
2. Selecione banco `credit-card` e tabela `stg_credit_card_transactions`
3. Explore as colunas e visualize dados

### 6.4) Criar Queries SQL

Para usar as views analíticas direto:

1. **+ New** → **Question** → **SQL query**
2. Cole uma das queries pré-prontas abaixo:

**Total Gasto (Período):**
```sql
SELECT 
  SUM(amount_brl) AS total_gasto_brl,
  COUNT(*) AS total_transacoes,
  MIN(data) AS primeira_compra,
  MAX(data) AS ultima_compra
FROM vw_fato_transacoes;
```

**Gastos por Mês (Tendência):**
```sql
SELECT 
  ano_mes,
  SUM(amount_brl) AS total_mes,
  COUNT(*) AS qtd_transacoes,
  ROUND(AVG(amount_brl), 2) AS ticket_medio
FROM vw_fato_transacoes
GROUP BY ano_mes
ORDER BY ano_mes;
```

**Gastos por Categoria:**
```sql
SELECT 
  categoria,
  SUM(amount_brl) AS total_categoria,
  ROUND(100 * SUM(amount_brl) / (SELECT SUM(amount_brl) FROM vw_fato_transacoes), 2) AS pct_total,
  COUNT(*) AS qtd_compras
FROM vw_fato_transacoes
GROUP BY categoria
ORDER BY total_categoria DESC;
```

**Compras Parceladas vs À Vista:**
```sql
SELECT 
  tipo_compra,
  SUM(amount_brl) AS total,
  COUNT(*) AS qtd_compras,
  ROUND(AVG(amount_brl), 2) AS ticket_medio
FROM vw_fato_transacoes
GROUP BY tipo_compra;
```

**Impacto Cambial (FX):**
```sql
SELECT 
  ano_mes,
  SUM(amount_brl) AS total_brl_realizado,
  SUM(amount_usd * fx_rate_brl) AS total_brl_cotacao_atual,
  SUM(impacto_cambial_brl) AS impacto_total,
  ROUND(100 * SUM(impacto_cambial_brl) / NULLIF(SUM(amount_brl), 0), 2) AS pct_impacto
FROM vw_fato_transacoes
WHERE amount_usd > 0
GROUP BY ano_mes
ORDER BY ano_mes;
```

**Compras Recorrentes:**
```sql
SELECT 
  descricao,
  categoria,
  cartao_sk,
  COUNT(*) AS ocorrencias,
  ROUND(AVG(amount_brl), 2) AS ticket_medio,
  MIN(data) AS primeira_compra,
  MAX(data) AS ultima_compra
FROM vw_fato_transacoes
GROUP BY descricao, categoria, cartao_sk
HAVING COUNT(*) > 1
ORDER BY ocorrencias DESC;
```

**Semanas com Maior Volume (por Mês):**
```sql
WITH semanal AS (
  SELECT
    ano_mes,
    inicio_semana,
    SUM(amount_brl) AS total_semana,
    COUNT(*) AS qtd_compras
  FROM vw_fato_transacoes
  GROUP BY ano_mes, inicio_semana
),
ranking AS (
  SELECT
    ano_mes,
    inicio_semana,
    total_semana,
    qtd_compras,
    ROW_NUMBER() OVER (PARTITION BY ano_mes ORDER BY total_semana DESC) AS ranking_no_mes
  FROM semanal
)
SELECT
  ano_mes,
  inicio_semana,
  total_semana,
  qtd_compras,
  ranking_no_mes
FROM ranking
WHERE ranking_no_mes <= 3
ORDER BY ano_mes, ranking_no_mes;
```

### 6.5) Criar Dashboard

1. **+ New** → **Dashboard**
2. Dê um nome: `Executive Summary - Cartão Crédito`
3. **Edit** → **Add** questions criadas acima
4. Organize visualmente com títulos e descrições
5. **Save**

### 6.6) Filtros Interativos (Optional)

No dashboard, adicione **filters** para:
- **Período (data):** Filtra `vw_fato_transacoes.data`
- **Categoria:** Filtra `vw_fato_transacoes.categoria`
- **Cartão:** Filtra `vw_fato_transacoes.cartao_sk`
- **Tipo de Compra:** Filtra `vw_fato_transacoes.tipo_compra`

## 7) Verificações Úteis

### PostgreSQL acessível

```bash
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -c "SELECT version();"
```

### Linhas carregadas no staging

```bash
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -c "
SELECT COUNT(*) AS total_linhas FROM stg_credit_card_transactions;
"
```

### Views principais criadas

```bash
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -c "
SELECT table_name FROM information_schema.views
WHERE table_schema = 'public' AND table_name LIKE 'vw_%'
ORDER BY table_name;
"
```

### Amostra de dados na fact

```bash
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -c "
SELECT id, purchase_date, categoria, amount_brl, parcelamento_tipo
FROM vw_fato_transacoes
LIMIT 5;
"
```

## 8) Fluxo de Trabalho Completo

**Primeira execução (setup inicial):**

```bash
# 1. Ativar venv
.venv\Scripts\activate

# 2. Subir PostgreSQL do compose
docker compose up -d db

# 3. Carregar dados
python csv-ingestion/main.py

# 4. Aplicar views SQL
cd sql/bi_views
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_views.sql
cd ../bi_kpis
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_kpis.sql

# 5. Iniciar Metabase
docker run -d -p 3000:3000 --name metabase metabase/metabase:latest
```

**Executar Metabase:**

```bash
# Abrir navegador
http://localhost:3000

# Setup conexão PostgreSQL (ver seção 6.2)
# Criar queries e dashboard (ver seção 6.4 e 6.5)
```

**Próximas execuções (novos CSVs):**

```bash
# 1. Copiar CSVs para csv-ingestion/app/datas/unread/
# 2. python csv-ingestion/main.py
# 3. No Metabase: Refresh (F5)
```

## 9) Troubleshooting

### Erro: Metabase não conecta ao PostgreSQL

**Causa:** `localhost` dentro do Docker não aponta para o host local.

**Solução:**

- **Windows/macOS:** Use `host.docker.internal` como Host
- **Linux:** Use `172.17.0.1` como Host
- **SSL:** deixe desativado (`Use a secure connection = No`)

### Erro: `This database doesn't have any tables` no Metabase

**Causa comum:** conexão criada com parâmetros incorretos (porta/host/SSL) ou sem sincronização de metadados.

**Solução:**

1. Vá em **Admin Settings → Databases → PostgreSQL → Edit**
2. Confirme:
  - Host: `host.docker.internal`
  - Port: `5433`
  - Database name: `credit-card`
  - Username: `postgres`
  - Password: `postgres`
  - SSL: `No`
3. Clique **Save**
4. Clique em **Sync database schema now** e depois **Re-scan field values now**
5. Abra novamente **Browse data**

Se ainda aparecer vazio, remova essa conexão e crie novamente com os mesmos parâmetros acima.

### Erro: `FATAL 3D000: banco de dados "credit-card" não existe`

**Solução:**

```bash
psql -U postgres -c "CREATE DATABASE \"credit-card\";"
```

### Erro: `relation "vw_*" does not exist` no Metabase

**Solução:**

```bash
cd sql/bi_views
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_views.sql
```

Depois, no Metabase: **Refresh Metadata** (⚙️ Settings > Admin Settings > Databases > credit-card > Refresh metadata)

### Erro: `No such file or directory` ao rodar `00_apply_all_views.sql`

**Causa:** script executado no diretório errado (os includes de `00_apply_all_views.sql` são relativos).

**Solução:**

```bash
cd sql/bi_views
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_views.sql
```

Se estiver em `sql/bi_kpis`, use `cd ../bi_views` (não `cd sql/bi_views`).

### Erro: `could not translate host name "db"`

**Causa:** ETL rodando no host tentando resolver hostname interno do Docker (`db`).

**Solução (execução no host):**

```powershell
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5433"
python csv-ingestion/main.py
```

### Erro: psql não encontrado

**Causa:** PostgreSQL CLI não instalado ou não no PATH.

**Solução (Windows):**

```bash
# Adicionar ao PATH:
# C:\Program Files\PostgreSQL\16\bin
```

Depois, abra novo terminal.

### Erro: Docker daemon not running

**Solução (Windows):**

1. Abra **Docker Desktop**
2. Aguarde inicializar (canto inferior esquerdo deve mostrar ✅)
3. Tente novamente: `docker run -d -p 3000:3000 --name metabase metabase/metabase:latest`

## 10) Arquitetura de Dados

```
csv-ingestion/app/datas/unread/ (CSVs de entrada)
        ↓
    ETL Python
        ↓
PostgreSQL: stg_credit_card_transactions (staging)
        ↓
    Views SQL
        ↓
(8 views analíticas)
        ↓
   Metabase
        ↓
KPIs & Dashboards Interativos
```

## 11) Referência SQL Views

Todas as views leem de `stg_credit_card_transactions` via `vw_base_transacoes`.

Para alterar fonte de dados, edite apenas:
- `sql/bi_views/00_vw_base_transacoes.sql`

Todos os queries e dashboards se atualizam automaticamente.

## 12) Próximas Etapas

1. ✅ ETL carregado (1,758 transações)
2. ✅ Views SQL aplicadas (8 views)
3. ⬜ Metabase conectado em `host.docker.internal:5433`
4. ⬜ Queries criadas (8 KPIs)
5. ⬜ Dashboard criado e interativo
6. ⬜ Filtros dinâmicos configurados
