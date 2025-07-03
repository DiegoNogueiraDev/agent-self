# PRD: Módulo de Predição com Inteligência Artificial

## 1. Objetivo

Substituir o atual `ThresholdPredictor`, que se baseia em um limiar estático, por um módulo preditivo inteligente que utiliza um modelo de Machine Learning para detectar anomalias em métricas de sistema. O novo módulo deve aprender com os dados históricos para identificar padrões anômalos que um limiar fixo não conseguiria detectar.

## 2. Requisitos Funcionais

### 2.1. Novo Preditivo (IsolationForestPredictor)
-   **RF-01:** Deve ser criada uma nova classe `IsolationForestPredictor` no arquivo `src/predictor/predictor.py`.
-   **RF-02:** A classe `IsolationForestPredictor` deve herdar da classe base `src.predictor.base.BasePredictor`.
-   **RF-03:** A classe deve implementar o método `load_model`, que será responsável por carregar um modelo `IsolationForest` treinado a partir de um arquivo (ex: `model.joblib`).
-   **RF-04:** A classe deve implementar o método `predict`, que receberá as métricas do sistema, irá pré-processá-las se necessário, e utilizará o modelo carregado para retornar uma predição.
-   **RF-05:** O retorno do método `predict` deve ser um dicionário compatível com o `Remediator`, contendo a chave `"is_anomaly": True/False`.

### 2.2. Script de Treinamento
-   **RF-06:** Deve ser criado um novo script `scripts/train_anomaly_model.py`.
-   **RF-07:** O script deve ser capaz de ler um conjunto de dados de métricas (a ser definido, pode ser um CSV), treinar um modelo `sklearn.ensemble.IsolationForest` com esses dados.
-   **RF-08:** Após o treinamento, o script deve salvar o modelo treinado em um arquivo usando `joblib`. O caminho do arquivo de saída deve ser configurável.

### 2.3. Configuração
-   **RF-09:** O arquivo `config/config.yaml` deve ser atualizado para permitir a seleção do novo preditor.
-   **RF-10:** A configuração do preditor deve incluir um novo campo `model_path` para especificar o caminho do arquivo do modelo treinado.
-   **RF-11:** A lógica em `src/predictor/__init__.py` ou `src/main.py` deve ser ajustada para instanciar o `IsolationForestPredictor` com base na nova configuração.

## 3. Requisitos Não-Funcionais

-   **RNF-01:** O novo módulo não deve introduzir uma sobrecarga de performance significativa no agente. O tempo de predição deve ser rápido.
-   **RNF-02:** A documentação do projeto (`DOCUMENTATION.md` e `README.md`) deve ser atualizada para refletir a nova capacidade de predição, explicando o novo modelo e como treiná-lo.

## 4. Coleta de Dados e Re-treinamento Periódico

-   **RF-12:** O agente deve coletar continuamente as métricas do sistema (ex: `cpu_percent`, `memory_percent`) e armazená-las de forma persistente (ex: em um arquivo CSV).
-   **RF-13:** O arquivo de dados deve ter um mecanismo de rotação ou limite de tamanho para evitar o consumo excessivo de disco.
-   **RF-14:** O script de treinamento (`scripts/train_anomaly_model.py`) deve ser adaptado para poder ser chamado periodicamente (manualmente ou por um agendador externo).
-   **RF-15:** O agente deve ser capaz de recarregar o modelo de predição sem a necessidade de ser reiniciado, permitindo a atualização "a quente" (hot-swap) do modelo.

## 5. Fora do Escopo

-   Re-treinamento totalmente automático e autônomo. O gatilho para o re-treinamento será externo por enquanto.
-   Implementação de múltiplos modelos de ML simultaneamente. Focaremos no `IsolationForest`. 