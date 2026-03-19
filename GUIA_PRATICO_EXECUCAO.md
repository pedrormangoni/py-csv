# Guia Prático de Execução - Data Warehouse

## Passo a Passo para Rodar o Projeto

### Preparação Inicial

#### Ativar Ambiente Virtual
```powershell
# PowerShell (Windows)
cd C:\Users\Pedro\Desktop\Works\py-csv
.\.venv\Scripts\Activate.ps1

# Ou bash/Linux
source venv/bin/activate
```

#### Instalar Dependências
```bash
pip install -r csv-ingestion/requirements.txt
```

### Configurar Banco de Dados PostgreSQL

#### Opção A: PostgreSQL Local

1. **Verificar se PostgreSQL está instalado**
```powershell
psql --version
```

2. **Iniciar o serviço PostgreSQL**
```powershell
# Windows - Services
Get-Service postgresql-x64-* | Start-Service

# Ou no terminal como admin
net start "postgresql-x64-15"
```

3. **Conectar ao PostgreSQL**
```bash
psql -U postgres -W
```

4. **Criar banco de dados**
```sql
CREATE DATABASE csv_dw;
\q
```

#### Opção B: Docker Compose

```bash
cd csv-ingestion
docker-compose up -d

# Verificar se está rodando
docker-compose ps
```

### Configurar Variáveis de Ambiente

#### Criar arquivo `.env`
```powershell
# csv-ingestion\.env
POSTGRES_HOST=localhost
POSTGRES_DB=csv_dw
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432
```

Ou exportar no terminal:
```powershell
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_DB = "csv_dw"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "postgres"
$env:POSTGRES_PORT = "5432"
```

### Executar o ETL

#### Opção 1: Python Direto
```bash
cd csv-ingestion

# Teste de conexão
python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'csv_dw'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )
    print('✓ Conexão bem-sucedida!')
    conn.close()
except Exception as e:
    print(f'✗ Erro: {e}')
"

# Executar ETL
python -c "from app.pipeline.etl import executar_etl; executar_etl()"
```

#### Opção 2: Script Principal (main.py)

Editar `csv-ingestion/main.py`:
```python
import os
from app.pipeline.etl import executar_etl
from app.pipeline.schema import create_database_tables
import psycopg2

# Executa a criação de tabelas e ETL
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    database=os.getenv("POSTGRES_DB", "csv_dw"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    port=os.getenv("POSTGRES_PORT", "5432")
)

print("Criando tabelas...")
create_database_tables(conn)
conn.close()

print("Executando ETL...")
executar_etl()
```

Depois rodar:
```bash
python main.py
```

### Verificar Dados Carregados

```sql
-- Conectar ao banco
psql -U postgres -d csv_dw

-- Contar registros
SELECT COUNT(*) FROM fato_transacoes;
SELECT COUNT(*) FROM dim_data;
SELECT COUNT(*) FROM dim_cartao;
SELECT COUNT(*) FROM dim_categoria;
SELECT COUNT(*) FROM dim_comerciante;

-- Visualizar primeiro registro
SELECT * FROM fato_transacoes LIMIT 5;
```

### Executar Consultas Analíticas

#### Via SQL Script
```bash
cd csv-ingestion
python -c "from app.pipeline.queries import listar_consultas; listar_consultas()"
```

#### Via Python
```python
import psycopg2
from app.pipeline.queries import CONSULTAS

conn = psycopg2.connect(
    host='localhost',
    database='csv_dw',
    user='postgres',
    password='postgres'
)
cur = conn.cursor()

# Executar consulta: Gasto por Categoria
cur.execute(CONSULTAS['gasto_categoria']['query'])
resultados = cur.fetchall()

print("Gasto por Categoria:")
print("-" * 60)
for linha in resultados:
    print(linha)

conn.close()
```

#### Via psql
```sql
\c csv_dw

-- Query: Gasto Total por Categoria
SELECT 
    dc.categoria,
    COUNT(*) as quantidade_transacoes,
    SUM(ft.valor_brl) as total_gasto_brl
FROM fato_transacoes ft
INNER JOIN dim_categoria dc ON ft.id_categoria = dc.id_categoria
GROUP BY dc.categoria
ORDER BY total_gasto_brl DESC;

-- Query: Top 10 Comerciantes
SELECT 
    dm.nome_comerciante,
    COUNT(*) as quantidade_transacoes,
    ROUND(SUM(ft.valor_brl), 2) as total_gasto_brl
FROM fato_transacoes ft
INNER JOIN dim_comerciante dm ON ft.id_comerciante = dm.id_comerciante
GROUP BY dm.nome_comerciante
ORDER BY total_gasto_brl DESC
LIMIT 10;

-- Query: Evolução de Gastos por Mês
SELECT 
    dd.ano,
    dd.mes,
    dd.mes_nome,
    COUNT(*) as quantidade_transacoes,
    ROUND(SUM(ft.valor_brl), 2) as total_gasto_brl
FROM fato_transacoes ft
INNER JOIN dim_data dd ON ft.id_data = dd.id_data
GROUP BY dd.ano, dd.mes, dd.mes_nome
ORDER BY dd.ano, dd.mes;
```

