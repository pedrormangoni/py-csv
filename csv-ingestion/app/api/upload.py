# O Upload tem como responsabilidade validar os arquivos CSV que são colocados na pasta 'unread' e transferi-los para a pasta 'read' se estiverem corretos. Ele pode ser implementado para verificar se os arquivos possuem as colunas esperadas, se estão no formato correto e se não estão vazios antes de movê-los para a pasta 'read'.

import csv, shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

EXPECTED_COLUMNS = [
    'Data de Compra', 
    'Nome no Cartão', 
    'Final do Cartão',
    'Categoria',
    'Descrição',
    'Parcela',
    'Valor (em US$)',
    'Cotação (em R$)',
    'Valor (em R$)']  # Colunas esperadas

# Função para validar as colunas do arquivo CSV
def validate_columns_file(file_path: Path) -> bool:
    # Verifica se o arquivo existe
    if not file_path.exists():
        logging.warning(f"{file_path.name} não encontrado.")
        return False
    # Verifica se o arquivo é um CSV ou XLSX
    if file_path.suffix.lower() not in [".csv", ".xlsx"]:
        logging.warning(f"{file_path.name} não é um arquivo CSV ou XLSX.")
        return False
    try:
        # Lê o arquivo CSV e verifica as colunas
        with open(file_path, "r", encoding="utf-8") as csvfile:
            # O delimitador é definido como ';' para arquivos CSV
            reader = csv.reader(csvfile, delimiter=";")
            # Lê a primeira linha do arquivo para obter as colunas
            header = next(reader)

            # Compara as colunas do arquivo com as colunas esperadas
            if header != EXPECTED_COLUMNS:
                logging.warning(f"{file_path.name} colunas inválidas: {header}")
                return False
            return True
        
    # Captura qualquer exceção que possa ocorrer durante a leitura do arquivo
    except Exception as e:
        logging.error(f"Erro ao validar {file_path.name}: {e}")
        return False



def transfer_csv_files():
    # Caminho absoluto para a pasta 'unread' a partir do diretório do script
    base_dir = Path(__file__).parent.parent / "datas" / "unread"

    # Verifica se a pasta existe
    base_dir.mkdir(parents=True, exist_ok=True)

    # Lista de arquivos CSV na pasta 'unread'
    csv_files = base_dir.glob("*.csv")

    # Caminho absoluto para a pasta 'read' a partir do diretório do script
    read_dir = Path(__file__).parent.parent / "datas" / "read"

    # Verifica se a pasta existe
    read_dir.mkdir(parents=True, exist_ok=True)

    # Contador arquivos transferidos
    transfered_files = 0
    # Contador arquivos não transferidos
    untransfered_files = 0

    # Move os arquivos lidosa
    for arquivo in base_dir.glob("*.csv"):
        # Valida o tamanho do arquivo
        if arquivo.stat().st_size > 0:
            if validate_columns_file(arquivo):
                # shutil aceita tanto strings quanto objetos Path
                shutil.move(str(arquivo), str(read_dir / arquivo.name))
                transfered_files += 1
        else:
            untransfered_files += 1

    print(transfered_files, "Arquivos transferidos")
    print(untransfered_files, "Arquivos não transferidos")

