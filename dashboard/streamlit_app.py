import os
from pathlib import Path

import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv
from psycopg2 import OperationalError


ROOT_DIR = Path(__file__).resolve().parents[1]


def _load_env() -> None:
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def _get_conn():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5433")
    db_config = {
        "host": host,
        "database": os.getenv("POSTGRES_DB", "credit-card"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "port": port,
    }

    attempts = [db_config.copy()]

    if host == "db":
        attempts.append({**db_config, "host": "localhost"})
        if str(port) == "5432":
            attempts.append({**db_config, "host": "localhost", "port": "5433"})

    last_error = None
    for attempt in attempts:
        try:
            return psycopg2.connect(**attempt)
        except OperationalError as exc:
            last_error = exc

    raise last_error


def _read_sql(relative_path: str) -> str:
    return (ROOT_DIR / relative_path).read_text(encoding="utf-8")


@st.cache_data(ttl=60)
def _load_dataframe(sql: str) -> pd.DataFrame:
    with _get_conn() as conn:
        return pd.read_sql_query(sql, conn)


@st.cache_data(ttl=60)
def load_kpis() -> dict:
    df = _load_dataframe(_read_sql("sql/bi_kpis/08_kpi_resumo_geral.sql"))
    if df.empty:
        return {}

    row = df.iloc[0].to_dict()
    return row


@st.cache_data(ttl=60)
def load_charts() -> dict:
    return {
        "mensal": _load_dataframe("SELECT * FROM vw_gastos_mensais ORDER BY mes"),
        "categoria": _load_dataframe("SELECT * FROM vw_gastos_categoria ORDER BY total_gasto_brl DESC"),
        "parcelamento": _load_dataframe("SELECT * FROM vw_parcelamento ORDER BY total_gasto_brl DESC"),
        "fx": _load_dataframe("SELECT * FROM vw_fx_impacto_mensal ORDER BY mes"),
        "frequencia": _load_dataframe(
            "SELECT * FROM vw_frequencia_categoria_mensal ORDER BY mes, frequencia_compras DESC"
        ),
    }


def _format_currency(value, prefix="R$") -> str:
    if value is None:
        return "-"
    return f"{prefix} {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _format_percent(value) -> str:
    if value is None:
        return "-"
    return f"{float(value):.2f}%".replace(".", ",")


def main() -> None:
    _load_env()
    st.set_page_config(page_title="Dashboard de Gastos", layout="wide")
    st.title("Dashboard Financeiro de Compras no Cartão")
    st.caption("Base: stg_credit_card_transactions (somente compras válidas)")

    try:
        kpis = load_kpis()
        charts = load_charts()
    except Exception as exc:
        st.error("Não foi possível carregar os dados do banco.")
        st.exception(exc)
        st.stop()

    if not kpis:
        st.warning("Sem dados para exibir no dashboard.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total gasto (BRL)", _format_currency(kpis.get("kpi_total_gasto_brl")))
    col2.metric("Total gasto (USD)", _format_currency(kpis.get("kpi_total_gasto_usd"), prefix="US$"))
    col3.metric("Ticket médio (BRL)", _format_currency(kpis.get("kpi_ticket_medio_brl")))
    col4.metric("Qtd compras", f"{int(kpis.get('kpi_quantidade_compras', 0))}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("% compras parceladas", _format_percent(kpis.get("kpi_percentual_compras_parceladas")))
    col6.metric("Mês de maior gasto", str(kpis.get("kpi_mes_maior_gasto", "-")))
    col7.metric("Valor mês líder", _format_currency(kpis.get("kpi_valor_mes_maior_gasto_brl")))
    col8.metric("Categoria líder", str(kpis.get("kpi_categoria_lider", "-")))

    st.subheader("Evolução mensal")
    mensal = charts["mensal"].copy()
    mensal["mes"] = pd.to_datetime(mensal["mes"])
    st.line_chart(mensal.set_index("mes")[["total_gasto_brl", "quantidade_compras"]])

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Gastos por categoria")
        categoria = charts["categoria"].copy()
        st.bar_chart(categoria.set_index("category")["total_gasto_brl"])

    with c2:
        st.subheader("Impacto de parcelamento")
        parcelamento = charts["parcelamento"].copy()
        st.bar_chart(parcelamento.set_index("tipo_compra")[["total_gasto_brl", "quantidade_compras"]])

    st.subheader("Impacto de cotação (USD x BRL)")
    fx = charts["fx"].copy()
    fx["mes"] = pd.to_datetime(fx["mes"])
    st.line_chart(fx.set_index("mes")[["total_usd", "total_brl_real", "cotacao_media"]])

    st.subheader("Frequência por categoria (detalhado)")
    st.dataframe(charts["frequencia"], use_container_width=True)


if __name__ == "__main__":
    main()