---

## Verificações Importantes

### Checklist Pré-Execução

```bash
# 1. Ambiente virtual ativado?
python --version  # Deve mostrar versão do Python

# 2. Dependências instaladas?
pip list | grep psycopg2
pip list | grep sqlalchemy

# 3. PostgreSQL rodando?
psql -U postgres -c "SELECT version();"

# 4. Variáveis de ambiente?
$env:POSTGRES_HOST
$env:POSTGRES_DB

# 5. Arquivos CSV presentes?
Get-ChildItem "C:\Users\Pedro\Desktop\Works\py-csv\csv-ingestion\app\datas\unread\*.csv" | Measure-Object
```

### Verificações Pós-Execução

```sql
-- Verificar quantidade de dados
SELECT 
    (SELECT COUNT(*) FROM fato_transacoes) as transacoes,
    (SELECT COUNT(*) FROM dim_data) as datas,
    (SELECT COUNT(*) FROM dim_cartao) as cartoes,
    (SELECT COUNT(*) FROM dim_categoria) as categorias,
    (SELECT COUNT(*) FROM dim_comerciante) as comerciantes;

-- Verificar datas carregadas
SELECT 
    MIN(dd.data_completa) as primeira_data,
    MAX(dd.data_completa) as ultima_data
FROM fato_transacoes ft
INNER JOIN dim_data dd ON ft.id_data = dd.id_data;

-- Verificar valores
SELECT 
    COUNT(*) as total_transacoes,
    ROUND(SUM(ft.valor_brl), 2) as total_brl,
    ROUND(AVG(ft.valor_brl), 2) as media_brl,
    ROUND(MIN(ft.valor_brl), 2) as minimo,
    ROUND(MAX(ft.valor_brl), 2) as maximo
FROM fato_transacoes ft;
```

---

## Troubleshooting Comum

### Problema: "FATAL: Ident authentication failed"
```
Solução: Editar postgresql.conf ou usar password authentication
Windows: C:\Program Files\PostgreSQL\15\data\pg_hba.conf
Mudar 'ident' para 'md5' ou 'scram-sha-256'
```

### Problema: "could not translate host name"
```
Solução: PostgreSQL não está rodando
- Verificar: Get-Service postgresql-x64-*
- Iniciar: Start-Service postgresql-x64-15
```

### Problema: "ERROR: column does not exist"
```
Solução: Tabelas não foram criadas
- Executar novamente: create_database_tables(conn)
- Ou: TRUNCATE TABLE fato_transacoes CASCADE; (para limpar)
```

### Problema: "CSV encoding error"
```
Solução: Arquivo tem encoding diferente
- Verificar encoding do CSV: file -i seu_arquivo.csv
- Editar etl.py linha 182: open(arquivo, encoding='utf-8')
```

---

## Amostra de Saída Esperada

```
INFO:root:Conectado ao PostgreSQL
INFO:root:Executando: CREATE TABLE IF NOT EXISTS dim_data...
✓ Tabelas criadas com sucesso!
INFO:root:Processando arquivo: ./app/datas/unread/Fatura_2025-03-20.csv
INFO:root:  50 registros processados...
INFO:root:  100 registros processados...
✓ 145 registros inseridos, 2 erros

INFO:root:Processando arquivo: ./app/datas/unread/Fatura_2025-04-20.csv
✓ 156 registros inseridos, 1 erro

==================================================
ETL Completo! Total de registros: 1546
==================================================
```

---

## Recursos Adicionais

- [MODELAGEM_STAR_SCHEMA.md](../MODELAGEM_STAR_SCHEMA.md) - Detalhes do modelo
- [DICIONARIO_DADOS.md](../DICIONARIO_DADOS.md) - Descrição de campos
- [README_DATA_WAREHOUSE.md](../README_DATA_WAREHOUSE.md) - Documentação completa

---

## Próximas Etapas

1. **Visualização**: Integrar com BI (Power BI, Looker, Metabase)
2. **Scheduler**: Agendar ETL diária (cron, APScheduler)
3. **API**: Criar endpoints para consultas
4. **Cache**: Implementar Redis para queries frequentes
5. **Alertas**: Notificações para gastos anormais

---

**Última atualização:** Março 2026
