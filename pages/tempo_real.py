import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from datetime import datetime
import os
import glob

load_dotenv()

RELATORIOS_PATH = os.getenv("RELATORIOS_PATH")

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

st.set_page_config(page_title="Atendimentos — Tempo Real", layout="wide")
st.title("Atendimentos Neppo — Tempo Real")

def encontrar_mais_recente(pasta, prefixo):
    arquivos = glob.glob(os.path.join(pasta, f"{prefixo}*.xlsx")) + \
               glob.glob(os.path.join(pasta, f"{prefixo}*.csv"))
    return max(arquivos, key=os.path.getmtime) if arquivos else None

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

if not RELATORIOS_PATH or not os.path.exists(RELATORIOS_PATH):
    st.error("Caminho de relatórios não configurado ou não encontrado.")
    st.stop()

arquivo_at = encontrar_mais_recente(RELATORIOS_PATH, "atendimentos")
arquivo_ev = encontrar_mais_recente(RELATORIOS_PATH, "envios")

if not arquivo_at and not arquivo_ev:
    st.warning("Sem arquivos na pasta configurada.")
    st.stop()

if arquivo_at:
    hora = datetime.fromtimestamp(os.path.getmtime(arquivo_at)).strftime("%d/%m/%Y %H:%M")
    st.caption(f"Atendimentos: {os.path.basename(arquivo_at)} ({hora})")

if arquivo_ev:
    hora = datetime.fromtimestamp(os.path.getmtime(arquivo_ev)).strftime("%d/%m/%Y %H:%M")
    st.caption(f"Envios: {os.path.basename(arquivo_ev)} ({hora})")

tipo = st.sidebar.radio("Gráfico:", ["Empilhado", "Agrupado", "Somado"])

at = processar_atendimentos(arquivo_at) if arquivo_at else pd.Series(dtype=int)
ev = processar_envios(arquivo_ev) if arquivo_ev else pd.Series(dtype=int)

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