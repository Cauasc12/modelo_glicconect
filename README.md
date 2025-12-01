# 🩸 GlicConnect - Simulador Glicêmico e Engenharia de Dados

> **Simulação Metabólica, Nutrição Inteligente e Geração de Dados Sintéticos para Diabetes Tipo 1.**

Este projeto é um sistema híbrido que une **Ciência de Dados** e **Modelagem Matemática Biológica**. Ele atua em duas frentes: uma interface visual para simulação de curvas glicêmicas e um pipeline de engenharia de dados para geração de datasets sintéticos voltados ao treinamento de IA.

---

## 🏗️ Arquitetura do Projeto

O sistema foi desenhado seguindo o princípio de **Separação de Responsabilidades (SoC)**, dividido em módulos independentes:

### 1. Camada de Dados e Lógica (`Backend`)
* **`nutricao.py`**: O "Bibliotecário".
    * Conecta-se à base de dados **TACO (Tabela Brasileira de Composição de Alimentos)**.
    * **Diferencial:** Possui um algoritmo de **Heurística Nutricional** que estima automaticamente a velocidade de absorção (Índice Glicêmico) baseando-se na quantidade de Fibras, Gorduras e palavras-chave (ex: "integral" vs "açúcar").
* **`metabolismo.py`**: O "Matemático".
    * Implementa fórmulas médicas de Farmacocinética.
    * Calcula o **IOB (Insulin On Board)** usando modelos de decaimento quadrático.
    * Realiza previsões pontuais baseadas nas regras de sensibilidade (Fator 1800 e Regra dos 500).

### 2. Camada de Aplicação (`Frontend`)
* **`app_simulador.py`**: A Interface Visual (Streamlit).
    * Integra o backend de nutrição com um motor de simulação temporal.
    * Utiliza a **Função Gamma** para desenhar curvas de subida e descida de glicose realistas ao longo de 5 horas.
    * Permite busca de alimentos, ajuste de doses e visualização de riscos (Hipo/Hiperglicemia).

### 3. Pipeline de Dados (`Data Engineering`)
* **`gerador_dataset.py`**: O "Fabricante".
    * Utiliza os módulos de backend para simular 5.000 cenários hipotéticos de pacientes.
    * Gera um dataset bruto (`dataset_glicemia_treino.csv`) contendo Peso, Glicemia Inicial, Carbos, Insulina e o Alvo (Target).
* **`analise_e_limpeza.py`**: O "Auditor".
    * Realiza a Análise Exploratória de Dados (EDA) com gráficos de correlação.
    * Limpa outliers biologicamente impossíveis.
    * Normaliza os dados (StandardScaler) preparando-os para algoritmos de Machine Learning.

### 4. Arquivos de Apoio
* **`alimentos.csv`**: A base de dados bruta (Tabela TACO processada).

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
Você precisa ter o Python instalado. Instale as dependências com o comando:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn streamlit
