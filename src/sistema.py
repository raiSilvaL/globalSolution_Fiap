import csv
import ast
from collections import deque 

# Cores ANSI para o Terminal
RESET = "\033[0m"
VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
CIANO = "\033[96m"
NEGRITO = "\033[1m"

# Estruturas Globais 
# Fila para organizar alertas dinâmicos gerados pelo sistema
fila_alertas_sistema = deque() 
# Pilha para registrar os últimos eventos críticos
pilha_eventos_criticos = [] 
# Matriz para leituras por horário e variável
matriz_historico = [] 

def lerDados(caminhoDados):
    """
    Objetivo: Carregar dados brutos de um arquivo CSV externo e alimentar a matriz global.
    """
    dados = {}
    try:
        with open(caminhoDados, 'r', newline='', encoding='utf-8') as file:
            leitor = csv.DictReader(file)
            cabecalho = leitor.fieldnames
            dados = {coluna: [] for coluna in cabecalho}
            
            global matriz_historico
            matriz_historico = [cabecalho]
            
            for linha in leitor:
                linha_matriz = []
                for coluna in cabecalho:
                    valor = linha[coluna]
                    try:
                        valor_num = float(valor) if '.' in valor else int(valor)
                        dados[coluna].append(valor_num)
                        linha_matriz.append(valor_num)
                    except ValueError:
                        dados[coluna].append(valor)
                        linha_matriz.append(valor)
                matriz_historico.append(linha_matriz)
    except Exception as e:
        print(f"{VERMELHO}Erro ao ler arquivo: {e}{RESET}")
    return dados

def organizarDados(dados):
    """
    Objetivo: Estruturar os dados em dicionários para acesso rápido e hierárquico.
    """
    if not dados: return {}
    return {
        'hRegistro': dados.get('dateTime', []),
        'hierarquia': {
            'energia': {
                'restante': dados.get('energiaRest(%)', []),
                'gerada': dados.get('energiaGerada(Kw/h)', [])
            },
            'habitat': {
                'tempInterna': dados.get('tempInterna(°C)', []),
                'tempExterna': dados.get('tempExterna(°C)', []),
                'radiacao': dados.get('nivelRadiacao(mSv)', [])
            }
        },
        'módulos': {
            'comunicacao': dados.get('modComunicacao', []),
            'habitacao': dados.get('modHabitacao', []),
            'laboratorio': dados.get('modLaboratorio', []),
            'armazenamento': dados.get('modArmazenamento', []),
            'energia': dados.get('modEnergia', []),
            'suporteVida': dados.get('modSupVida', [])
        },
        'sensores': {
            'energiaRestante': dados.get('energiaRest(%)', []),
            'energiaGerada': dados.get('energiaGerada(Kw/h)', []),
            'tempExterna': dados.get('tempExterna(°C)', []),
            'tempInterna': dados.get('tempInterna(°C)', []),
            'radiacao': dados.get('nivelRadiacao(mSv)', []),
            'velVento': dados.get('velVento(m/s)', [])
        },
        'comunicacaoStatus': dados.get('qldComunicacao', []),
        'logEventos': dados.get('logEventos', [])
    }

def realizarPrevisao(dados_energia, janela=3):
    """
    Objetivo: Aplicar média móvel para prever a tendência de energia.
    """
    if len(dados_energia) < 2: return dados_energia[-1] if dados_energia else 0
    ultimos = dados_energia[-janela:]
    media = sum(ultimos) / len(ultimos)
    tendencia = ultimos[-1] - ultimos[-2]
    return round(max(0.0, min(100.0, media + tendencia)), 2)

def colorirValor(valor, tipo):
    """
    Objetivo: Aplicar cores baseadas em faixas de segurança oficiais.
    """
    if tipo == 'energiaRestante':
        if valor < 20: return f"{VERMELHO}{valor}%{RESET}"
        if valor < 40: return f"{AMARELO}{valor}%{RESET}"
        return f"{VERDE}{valor}%{RESET}"
    
    if tipo == 'radiacao':
        if valor > 13: return f"{VERMELHO}{valor} mSv{RESET}"
        if valor > 10: return f"{AMARELO}{valor} mSv{RESET}"
        return f"{VERDE}{valor} mSv{RESET}"
    
    if tipo == 'tempInterna':
        if valor < 15 or valor > 30: return f"{VERMELHO}{valor}°C{RESET}"
        return f"{VERDE}{valor}°C{RESET}"
    
    if tipo == 'tempExterna':
        if valor < -10 or valor > 40: return f"{AMARELO}{valor}°C{RESET}"
        return f"{VERDE}{valor}°C{RESET}"
    
    if tipo == 'velVento':
        if valor > 10: return f"{AMARELO}{valor} m/s{RESET}"
        return f"{VERDE}{valor} m/s{RESET}"
    
    if tipo == 'energiaGerada':
        if valor < 2800: return f"{AMARELO}{valor} Kw/h{RESET}"
        return f"{VERDE}{valor} Kw/h{RESET}"

    return f"{valor}"

