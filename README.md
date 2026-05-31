# Sistema de Controle de Missão em Tempo Real

## Equipe

*   **Integrantes:**
    * Rai da Silva Lima - RM572070

## Resumo do Problema e Cenário Analisado

Este projeto implementa um sistema de controle de missão em tempo real, projetado para monitorar e diagnosticar o estado operacional de uma estação espacial ou base remota. O cenário analisado envolve a coleta de dados de telemetria (como níveis de energia, temperaturas, radiação e status de módulos) para identificar situações críticas, gerar alertas automáticos e fornecer recomendações de ação. O objetivo principal é garantir a segurança e a eficiência das operações, prevenindo falhas e otimizando a tomada de decisões.

## Estruturas de Dados Utilizadas

O sistema faz uso estratégico de diversas estruturas de dados para otimizar o armazenamento, acesso e processamento das informações:

*   **`deque` (Fila de Duas Pontas) para `fila_alertas_sistema`:** Utilizada para gerenciar alertas dinâmicos gerados pelo sistema. A natureza FIFO (First-In, First-Out) da fila garante que os alertas sejam processados na ordem em que ocorrem ou são priorizados, sendo ideal para a exibição sequencial de notificações.

*   **Lista (simulando Pilha) para `pilha_eventos_criticos`:** Empregada para registrar os últimos eventos críticos detectados. A funcionalidade de pilha (LIFO - Last-In, First-Out) permite acessar rapidamente o evento crítico mais recente, o que é crucial para investigações pós-incidente.

*   **Lista de Listas (Matriz) para `matriz_historico`:** Armazena o histórico completo das leituras de telemetria por horário e variável. Esta estrutura é eficiente para representar dados tabulares, facilitando a recuperação de séries temporais e a análise de tendências.

*   **Dicionários para `dados`, `organizados`, `situacao` e `modulos`/`sensores`:** Amplamente utilizados para estruturar os dados de forma hierárquica e permitir acesso rápido por chaves nomeadas. Isso é fundamental para organizar informações complexas como o estado dos módulos, leituras de sensores e a hierarquia da missão (energia, habitat).

*   **Listas para Séries de Dados:** Dentro dos dicionários, listas são usadas para armazenar sequências de valores ao longo do tempo, como `energiaRest(%`, `energiaGerada(Kw/h)`, `tempInterna(°C)`, etc. Isso permite a análise de tendências e a aplicação de técnicas de previsão.

## Regras Lógicas Principais do Diagnóstico

O coração do sistema reside na função `classificarMissao`, que avalia o estado geral da missão com base em regras lógicas bem definidas. A expressão booleana principal para determinar um estado **crítico** é:

```python
is_critico = (falhas_criticas >= 1) or (sensores["energiaRestante"] < 20) or (sensores["radiacao"] > 13.0)
```

**Explicação:**

*   `falhas_criticas >= 1`: Se houver falha em pelo menos um dos módulos críticos (suporte de vida, energia, habitação), a missão é considerada crítica.
*   `sensores["energiaRestante"] < 20`: Se a energia restante cair abaixo de 20%, um nível perigosamente baixo, a missão entra em estado crítico.
*   `sensores["radiacao"] > 13.0`: Níveis de radiação acima de 13.0 mSv são considerados perigosos e elevam o status da missão para crítico.

Um estado de **alerta** é determinado pela seguinte lógica:

```python
is_alerta = (not is_critico) and (sum(modulos.values()) < len(modulos) or sensores["energiaRestante"] < 40)
```

**Explicação:**

*   `not is_critico`: O sistema só pode estar em alerta se não estiver em estado crítico.
*   `sum(modulos.values()) < len(modulos)`: Indica que nem todos os módulos estão operacionais (algum módulo está com falha, mas não é um dos críticos que causaria um estado crítico geral).
*   `sensores["energiaRestante"] < 40`: Se a energia restante estiver abaixo de 40% (mas não abaixo de 20%), é um sinal de atenção que justifica um alerta.

Caso nenhuma das condições acima seja verdadeira, o sistema é classificado como **NORMAL**.

## Técnica de Previsão Utilizada e Resultado

O sistema emprega uma técnica de **média móvel com ajuste de tendência** para prever o comportamento da `energiaRestante`. A função `realizarPrevisao` calcula a média dos últimos `janela` (padrão 3) pontos de dados e adiciona a tendência observada entre os dois últimos pontos para projetar o próximo valor.

**Exemplo de Resultado:**

Na interface de saída, a previsão é apresentada de forma clara, como: `Energia Restante: XX% (Previsto: YY%)`.

Esta previsão influencia diretamente a geração de alertas, como visto na linha 175 do código: `if previsao < s["energiaRestante"]:` que gera um alerta se a energia prevista for menor que a energia atual, indicando uma tendência de queda.

## Como Executar

Para executar o sistema, siga os passos abaixo:

1.  Certifique-se de ter o Python 3 instalado em seu ambiente.
2.  Navegue até o diretório raiz do projeto no terminal.
3.  Execute o script principal:

    ```bash
    python3 src/sistema.py
    ```

## Simulador de Dados

Para facilitar os testes e a demonstração do sistema, foi desenvolvido um simulador de dados que gera um arquivo `dados.csv` com informações de telemetria fictícias. Este simulador permite criar cenários variados, incluindo situações normais, de alerta e críticas, para validar o comportamento do sistema de controle de missão.

### Como o Simulador Funciona

O simulador (`data/simuladorDados.py`) realiza as seguintes ações:

