# Consultas BI

Este diretório contém consultas SQL alinhadas às perguntas de negócio do escopo.

## Arquivos

- `01_total_gasto_periodo.sql`: valor total gasto no período.
- `02_evolucao_mensal_gastos.sql`: evolução mensal de gastos.
- `03_distribuicao_gastos_categoria.sql`: distribuição e proporção por categoria.
- `04_ticket_medio_compras.sql`: ticket médio das compras.
- `05_compras_parceladas_impacto.sql`: volume e impacto de parceladas vs à vista.
- `06_impacto_cotacao_dolar.sql`: efeito de USD/cotação no valor em BRL.
- `07_frequencia_categoria_tempo.sql`: frequência de categorias ao longo do tempo.

## Como executar

1. Conecte no PostgreSQL pelo pgAdmin.
2. Abra o Query Tool no banco `credit-card`.
3. Execute o SQL desejado.

As consultas usam a tabela `stg_credit_card_transactions`, carregada pelo ETL atual.