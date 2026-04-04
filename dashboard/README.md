# Dashboard (Streamlit)

Dashboard analítico conectado ao PostgreSQL com base nas views e KPIs do projeto.

## Pré-requisitos

- Banco PostgreSQL ativo (`docker compose up -d db`)
- ETL já executado
- Views/KPIs aplicados no banco

## Instalação

Na raiz do projeto:

```bash
source .venv/bin/activate
python -m pip install -r csv-ingestion/requirements.txt
```

## Execução

```bash
streamlit run dashboard/streamlit_app.py
```

Acesse no navegador: `http://localhost:8501`

## O que o dashboard mostra

- KPIs principais (gasto total, ticket médio, percentual parcelado, categoria líder)
- Evolução mensal de gastos e quantidade
- Distribuição por categoria
- Impacto de parcelamento
- Impacto de cotação USD/BRL
- Frequência por categoria ao longo do tempo
