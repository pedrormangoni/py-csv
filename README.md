# ETL de CSV de cartão + base analítica BI (em dev)

Este README descreve como executar o projeto, rodar testes e usar os artefatos SQL de análise.

## Fluxo do sistema (resumo)

1. **Entrada dos arquivos CSV**
	- Os arquivos chegam em `csv-ingestion/app/datas/unread/`.
	- O ETL identifica os CSVs pendentes para processamento.

2. **Validação inicial**
	- O sistema verifica se o arquivo está vazio e se o cabeçalho bate com o layout esperado.
	- Arquivos inválidos entram no resumo como não processados.

3. **Controle de lote (idempotência)**
	- É gerado hash do arquivo e feito registro em `etl_file_batches`.
	- Se o hash já foi carregado anteriormente, o arquivo é marcado como já processado.

4. **Transformação e carga**
	- Cada linha do CSV é normalizada e convertida (data, parcelas, valores, cotação).
	- As linhas são inseridas na tabela `stg_credit_card_transactions`.

5. **Status final e movimentação do arquivo**
	- Em sucesso: lote marcado como `loaded` e arquivo movido para `csv-ingestion/app/datas/read/`.
	- Em erro: lote marcado como `failed` com mensagem de erro registrada.

6. **Consumo analítico (BI) (EM DEV)** 
	- As consultas e visões SQL em `sql/` usam os dados carregados para KPIs, análises e checks de qualidade.

## Pré-requisitos

- Docker + Docker Compose **ou** Python 3.11+
- PostgreSQL (somente para execução local sem Docker)

## 1) Configurar variáveis de ambiente

Na raiz do projeto, crie/ajuste o arquivo `.env`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=credit-card
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Se for rodar **local sem Docker**, use `POSTGRES_HOST=localhost`.

## 2) Rodar com Docker (recomendado)

Na raiz do projeto:

```bash
docker compose up --build
```

Isso sobe:
- banco PostgreSQL (`db`)
- aplicação Python (`app`), que executa o ETL automaticamente

Para subir apenas o banco (ex.: usar pgAdmin ou rodar testes de integração):

```bash
docker compose up -d db
```

Para parar:

```bash
docker compose down
```

## 3) Rodar local (sem Docker)

Na raiz do projeto:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r csv-ingestion/requirements.txt
python csv-ingestion/main.py
```

## 4) Resultado esperado

Ao final da execução, o terminal mostra o resumo:

- Arquivos encontrados
- Arquivos carregados
- Arquivos inválidos
- Arquivos já processados
- Arquivos com falha
- Linhas carregadas

## 5) Rodar testes (ainda não completos)

Na pasta `csv-ingestion`:

```bash
/home/pedro/Documents/py-csv/.venv/bin/python -m pytest -q
```

Separando por tipo:

```bash
/home/pedro/Documents/py-csv/.venv/bin/python -m pytest tests/unit -q
/home/pedro/Documents/py-csv/.venv/bin/python -m pytest tests/integration -q -m integration
```

## 6) SQL para BI e governança (em dev)

Os artefatos SQL já prontos estão organizados em:

- `sql/bi_queries`: consultas por pergunta de negócio.
- `sql/bi_views`: camada analítica (`CREATE VIEW`) para consumo em BI.
- `sql/bi_kpis`: consultas de KPI (cards de dashboard).
- `sql/bi_quality`: checks de qualidade e consistência dos dados.

Cada pasta contém um `README.md` com instruções de execução no pgAdmin e no `psql`.
