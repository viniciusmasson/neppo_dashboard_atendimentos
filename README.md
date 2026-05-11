# Neppo Dashboard — Atendimentos

Automação completa para extração e visualização de dados de atendimentos do Neppo (plataforma omnichannel).

## O que faz

- **coletor.py** — bot Selenium que faz login no Neppo, aplica filtros de data e baixa automaticamente os relatórios de histórico de sessões e status de mensagens diretas
- **dashboard.py** — dashboard Streamlit que lê os relatórios baixados e exibe atendimentos e envios por agente, agrupados por unidade comercial

## Stack

Python · Selenium · Streamlit · Pandas · Plotly · python-dotenv

## Como rodar localmente

1. Clone o repositório
2. Instale as dependências: pip install -r requirements.txt
3. Copie o .env.example para .env e preencha com suas credenciais
4. Para gerar dados de demonstração: python gerar_dados_mock.py
5. Para rodar o dashboard: streamlit run dashboard.py
6. Para rodar o coletor: python coletor.py

## Estrutura

- coletor.py — Automação Selenium
- dashboard.py — Dashboard Streamlit
- gerar_dados_mock.py — Gerador de dados fictícios para demo
- requirements.txt
- .env.example — Template de variáveis de ambiente
- data/ — Relatórios baixados (ignorado pelo git)

## Preview

![Dashboard](preview.png)