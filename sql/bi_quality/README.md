# Quality Checks (BI)

Consultas SQL para monitoramento de qualidade dos dados carregados em `stg_credit_card_transactions`.

## Arquivos

- `01_qc_contagem_geral.sql`: volume total, período e quantidade de arquivos.
- `02_qc_nulos_vazios.sql`: contagem de nulos/vazios por campo crítico.
- `03_qc_duplicidade_potencial.sql`: possíveis duplicados por chave de negócio.
- `04_qc_consistencia_cambial.sql`: diferenças relevantes entre `amount_brl` e `amount_usd * fx_rate_brl`.
- `05_qc_parcelamento_inconsistente.sql`: inconsistências no parcelamento.
- `06_qc_categorias_semelhantes.sql`: variações de escrita na mesma categoria.
- `07_qc_outliers_valor.sql`: outliers de valor em BRL (método IQR).
- `08_qc_resumo_status.sql`: resumo consolidado de qualidade.

## Como executar

### pgAdmin
Execute os arquivos individualmente no Query Tool do banco `credit-card`.

### psql (terminal)
Na pasta `sql/bi_quality`, execute:

```bash
psql -h localhost -p 5433 -U postgres -d credit-card -f 00_apply_all_quality_checks.sql
```

> Observação: o arquivo agregador usa `\\i`, que é comando do `psql`.