def classificarMissao(situacao):
    """
    Objetivo: Definir o status global via lógica booleana.
    """
    modulos = situacao['modulos']
    sensores = situacao['sensores']
    
    falhas_criticas = sum(1 for v in [modulos['suporteVida'], modulos['energia'], modulos['habitacao']] if v == 0)
    
    is_critico = (falhas_criticas >= 1) or (sensores['energiaRestante'] < 20) or (sensores['radiacao'] > 13.0)
    is_alerta = (not is_critico) and (sum(modulos.values()) < len(modulos) or sensores['energiaRestante'] < 40)

    if is_critico:
        return f"{VERMELHO}{NEGRITO}CRÍTICO{RESET}", f"{VERMELHO}Risco imediato à integridade da missão.{RESET}", 3
    elif is_alerta:
        return f"{AMARELO}{NEGRITO}ALERTA{RESET}", f"{AMARELO}Sistemas em estado de atenção.{RESET}", 2
    else:
        return f"{VERDE}{NEGRITO}NORMAL{RESET}", f"{VERDE}Todos os sistemas operando nominalmente.{RESET}", 1

def gerenciarAlertas(status, situacao, previsao):
    """
    Objetivo: Gerar alertas e recomendações, separando-os por prioridade.
    """
    alertas_ciclo = []
    recomendas = []
    
    # 1. Alertas de Falha de Módulos (Crítico)
    for mod, val in situacao['modulos'].items():
        if val == 0:
            msg = f"FALHA NO MÓDULO: {mod.upper()} está inoperante!"
            alertas_ciclo.append({'prioridade': 3, 'msg': f"{VERMELHO}! {msg}{RESET}"})
            pilha_eventos_criticos.append(f"{situacao['horario']} - {msg}")

    # 2. Alertas de Sensores
    s = situacao['sensores']
    if s['energiaRestante'] < 20:
        alertas_ciclo.append({'prioridade': 3, 'msg': f"{VERMELHO}! ENERGIA CRÍTICA: Reserva abaixo de 20%{RESET}"})
    elif s['energiaRestante'] < 40:
        alertas_ciclo.append({'prioridade': 2, 'msg': f"{AMARELO}! ENERGIA BAIXA: Reserva em nível de atenção{RESET}"})

    if s['radiacao'] > 13:
        alertas_ciclo.append({'prioridade': 3, 'msg': f"{VERMELHO}! RADIAÇÃO: Níveis perigosos detectados{RESET}"})

    # 3. Alertas Preditivos
    if previsao < s['energiaRestante']:
        alertas_ciclo.append({'prioridade': 2, 'msg': f"{AMARELO}! TENDÊNCIA: Energia deve cair para {previsao}%{RESET}"})

    # Ordenar alertas por prioridade (3=Crítico, 2=Alerta, 1=Normal)
    alertas_ciclo.sort(key=lambda x: x['prioridade'], reverse=True)
    
    # Adicionar à fila global
    for a in alertas_ciclo:
        fila_alertas_sistema.append(a['msg'])

    # Gerar recomendações baseadas no status
    if "CRÍTICO" in status:
        recomendas.append("AÇÃO 1 (CRÍTICA): Manter suporte à vida e comunicação de emergência.")
        recomendas.append("AÇÃO 2 (ALTA): Desligar o laboratório e sistemas não essenciais.")
    elif "ALERTA" in status:
        recomendas.append("AÇÃO 1: Redirecionar energia para habitat e carregamento de baterias.")
        recomendas.append("AÇÃO 2: Verificar integridade dos módulos em falha.")

    return recomendas

