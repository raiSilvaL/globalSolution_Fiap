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

def organizarDados(dados):
    if not dados:
        return "Nenhum dado para organizar."

    dadosOrganizados = {}

    # 1. hRegistro (Mapeado de dateTime)
    dadosOrganizados['hRegistro'] = dados.get('dateTime', [])

    # 2. Dicionário de Módulos
    modulos = {}
    modulo_keys = [
        'modComunicacao', 'modHabitacao', 'modLaboratorio',
        'modArmazenamento', 'modEnergia', 'modSupVida'
    ]
    for key in modulo_keys:
        modulos[key] = dados.get(key, [])
    dadosOrganizados['módulos'] = modulos

    # 3. Sensores e Dados Técnicos
    sensor_keys = [
        'capEnergia(Kw/h)', 'energiaRest(%)', 'energiaGerada(Kw/h)',
        'tempExterna(°C)', 'tempInterna(°C)', 'nivelRadiacao(mSv)',
        'qldComunicacao', 'velVento(m/s)'
    ]
    for key in sensor_keys:
        dadosOrganizados[key] = dados.get(key, [])

    # 4. logEventos (Estrutura de Lista de Listas)
    if 'logEventos' in dados and dados['logEventos']:
        dadosOrganizados['logEventos'] = [dados['logEventos']]
    else:
        dadosOrganizados['logEventos'] = [[]]

    return dadosOrganizados

def sistuacaoAtual(dadosOrganizados):
    dadosAtuais = dadosOrganizados['hRegistro'][-1]  # Pega os dados mais recentes

    return dadosAtuais

def main():
    caminhoDados = 'data/dados.csv' 
    dados = lerDados(caminhoDados)
    dadosOrganizados = organizarDados(dados)
    status = sistuacaoAtual(dadosOrganizados)
    print(f"Situação Atual: {status}")

if __name__ == "__main__":
    main()