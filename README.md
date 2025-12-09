# Projeto de Simulação de Big Data Financeiro (Banco Fake)

## 🎯 Objetivo do Projeto

Este repositório visa simular um ambiente de dados de alta volumetria (Big Data) para fins de estudo e prática de Engenharia e Análise de Dados. Os dados são fictícios e gerados sinteticamente.

## 📁 Estrutura do Repositório

O projeto segue um padrão de organização claro, separando código, dados e análises:
* `scripts/`: Contém todo o código-fonte Python e SQL necessário para gerar, carregar e otimizar o banco de dados.
* `data/`: Armazena o output do pipeline: arquivos CSV, o banco de dados SQLite (`banco_fake.db`) e backups pontuais.
* `analysis/`: Destinado a scripts de análise, consultas SQL complexas e relatórios.

## ⚙️ Pipeline de Execução

O banco de dados é gerado em etapas sequenciais, garantindo a integridade referencial:

1.  `01_gerar_clientes.py`
2.  `02_gerar_contas.py`
3.  `03_gerar_credito.py`
4.  **`04_gerar_transacoes.py` (Geração de 10.000.000 de registros)**
5.  *Carga para o SQLite*
6.  `05_otimizar_db.sql` (Criação de índices para performance)

## 🚀 Como Iniciar

1.  **Ambiente:** Crie e ative um ambiente virtual (`db_venv`).
2.  **Dependências:** Instale as bibliotecas necessárias (ex: `Faker`, `Pandas`).
3.  **Execução:** Execute os scripts na ordem numérica, começando por `scripts/01_gerar_clientes.py`.
