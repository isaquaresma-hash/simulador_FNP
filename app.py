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
    page_title="Simulador FNP",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# 2. CARREGAMENTO E LIMPEZA ROBUSTA DA PLANILHA EXCEL
# -----------------------------------------------------------------------------
NOME_ARQUIVO_PLANILHA = "Simulador de contribuição .xlsx"


def converter_valor_ptbr(valor):
    """Converte com segurança valores em formato monetário BR ou números para float puro."""
    try:
        if valor is None:
            return 0.0

        if isinstance(valor, (int, float)):
            return float(valor)

        val_str = str(valor).strip()
        if val_str.lower() in ["nan", "none", "", "null", "-", "none"]:
            return 0.0

        # Remove símbolos de moeda e espaços
        val_str = val_str.replace("R$", "").replace(" ", "").strip()

        # Tratamento de pontuação brasileira
        if "," in val_str:
            val_str = val_str.replace(".", "").replace(",", ".")
        return float(val_str)
    except Exception:
        return 0.0


def formatar_ranking(v):
    """Formata com segurança a coluna de ranking."""
    try:
        if pd.isna(v) or v is None:
            return ""
        v_float = float(v)
        return str(int(v_float)) if v_float.is_integer() else str(v_float)
    except Exception:
        return str(v).strip()


@st.cache_data
def carregar_dados():
    if not os.path.exists(NOME_ARQUIVO_PLANILHA):
        st.error(f"Arquivo '{NOME_ARQUIVO_PLANILHA}' não encontrado.")
        return pd.DataFrame()

    df = pd.read_excel(NOME_ARQUIVO_PLANILHA)

    if "Ranking" in df.columns:
        df["Ranking"] = [formatar_ranking(v) for v in df["Ranking"]]

    # Converte as colunas numéricas com tratamento de segurança
    for col in ["Valor_Integral", "Valor_D10", "Valor_D25", "Valor_D50"]:
        if col in df.columns:
            df[col] = [converter_valor_ptbr(v) for v in df[col]]

    return df


df_base = carregar_dados()

# -----------------------------------------------------------------------------
# 3. ESTILOS CSS E IMAGEM DE FUNDO (ADAPTADO PARA COMPUTADOR E CELULAR)
# -----------------------------------------------------------------------------
CAMINHO_IMAGEM_FUNDO = "simulador.png.jpeg"


def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""


bin_str = get_base64_of_bin_file(CAMINHO_IMAGEM_FUNDO)

