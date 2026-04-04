"""
Script DDL para criar as tabelas do Data Warehouse
PostgreSQL
"""

CREATE_TABLES_SQL = """

-- Criar tabela de dimensão de datas
CREATE TABLE IF NOT EXISTS dim_data (
    id_data SERIAL PRIMARY KEY,
    data_completa DATE UNIQUE NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes >= 1 AND mes <= 12),
    mes_nome VARCHAR(20) NOT NULL,
    dia INTEGER NOT NULL CHECK (dia >= 1 AND dia <= 31),
    dia_semana INTEGER NOT NULL CHECK (dia_semana >= 1 AND dia_semana <= 7),
    dia_semana_nome VARCHAR(20) NOT NULL,
    semana_ano INTEGER NOT NULL CHECK (semana_ano >= 1 AND semana_ano <= 53),
    trimestre INTEGER NOT NULL CHECK (trimestre >= 1 AND trimestre <= 4),
    eh_fim_semana BOOLEAN NOT NULL
);

-- Criar índice na tabela dim_data
CREATE INDEX IF NOT EXISTS idx_data_completa ON dim_data(data_completa);
CREATE INDEX IF NOT EXISTS idx_data_mes_ano ON dim_data(mes, ano);

-- Criar tabela de dimensão de cartões
CREATE TABLE IF NOT EXISTS dim_cartao (
    id_cartao SERIAL PRIMARY KEY,
    nome_titular VARCHAR(255) NOT NULL,
    final_cartao VARCHAR(4) NOT NULL,
    chave_cartao VARCHAR(265) UNIQUE NOT NULL
);

-- Criar índice na tabela dim_cartao
CREATE UNIQUE INDEX IF NOT EXISTS idx_chave_cartao ON dim_cartao(chave_cartao);

-- Criar tabela de dimensão de categorias
CREATE TABLE IF NOT EXISTS dim_categoria (
    id_categoria SERIAL PRIMARY KEY,
    categoria VARCHAR(255) UNIQUE NOT NULL,
    tipo_despesa VARCHAR(100)
);

-- Criar índice na tabela dim_categoria
CREATE INDEX IF NOT EXISTS idx_categoria ON dim_categoria(categoria);

-- Criar tabela de dimensão de comerciantes
CREATE TABLE IF NOT EXISTS dim_comerciante (
    id_comerciante SERIAL PRIMARY KEY,
    nome_comerciante VARCHAR(255) NOT NULL,
    categoria_comerciante VARCHAR(100),
    UNIQUE(nome_comerciante)
);

-- Criar índice na tabela dim_comerciante
CREATE INDEX IF NOT EXISTS idx_comerciante ON dim_comerciante(nome_comerciante);

-- Criar tabela de fatos (transações)
CREATE TABLE IF NOT EXISTS fato_transacoes (
    id_transacao SERIAL PRIMARY KEY,
    id_data INTEGER NOT NULL REFERENCES dim_data(id_data),
    id_cartao INTEGER NOT NULL REFERENCES dim_cartao(id_cartao),
    id_categoria INTEGER NOT NULL REFERENCES dim_categoria(id_categoria),
    id_comerciante INTEGER NOT NULL REFERENCES dim_comerciante(id_comerciante),
    valor_usd NUMERIC(10, 2),
    cotacao NUMERIC(10, 4) NOT NULL CHECK (cotacao > 0),
    valor_brl NUMERIC(10, 2) NOT NULL,
    numero_parcela INTEGER,
    total_parcelas INTEGER,
    data_insercao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices na tabela fato_transacoes
CREATE INDEX IF NOT EXISTS idx_fato_data ON fato_transacoes(id_data);
CREATE INDEX IF NOT EXISTS idx_fato_cartao ON fato_transacoes(id_cartao);
CREATE INDEX IF NOT EXISTS idx_fato_categoria ON fato_transacoes(id_categoria);
CREATE INDEX IF NOT EXISTS idx_fato_comerciante ON fato_transacoes(id_comerciante);
CREATE INDEX IF NOT EXISTS idx_fato_data_cartao ON fato_transacoes(id_data, id_cartao);

"""

def create_database_tables(conn):
    """
    Executa os comandos SQL para criar as tabelas do Data Warehouse
    
    Args:
        conn: Conexão com o banco de dados PostgreSQL
    """
    try:
        cur = conn.cursor()
        
        # Dividir e executar cada comando separadamente
        commands = CREATE_TABLES_SQL.split(';')
        for command in commands:
            command = command.strip()
            if command:
                print(f"Executando: {command[:60]}...")
                cur.execute(command)
        
        conn.commit()
        print("Tabelas criadas com sucesso!")
        cur.close()
        
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        conn.rollback()
        raise


if __name__ == "__main__":
    import psycopg2
    import os
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database=os.getenv("POSTGRES_DB", "csv_dw"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            port=os.getenv("POSTGRES_PORT", "5432")
        )
        
        create_database_tables(conn)
        conn.close()
        
    except Exception as e:
        print(f"Erro de conexão: {e}")
