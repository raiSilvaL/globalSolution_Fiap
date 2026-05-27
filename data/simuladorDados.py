import csv
import os
import random
from datetime import datetime, timedelta

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = os.path.join(PASTA, 'dados.csv')

_data_atual = datetime(2025, 1, 1, 10, 0, 0)

def statusLog(dados):
    logEventos = []

    if dados['modComunicacao'] == 0:
        logEventos.append("Falha no sistema de comunicação")
    if dados['modHabitacao'] == 0:
        logEventos.append("Falha no sistema de habitação")
    if dados['modLaboratorio'] == 0:
        logEventos.append("Falha no sistema de laboratório")
    if dados['modArmazenamento'] == 0:
        logEventos.append("Falha no sistema de armazenamento")
    if dados['modEnergia'] == 0:
        logEventos.append("Falha no sistema de energia")
    if dados['modSupVida'] == 0:
        logEventos.append("Falha no sistema de suporte à vida")
    if dados['energiaGerada(Kw/h)'] < 2800:
        logEventos.append("Geração de energia baixa")
    if dados['energiaRest(%)'] < 20:
        logEventos.append("Nível de energia crítica")
    if dados['tempExterna(°C)'] < -10 or dados['tempExterna(°C)'] > 40:
        logEventos.append("Temperatura externa fora dos padrões")
    if dados['tempInterna(°C)'] < 15 or dados['tempInterna(°C)'] > 30:
        logEventos.append("Temperatura interna fora dos padrões")
    if dados['nivelRadiacao(mSv)'] > 13:
        logEventos.append("Nível de radiação elevado")
    if dados['velVento(m/s)'] > 10:
        logEventos.append("Vento forte detectado")
    if dados['qldComunicacao'] == 'Instavel':
        logEventos.append("Sistema de comunicação instável")

    return logEventos

def gerarDados():
    global _data_atual
    _data_atual += timedelta(
        days=random.randint(0, 7),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    dados = {
        'dateTime': _data_atual.strftime('%Y-%m-%d %H:%M:%S'),
        'modComunicacao': random.choices([0, 1], weights=[0.2, 0.8], k=1)[0],
        'modHabitacao': random.choices([0, 1], weights=[0.2, 0.8], k=1)[0],
        'modLaboratorio': random.choices([0, 1], weights=[0.2, 0.8], k=1)[0],
        'modArmazenamento': random.choices([0, 1], weights=[0.2, 0.8], k=1)[0],
        'modEnergia': random.choices([0, 1], weights=[0.2, 0.8], k=1)[0],
        'modSupVida': random.choices([0, 1], weights=[0.2, 0.8], k=1)[0],
        'capEnergia(Kw/h)': round(random.uniform(100000, 215000), 2),
        'energiaRest(%)': random.randint(0, 100),
        'energiaGerada(Kw/h)': round(random.uniform(1000, 5200), 2),
        'tempExterna(°C)': round(random.uniform(-50, 50), 1),
        'tempInterna(°C)': round(random.uniform(15, 30), 1),
        'nivelRadiacao(mSv)': round(random.uniform(0, 20), 3),
        'qldComunicacao': random.choices(['Estavel', 'Instavel'], weights=[0.8, 0.2], k=1)[0],
        'velVento(m/s)': round(random.uniform(0, 20), 1),
    }

    dados['logEventos'] = (statusLog(dados))

    return dados


cabecalho = ['dateTime', 
             'modComunicacao', 
             'modHabitacao', 
             'modLaboratorio', 
             'modArmazenamento', 
             'modEnergia', 
             'modSupVida', 
             'capEnergia(Kw/h)', 
             'energiaRest(%)', 
             'energiaGerada(Kw/h)', 
             'tempExterna(°C)', 
             'tempInterna(°C)', 
             'nivelRadiacao(mSv)', 
             'qldComunicacao', 
             'velVento(m/s)', 
             'logEventos']

with open(ARQUIVO, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=cabecalho)
    writer.writeheader()
    for _ in range(50):
        writer.writerow(gerarDados())