if bin_str:
    page_bg_img = f"""
        <style>
        /* Estilo para Computador */
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .block-container {{ padding-top: 200px !important; padding-bottom: 2rem !important; }}
        #MainMenu, footer, header {{ visibility: hidden; }}

        /* REGRA EXCLUSIVA PARA CELULARES (Muda apenas em telas menores que 768px) */
        @media (max-width: 768px) {{
            .stApp {{
                background-size: 100% auto !important; /* Ajusta a imagem na largura para não cortar o topo/logo */
                background-position: top center !important;
            }}
            .block-container {{
                padding-top: 130px !important; /* Ajusta o espaçamento superior no celular */
            }}
        }}

        .page-title {{
            color: #0A3663;
            font-size: 1.6rem;
        }}
        </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)


def fmt_br(valor):
    """Formata valores numéricos para o padrão de moeda brasileiro."""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def obter_valores_validados(row_or_df):
    """Garante que os valores de descontos existam e sejam válidos."""
    val_integral = row_or_df["Valor_Integral"].sum() if isinstance(row_or_df, pd.DataFrame) else row_or_df["Valor_Integral"]
    val_d10 = row_or_df["Valor_D10"].sum() if isinstance(row_or_df, pd.DataFrame) else row_or_df["Valor_D10"]
    val_d25 = row_or_df["Valor_D25"].sum() if isinstance(row_or_df, pd.DataFrame) else row_or_df["Valor_D25"]
    val_d50 = row_or_df["Valor_D50"].sum() if isinstance(row_or_df, pd.DataFrame) else row_or_df["Valor_D50"]

    # Se a planilha estiver sem o valor de desconto, calcula automaticamente
    if val_d10 <= 0 or val_d10 >= val_integral:
        val_d10 = val_integral * 0.90
    if val_d25 <= 0 or val_d25 >= val_integral:
        val_d25 = val_integral * 0.75
    if val_d50 <= 0 or val_d50 >= val_integral:
        val_d50 = val_integral * 0.50

    return val_integral, val_d10, val_d25, val_d50


# -----------------------------------------------------------------------------
# 4. EXECUÇÃO DO APLICATIVO
# -----------------------------------------------------------------------------
if not df_base.empty:
    municipios = sorted(df_base["Município"].dropna().unique())
    municipio_sel = st.selectbox("Selecione o Município:", municipios)

    df_filtrado = df_base[df_base["Município"] == municipio_sel]

    eh_filiado = (
        str(df_filtrado["Situação"].values[0]).strip().lower() == "filiado"
        if "Situação" in df_filtrado.columns and not df_filtrado.empty
        else False
    )

    # Aplica validação estrita
    val_integral_t, val_d10_t, val_d25_t, val_d50_t = obter_valores_validados(df_filtrado)

    # Obtenção validada dos valores sem risco de distorção
    val_integral, val_d10, val_d25, val_d50 = obter_valores_validados(df_filtrado)

    if eh_filiado:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""
                    <div class="sim-card" style="border-left: 4px solid #1E3A8A;">
                        <div class="sim-title" style="color: #4A5568;">VALOR INTEGRAL</div>
                        <div class="sim-value">R$ {fmt_br(val_integral)}</div>
                        <div class="sim-sub">Sem Desconto</div>
                    </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                    <div class="sim-card" style="border-left: 4px solid #2563EB;">
                        <div class="sim-title" style="color: #2563EB;">DESCONTO 10%</div>
                        <div class="sim-value">R$ {fmt_br(val_d10)}</div>
                        <div class="sim-sub">Pacote: Até 12x</div>
                    </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f"""
                    <div class="sim-card" style="border-left: 4px solid #1E3A8A;">
                        <div class="sim-title" style="color: #4A5568;">VALOR INTEGRAL</div>
                        <div class="sim-value">R$ {fmt_br(val_integral)}</div>
                        <div class="sim-sub">Sem Desconto</div>
                    </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                    <div class="sim-card" style="border-left: 4px solid #2563EB;">
                        <div class="sim-title" style="color: #2563EB;">DESCONTO 10%</div>
                        <div class="sim-value">R$ {fmt_br(val_d10)}</div>
                        <div class="sim-sub">Pacote: Até 12x</div>
                    </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""
                    <div class="sim-card" style="border-left: 4px solid #7C3AED;">
                        <div class="sim-title" style="color: #7C3AED;">DESCONTO 25%</div>
                        <div class="sim-value">R$ {fmt_br(val_d25)}</div>
                        <div class="sim-sub">Pacote: Até 10x</div>
                    </div>
                """,
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                f"""
                    <div class="sim-card" style="border-left: 4px solid #10B981;">
                        <div class="sim-title" style="color: #10B981;">DESCONTO 50%</div>
                        <div class="sim-value">R$ {fmt_br(val_d50)}</div>
                        <div class="sim-sub">Pacote: Até 10x</div>
                    </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="badge-main">⚙️ Calculadora de parcelamento</div>',
        unsafe_allow_html=True,
    )

    calc_col1, calc_col2 = st.columns(2)

    with calc_col1:
        st.markdown(
            '<div class="badge-filter">1. Escolha o cenário de valor base:</div>',
            unsafe_allow_html=True,
        )
        opcoes_cenario = (
            ["Desconto 10%", "Valor Integral"]
            if eh_filiado
            else ["Desconto 10%", "Desconto 25%", "Desconto 50%", "Valor Integral"]
        )
        cenario = st.selectbox(
            "", opcoes_cenario, key="cenario_calc", label_visibility="collapsed"
        )

    opcoes_parcelas = (
        list(range(1, 11))
        if cenario in ["Desconto 25%", "Desconto 50%"]
        else list(range(1, 13))
    )

    with calc_col2:
        st.markdown(
            '<div class="badge-filter">2. Escolha o número de parcelas desejado:</div>',
            unsafe_allow_html=True,
        )
        num_parcelas = st.selectbox(
            "",
            opcoes_parcelas,
            index=len(opcoes_parcelas) - 1,
            format_func=lambda x: f"{x}x",
            key="num_parcelas_calc",
            label_visibility="collapsed",
        )

    if cenario == "Desconto 10%":
        valor_negociado = val_d10
    elif cenario == "Desconto 25%":
        valor_negociado = val_d25
    elif cenario == "Desconto 50%":
        valor_negociado = val_d50
    else:
        valor_negociado = val_integral

    economia = val_integral - valor_negociado
    valor_parcela = valor_negociado / num_parcelas if num_parcelas > 0 else 0.0

    res1, res2, res3 = st.columns(3)
    with res1:
        st.markdown(
            f"""
                <div class="res-card-dark">
                    <div class="res-title">VALOR DE CADA PARCELA</div>
                    <div class="res-val">R$ {fmt_br(valor_parcela)}</div>
                    <div class="res-sub">Plano em {num_parcelas} parcelas mensais</div>
                </div>
            """,
            unsafe_allow_html=True,
        )

    with res2:
        st.markdown(
            f"""
                <div class="res-card-blue">
                    <div class="res-title">VALOR TOTAL DA NEGOCIAÇÃO</div>
                    <div class="res-val">R$ {fmt_br(valor_negociado)}</div>
                    <div class="res-sub">Cenário: {cenario}</div>
                </div>
            """,
            unsafe_allow_html=True,
        )

    with res3:
        st.markdown(
            f"""
                <div class="res-card-green">
                    <div class="res-title">ECONOMIA PARA O MUNICÍPIO</div>
                    <div class="res-val">R$ {fmt_br(economia)}</div>
                    <div class="res-sub">Em relação ao valor integral de R$ {fmt_br(val_integral)}</div>
                </div>
            """,
            unsafe_allow_html=True,
        )
