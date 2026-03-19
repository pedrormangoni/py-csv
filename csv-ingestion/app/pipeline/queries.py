"""
Consultas SQL Analíticas para o Data Warehouse de Transações

Este arquivo contém um conjunto de consultas SQL pré-definidas que respondem
às principais perguntas de negócio relacionadas a análise de despesas.
"""

# ============================================================================
# CONSULTAS DE ANÁLISE DE GASTOS POR CATEGORIA
# ============================================================================

# 1. Gasto Total por Categoria (com ranking)
GASTO_POR_CATEGORIA = """
SELECT 
    dc.categoria,
    COUNT(*) as quantidade_transacoes,
    SUM(ft.valor_brl) as total_gasto_brl,
    ROUND(AVG(ft.valor_brl), 2) as ticket_medio,
    ROUND(STDDEV(ft.valor_brl), 2) as desvio_padrao,
    RANK() OVER (ORDER BY SUM(ft.valor_brl) DESC) as ranking
FROM fato_transacoes ft
INNER JOIN dim_categoria dc ON ft.id_categoria = dc.id_categoria
GROUP BY dc.categoria
ORDER BY total_gasto_brl DESC;
"""

# 2. Gastos por Categoria e Mês
GASTO_CATEGORIA_MES = """
SELECT 
    dd.mes,
    dd.mes_nome,
    dc.categoria,
    COUNT(*) as quantidade,
    ROUND(SUM(ft.valor_brl), 2) as total_brl,
    ROUND(SUM(ft.valor_usd), 2) as total_usd
FROM fato_transacoes ft
INNER JOIN dim_data dd ON ft.id_data = dd.id_data
INNER JOIN dim_categoria dc ON ft.id_categoria = dc.id_categoria
WHERE dd.ano = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY dd.mes, dd.mes_nome, dc.categoria
ORDER BY dd.mes, total_brl DESC;
"""

# ============================================================================
# CONSULTAS DE ANÁLISE TEMPORAL
# ============================================================================

# 3. Evolução de Gastos por Mês (Série Temporal)
EVOLUCAO_GASTOS_MES = """
SELECT 
    dd.ano,
    dd.mes,
    dd.mes_nome,
    COUNT(*) as quantidade_transacoes,
    ROUND(SUM(ft.valor_brl), 2) as total_gasto_brl,
    ROUND(AVG(ft.valor_brl), 2) as ticket_medio,
    ROUND(STDDEV(ft.valor_brl), 2) as desvio_padrao
FROM fato_transacoes ft
INNER JOIN dim_data dd ON ft.id_data = dd.id_data
GROUP BY dd.ano, dd.mes, dd.mes_nome
ORDER BY dd.ano, dd.mes;
"""

# 4. Gasto por Trimestre
GASTO_POR_TRIMESTRE = """
SELECT 
    dd.ano,
    dd.trimestre,
    CASE 
        WHEN dd.trimestre = 1 THEN '1º Trimestre'
        WHEN dd.trimestre = 2 THEN '2º Trimestre'
        WHEN dd.trimestre = 3 THEN '3º Trimestre'
        WHEN dd.trimestre = 4 THEN '4º Trimestre'
    END as trimestre_nome,
    COUNT(*) as quantidade_transacoes,
    ROUND(SUM(ft.valor_brl), 2) as total_gasto_brl,
    ROUND(AVG(ft.valor_brl), 2) as ticket_medio
FROM fato_transacoes ft
INNER JOIN dim_data dd ON ft.id_data = dd.id_data
GROUP BY dd.ano, dd.trimestre
ORDER BY dd.ano, dd.trimestre;
"""

# 5. Comparação: Dias de Semana vs Fim de Semana
GASTOS_DIA_SEMANA = """
SELECT 
    CASE 
        WHEN dd.eh_fim_semana = TRUE THEN 'Fim de Semana'
        ELSE 'Dia de Semana'
    END as tipo_dia,
    COUNT(*) as quantidade_transacoes,
    ROUND(SUM(ft.valor_brl), 2) as total_gasto_brl,
    ROUND(AVG(ft.valor_brl), 2) as ticket_medio,
    ROUND(SUM(ft.valor_brl) / COUNT(*), 2) as gasto_medio
FROM fato_transacoes ft
INNER JOIN dim_data dd ON ft.id_data = dd.id_data
GROUP BY dd.eh_fim_semana
ORDER BY tipo_dia;
"""

# ============================================================================
# CONSULTAS DE ANÁLISE DE CARTÕES
# ============================================================================

