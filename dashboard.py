from faker import Faker
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os
import glob
import re

load_dotenv()

RELATORIOS_PATH = os.getenv("RELATORIOS_PATH")

fake = Faker("pt_BR")
Faker.seed(42)

mapeamento_agentes_unidades = {
    "Ana Souza":            "Comercial Unidade Grandes Clínicas",
    "Bruno Lima":           "Comercial Unidade Grandes Clínicas",
    "Carla Mendes":         "Comercial Unidade Grandes Clínicas",
    "Diego Ferreira":       "Comercial Unidade Grandes Clínicas",
    "Eliane Costa":         "Comercial Unidade Franquias",
    "Felipe Nunes":         "Comercial Unidade Franquias",
    "Gisele Rocha":         "Comercial Unidade Franquias",
    "Henrique Alves":       "Comercial Unidade Franquias",
    "Isabela Martins":      "Comercial Unidade MRC",
    "João Pedro Silva":     "Comercial Unidade MRC",
    "Karina Oliveira":      "Comercial Unidade MRC",
    "Leonardo Santos":      "Comercial Unidade MRC",
    "Mariana Pereira":      "Comercial Unidade VDA",
    "Nelson Ribeiro":       "Comercial Unidade VDA",
    "Olivia Teixeira":      "Comercial Unidade VDA",
    "Paulo Gomes":          "Comercial Unidade VDA",
    "Renata Barros":        "Comercial Unidade Cursos e Distribuição",
    "Sergio Campos":        "Comercial Unidade Cursos e Distribuição",
}

st.set_page_config(page_title="Atendimentos Neppo", layout="wide")
st.title("Atendimentos Neppo")

def extrair_data_do_nome_arquivo(nome_arquivo):
    nome_base = os.path.splitext(nome_arquivo)[0]
    padrao = re.search(r'(\d{2})(\d{2})(\d{4})', nome_base)
    if padrao:
        dia, mes, ano = padrao.groups()
        return f"{dia}/{mes}/{ano}"
    return None

def listar_arquivos_por_data(pasta):
    if not os.path.exists(pasta):
        return {}
    arquivos = glob.glob(os.path.join(pasta, "*.xlsx")) + glob.glob(os.path.join(pasta, "*.csv"))
    arquivos_por_data = {}
    for arquivo in arquivos:
        nome = os.path.basename(arquivo)
        data = extrair_data_do_nome_arquivo(nome)
        if data:
            if data not in arquivos_por_data:
                arquivos_por_data[data] = {}
            if "atendimentos" in nome.lower():
                arquivos_por_data[data]["atendimentos"] = arquivo
            elif "envios" in nome.lower():
                arquivos_por_data[data]["envios"] = arquivo
    return arquivos_por_data

def ler_arquivo(caminho):
    try:
        return pd.read_excel(caminho)
    except:
        return pd.read_csv(caminho)

def processar_atendimentos(caminho):
    try:
        df = ler_arquivo(caminho)
        df = df[df["Agente"].isin(mapeamento_agentes_unidades.keys())]
        return df.groupby("Agente").size()
    except:
        return pd.Series(dtype=int)

def processar_envios(caminho):
    try:
        df = ler_arquivo(caminho)
        cont = pd.Series(dtype=int)
        for agente in mapeamento_agentes_unidades.keys():
            total = 0
            for col in df.columns:
                if df[col].dtype == "object":
                    total += df[col].astype(str).str.contains(agente, na=False, case=False).sum()
            if total > 0:
                cont[agente] = total
        return cont
    except:
        return pd.Series(dtype=int)

if RELATORIOS_PATH and os.path.exists(RELATORIOS_PATH):
    arquivos_por_data = listar_arquivos_por_data(RELATORIOS_PATH)

    if arquivos_por_data:
        data_sel = st.sidebar.selectbox("Data:", sorted(arquivos_por_data.keys()))
        tipo = st.sidebar.radio("Gráfico:", ["Empilhado", "Agrupado", "Somado"])

        arquivos = arquivos_por_data[data_sel]

        at = processar_atendimentos(arquivos.get("atendimentos", "")) if "atendimentos" in arquivos else pd.Series(dtype=int)
        ev = processar_envios(arquivos.get("envios", "")) if "envios" in arquivos else pd.Series(dtype=int)

        df_at = pd.DataFrame({"Agente": at.index, "Quantidade": at.values, "Tipo": "Atendimentos"})
        df_ev = pd.DataFrame({"Agente": ev.index, "Quantidade": ev.values, "Tipo": "Envios"})
        df = pd.concat([df_at, df_ev], ignore_index=True)

        base = pd.DataFrame({"Agente": list(mapeamento_agentes_unidades.keys())})
        tipos = pd.DataFrame({"Tipo": ["Atendimentos", "Envios"]})
        base = base.merge(tipos, how="cross")

        df = base.merge(df, on=["Agente", "Tipo"], how="left")
        df["Quantidade"] = df["Quantidade"].fillna(0)
        df["Grupo"] = df["Agente"].map(mapeamento_agentes_unidades)

        for grupo in sorted(df["Grupo"].unique()):
            df_g = df[df["Grupo"] == grupo].copy()
            ordem = (
                df_g.groupby("Agente")["Quantidade"]
                .sum()
                .sort_values(ascending=False)
                .index
            )
            df_g["Agente"] = pd.Categorical(df_g["Agente"], categories=ordem, ordered=True)
            df_g = df_g.sort_values("Agente")

            st.subheader(grupo)

            if tipo == "Somado":
                df_plot = (
                    df_g.groupby("Agente")["Quantidade"]
                    .sum()
                    .reset_index()
                    .sort_values("Quantidade", ascending=False)
                )
                fig = px.bar(df_plot, y="Agente", x="Quantidade", orientation="h", text="Quantidade")
            else:
                fig = px.bar(
                    df_g,
                    y="Agente",
                    x="Quantidade",
                    color="Tipo",
                    barmode="stack" if tipo == "Empilhado" else "group",
                    orientation="h",
                    text="Quantidade"
                )

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sem arquivos na pasta configurada.")
else:
    st.error("Caminho de relatórios não configurado ou não encontrado.")