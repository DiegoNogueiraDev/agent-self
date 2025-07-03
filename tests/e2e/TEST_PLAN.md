# Plano de Testes - Agente de Auto-Recuperação

## 1. Introdução

Este documento descreve a estratégia e o plano de testes para o projeto do Agente de Auto-Recuperação (Self-Healing Agent). O objetivo é garantir a qualidade, funcionalidade, performance e robustez do sistema.

## 2. Escopo dos Testes

### Em Escopo:
-   **Testes de Unidade:** Validação de componentes individuais (Collector, Predictor, Remediator).
-   **Testes de Integração:** Validação da interação entre os módulos.
-   **Testes End-to-End (E2E):** Validação do fluxo completo, simulando um cenário real de detecção e remediação.
-   **Testes de Performance:** Medição do consumo de CPU e memória do agente sob condições normais.

### Fora de Escopo:
-   Testes de carga e estresse em larga escala.
-   Testes de usabilidade da interface (se aplicável).
-   Testes de segurança exaustivos (além das boas práticas implementadas).

## 3. Estratégia de Testes

### 3.1. Testes de Unidade
-   **Ferramenta:** `pytest`
-   **Objetivo:** Isolar e verificar a lógica de cada função/método nos módulos principais.
    -   `Collector`: Verificar a coleta correta de dados (CPU, memória).
    -   `Predictor`: Verificar a lógica de predição com dados de entrada controlados.
    -   `Remediator`: Verificar se as ações de remediação corretas são acionadas.

### 3.2. Testes de Integração
-   **Ferramenta:** `pytest`
-   **Objetivo:** Garantir que os módulos se comuniquem corretamente.
    -   Verificar se os dados coletados pelo `Collector` são passados corretamente para o `Predictor`.
    -   Verificar se o `Predictor` aciona o `Remediator` com os parâmetros esperados.

### 3.3. Testes End-to-End (E2E)
-   **Ferramenta:** `pytest` (usando `subprocess` para orquestração)
-   **Objetivo:** Simular um cenário completo e realista.
    -   **Cenário:** Iniciar um processo que consome recursos excessivos.
    -   **Fluxo Esperado:**
        1.  O `Collector` detecta o alto consumo.
        2.  O `Predictor` identifica a anomalia como um risco.
        3.  O `Remediator` é acionado e executa uma ação (ex: registrar um alerta ou finalizar o processo anômalo).
    -   **Validação:** Verificar se a ação de remediação foi executada com sucesso.

### 3.4. Testes de Performance
-   **Ferramenta:** `pytest` e `psutil`
-   **Objetivo:** Monitorar o próprio agente para garantir que ele não seja uma fonte de sobrecarga.
-   **Métricas:**
    -   Uso de CPU (%).
    -   Uso de Memória (MB).
-   **Critério de Aceite:** O consumo de recursos deve permanecer dentro de limites pré-definidos.

## 4. Ambiente de Testes
-   **Linguagem:** Python 3.9+
-   **Dependências:** `pytest`, `psutil`. As dependências do projeto estão em `requirements.txt`.
-   **Execução:** Os testes serão executados automaticamente via GitHub Actions em cada push/PR para as branches `develop` e `main`.

## 5. Critérios de Sucesso
-   Todos os testes de unidade, integração e E2E devem passar.
-   A cobertura de código (se medida) deve atingir um patamar mínimo (ex: 70%).
-   Os testes de performance não devem exceder os limiares definidos.

# End-to-End Test Plan

This document outlines the test scenarios for validating the end-to-end functionality of the Self-Healing Agent.

## Scenarios

### 1. Normal Operation
- **Description:** The agent runs, collects system metrics, but no anomalies are detected as no process exceeds the defined threshold.
- **Expected Outcome:**
    - The agent logs regular metric collection snapshots.
    - No remediation actions are triggered.
    - The application runs indefinitely without errors.

### 2. Anomaly Detection and Successful Remediation
- **Description:** A dummy process is started that intentionally consumes memory above the configured threshold. The agent should detect this anomaly and perform remediation.
- **Expected Outcome:**
    - The agent identifies the high-consumption process as an offender.
    - The agent triggers the `kill_process_by_pid` action.
    - A structured JSON log message is recorded for the remediation action, with `"success": true`.
    - The dummy process is terminated.

### 3. Remediation Failure (Process Not Found)
- **Description:** The agent identifies an offender, but the process terminates on its own before the agent can kill it.
- **Expected Outcome:**
    - The agent attempts to kill the process.
    - The `kill_process_by_pid` action fails because the PID no longer exists.
    - A structured JSON log message is recorded with `"success": false`.

### 4. Process Exclusion
- **Description:** A process that was recently actioned upon (and failed to be terminated, hypothetically) should be temporarily excluded from further remediation attempts to prevent action loops.
- **Expected Outcome:**
    - After a failed remediation attempt on a PID, the agent adds the PID to an exclusion list.
    - In the next cycle, even if the process is still identified as an offender, no remediation action is taken for that specific PID.
    - A log message indicates that the process is on the exclusion list. 