# 6. Gastos por Cartão (Titular)
GASTO_POR_CARTAO = """
SELECT 
    dc.nome_titular,
    dc.final_cartao,
    COUNT(*) as quantidade_transacoes,
    ROUND(SUM(ft.valor_brl), 2) as total_gasto_brl,
    ROUND(AVG(ft.valor_brl), 2) as ticket_medio,
    MIN(ft.valor_brl) as menor_gasto,
    MAX(ft.valor_brl) as maior_gasto
FROM fato_transacoes ft
INNER JOIN dim_cartao dc ON ft.id_cartao = dc.id_cartao
GROUP BY dc.nome_titular, dc.final_cartao
ORDER BY total_gasto_brl DESC;
"""

# 7. Cartão com Maior Parcelas Pendentes
CARTAO_PARCELAS_PENDENTES = """
SELECT 
    dc.nome_titular,
    dc.final_cartao,
    COUNT(*) as total_parcelas_pendentes,
    ROUND(SUM(ft.valor_brl), 2) as total_valor_parcelado,
    ROUND(AVG(ft.valor_brl), 2) as media_parcela
FROM fato_transacoes ft
INNER JOIN dim_cartao dc ON ft.id_cartao = dc.id_cartao
WHERE ft.numero_parcela < ft.total_parcelas
GROUP BY dc.nome_titular, dc.final_cartao
ORDER BY total_parcelas_pendentes DESC;
"""

# ============================================================================
# CONSULTAS DE ANÁLISE DE COMERCIANTES
# ============================================================================

# 8. Top 10 Comerciantes com Maior Gasto
TOP_10_COMERCIANTES = """
SELECT 
    dm.nome_comerciante,
    COUNT(*) as quantidade_transacoes,
    ROUND(SUM(ft.valor_brl), 2) as total_gasto_brl,
    ROUND(AVG(ft.valor_brl), 2) as ticket_medio,
    RANK() OVER (ORDER BY SUM(ft.valor_brl) DESC) as ranking
FROM fato_transacoes ft
INNER JOIN dim_comerciante dm ON ft.id_comerciante = dm.id_comerciante
GROUP BY dm.nome_comerciante
ORDER BY total_gasto_brl DESC
LIMIT 10;
"""

# 9. Frequência de Compra por Comerciante
FREQUENCIA_COMERCIANTE = """
SELECT 
    dm.nome_comerciante,
    COUNT(*) as vezes_visitado,
    ROUND(SUM(ft.valor_brl), 2) as total_gasto_brl,
    ROUND(AVG(ft.valor_brl), 2) as ticket_medio,
    MAX(dd.data_completa) as ultima_compra,
    MIN(dd.data_completa) as primeira_compra
FROM fato_transacoes ft
INNER JOIN dim_comerciante dm ON ft.id_comerciante = dm.id_comerciante
INNER JOIN dim_data dd ON ft.id_data = dd.id_data
GROUP BY dm.nome_comerciante
ORDER BY vezes_visitado DESC;
"""

# ============================================================================
# CONSULTAS DE ANÁLISE DE MOEDAS E COTAÇÃO
# ============================================================================

# 10. Estatísticas de Cotação por Mês
COTACAO_POR_MES = """
SELECT 
    dd.ano,
    dd.mes,
    dd.mes_nome,
    COUNT(*) as quantidade_transacoes,
    ROUND(MIN(ft.cotacao), 4) as cotacao_minima,
    ROUND(MAX(ft.cotacao), 4) as cotacao_maxima,
    ROUND(AVG(ft.cotacao), 4) as cotacao_media,
    ROUND(STDDEV(ft.cotacao), 4) as cotacao_desvio
FROM fato_transacoes ft
INNER JOIN dim_data dd ON ft.id_data = dd.id_data
WHERE ft.valor_usd > 0
GROUP BY dd.ano, dd.mes, dd.mes_nome
ORDER BY dd.ano, dd.mes;
"""

# 11. Conversão USD/BRL
CONVERSAO_USD_BRL = """
SELECT 
    ROUND(SUM(ft.valor_usd), 2) as total_usd,
    ROUND(SUM(ft.valor_brl), 2) as total_brl,
    ROUND(SUM(ft.valor_brl) / NULLIF(SUM(ft.valor_usd), 0), 4) as taxa_media_efetiva,
    COUNT(*) as quantidade_transacoes_usd
FROM fato_transacoes ft
WHERE ft.valor_usd > 0;
"""

# ============================================================================
# CONSULTAS DE ANÁLISE DE PARCELAMENTO
# ============================================================================

# 12. Distribuição de Parcelamento
DISTRIBUICAO_PARCELAMENTO = """
SELECT 
    ft.total_parcelas,
    COUNT(*) as quantidade_compras,
    ROUND(SUM(ft.valor_brl), 2) as total_valor,
    ROUND(AVG(ft.valor_brl), 2) as ticket_medio,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentual_compras
FROM fato_transacoes ft
WHERE ft.total_parcelas IS NOT NULL
GROUP BY ft.total_parcelas
ORDER BY ft.total_parcelas;
"""

