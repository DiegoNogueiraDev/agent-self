# Documentação Completa: Agente de Auto-Recuperação

## Tabela de Conteúdos
1.  [Visão Geral](#1-visão-geral)
2.  [Arquitetura do Projeto](#2-arquitetura-do-projeto)
3.  [Tecnologias Utilizadas](#3-tecnologias-utilizadas)
4.  [Metodologias e Lógica de Decisão](#4-metodologias-e-lógica-de-decisão)
5.  [Guia de Instalação](#5-guia-de-instalação)
6.  [Guia de Uso](#6-guia-de-uso)
7.  [Testes](#7-testes)
8.  [Como Contribuir](#8-como-contribuir)

---

## 1. Visão Geral

O **Agente de Auto-Recuperação (Self-Healing Agent)** é um sistema autônomo projetado para monitorar continuamente os recursos de uma máquina (CPU, memória), prever anomalias e executar ações corretivas para garantir a estabilidade do sistema. Ele opera em um ciclo contínuo de **Coleta -> Predição -> Remediação**.

O objetivo principal é mitigar proativamente problemas de performance, como processos com consumo excessivo de memória, antes que eles impactem a saúde geral do sistema.

## 2. Arquitetura do Projeto

O agente é construído em uma arquitetura modular para facilitar a manutenção e a extensibilidade. Os componentes principais estão localizados no diretório `src/` e são:

-   `src/collector/collector.py`: **Módulo Coletor**
    -   **Responsabilidade:** Coletar métricas vitais do sistema.
    -   **Funções:** Utiliza a biblioteca `psutil` para obter dados em tempo real sobre o uso de CPU, memória, disco e uma lista detalhada de processos em execução.

-   `src/predictor/predictor.py`: **Módulo Preditivo**
    -   **Responsabilidade:** Analisar as métricas coletadas e prever se o estado atual do sistema representa uma anomalia.
    -   **Funções:** Atualmente, implementa uma lógica baseada em limiares (`ThresholdPredictor`). Ele compara as métricas atuais (ex: `memory_percent`) com um limiar pré-configurado. Se o valor ultrapassar o limiar, ele sinaliza uma anomalia.

-   `src/remediator/remediator.py`: **Módulo de Remediação**
    -   **Responsabilidade:** Executar ações corretivas quando uma anomalia é detectada.
    -   **Funções:** Recebe o snapshot completo de dados quando o preditor sinaliza um problema. Ele então realiza uma análise de causa raiz (`_analyze_root_cause`) para identificar o processo mais ofensivo (atualmente baseado no maior consumo de memória) e executa uma ação, como finalizar o processo (`kill_process_by_pid`).

-   `src/main.py`: **Orquestrador Principal**
    -   **Responsabilidade:** Gerenciar o ciclo de vida do agente e orquestrar a interação entre os módulos.
    -   **Funções:** Executa um loop infinito que chama o Coletor, passa os dados para o Preditivo e, se necessário, aciona o Remediador.

-   `src/logger/logger.py`: **Módulo de Logging**
    -   **Responsabilidade:** Fornecer uma instância de logger configurada para registrar eventos importantes em formato JSON estruturado, facilitando a análise e o debug.

-   `config/config.yaml`: **Arquivo de Configuração**
    -   Centraliza parâmetros configuráveis, como limiares de predição e intervalos de monitoramento.

## 3. Tecnologias Utilizadas

-   **Linguagem:** Python 3
-   **Monitoramento de Sistema:** `psutil` - Uma biblioteca multiplataforma para obter informações sobre processos em execução e utilização do sistema (CPU, memória, discos, rede).
-   **Testes:**
    -   `pytest`: Framework para escrever e executar testes de unidade, integração e E2E.
    -   `unittest.mock`: Para criar mocks e patches durante os testes.
-   **Containerização:** `Dockerfile` - Para criar uma imagem de contêiner leve e segura, garantindo um ambiente de execução consistente.

## 4. Metodologias e Lógica de Decisão

O agente opera com base em uma lógica de decisão direta e pragmática:

1.  **Ciclo de Monitoramento:** A cada `X` segundos (definido no `config.yaml`), o `main.py` aciona o `collector.collect()`.
2.  **Análise de Limiar (Thresholding):** O `predictor.predict()` recebe as métricas do sistema. A lógica padrão é:
    ```
    se system_metrics['memory_percent'] > config['threshold']:
        retornar { "is_anomaly": True }
    ```
3.  **Análise de Causa Raiz (Root Cause Analysis):** Se `is_anomaly` for verdadeiro, o `remediator.perform_remediation()` é chamado. Sua lógica é:
    -   Ignorar processos que estão em uma "lista de exclusão" temporária (para evitar loops de remediação).
    -   Ordenar os processos restantes pelo maior consumo de `memory_percent`.
    -   Selecionar o processo no topo da lista como o "ofensor".
4.  **Ação Corretiva:** O Remediador executa a ação `kill_process_by_pid()` no PID do processo ofensor.
5.  **Mecanismo de Segurança (Cooldown):** Após uma ação, o PID do processo finalizado é adicionado a uma lista de exclusão com um timestamp. Ele não será alvo de uma nova ação por um período de tempo configurável (padrão: 300 segundos), prevenindo ações repetitivas no mesmo processo caso ele seja reiniciado rapidamente.

## 5. Guia de Instalação

### Pré-requisitos
-   Python 3.9+
-   `pip` (gerenciador de pacotes do Python)
-   Git

### Passos de Instalação
1.  Clone o repositório:
    ```bash
    git clone https://github.com/DiegoNogueiraDev/agent-self.git
    cd agent-self
    ```

2.  Crie e ative um ambiente virtual (recomendado):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

### Instalação com Docker
Para uma execução isolada e consistente, você pode usar o Docker.

1.  Construa a imagem a partir do `Dockerfile`:
    ```bash
    docker build -t self-healing-agent .
    ```

## 6. Guia de Uso

### Executando o Agente Diretamente
Com o ambiente configurado e as dependências instaladas, inicie o agente com:
```bash
python3 src/main.py
```
O agente começará a monitorar o sistema e registrará suas atividades no console e/ou em arquivos de log, conforme configurado.

### Executando o Agente com Docker
Para rodar o agente dentro de um contêiner Docker:
```bash
docker run --rm -it self-healing-agent
```
**Nota:** Para que o agente monitore o host e não apenas o contêiner, são necessárias flags adicionais, como `--pid=host`.

### Configuração
Edite o arquivo `config/config.yaml` para ajustar o comportamento do agente:
-   `monitoring_interval_seconds`: Intervalo entre os ciclos de coleta.
-   `predictor`: Configurações do preditor, como a métrica a ser observada e o limiar.
-   `remediator`: Configurações do remediador, como o período de exclusão.

## 7. Testes

O projeto utiliza `pytest` para testes.

### Executando todos os testes
Para rodar a suíte completa de testes (unidade, integração e E2E):
```bash
pytest
```
*Nota: A execução pode exigir privilégios adicionais dependendo do ambiente.*

### Testes Específicos
-   **Testes de Unidade/Integração:** `pytest tests/test_*.py`
-   **Testes End-to-End:** `pytest tests/e2e/`
-   **Teste de Performance:** `pytest tests/test_performance.py`

## 8. Como Contribuir
Contribuições são bem-vindas! Por favor, siga o fluxo de trabalho padrão:
1.  Crie uma fork do repositório.
2.  Crie uma branch para sua feature (`git checkout -b feature/nome-da-feature`).
3.  Faça commit de suas mudanças (`git commit -m 'feat: Adiciona nova feature'`).
4.  Faça push para a branch (`git push origin feature/nome-da-feature`).
5.  Abra um Pull Request. 