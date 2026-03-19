"""
Pipeline ETL para ingestão de dados de faturas CSV
Extrai dados dos CSVs, transforma e carrega no Data Warehouse PostgreSQL
"""

import os
import csv
import psycopg2
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """Pipeline ETL para processamento de faturas CSV"""
    
    def __init__(self, conn):
        self.conn = conn
        self.cur = conn.cursor()
        self.dimensoes_cache = {
            'cartao': {},
            'categoria': {},
            'comerciante': {},
            'data': {}
        }
        
    def extrair_numero_parcela(self, parcela_str: str) -> Tuple[int, int]:
        """
        Extrai número da parcela e total de parcelas
        Formato esperado: '5/10' (5 de 10)
        
        Args:
            parcela_str: String no formato 'X/Y'
            
        Returns:
            Tupla (numero_parcela, total_parcelas)
        """
        try:
            if not parcela_str or parcela_str.strip() == '':
                return None, None
            
            partes = parcela_str.strip().split('/')
            if len(partes) == 2:
                numero = int(partes[0].strip())
                total = int(partes[1].strip())
                return numero, total
        except (ValueError, IndexError):
            logger.warning(f"Erro ao parsear parcela: '{parcela_str}'")
        
        return None, None
    
    def limpar_valor(self, valor_str: str) -> float:
        """
        Limpa e converte valor numérico
        Remove espaços e converte vírgula em ponto
        
        Args:
            valor_str: String com o valor
            
        Returns:
            Float com o valor convertido
        """
        try:
            if not valor_str or valor_str.strip() == '':
                return 0.0
            
            # Remover espaços
            valor_str = valor_str.strip()
            # Converter vírgula em ponto
            valor_str = valor_str.replace(',', '.')
            return float(valor_str)
        except ValueError:
            logger.warning(f"Erro ao converter valor: '{valor_str}'")
            return 0.0
    
    def parsear_data(self, data_str: str) -> datetime.date:
        """
        Converte string de data em objeto date
        Formato esperado: 'DD/MM/YYYY'
        
        Args:
            data_str: String com a data
            
        Returns:
            datetime.date ou None
        """
        try:
            if not data_str or data_str.strip() == '':
                return None
            
            partes = data_str.strip().split('/')
            if len(partes) == 3:
                dia = int(partes[0])
                mes = int(partes[1])
                ano = int(partes[2])
                return datetime(ano, mes, dia).date()
        except (ValueError, IndexError):
            logger.warning(f"Erro ao parsear data: '{data_str}'")
        
        return None
    
    def carregar_ou_criar_dim_data(self, data: datetime.date) -> int:
        """
        Retorna id_data da dimensão, criando se necessário
        
        Args:
            data: datetime.date object
            
        Returns:
            id_data (int)
        """
        if data in self.dimensoes_cache['data']:
            return self.dimensoes_cache['data'][data]
        
        try:
            # Verificar se já existe
            self.cur.execute(
                "SELECT id_data FROM dim_data WHERE data_completa = %s",
                (data,)
            )
            resultado = self.cur.fetchone()
            
            if resultado:
                id_data = resultado[0]
            else:
                # Criar novo
                dia_semana = data.weekday() + 1  # Python: 0=seg, 6=dom; SQL: 1=dom, 7=sab
                if dia_semana == 7:  # Segunda de Python = 7 em SQL
                    dia_semana = 1
                else:
                    dia_semana = dia_semana + 1
                
                mes_nomes = [
                    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
                ]
                dia_semana_nomes = [
                    'Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'
                ]
                
                semana_ano = data.isocalendar()[1]
                trimestre = (data.month - 1) // 3 + 1
                eh_fim_semana = data.weekday() >= 5  # Sábado=5, Domingo=6
                
                self.cur.execute(
                    """INSERT INTO dim_data 
                    (data_completa, ano, mes, mes_nome, dia, dia_semana, dia_semana_nome, 
                     semana_ano, trimestre, eh_fim_semana)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_data""",
                    (data, data.year, data.month, mes_nomes[data.month - 1],
                     data.day, dia_semana, dia_semana_nomes[(dia_semana - 1) % 7],
                     semana_ano, trimestre, eh_fim_semana)
                )
                id_data = self.cur.fetchone()[0]
            
            self.dimensoes_cache['data'][data] = id_data
            return id_data
            
        except Exception as e:
            logger.error(f"Erro ao processar dimensão de data: {e}")
            raise
    
    def carregar_ou_criar_dim_cartao(self, nome_titular: str, final_cartao: str) -> int:
        """
        Retorna id_cartao da dimensão, criando se necessário
        
        Args:
            nome_titular: Nome do titular
            final_cartao: Últimos 4 dígitos
            
        Returns:
            id_cartao (int)
        """
        chave = f"{nome_titular.upper()}_{final_cartao}"
        
        if chave in self.dimensoes_cache['cartao']:
            return self.dimensoes_cache['cartao'][chave]
        
        try:
            self.cur.execute(
                "SELECT id_cartao FROM dim_cartao WHERE chave_cartao = %s",
                (chave,)
            )
            resultado = self.cur.fetchone()
            
            if resultado:
                id_cartao = resultado[0]
            else:
                self.cur.execute(
                    """INSERT INTO dim_cartao (nome_titular, final_cartao, chave_cartao)
                    VALUES (%s, %s, %s)
                    RETURNING id_cartao""",
                    (nome_titular.upper(), final_cartao, chave)
                )
                id_cartao = self.cur.fetchone()[0]
            
            self.dimensoes_cache['cartao'][chave] = id_cartao
            return id_cartao
            
        except Exception as e:
            logger.error(f"Erro ao processar dimensão de cartão: {e}")
            raise
    
    def carregar_ou_criar_dim_categoria(self, categoria: str) -> int:
        """
        Retorna id_categoria da dimensão, criando se necessário
        
        Args:
            categoria: Nome da categoria
            
        Returns:
            id_categoria (int)
        """
        categoria_upper = categoria.upper()
        
        if categoria_upper in self.dimensoes_cache['categoria']:
            return self.dimensoes_cache['categoria'][categoria_upper]
        
        try:
            self.cur.execute(
                "SELECT id_categoria FROM dim_categoria WHERE categoria = %s",
                (categoria_upper,)
            )
            resultado = self.cur.fetchone()
            
            if resultado:
                id_categoria = resultado[0]
            else:
                self.cur.execute(
                    "INSERT INTO dim_categoria (categoria) VALUES (%s) RETURNING id_categoria",
                    (categoria_upper,)
                )
                id_categoria = self.cur.fetchone()[0]
            
            self.dimensoes_cache['categoria'][categoria_upper] = id_categoria
            return id_categoria
            
        except Exception as e:
            logger.error(f"Erro ao processar dimensão de categoria: {e}")
            raise
    
    def carregar_ou_criar_dim_comerciante(self, nome_comerciante: str) -> int:
        """
        Retorna id_comerciante da dimensão, criando se necessário
        
        Args:
            nome_comerciante: Nome do comerciante
            
        Returns:
            id_comerciante (int)
        """
        comerciante_upper = nome_comerciante.upper()
        
        if comerciante_upper in self.dimensoes_cache['comerciante']:
            return self.dimensoes_cache['comerciante'][comerciante_upper]
        
        try:
            self.cur.execute(
                "SELECT id_comerciante FROM dim_comerciante WHERE nome_comerciante = %s",
                (comerciante_upper,)
            )
            resultado = self.cur.fetchone()
            
            if resultado:
                id_comerciante = resultado[0]
            else:
                self.cur.execute(
                    "INSERT INTO dim_comerciante (nome_comerciante) VALUES (%s) RETURNING id_comerciante",
                    (comerciante_upper,)
                )
                id_comerciante = self.cur.fetchone()[0]
            
            self.dimensoes_cache['comerciante'][comerciante_upper] = id_comerciante
            return id_comerciante
            
        except Exception as e:
            logger.error(f"Erro ao processar dimensão de comerciante: {e}")
            raise
    
    def processar_arquivo_csv(self, caminho_arquivo: str) -> int:
        """
        Processa um arquivo CSV e carrega os dados no DW
        
        Args:
            caminho_arquivo: Caminho completo do arquivo CSV
            
        Returns:
            Número de registros inseridos
        """
        registros_inseridos = 0
        registros_errados = 0
        
        logger.info(f"Processando arquivo: {caminho_arquivo}")
        
        try:
            with open(caminho_arquivo, 'r', encoding='latin-1') as f:
                reader = csv.DictReader(f, delimiter=';')
                
                for idx, linha in enumerate(reader, 1):
                    try:
                        # Extrair e limpar dados
                        data = self.parsear_data(linha.get('Data de Compra', ''))
                        nome_titular = linha.get('Nome no Cartão', '').strip()
                        final_cartao = linha.get('Final do Cartão', '').strip()
                        categoria = linha.get('Categoria', '').strip()
                        descricao = linha.get('Descrição', '').strip()
                        parcela_str = linha.get('Parcela', '').strip()
                        valor_usd = self.limpar_valor(linha.get('Valor (em US$)', '0'))
                        cotacao = self.limpar_valor(linha.get('Cotação (em R$)', '0'))
                        valor_brl = self.limpar_valor(linha.get('Valor (em R$)', '0'))
                        
                        # Validações
                        if not data:
                            logger.warning(f"Data inválida na linha {idx}")
                            registros_errados += 1
                            continue
                        
                        if not nome_titular or not final_cartao:
                            logger.warning(f"Cartão inválido na linha {idx}")
                            registros_errados += 1
                            continue
                        
                        if valor_usd == 0 and valor_brl == 0:
                            logger.warning(f"Valor zerado na linha {idx}")
                            registros_errados += 1
                            continue
                        
                        # Carregar ou criar dimensões
                        id_data = self.carregar_ou_criar_dim_data(data)
                        id_cartao = self.carregar_ou_criar_dim_cartao(nome_titular, final_cartao)
                        id_categoria = self.carregar_ou_criar_dim_categoria(categoria)
                        id_comerciante = self.carregar_ou_criar_dim_comerciante(descricao)
                        
                        # Extrair número de parcelas
                        numero_parcela, total_parcelas = self.extrair_numero_parcela(parcela_str)
                        
                        # Inserir na tabela de fatos
                        self.cur.execute(
                            """INSERT INTO fato_transacoes 
                            (id_data, id_cartao, id_categoria, id_comerciante, valor_usd, 
                             cotacao, valor_brl, numero_parcela, total_parcelas)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (id_data, id_cartao, id_categoria, id_comerciante, valor_usd,
                             cotacao, valor_brl, numero_parcela, total_parcelas)
                        )
                        
                        registros_inseridos += 1
                        
                        if registros_inseridos % 50 == 0:
                            logger.info(f"  {registros_inseridos} registros processados...")
                        
                    except Exception as e:
                        logger.error(f"Erro ao processar linha {idx}: {e}")
                        registros_errados += 1
                        continue
                
                # Confirmar transação
                self.conn.commit()
                
        except Exception as e:
            logger.error(f"Erro ao processar arquivo: {e}")
            self.conn.rollback()
            raise
        
        logger.info(f"✓ {registros_inseridos} registros inseridos, {registros_errados} erros")
        return registros_inseridos
    
    def processar_todos_csvs(self, diretorio: str) -> int:
        """
        Processa todos os arquivos CSV no diretório especificado
        
        Args:
            diretorio: Caminho do diretório com arquivos CSV
            
        Returns:
            Total de registros inseridos
        """
        total_inseridos = 0
        
        logger.info(f"Buscando arquivos CSV em: {diretorio}")
        
        arquivos_csv = list(Path(diretorio).glob("*.csv"))
        
        if not arquivos_csv:
            logger.warning(f"Nenhum arquivo CSV encontrado em: {diretorio}")
            return 0
        
        logger.info(f"Encontrados {len(arquivos_csv)} arquivos CSV")
        
        for arquivo in sorted(arquivos_csv):
            try:
                inseridos = self.processar_arquivo_csv(str(arquivo))
                total_inseridos += inseridos
            except Exception as e:
                logger.error(f"Falha ao processar {arquivo.name}: {e}")
                continue
        
        return total_inseridos


def executar_etl(diretorio_csv: str = None):
    """
    Função principal para executar o ETL
    
    Args:
        diretorio_csv: Diretório com arquivos CSV (padrão: ./app/datas/unread)
    """
    if diretorio_csv is None:
        diretorio_csv = os.path.join(
            os.path.dirname(__file__), 
            "..", "datas", "unread"
        )
    
    try:
        # Conectar ao banco de dados
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database=os.getenv("POSTGRES_DB", "csv_dw"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            port=os.getenv("POSTGRES_PORT", "5432")
        )
        
        logger.info("✓ Conectado ao PostgreSQL")
        
        # Importar e criar tabelas
        from app.pipeline.schema import create_database_tables
        create_database_tables(conn)
        
        # Executar ETL
        pipeline = ETLPipeline(conn)
        total = pipeline.processar_todos_csvs(diretorio_csv)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"ETL Completo! Total de registros: {total}")
        logger.info(f"{'='*50}\n")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Erro geral: {e}")
        raise


if __name__ == "__main__":
    executar_etl()