# 13. Valor Médio por Número de Parcelas
VALOR_MEDIO_PARCELAS = """
SELECT 
    ft.total_parcelas,
    COUNT(*) as quantidade_compras,
    ROUND(AVG(ft.valor_brl), 2) as valor_medio_brl,
    MIN(ft.valor_brl) as valor_minimo,
    MAX(ft.valor_brl) as valor_maximo
FROM fato_transacoes ft
WHERE ft.total_parcelas IS NOT NULL AND ft.total_parcelas > 0
GROUP BY ft.total_parcelas
ORDER BY ft.total_parcelas;
"""

# ============================================================================
# CONSULTAS DE DASHBOARD / KPIs
# ============================================================================

# 14. Dashboard de Resumo Geral
RESUMO_GERAL = """
SELECT 
    'Período Analisado' as metrica,
    (SELECT MIN(dd.data_completa)::text FROM fato_transacoes ft INNER JOIN dim_data dd ON ft.id_data = dd.id_data) || 
    ' a ' || 
    (SELECT MAX(dd.data_completa)::text FROM fato_transacoes ft INNER JOIN dim_data dd ON ft.id_data = dd.id_data) as valor
UNION ALL
SELECT 'Total de Transações' as metrica, COUNT(*)::text as valor FROM fato_transacoes
UNION ALL
SELECT 'Gasto Total (BRL)' as metrica, 'R$ ' || ROUND(SUM(ft.valor_brl), 2)::text as valor FROM fato_transacoes ft
UNION ALL
SELECT 'Gasto Total (USD)' as metrica, 'US$ ' || ROUND(SUM(ft.valor_usd), 2)::text as valor FROM fato_transacoes ft WHERE ft.valor_usd > 0
UNION ALL
SELECT 'Ticket Médio (BRL)' as metrica, 'R$ ' || ROUND(AVG(ft.valor_brl), 2)::text as valor FROM fato_transacoes ft
UNION ALL
SELECT 'Maior Gasto' as metrica, 'R$ ' || ROUND(MAX(ft.valor_brl), 2)::text as valor FROM fato_transacoes ft
UNION ALL
SELECT 'Menor Gasto' as metrica, 'R$ ' || ROUND(MIN(ft.valor_brl), 2)::text as valor FROM fato_transacoes ft
UNION ALL
SELECT 'Número de Categorias' as metrica, COUNT(DISTINCT id_categoria)::text as valor FROM fato_transacoes ft
UNION ALL
SELECT 'Número de Comerciantes' as metrica, COUNT(DISTINCT id_comerciante)::text as valor FROM fato_transacoes ft
UNION ALL
SELECT 'Número de Cartões' as metrica, COUNT(DISTINCT id_cartao)::text as valor FROM fato_transacoes ft;
"""

# 15. Tendência de Gastos (últimos 6 meses)
TENDENCIA_6_MESES = """
SELECT 
    dd.data_completa,
    ROUND(SUM(ft.valor_brl), 2) as gasto_diario,
    ROUND(AVG(SUM(ft.valor_brl)) OVER (ORDER BY dd.data_completa ROWS BETWEEN 29 PRECEDING AND CURRENT ROW), 2) as media_movel_30d
FROM fato_transacoes ft
INNER JOIN dim_data dd ON ft.id_data = dd.id_data
WHERE dd.data_completa >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY dd.data_completa
ORDER BY dd.data_completa DESC;
"""

# ============================================================================
# CONSULTAS DE ANÁLISE DE ANOMALIAS
# ============================================================================

# 16. Transações Anormalmente Altas (Top 5%)
TRANSACOES_ANOMALAS = """
WITH percentil AS (
    SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY valor_brl) as valor_p95
    FROM fato_transacoes
)
SELECT 
    ft.id_transacao,
    dd.data_completa,
    dc.nome_titular,
    dm.nome_comerciante,
    dcg.categoria,
    ROUND(ft.valor_brl, 2) as valor_brl,
    (ROUND(ft.valor_brl, 2) - (SELECT AVG(valor_brl) FROM fato_transacoes))::numeric as desvio_media
FROM fato_transacoes ft
INNER JOIN dim_data dd ON ft.id_data = dd.id_data
INNER JOIN dim_cartao dc ON ft.id_cartao = dc.id_cartao
INNER JOIN dim_comerciante dm ON ft.id_comerciante = dm.id_comerciante
INNER JOIN dim_categoria dcg ON ft.id_categoria = dcg.id_categoria
CROSS JOIN percentil
WHERE ft.valor_brl > percentil.valor_p95
ORDER BY ft.valor_brl DESC;
"""