1.  **Geração de Dados Aleatórios:** Utiliza a biblioteca `random` para gerar valores para cada variável de telemetria (energia restante, energia gerada, temperaturas, radiação, status de módulos, etc.).
2.  **Avanço Temporal:** Simula o avanço do tempo, gerando novos registros de dados em intervalos aleatórios, mas sequenciais.
3.  **Registro de Eventos:** A função `statusLog` analisa os dados gerados e cria uma lista de eventos (logEventos) com base em condições predefinidas (ex: falha de comunicação, nível de energia crítico, radiação elevada).
4.  **Exportação CSV:** Os dados gerados são formatados e escritos em um arquivo CSV (`dados.csv`), que serve como entrada para o sistema principal.

### Como Executar o Simulador

Para gerar um novo conjunto de dados para o sistema, execute o script do simulador:

```bash
python3 data/simuladorDados.py
```

Este comando criará ou sobrescreverá o arquivo `dados.csv` na pasta `data/`, que será então lido pelo sistema principal.

## Exemplo de Entrada e Saída do Sistema

**Entrada (Exemplo de `data/dados.csv`):**

```csv
dateTime,energiaRest(%),energiaGerada(Kw/h),tempInterna(°C),tempExterna(°C),nivelRadiacao(mSv),velVento(m/s),modComunicacao,modHabitacao,modLaboratorio,modArmazenamento,modEnergia,modSupVida,qldComunicacao,logEventos
2026-05-31 10:00:00,32,2500,22,5,10,8,1,1,1,1,1,1,Estavel,
2026-05-31 10:00:00,32,2500,22,5,10,8,1,1,1,1,1,1,Estavel,"[]"
2026-05-31 10:05:00,18,2000,25,7,15,10,0,1,1,1,1,1,Instavel,"[""Falha no Modulo de Comunicacao"", ""Radiacao Elevada"", ""Energia Critica"" ]"
```

**Saída (Exemplo de Execução no Terminal):**

```
============================================================
          MISSION CONTROL CENTER TELEMETRY
============================================================
HORÁRIO: 2026-05-31 10:05:00
STATUS GERAL: CRÍTICO
DIAGNÓSTICO:  Risco imediato à integridade da missão.
------------------------------------------------------------
[ ESTADO DOS MÓDULOS ]
 - Comunicacao    : ✗ FALHA DETECTADA
 - Habitacao      : ✓ OPERACIONAL
 - Laboratorio    : ✓ OPERACIONAL
 - Armazenamento  : ✓ OPERACIONAL
 - Energia        : ✓ OPERACIONAL
 - Suportevida    : ✓ OPERACIONAL

[ LEITURAS DOS SENSORES (FAIXAS DE SEGURANÇA) ]
 - Energia Restante: 18% (Previsto: 19.0%)
 - Geração Energia:  2000 Kw/h
 - Nível Radiação:   15 mSv
 - Temp. Interna:    25°C
 - Temp. Externa:    7°C
 - Velocidade Vento: 10 m/s
 - Qualidade Com.:   Instavel

[ RECOMENDAÇÕES AUTOMÁTICAS ]
 ➜ AÇÃO 1 (CRÍTICA): Manter suporte à vida e comunicação de emergência.
 ➜ AÇÃO 2 (ALTA): Desligar o laboratório e sistemas não essenciais.

[ ALERTAS GERADOS PELO SISTEMA (PRIORIZADOS) ]
 ! FALHA NO MÓDULO: COMUNICACAO está inoperante!
 ! RADIAÇÃO: Níveis perigosos detectados
 ! ENERGIA CRÍTICA: Reserva abaixo de 20%
 ! TENDÊNCIA: Energia deve cair para 19.0%

[ LOGS DA BASE DE DADOS (HISTÓRICO) ]
 • Falha no Modulo de Comunicacao
 • Radiacao Elevada
 • Energia Critica

[ ÚLTIMO EVENTO CRÍTICO (PILHA) ]
 ⚠ 2026-05-31 10:05:00 - FALHA NO MÓDULO: COMUNICACAO está inoperante!
============================================================
```

## Recomendações Geradas pelo Sistema

As recomendações são geradas dinamicamente com base no status geral da missão (CRÍTICO, ALERTA ou NORMAL). Por exemplo:

*   **Em estado CRÍTICO:**
    *   `AÇÃO 1 (CRÍTICA): Manter suporte à vida e comunicação de emergência.`
    *   `AÇÃO 2 (ALTA): Desligar o laboratório e sistemas não essenciais.`

*   **Em estado de ALERTA:**
    *   `AÇÃO 1: Redirecionar energia para habitat e carregamento de baterias.`
    *   `AÇÃO 2: Verificar integridade dos módulos em falha.`

## Link do Vídeo no YouTube

[Link para o vídeo de demonstração do projeto no YouTube]()

## Conclusões e Aprendizados

Este projeto demonstrou a aplicação prática de conceitos fundamentais de programação e estruturas de dados para resolver um problema complexo de monitoramento e controle. Os principais aprendizados incluem:

*   A importância da escolha correta das estruturas de dados para otimizar o desempenho e a clareza do código.
*   O desenvolvimento de lógica condicional robusta para diagnósticos precisos e tomadas de decisão automatizadas.
*   A implementação de sistemas de alerta e recomendação que melhoram a capacidade de resposta a eventos críticos.
*   A integração de técnicas de análise e previsão de dados, mesmo que simples, para adicionar inteligência preditiva ao sistema.
*   A criação de uma interface de usuário clara e informativa, utilizando recursos como cores ANSI para destacar informações importantes.

O sistema final é uma prova da capacidade de construir soluções eficazes e confiáveis para cenários de alta exigência, como o controle de missões espaciais, utilizando Python.
