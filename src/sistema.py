import csv

def lerDados(caminhoDados):
    dados = {}
    try:
        with open(caminhoDados, 'r', newline='', encoding='utf-8') as file:
            leitor = csv.reader(file)
            cabecalho = next(leitor)  # Lê o cabeçalho
            dados = {coluna: [] for coluna in cabecalho}

            for linha in leitor:
                if linha:  # Verifica se a linha não está vazia
                    for coluna, valor in zip(cabecalho, linha):
                        dados[coluna].append(valor)
    except FileNotFoundError:
        print("Arquivo não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    return dados