# 17. Comerciantes de Uma Única Compra
COMERCIANTES_UNICOS = """
SELECT 
    dm.nome_comerciante,
    ROUND(ft.valor_brl, 2) as valor_gasto,
    dd.data_completa as data_compra,
    dc.nome_titular,
    dcg.categoria
FROM fato_transacoes ft
INNER JOIN dim_comerciante dm ON ft.id_comerciante = dm.id_comerciante
INNER JOIN dim_data dd ON ft.id_data = dd.id_data
INNER JOIN dim_cartao dc ON ft.id_cartao = dc.id_cartao
INNER JOIN dim_categoria dcg ON ft.id_categoria = dcg.id_categoria
WHERE dm.id_comerciante IN (
    SELECT id_comerciante 
    FROM fato_transacoes 
    GROUP BY id_comerciante 
    HAVING COUNT(*) = 1
)
ORDER BY ft.valor_brl DESC;
"""

# ============================================================================
# DICIONÁRIO DE CONSULTAS (para uso programático)
# ============================================================================

CONSULTAS = {
    'gasto_categoria': {
        'descricao': 'Gasto total por categoria com ranking',
        'query': GASTO_POR_CATEGORIA
    },
    'gasto_categoria_mes': {
        'descricao': 'Gastos por categoria e mês',
        'query': GASTO_CATEGORIA_MES
    },
    'evolucao_gastos': {
        'descricao': 'Evolução de gastos por mês (série temporal)',
        'query': EVOLUCAO_GASTOS_MES
    },
    'gasto_trimestre': {
        'descricao': 'Gasto por trimestre',
        'query': GASTO_POR_TRIMESTRE
    },
    'gastos_dia_semana': {
        'descricao': 'Comparação entre dias de semana e fim de semana',
        'query': GASTOS_DIA_SEMANA
    },
    'gasto_cartao': {
        'descricao': 'Gastos por cartão (titular)',
        'query': GASTO_POR_CARTAO
    },
    'parcelas_pendentes': {
        'descricao': 'Cartões com maior número de parcelas pendentes',
        'query': CARTAO_PARCELAS_PENDENTES
    },
    'top_comerciantes': {
        'descricao': 'Top 10 comerciantes com maior gasto',
        'query': TOP_10_COMERCIANTES
    },
    'frequencia_comerciante': {
        'descricao': 'Frequência de compra por comerciante',
        'query': FREQUENCIA_COMERCIANTE
    },
    'cotacao_mes': {
        'descricao': 'Estatísticas de cotação USD/BRL por mês',
        'query': COTACAO_POR_MES
    },
    'conversao_usd_brl': {
        'descricao': 'Conversão total USD para BRL',
        'query': CONVERSAO_USD_BRL
    },
    'distribuicao_parcelamento': {
        'descricao': 'Distribuição de parcelamentos',
        'query': DISTRIBUICAO_PARCELAMENTO
    },
    'valor_medio_parcelas': {
        'descricao': 'Valor médio por número de parcelas',
        'query': VALOR_MEDIO_PARCELAS
    },
    'resumo_geral': {
        'descricao': 'Dashboard de KPIs gerais',
        'query': RESUMO_GERAL
    },
    'tendencia_6_meses': {
        'descricao': 'Tendência de gastos últimos 6 meses',
        'query': TENDENCIA_6_MESES
    },
    'transacoes_anomalas': {
        'descricao': 'Transações anormalmente altas (top 5%)',
        'query': TRANSACOES_ANOMALAS
    },
    'comerciantes_unicos': {
        'descricao': 'Comerciantes com apenas uma compra',
        'query': COMERCIANTES_UNICOS
    }
}


def listar_consultas():
    """Lista todas as consultas disponíveis"""
    print("\n" + "="*70)
    print("CONSULTAS SQL DISPONÍVEIS")
    print("="*70 + "\n")
    
    for chave, info in CONSULTAS.items():
        print(f"  • {chave}")
        print(f"    {info['descricao']}\n")
    
    print("="*70)


if __name__ == "__main__":
    import psycopg2
    import os
    
    listar_consultas()
    
    # Exemplo de uso programático
    print("\nPara executar uma consulta, use:")
    print("  from app.pipeline.queries import CONSULTAS")
    print("  from psycopg2 import connect")
    print("  ")
    print("  conn = connect(...)")
    print("  cur = conn.cursor()")
    print("  cur.execute(CONSULTAS['gasto_categoria']['query'])")
    print("  resultados = cur.fetchall()")
