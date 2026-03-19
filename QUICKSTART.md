QUICKSTART - Data Warehouse em 5 minutos

Este arquivo fornece os comandos essenciais para rodar o projeto rapidamente.

1. ATIVAR AMBIENTE
# PowerShell (Windows):
.\.venv\Scripts\Activate.ps1

# Bash/Linux:
source venv/bin/activate

2. INSTALAR DEPENDÊNCIAS
pip install -r csv-ingestion/requirements.txt

3. CONFIGURAR POSTGRESQL
# Opção A: Local (Windows)
# - Iniciar PostgreSQL
# - Criar banco: psql -U postgres -c "CREATE DATABASE csv_dw;"

# Opção B: Docker
cd csv-ingestion
docker-compose up -d
cd ..

4. CONFIGURAR VARIÁVEIS (PowerShell)
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_DB = "csv_dw"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "postgres"
$env:POSTGRES_PORT = "5432"

5. EXECUTAR ETL
cd csv-ingestion
python -c "from app.pipeline.etl import executar_etl; executar_etl()"
cd ..

COMANDOS ÚTEIS

# Listar consultas disponíveis
python -c "from app.pipeline.queries import listar_consultas; listar_consultas()"

# Executar consulta: Gasto por Categoria
python -c "
import psycopg2
from app.pipeline.queries import CONSULTAS

conn = psycopg2.connect(
    host='localhost', database='csv_dw',
    user='postgres', password='postgres'
)
cur = conn.cursor()
cur.execute(CONSULTAS['gasto_categoria']['query'])
for row in cur.fetchall():
    print(row)
conn.close()
"

# Conectar ao banco diretamente
psql -U postgres -d csv_dw

VERIFICAÇÕES

# Verificar se PostgreSQL está rodando
psql -U postgres -c "SELECT version();"

# Contar registros no DW
psql -U postgres -d csv_dw -c "
SELECT 
    (SELECT COUNT(*) FROM fato_transacoes) as transacoes,
    (SELECT COUNT(*) FROM dim_data) as datas,
    (SELECT COUNT(*) FROM dim_cartao) as cartoes;
"

# Gasto total
psql -U postgres -d csv_dw -c "
SELECT ROUND(SUM(valor_brl), 2) as total_brl 
FROM fato_transacoes;
"

CONSULTAS RÁPIDAS (SQL)

# Q1: Quanto gastei no total?
SELECT ROUND(SUM(valor_brl), 2) FROM fato_transacoes;

# Q2: Em qual categoria gastei mais?
SELECT categoria, SUM(valor_brl) as total 
FROM fato_transacoes ft
JOIN dim_categoria dc ON ft.id_categoria = dc.id_categoria
GROUP BY categoria ORDER BY total DESC LIMIT 1;

# Q3: Qual foi meu maior gasto?
SELECT ROUND(MAX(valor_brl), 2) FROM fato_transacoes;

# Q4: Qual é meu gasto médio?
SELECT ROUND(AVG(valor_brl), 2) FROM fato_transacoes;

# Q5: Top 5 comerciantes
SELECT nome_comerciante, SUM(valor_brl) as total 
FROM fato_transacoes ft
JOIN dim_comerciante dm ON ft.id_comerciante = dm.id_comerciante
GROUP BY nome_comerciante ORDER BY total DESC LIMIT 5;

TROUBLESHOOTING RÁPIDO

# Erro: "could not connect to server"
# → Verificar se PostgreSQL está rodando
# → Windows: services.msc ou Start-Service postgresql-x64-15

# Erro: "database csv_dw does not exist"
# → Criar banco: psql -U postgres -c "CREATE DATABASE csv_dw;"

# Erro: "UNIQUE constraint violated"
# → Limpar dados: TRUNCATE TABLE fato_transacoes CASCADE;

# Erro: "no module named psycopg2"
# → Instalar: pip install psycopg2-binary

# ============================================================================
# DOCUMENTAÇÃO RÁPIDA
# ============================================================================

