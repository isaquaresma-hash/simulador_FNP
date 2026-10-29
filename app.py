import base64
import os
import re
import tempfile
import pandas as pd
import streamlit as st
from fpdf import FPDF

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Simulador FNP 2027",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Constantes globais
MESES_ANO = [
    ("Janeiro", 12), ("Fevereiro", 11), ("Março", 10), ("Abril", 9),
    ("Maio", 8), ("Junho", 7), ("Julho", 6), ("Agosto", 5),
    ("Setembro", 4), ("Outubro", 3), ("Novembro", 2), ("Dezembro", 1)
]

# -----------------------------------------------------------------------------
# 2. CARREGAMENTO E LIMPEZA ROBUSTA DA PLANILHA EXCEL / CSV
# -----------------------------------------------------------------------------
def converter_valor_ptbr(valor):
    if valor is None or pd.isna(valor):
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)

    val_str = str(valor).strip()
    if val_str.lower() in ["nan", "none", "", "null", "-", "none"]:
        return 0.0

    try:
        val_clean = val_str.replace("R$", "").replace(" ", "").strip()
        if "," in val_clean:
            val_clean = val_clean.replace(".", "").replace(",", ".")
        else:
            partes = val_clean.split(".")
            if len(partes) > 1 and len(partes[-1]) == 3:
                val_clean = val_clean.replace(".", "")
        return float(val_clean)
    except Exception:
        return 0.0


def formatar_inteiro_ptbr(valor):
    if pd.isna(valor) or str(valor).strip().lower() in ["nan", "none", "", "null", "-"]:
        return "-"
    try:
        val_num = int(round(converter_valor_ptbr(valor)))
        return f"{val_num:,}".replace(",", ".")
    except Exception:
        return str(valor)


def formatar_ranking(valor):
    if pd.isna(valor) or str(valor).strip().lower() in ["nan", "none", "", "null", "-"]:
        return "-"
    val_str = str(valor).strip()
    if "%" in val_str:
        return val_str
    try:
        val_num = float(val_str.replace(",", "."))
        if 0 < val_num <= 1:
            return f"{int(round(val_num * 100))}%"
        elif val_num.is_integer():
            return f"{int(val_num)}%"
    except ValueError:
        pass
    return val_str


def fmt_br(valor):
    if isinstance(valor, (int, float)):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(valor)


def formatar_bilhoes_milhoes(valor):
    if not isinstance(valor, (int, float)) or valor <= 0:
        return "R$ 0,00"
    if valor >= 1_000_000_000:
        val_bi = valor / 1_000_000_000
        return f"R$ {val_bi:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".") + " bilhões"
    elif valor >= 1_000_000:
        val_mi = valor / 1_000_000
        return f"R$ {val_mi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " milhões"
    return f"R$ {fmt_br(valor)}"


@st.cache_data
def carregar_dados():
    caminho_encontrado = None
    arquivos = sorted(os.listdir("."))
    for f in arquivos:
        if f.endswith(".xlsx") or f.endswith(".csv"):
            caminho_encontrado = f
            break

    if not caminho_encontrado:
        st.error("Erro: Nenhum arquivo Excel (.xlsx) ou CSV foi encontrado na pasta do projeto!")
        st.stop()

    try:
        if caminho_encontrado.endswith(".csv"):
            df = pd.read_csv(caminho_encontrado, header=2, dtype=str)
        else:
            df = pd.read_excel(caminho_encontrado, header=2, engine="openpyxl", dtype=str)
    except Exception as e:
        st.error(f"Erro ao ler a planilha '{caminho_encontrado}': {e}")
        st.stop()

    colunas_padrao = [
        "Situação", "Porte", "UF", "Município", "Ranking",
        "Valor_Integral", "Valor_D10", "Valor_D50", "Valor_D25",
        "Parcela_12x", "Parcela_D50_x", "Parcela_D25_x",
        "População", "RCL", "Receita per capita", "Decil"
    ]

    novas_colunas = {}
    for i, col_orig in enumerate(df.columns):
        if i < len(colunas_padrao):
            novas_colunas[col_orig] = colunas_padrao[i]
        else:
            novas_colunas[col_orig] = f"Extra_{i}"

    df = df.rename(columns=novas_colunas)
    df = df.loc[:, ~df.columns.duplicated()]

    if "Município" in df.columns:
        df = df.dropna(subset=["Município"])
        df = df[df["Município"].astype(str).str.strip() != ""]

    if "Ranking" in df.columns:
        df["Ranking"] = [formatar_ranking(v) for v in df["Ranking"]]

    for col in ["Valor_Integral", "Valor_D10", "Valor_D25", "Valor_D50", "RCL", "Receita per capita"]:
        if col in df.columns:
            df[col] = [converter_valor_ptbr(v) for v in df[col]]
        else:
            df[col] = 0.0

    return df


df_base = carregar_dados()

# -----------------------------------------------------------------------------
# 3. ESTILOS CSS - CARREGAMENTO DA IMAGEM DE FUNDO COM CACHE
# -----------------------------------------------------------------------------
@st.cache_data
def obter_fundo_base64():
    arquivo_fundo = "simulador.png.jpg"
    if os.path.exists(arquivo_fundo):
        try:
            with open(arquivo_fundo, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception:
            return None
    return None


def set_bg_hack():
    bin_str = obter_fundo_base64()
    bg_css = f'background-image: url("data:image/jpeg;base64,{bin_str}");' if bin_str else 'background-color: #0A3663;'

    page_bg_img = f"""
        <style>
        .stApp {{
            {bg_css}
            background-size: cover;
            background-position: center top;
            background-repeat: no-repeat;
        }}
        .block
