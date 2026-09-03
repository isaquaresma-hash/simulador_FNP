import base64
import os
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

# -----------------------------------------------------------------------------
# 2. CARREGAMENTO E TRATAMENTO DE DADOS
# -----------------------------------------------------------------------------
def converter_valor_ptbr(valor):
    try:
        if valor is None:
            return 0.0
        if isinstance(valor, (int, float)):
            return float(valor)
        val_str = str(valor).strip()
        if val_str.lower() in ["nan", "none", "", "null", "-", "none"]:
            return 0.0
        val_str = val_str.replace("R$", "").replace(" ", "").strip()
        if "," in val_str:
            val_str = val_str.replace(".", "").replace(",", ".")
        else:
            if val_str.count(".") > 1 or (
                len(val_str.split(".")[-1]) != 2 and val_str.count(".") == 1
            ):
                val_str = val_str.replace(".", "")
        return float(val_str)
    except Exception:
        return 0.0


def formatar_inteiro_ptbr(valor):
    if pd.isna(valor) or str(valor).strip().lower() in ["nan", "none", "", "null", "-"]:
        return "-"
    try:
        val_clean = str(valor).replace("R$", "").replace(".", "").replace(",", ".").strip()
        val_num = int(float(val_clean))
        return f"{val_num:,}".replace(",", ".")
    except Exception:
        return str(valor)


def fmt_br(valor):
    if isinstance(valor, (int, float)):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(valor)


@st.cache_data
def carregar_dados():
    caminho_encontrado = None
    for f in os.listdir("."):
        if f.endswith(".xlsx") or f.endswith(".csv"):
            caminho_encontrado = f
            break

    if not caminho_encontrado:
        st.error("Erro: Nenhum arquivo Excel (.xlsx) ou CSV foi encontrado no repositório!")
        st.stop()

    try:
        if caminho_encontrado.endswith(".csv"):
            df = pd.read_csv(caminho_encontrado, header=2, dtype=str)
        else:
            df = pd.read_excel(caminho_encontrado, header=2, engine="openpyxl", dtype=str)
    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")
        st.stop()

    colunas_padrao = [
        "Situação",            # A
        "Porte",               # B
        "UF",                  # C
        "Município",           # D
        "Ranking",             # E
        "Valor_Integral",      # F
        "Valor_D10",           # G
        "Valor_D50",           # H
        "Valor_D25",           # I
        "Parcela_12x",         # J
        "Parcela_D50_x",       # K
        "Parcela_D25_x",       # L
        "População",           # M
        "RCL",                 # N
        "Receita per capita",  # O
        "Decil"                # P
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

    for col in ["Valor_Integral", "Valor_D10", "Valor_D25", "Valor_D50", "RCL", "Receita per capita"]:
        if col in df.columns:
            df[col] = [converter_valor_ptbr(v) for v in df[col]]
        else:
            df[col] = 0.0

    return df


df_base = carregar_dados()

# -----------------------------------------------------------------------------
# 3. LÓGICA DE ENQUADRAMENTO DA TABELA FNP (MANUAL 2027 V2.0)
# -----------------------------------------------------------------------------
def obter_grupo_rclpc(rcl_pc):
    """Mapeia a RCL per capita para o grupo correspondente (1 a 10) do manual."""
    if rcl_pc <= 4832.71:
        return 1
    elif rcl_pc <= 5354.64:
        return 2
    elif rcl_pc <= 5846.24:
        return 3
    elif rcl_pc <= 6295.10:
        return 4
    elif rcl_pc <= 6787.76:
        return 5
    elif rcl_pc <= 7421.25:
        return 6
    elif rcl_pc <= 8275.17:
        return 7
    elif rcl_pc <= 8454.71:
        return 8
    elif rcl_pc <= 11968.65:
        return 9
    else:
        return 10


def obter_valores_validados(row_or_df):
    val_integral = row_or_df["Valor_Integral"].sum()
    val_d10 = row_or_df["Valor_D10"].sum()
    val_d25 = row_or_df["Valor_D25"].sum()
    val_d50 = row_or_df["Valor_D50"].sum()

    if val_d10 <= 0 or val_d10 >= val_integral:
        val_d10 = val_integral * 0.90
    if val_d25 <= 0 or val_d25 >= val_integral:
        val_d25 = val_integral * 0.75
    if val_d50 <= 0 or val_d50 >= val_integral:
        val_d50 = val_integral * 0.50

    return val_integral, val_d10, val_d25, val_d50

# -----------------------------------------------------------------------------
# 4. INTERFACE E EXIBIÇÃO DA MEMÓRIA DE CÁLCULO
# -----------------------------------------------------------------------------
# [Abaixo você pode inserir esta seção no seu código onde exibe os detalhes do município]

def exibir_memoria_calculo_manual(municipio, uf, rcl, populacao, receita_per_capita, valor_integral):
    grupo_rclpc = obter_grupo_rclpc(receita_per_capita)
    
    st.markdown("### 📘 Memória de Cálculo das Contribuições 2027 (Manual v2.0)")
    
    st.markdown(f"""
    <div style="background-color: #F8FAFC; border-left: 5px solid #0A3663; padding: 1rem; border-radius: 6px; color: #1E293B;">
        <p><b>Município:</b> {municipio} / {uf}</p>
        <p><b>1. Apuração da Receita Corrente Líquida per capita (RCLpc):</b><br>
        Dividindo a RCL total de <b>R$ {fmt_br(rcl)}</b> pela população de <b>{formatar_inteiro_ptbr(populacao)} habitantes</b>, obtém-se a RCLpc de <b>R$ {fmt_br(receita_per_capita)}</b>.</p>
        
        <p><b>2. Enquadramento do Grupo de RCLpc (Coluna da Tabela):</b><br>
        Com o valor de R$ {fmt_br(receita_per_capita)}, o município enquadra-se no <b>Grupo {grupo_rclpc}</b> da tabela de contribuição.</p>
        
        <p><b>3. Enquadramento da Faixa de RCL (Linha da Tabela):</b><br>
        A RCL total de R$ {fmt_br(rcl)} define a linha do intervalo orçamentário correspondente na Tabela de Contribuições FNP 2027.</p>
        
        <p><b>4. Valor da Contribuição Apurado:</b><br>
        Ao cruzar a linha da Faixa de RCL com a coluna do <b>Grupo {grupo_rclpc}</b>, chega-se ao valor de contribuição anual integral de <b>R$ {fmt_br(valor_integral)}</b>.</p>
    </div>
    """, unsafe_allow_html=True)