def main():
    caminho = 'data/dados.csv'
    raw_dados = lerDados(caminho)
    if not raw_dados: return

    organizados = organizarDados(raw_dados)
    idx = -1 
    
    log_raw = organizados['logEventos'][idx]
    try:
        eventos_base = ast.literal_eval(log_raw) if isinstance(log_raw, str) else log_raw
    except:
        eventos_base = []

    situacao = {
        'horario': organizados['hRegistro'][idx],
        'modulos': {k: v[idx] for k, v in organizados['módulos'].items()},
        'sensores': {k: v[idx] for k, v in organizados['sensores'].items()},
        'comunicacao': organizados['comunicacaoStatus'][idx],
        'eventos': eventos_base
    }

    previsao_energia = realizarPrevisao(organizados['sensores']['energiaRestante'])
    status, desc, prioridade = classificarMissao(situacao)
    recomendas = gerenciarAlertas(status, situacao, previsao_energia)
    s = situacao['sensores']

    # --------------------------------------------------------------------------
    # INTERFACE DE SAÍDA
    # --------------------------------------------------------------------------
    print("\n" + f"{CIANO}="*60 + f"{RESET}")
    print(f"{CIANO}{NEGRITO} MISSION CONTROL CENTER TELEMETRY {RESET}".center(70))
    print(f"{CIANO}="*60 + f"{RESET}")
    
    print(f"{NEGRITO}HORÁRIO:{RESET} {situacao['horario']}")
    print(f"{NEGRITO}STATUS GERAL:{RESET} {status}")
    print(f"{NEGRITO}DIAGNÓSTICO:{RESET}  {desc}")
    print(f"{CIANO}-"*60 + f"{RESET}")

    print(f"{NEGRITO}[ ESTADO DOS MÓDULOS ]{RESET}")
    for mod, val in situacao['modulos'].items():
        st = f"{VERDE}✓ OPERACIONAL{RESET}" if val == 1 else f"{VERMELHO}✗ FALHA DETECTADA{RESET}"
        print(f" - {mod.capitalize():<15}: {st}")

    print(f"\n{NEGRITO}[ LEITURAS DOS SENSORES (FAIXAS DE SEGURANÇA) ]{RESET}")
    print(f" - Energia Restante: {colorirValor(s['energiaRestante'], 'energiaRestante')} (Previsto: {previsao_energia}%)")
    print(f" - Geração Energia:  {colorirValor(s['energiaGerada'], 'energiaGerada')}")
    print(f" - Nível Radiação:   {colorirValor(s['radiacao'], 'radiacao')}")
    print(f" - Temp. Interna:    {colorirValor(s['tempInterna'], 'tempInterna')}")
    print(f" - Temp. Externa:    {colorirValor(s['tempExterna'], 'tempExterna')}")
    print(f" - Velocidade Vento: {colorirValor(s['velVento'], 'velVento')}")
    
    com_color = VERDE if situacao['comunicacao'] == 'Estavel' else AMARELO
    print(f" - Qualidade Com.:   {com_color}{situacao['comunicacao']}{RESET}")

    # Recomendações Automáticas
    print(f"\n{NEGRITO}[ RECOMENDAÇÕES AUTOMÁTICAS ]{RESET}")
    if recomendas:
        for r in recomendas:
            print(f" {NEGRITO}➜{RESET} {r}")
    else:
        print(f" {VERDE}✓ Nenhuma ação imediata necessária.{RESET}")

    # SEPARAÇÃO DE LOGS
    print(f"\n{NEGRITO}[ ALERTAS GERADOS PELO SISTEMA (PRIORIZADOS) ]{RESET}")
    if fila_alertas_sistema:
        while fila_alertas_sistema:
            print(f" {fila_alertas_sistema.popleft()}")
    else:
        print(f" {VERDE}✓ Nenhum alerta dinâmico gerado.{RESET}")

    print(f"\n{NEGRITO}[ LOGS DA BASE DE DADOS (HISTÓRICO) ]{RESET}")
    if situacao['eventos']:
        for ev in situacao['eventos']:
            cor_log = VERMELHO if "Falha" in ev or "crítica" in ev.lower() else AMARELO
            print(f" • {cor_log}{ev}{RESET}")
    else:
        print(f" {VERDE}✓ Nenhum evento registrado na base.{RESET}")
    
    # Último evento crítico da Pilha
    if pilha_eventos_criticos:
        print(f"\n{NEGRITO}[ ÚLTIMO EVENTO CRÍTICO (PILHA) ]{RESET}")
        print(f" {VERMELHO}⚠ {pilha_eventos_criticos[-1]}{RESET}")
    
    print(f"{CIANO}="*60 + f"{RESET}\n")

if __name__ == "__main__":
    main()
