# Camada Analítica (Views BI)

Este diretório contém views para consumo em pgAdmin e ferramentas de BI.

## Views disponíveis

- `vw_gastos_mensais`: total, volume e ticket médio por mês.
- `vw_gastos_categoria`: distribuição de gastos por categoria com percentual.
- `vw_parcelamento`: comparação entre compras parceladas e à vista.
- `vw_fx_impacto_mensal`: impacto mensal da cotação sobre compras em USD.
- `vw_frequencia_categoria_mensal`: frequência e valor por categoria ao longo do tempo.

## Como aplicar

### Opção 1: executar arquivo por arquivo
No Query Tool (banco `credit-card`), execute os arquivos `01` a `05`.

### Opção 2: aplicar tudo via psql
Dentro da pasta `sql/bi_views`, execute:

```bash
psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_views.sql
```

> Observação: o arquivo `00_apply_all_views.sql` usa comandos `\\i` (psql). No pgAdmin, execute os arquivos individualmente.