Documentos:
  - MODELAGEM_STAR_SCHEMA.md     - Modelo (20 min)
  - DICIONARIO_DADOS.md          - Campos (30 min)
  - README_DATA_WAREHOUSE.md     - Guia (25 min)
  - GUIA_PRATICO_EXECUCAO.md    - Steps (15 min)
  - SUMARIO_EXECUTIVO.md         - Resumo (10 min)
  - INDICE.md                    - Links (5 min)

Código:
  - csv-ingestion/app/pipeline/schema.py   - DDL
  - csv-ingestion/app/pipeline/etl.py      - ETL
  - csv-ingestion/app/pipeline/queries.py  - SQL

# ============================================================================
# ESTRUTURA DO PROJETO
# ============================================================================

Star Schema:
  dim_data ─────────┐
  dim_cartao ───────┼──→ fato_transacoes
  dim_categoria ────┤
  dim_comerciante ──┘

Dados Esperados:
  • ~1000 transações
  • ~50 comerciantes
  • ~15 categorias
  • Período: Mar/2025 - Jan/2026

# ============================================================================
# PRÓXIMOS PASSOS
# ============================================================================

1. Instalar dependências
2. Configurar PostgreSQL
3. Executar ETL
4. Executar consultas
5. Criar dashboard (Metabase/Power BI)
6. Agendar ETL diária
7. Deploy em produção

# ============================================================================
# CONTATO / DÚVIDAS
# ============================================================================

Ver documentação em INDICE.md para navegação rápida
ou abrir arquivo correspondente:
  - Modelagem?       -> MODELAGEM_STAR_SCHEMA.md
  - Campos?          -> DICIONARIO_DADOS.md
  - Como rodar?      -> GUIA_PRATICO_EXECUCAO.md
  - Código?          -> README_DATA_WAREHOUSE.md
  - Resumo?          -> SUMARIO_EXECUTIVO.md
  - Índice?          -> INDICE.md

# ============================================================================
"""

# ============================================================================
# EXEMPLO: EXECUTAR TUDO EM PYTHON
# ============================================================================

import os
import psycopg2
from app.pipeline.schema import create_database_tables
from app.pipeline.etl import executar_etl
from app.pipeline.queries import CONSULTAS

def run_complete_pipeline():
    """Executa o pipeline completo"""
    
    # 1. Conectar ao banco
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "csv_dw"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )
    print("✓ Conectado ao PostgreSQL")
    
    # 2. Criar tabelas
    create_database_tables(conn)
    conn.close()
    
    # 3. Executar ETL
    executar_etl()
    
    # 4. Executar algumas consultas
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "csv_dw"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )
    
    cur = conn.cursor()
    
    # Query 1: Resumo geral
    print("\n" + "="*60)
    print("RESUMO GERAL")
    print("="*60)
    cur.execute(CONSULTAS['resumo_geral']['query'])
    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]}")
    
    # Query 2: Gasto por categoria
    print("\n" + "="*60)
    print("GASTO POR CATEGORIA")
    print("="*60)
    cur.execute(CONSULTAS['gasto_categoria']['query'])
    cols = [desc[0] for desc in cur.description]
    print(f"{cols[0]:<40} {cols[1]:<10} {cols[2]:<15}")
    print("-" * 65)
    for row in cur.fetchall():
        print(f"{row[0]:<40} {row[1]:<10} {row[2]:<15}")
    
    # Query 3: Top comerciantes
    print("\n" + "="*60)
    print("TOP 10 COMERCIANTES")
    print("="*60)
    cur.execute(CONSULTAS['top_comerciantes']['query'])
    cols = [desc[0] for desc in cur.description]
    print(f"{cols[0]:<35} {cols[1]:<10} {cols[2]:<15}")
    print("-" * 60)
    for row in cur.fetchall():
        print(f"{row[0]:<35} {row[1]:<10} {row[2]:<15}")
    
    conn.close()
    print("\n✓ Pipeline completo!")

if __name__ == "__main__":
    run_complete_pipeline()
