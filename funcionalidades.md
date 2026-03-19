# Funcionalidades do Sistema (estado atual)

Este documento descreve o que já está implementado no projeto, como o fluxo funciona hoje e o que falta para concluir a entrega alinhada ao escopo de BI.

## 1) Visão geral da arquitetura atual

- **Entrada de dados**: arquivos CSV colocados em `csv-ingestion/app/datas/unread`.
- **Processamento**: execução do ETL via `python main.py` (container `python_app`).
- **Persistência**: PostgreSQL (serviço `db` no Docker Compose).
- **Saída operacional**:
  - resumo no terminal com contadores de arquivos/linhas;
  - dados carregados em tabelas no banco;
  - arquivos processados movidos para `csv-ingestion/app/datas/read`.

## 2) Fluxo atual do sistema (fim a fim)

1. O `main.py` chama `run_etl_from_unread()`.
2. O ETL busca todos os CSVs em `app/datas/unread`.
3. Para cada arquivo:
   - valida se o arquivo não está vazio;
   - valida se o cabeçalho bate com as colunas esperadas;
   - calcula hash do arquivo (SHA-256) para controle de reprocessamento;
   - cria/atualiza o lote na tabela de controle;
   - se o arquivo já foi carregado anteriormente, marca como **skipped** e move para `read`;
   - se for novo/pendente, parseia linhas e transforma campos;
   - insere registros na tabela de staging;
   - marca lote como **loaded**;
   - move o arquivo para `read`.
4. Em caso de erro no arquivo, faz rollback, marca lote como **failed** e continua nos próximos arquivos.
5. Ao final, imprime o resumo da execução.

## 3) Validações e regras já implementadas

- **Cabeçalho obrigatório** com as 9 colunas esperadas:
  - Data de Compra
  - Nome no Cartão
  - Final do Cartão
  - Categoria
  - Descrição
  - Parcela
  - Valor (em US$)
  - Cotação (em R$)
  - Valor (em R$)
- **Delimitador CSV**: `;`.
- **Data**: parse no formato `dd/mm/yyyy`.
- **Números**: normalização de vírgula para ponto e conversão para decimal.
- **Parcela**:
  - aceita `única`/`unica`;
  - interpreta padrão `n/m` em número da parcela e total.
- **Idempotência**:
  - hash por arquivo (`file_hash`) e hash por linha (`row_hash`);
  - evita duplicidade por `UNIQUE(batch_id, row_hash)`;
  - permite reprocessar o mesmo lote removendo dados anteriores do `batch_id` antes de inserir novamente.
- **Resiliência**:
  - retry de conexão com o banco;
  - fallback de host `db` para `localhost`.

## 4) Estrutura de dados criada automaticamente no banco

### 4.1 Tabela de controle de carga: `etl_file_batches`

Controla:
- nome/tamanho/hash do arquivo;
- status (`processing`, `loaded`, `failed`);
- quantidade lida/carregada;
- mensagem de erro;
- timestamps de criação, atualização e processamento.

### 4.2 Tabela de staging: `stg_credit_card_transactions`

Armazena as transações normalizadas com:
- dados da compra (data, cartão, categoria, descrição, parcela);
- valores em USD, cotação e valor em BRL;
- metadados de linha/lote/arquivo.

## 5) O que já atende o escopo de BI

Com o que existe hoje, já é possível responder (via SQL ou ferramenta BI conectada ao Postgres):

- total gasto no período;
- evolução mensal dos gastos;
- distribuição de gastos por categoria;
- ticket médio;
- volume e impacto de compras parceladas;
- impacto cambial (USD/cotação/BRL);
- frequência por categoria ao longo do tempo.

## 6) Status de entrega e o que falta para finalizar

### 6.1 Entregas já concluídas

- **Consultas de negócio versionadas** em `sql/bi_queries`.
- **Camada analítica com views** em `sql/bi_views`.
- **KPIs prontos para dashboard** em `sql/bi_kpis`.
- **Checks de qualidade de dados** em `sql/bi_quality`.
- **Testes automatizados** com `pytest`:
   - unitários para validação e parsing;
   - integração para carga ETL no PostgreSQL.

### 6.2 Pendências principais (backlog atual)

Abaixo está o backlog atualizado para concluir a solução com foco em uso de BI:

### Prioridade alta (necessário para entrega completa)

1. **Carga incremental contínua / agendamento**
   - Definir rotina de execução (cron, scheduler ou execução por pipeline).
   - Garantir processamento automático de novos CSVs sem intervenção manual.

2. **Padronização efetiva de categorias**
   - Implementar regra de normalização/mapeamento no ETL (hoje há checks SQL, mas não correção automática).
   - Evita distorções na análise de distribuição por categoria.

### Prioridade média (melhora robustez e manutenção)

3. **Migrations versionadas**
   - Embora `alembic` e `sqlalchemy` estejam nas dependências, o schema atual é criado via SQL em runtime.
   - Formalizar migrations para governança de mudanças.

4. **Observabilidade do ETL**
   - Trocar `print` por logging estruturado.
   - Incluir métricas e erro por arquivo/lote com melhor rastreabilidade.

### Prioridade baixa (opcional, mas agrega valor)

5. **Interface de ingestão (opcional)**
   - Hoje não há endpoint HTTP ativo; a ingestão ocorre por arquivo em pasta.
   - Opcional: adicionar API/webhook/upload para entrada de novos arquivos.

6. **Dashboards prontos**
   - Publicar dashboard (Power BI/Metabase/Superset) com as métricas do escopo.

## 7) Riscos e pontos de atenção atuais

- Se um arquivo for inválido, ele permanece em `unread` e pode voltar a ser tentado em execuções futuras.
- O módulo `reader.py` usa `pandas`, mas `pandas` não está no `requirements.txt` (não impacta o fluxo principal atual porque esse módulo não é usado no ETL principal).
- O fluxo já possui camada analítica SQL, mas ainda depende de execução/agendamento operacional para uso contínuo.

## 8) Definição de pronto sugerida

Considerar o projeto finalizado quando:

- ETL processar automaticamente novos CSVs com logs e rastreabilidade;
- camada analítica e KPIs estiverem aplicados no Postgres;
- checks de qualidade forem executados de forma recorrente;
- dashboard conectado ao banco responder às perguntas-chave do negócio.
