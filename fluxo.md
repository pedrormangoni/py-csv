# Fluxo Técnico do Sistema

Este documento descreve o fluxo técnico atual do projeto e a responsabilidade de cada arquivo principal, para facilitar onboarding e manutenção.

## 1. Visão geral da execução

Fluxo operacional padrão:

1. O processo inicia em `csv-ingestion/main.py`.
2. O `main.py` chama `run_etl_from_unread()` em `app/pipeline/etl.py`.
3. O ETL lista arquivos CSV em `app/datas/unread` (via `app/api/upload.py`).
4. Cada arquivo passa por validação (existência, extensão, cabeçalho, tamanho).
5. O ETL abre conexão no PostgreSQL com retry e fallback de host (`db` -> `localhost`).
6. O ETL cria/garante tabelas de controle e staging.
7. O ETL controla idempotência por hash do arquivo e hash de linha.
8. Registros válidos são transformados e inseridos no banco.
9. O lote é marcado como `loaded` (ou `failed`, em erro).
10. Em sucesso, o arquivo é movido de `unread` para `read`.
11. O processo retorna resumo com contadores de arquivos e linhas.

## 2. Fluxo técnico detalhado (ETL)

### 2.1 Entrada

- Origem: arquivos `*.csv` em `csv-ingestion/app/datas/unread/`.
- Delimitador esperado: `;`. (Pode ser configurado em 'csv-ingestion/app/api/config.py')
- Layout esperado: 9 colunas (constante `EXPECTED_COLUMNS` (Pode ser configurado em 'csv-ingestion/app/api/config.py')).

### 2.2 Conexão e preparação

- `_load_env_file()` carrega variáveis do `.env` na raiz do projeto.
- `_get_db_connection()` tenta conectar no PostgreSQL com retry.
- `_ensure_tables()` garante as tabelas:
  - `etl_file_batches` (controle de lote/arquivo).
  - `stg_credit_card_transactions` (staging das transações).

### 2.3 Validação por arquivo

- `validate_columns_file()` valida extensão e cabeçalho.
- Arquivo vazio ou inválido incrementa `files_invalid` e não carrega linhas.

### 2.4 Idempotência e controle de lote

- `_compute_file_hash()` gera SHA-256 do arquivo.
- `_upsert_batch_start()` insere/atualiza lote em `etl_file_batches`.
- Se o hash já estiver com status `loaded`, o arquivo é considerado já processado (`files_skipped`).

### 2.5 Transformação por linha

Durante `_parse_rows()`:

- Data: `dd/mm/yyyy` -> `DATE` (`_parse_purchase_date`).
- Texto: normalização de espaços (`_normalize_text`).
- Números: vírgula para ponto e conversão para `Decimal` (`_parse_decimal`).
- Parcela: interpreta `única/unica` ou padrão `n/m` (`_parse_installment`).
- Hash de linha para deduplicação no lote (`_hash_row`).

### 2.6 Carga e finalização

- `_delete_previous_rows()` remove linhas do mesmo `batch_id` antes de recarga.
- `_insert_rows()` faz `INSERT ... ON CONFLICT DO NOTHING` por `(batch_id, row_hash)`.
- `_mark_batch_loaded()` atualiza status e métricas de leitura/carga.
- Em erro, rollback + `_mark_batch_failed()` com mensagem.
- Em sucesso, `move_file_to_read()` move o CSV para `read`.

## 3. Responsabilidade por arquivo

### 3.1 Raiz do projeto

- `README.md`: guia geral de setup, execução e visão operacional.
- `QUICKSTART.md`: passos mínimos para execução rápida (Linux).
- `GUIA_PRATICO_EXECUCAO.md`: guia expandido com comandos e troubleshooting.
- `escopo.md`: contexto de negócio, perguntas analíticas e limites do projeto.
- `funcionalidades.md`: estado atual da implementação e backlog.
- `docker-compose.yml`: orquestra serviços `db` (Postgres) e `app` (ETL).

### 3.2 Aplicação Python (`csv-ingestion`)

- `main.py`: ponto de entrada da execução, imprime resumo final do ETL.
- `requirements.txt`: dependências Python do serviço.
- `Dockerfile`: build da imagem da aplicação Python.

### `app/api`

- `upload.py`: utilitários de ingestão de arquivos
  - define `EXPECTED_COLUMNS`;
  - lista CSVs pendentes em `unread`;
  - valida cabeçalho/arquivo;
  - move arquivo para `read` após processamento.

### `app/pipeline`

- `etl.py`: núcleo do processamento fim a fim.
  - conexão com banco;
  - criação de tabelas de staging/controle;
  - parsing e transformação;
  - idempotência por hash;
  - controle de status do lote;
  - resumo de execução.

- `queries.py`: catálogo de consultas SQL analíticas para consumo programático.
  - mantém constantes SQL;
  - organiza consultas em dicionário `CONSULTAS`;
  - expõe `listar_consultas()`.

- `schema.py`: DDL de um modelo dimensional (`dim_*` e `fato_transacoes`).
  - utilitário separado do ETL principal atual;
  - não é chamado por `main.py` no fluxo atual.

- `reader.py`: leitura de CSV com pandas para cenários auxiliares.
  - não participa do fluxo principal de carga atual.

### `app/datas`

- `read/`: arquivos já processados com sucesso.
- `unread/`: fila de entrada de arquivos pendentes.


### 3.3 Camada SQL (`sql`)

### `sql/bi_queries`

- Consultas de negócio diretas sobre staging para responder perguntas analíticas.

### `sql/bi_views`

- Views para consumo por BI, reduzindo complexidade das consultas no dashboard.

### `sql/bi_kpis`

- Consultas de KPIs em formato de cards (1 KPI por query e resumo consolidado).

### `sql/bi_quality`

- Checks de qualidade de dados (nulos, duplicidade, consistência cambial, outliers, etc.).

## 4. Pontos de atenção para desenvolvimento

- O ETL principal grava em tabelas `etl_file_batches` e `stg_credit_card_transactions`.
- O modelo dimensional de `schema.py` usa tabelas diferentes (`dim_*`, `fato_transacoes`) e hoje é paralelo ao fluxo principal.
- Qualquer mudança no layout CSV deve atualizar:
  - `EXPECTED_COLUMNS` em `upload.py`;
  - parsing e hashing em `etl.py`;
  - consultas SQL que dependem desses campos.
- A execução local depende de variáveis `POSTGRES_*` coerentes com porta/host do ambiente.
