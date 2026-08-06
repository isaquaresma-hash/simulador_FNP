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
# 2. IMAGEM DE FUNDO E ESTILOS CSS DEFINITIVOS
# -----------------------------------------------------------------------------
CAMINHO_IMAGEM_FUNDO = "simulador.png.jpeg"

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def set_bg_hack(main_bg):
    bin_str = get_base64_of_bin_file(main_bg)
    if bin_str:
        page_bg_img = f"""
        <style>
        /* Fundo em Tela Cheia contendo a logo original */
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Alinhamento superior do container para respeitar a logo de fundo */
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }}

        /* Força a cor padrão do texto para azul escuro */
        .stApp, p, span, label, .stMarkdown {{
            color: #1E3A8A !important;
        }}

        /* Título Principal */
        .main-title {{
            color: #0F172A !important;
            font-size: 1.8rem !important;
            font-weight: 800 !important;
            margin-top: 2.5rem !important;
            margin-bottom: 1.2rem !important;
        }}

        /* Badges (Consulta e Filtros / Calculadora) */
        .badge-title {{
            background-color: #334155;
            color: #FFFFFF !important;
            padding: 6px 14px;
            border-radius: 6px;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 10px;
            font-size: 0.85rem;
        }}

        /* Cards das Métricas Superiores (Brancos) */
        div[data-testid="stMetric"] {{
            background-color: #FFFFFF !important;
            padding: 12px 20px !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.08) !important;
        }}

        div[data-testid="stMetricValue"] > div {{
            color: #0F172A !important;
            font-size: 2rem !important;
            font-weight: 800 !important;
        }}

        div[data-testid="stMetricLabel"] > div > p {{
            color: #64748B !important;
            font-weight: 700 !important;
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
        }}

        div[data-testid="stMetricDelta"] > div > span {{
            color: #16A34A !important;
            font-size: 0.75rem !important;
        }}

        /* Cards de Simulação */
        .sim-card {{
            background-color: #FFFFFF;
            padding: 1.2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.08);
            height: 100%;
        }}
        .sim-card .title-card {{
            font-size: 0.75rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
        }}
        .sim-card h4 {{
            color: #0F172A !important;
            font-size: 1.8rem !important;
            font-weight: bold !important;
            margin: 0.2rem 0 !important;
        }}
        .sim-card .sub-card {{
            color: #64748B !important;
            font-size: 0.75rem !important;
        }}

        /* Selectbox e Inputs */
        .stSelectbox div[data-baseweb="select"] > div {{
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border-radius: 8px !important;
        }}

        /* Cards de Resultado no Rodapé */
        .result-card-darkblue {{
            background-color: #003366;
            color: #FFFFFF !important;
            padding: 1.2rem;
            border-radius: 8px;
        }}
        .result-card-blue {{
            background-color: #2563EB;
            color: #FFFFFF !important;
            padding: 1.2rem;
            border-radius: 8px;
        }}
        .result-card-green {{
            background-color: #059669;
            color: #FFFFFF !important;
            padding: 1.2rem;
            border-radius: 8px;
        }}
        .res-title {{
            font-size: 0.75rem;
            font-weight: 800;
            color: #FFFFFF !important;
            margin-bottom: 0.2rem;
        }}
        .res-value {{
            font-size: 1.8rem;
            font-weight: 800;
            color: #FFFFFF !important;
            margin: 0.2rem 0;
        }}
        .res-sub {{
            font-size: 0.75rem;
            color: rgba(255,255,255,0.8) !important;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)

set_bg_hack(CAMINHO_IMAGEM_FUNDO)

# -----------------------------------------------------------------------------
# 3. BASE DE DADOS
# -----------------------------------------------------------------------------
data = {
    "Porte": ["150 a 350mil hab.", "Capital", "Grande", "Médio"],
    "UF": ["AL", "AM", "SP", "RJ"],
    "Município": ["Arapiraca", "Manaus", "São Paulo", "Rio de Janeiro"],
    "Classificação": ["Inadimplente", "Adimplente", "Adimplente", "Inadimplente"],
    "Filiado": [False, True, True, False],
    "Valor_Integral": [60728.00, 197700.00, 500000.00, 350000.00],
    "Ranking": [70, 95, 100, 60]
}
df_base = pd.DataFrame(data)

# -----------------------------------------------------------------------------
# 4. GERADOR DE PDF
# -----------------------------------------------------------------------------
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "FNP - Simulador de Contribuicao e Parcelamento", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")

def gerar_pdf_simulacao(municipio, uf, cenario, parcelas, valor_total, valor_parcela, economia):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)

    pdf.cell(0, 10, f"Relatorio de Simulacao - {municipio} ({uf})", 0, 1)
    pdf.ln(5)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Cenario Selecionado: {cenario}", 0, 1)
    pdf.cell(0, 8, f"Numero de Parcelas: {parcelas}x", 0, 1)
    pdf.cell(0, 8, f"Valor Total da Negociacao: R$ {valor_total:,.2f}", 0, 1)
    pdf.cell(0, 8, f"Valor de Cada Parcela: R$ {valor_parcela:,.2f}", 0, 1)
    pdf.cell(0, 8, f"Economia para o Municipio: R$ {economia:,.2f}", 0, 1)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        temp_filename = tmp_file.name

    pdf.output(temp_filename)

    with open(temp_filename, "rb") as f:
        pdf_bytes = f.read()

    if os.path.exists(temp_filename):
        os.remove(temp_filename)

    return pdf_bytes

# -----------------------------------------------------------------------------
# 5. ESTRUTURA DA INTERFACE (IDÊNTICA À REFERÊNCIA)
# -----------------------------------------------------------------------------

# Topo: Espaçamento para a logo da imagem de fundo + Botões na direita
header_col1, header_col2, header_col3 = st.columns([3, 1.5, 1.5])

with header_col1:
    st.write("") # Espaço em branco para deixar visível a logo que já vem na imagem de fundo

pdf_bytes = gerar_pdf_simulacao("Arapiraca", "AL", "Desconto 10%", 12, 54655.00, 4555.00, 6073.00)

with header_col2:
    st.download_button(
        label="📄 Baixar Simulação em PDF",
        data=pdf_bytes,
        file_name="simulacao_Arapiraca.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

with header_col3:
    if st.button("🔄 Atualização Base", use_container_width=True):
        st.success("Base atualizada!")

st.markdown('<div class="main-title">Simulador de Contribuição e Parcelamento</div>', unsafe_allow_html=True)

# Indicadores do Topo
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("CAPITAIS", "27", "↑ Quantidade de capitais no Brasil")
with col2:
    st.metric("MUNICÍPIOS ACIMA DE 80 MIL HABITANTES", "1.227", "↑ Municípios com mais de 80 mil habitantes")
with col3:
    st.metric("POTENCIAL DE ARRECADAÇÃO", "R$ 5,63 Bi", "↑ Potencial total de arrecadação anual")

st.markdown("<br>", unsafe_allow_html=True)

# Filtros
st.markdown('<div class="badge-title">🔍 Consulta e Filtros</div>', unsafe_allow_html=True)
f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1, 2.5, 1.2])

with f_col1:
    porte_sel = st.selectbox("Porte", df_base["Porte"].unique())
df_filtered = df_base[df_base["Porte"] == porte_sel]

with f_col2:
    uf_sel = st.selectbox("UF", df_filtered["UF"].unique())
df_filtered = df_filtered[df_filtered["UF"] == uf_sel]

with f_col3:
    mun_sel = st.selectbox("Município", df_filtered["Município"].unique())
df_final = df_filtered[df_filtered["Município"] == mun_sel].iloc[0]

with f_col4:
    st.markdown("**Ranking**")
    st.markdown(f"""
        <div style="background-color: white; color: #000000; font-weight: 800; text-align: center; padding: 6px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            {df_final['Ranking']}%
        </div>
    """, unsafe_allow_html=True)

# Painel de Simulação
status_text = "(Filiado)" if df_final["Filiado"] else "(Não Filiado)"
status_color = "🟢" if df_final["Filiado"] else "🔴"

st.markdown(f"#### **Painel de Simulação — {mun_sel}** {status_color} **{status_text}**")

val_integral = df_final["Valor_Integral"]
val_d10 = val_integral * 0.90
val_d25 = val_integral * 0.75
val_d50 = val_integral * 0.50

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div class="sim-card">
            <div class="title-card" style="color: #64748B;">VALOR INTEGRAL</div>
            <h4>R$ {val_integral:,.0f}</h4>
            <div class="sub-card">Sem Desconto</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="sim-card" style="border-left: 5px solid #003366;">
            <div class="title-card" style="color: #003366;">DESCONTO 10%</div>
            <h4>R$ {val_d10:,.0f}</h4>
            <div class="sub-card">Parcela Padrão: 12x</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="sim-card" style="border-left: 5px solid #6B21A8;">
            <div class="title-card" style="color: #6B21A8;">DESCONTO 25%</div>
            <h4>R$ {val_d25:,.0f}</h4>
            <div class="sub-card">Parcela Padrão: 10x</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="sim-card" style="border-left: 5px solid #059669;">
            <div class="title-card" style="color: #059669;">DESCONTO 50%</div>
            <h4>R$ {val_d50:,.0f}</h4>
            <div class="sub-card">Parcela Padrão: 10x</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Calculadora de Parcelamento
st.markdown('<div class="badge-title">⚙️ Calculadora de parcelamento</div>', unsafe_allow_html=True)

calc_col1, calc_col2 = st.columns(2)

with calc_col1:
    cenario = st.selectbox(
        "1. Escolha o cenário de valor base:", 
        ["Desconto 10%", "Desconto 25%", "Desconto 50%", "Valor Integral"]
    )

with calc_col2:
    num_parcelas = st.selectbox(
        "2. Escolha o número de parcelas desejado:",
        [12, 24, 36, 48],
        format_func=lambda x: f"{x}x ({x} parcelas)",
    )

# Cálculos da Calculadora
if cenario == "Desconto 10%":
    valor_negociado = val_d10
elif cenario == "Desconto 25%":
    valor_negociado = val_d25
elif cenario == "Desconto 50%":
    valor_negociado = val_d50
else:
    valor_negociado = val_integral

economia = val_integral - valor_negociado
valor_parcela = valor_negociado / num_parcelas

# Cards do Rodapé
res1, res2, res3 = st.columns(3)

with res1:
    st.markdown(f"""
        <div class="result-card-darkblue">
            <div class="res-title">VALOR DE CADA PARCELA</div>
            <div class="res-value">R$ {valor_parcela:,.0f}</div>
            <div class="res-sub">Plano em {num_parcelas} parcelas mensais</div>
        </div>
    """, unsafe_allow_html=True)

with res2:
    st.markdown(f"""
        <div class="result-card-blue">
            <div class="res-title">VALOR TOTAL DA NEGOCIAÇÃO</div>
            <div class="res-value">R$ {valor_negociado:,.0f}</div>
            <div class="res-sub">Cenário: {cenario}</div>
        </div>
    """, unsafe_allow_html=True)

with res3:
    st.markdown(f"""
        <div class="result-card-green">
            <div class="res-title">ECONOMIA PARA O MUNICÍPIO</div>
            <div class="res-value">R$ {economia:,.0f}</div>
            <div class="res-sub">Em relação ao valor integral de R$ {val_integral:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)
