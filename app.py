import base64
import os
import tempfile
import pandas as pd
import streamlit as st
from fpdf import FPDF

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA (WIDE MODE E FAVICON)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Simulador FNP",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# 2. IMAGEM DE FUNDO E CSS PERSONALIZADO (Exatamente como a referência)
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
        # Define a cor do texto padrão como branco para o fundo
        text_color = "white"
        
        page_bg_img = f"""
        <style>
        /* Imagem de Fundo em tela cheia */
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: {text_color};
        }}

        /* Centralizar o container principal e remover paddings padrão excessivos */
        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }}

        /* Estilização para o LOGO no topo esquerdo */
        [data-testid="stHeader"] {{
            background-color: rgba(0,0,0,0) !important;
        }}
        
        /* Estilização geral de Títulos e Textos */
        h1, h2, h3, h4, h5, h6, .stMarkdown, p, li, .stCaption {{
            color: {text_color} !important;
        }}

        /* Estilização específica para os Cards de Métricas (Superiores) */
        div[data-testid="stMetricValue"] > div {{
            color: #31333F !important; /* Cor escura para o valor dentro do card branco */
            font-size: 2.5rem !important;
        }}
        div[data-testid="stMetricLabel"] > div > p {{
            color: #6D6D6D !important; /* Cor cinza para a label dentro do card branco */
            font-size: 0.8rem !important;
            font-weight: bold;
        }}
        div[data-testid="stMetricValue"] ~ div[data-testid="stMetricDelta"] > div > span {{
            color: #797979 !important; /* Cor do delta */
            font-size: 0.7rem !important;
        }}
        
        /* Adicionar padding e bordas nos cards de métricas st.metric */
        div[data-testid="stMetric"] {{
            background-color: rgba(255, 255, 255, 1);
            padding: 15px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: #31333F !important;
            margin-bottom: 10px;
        }}

        /* Estilização específica para as linhas de Simulação (Cards Brancos Maiores) */
        .sim-card {{
            background-color: rgba(255, 255, 255, 1);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: #31333F;
            margin-bottom: 1rem;
        }}
        .sim-card h4 {{ color: #31333F !important; margin-bottom: 0.5rem; }}
        .sim-card p {{ color: #31333F !important; margin: 0; }}
        .sim-card .caption {{ color: #797979 !important; font-size: 0.8rem; margin-top: 0.3rem; }}

        /* Estilização para as labels dos inputs (Selectbox e outros) */
        .stSelectbox label p {{
            color: {text_color} !important;
            font-weight: bold;
        }}

        /* Estilização para os inputs brancos */
        .stSelectbox div[data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 1) !important;
            color: #31333F !important;
            border-radius: 8px;
        }}
        
        /* Cor de fundo para as mensagens de info/success/error */
        .stAlert {{
            background-color: rgba(255, 255, 255, 0.8) !important;
            color: #31333F !important;
        }}
        
        /* Estilização dos Botões Superiores Brancos */
        .stButton button {{
            background-color: #FFFFFF !important;
            color: #31333F !important;
            border: 1px solid #C4C4C4 !important;
            border-radius: 8px !important;
            font-weight: bold !important;
            padding: 0.5rem 1rem !important;
        }}
        
        /* Estilização dos Cards de Resultado (Azul e Verde no final) */
        .result-card-blue {{
            background-color: #1A4D96 !important; /* Azul escuro FNP */
            color: #FFFFFF !important;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }}
        .result-card-blue h4, .result-card-blue p, .result-card-blue span {{
            color: #FFFFFF !important;
        }}
        
        .result-card-green {{
            background-color: #1E8449 !important; /* Verde FNP */
            color: #FFFFFF !important;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }}
        .result-card-green h4, .result-card-green p, .result-card-green span {{
            color: #FFFFFF !important;
        }}

        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)

set_bg_hack(CAMINHO_IMAGEM_FUNDO)

# -----------------------------------------------------------------------------
# 3. BASE DE DADOS (Exemplo conforme a referência)
# -----------------------------------------------------------------------------
data = {
    "Porte": ["150 a 350mil hab.", "Capital", "Grande", "Médio"],
    "UF": ["AL", "AM", "SP", "RJ"],
    "Município": ["Arapiraca", "Manaus", "São Paulo", "Rio de Janeiro"],
    "Classificação": ["Inadimplente", "Adimplente", "Adimplente", "Inadimplente"],
    "Filiado": [False, True, True, False],
    "Valor_Integral": [60728.00, 197700.00, 500000.00, 350000.00],
    "Ranking": [70, 95, 100, 60] # Valor do ranking em %
}
df_base = pd.DataFrame(data)

# -----------------------------------------------------------------------------
# 4. FUNÇÕES DE PDF E CÁLCULO
# -----------------------------------------------------------------------------
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "FNP - Simulador de Contribuição e Parcelamento", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

def gerar_pdf_simulacao(municipio, uf, filiado, v_integral, v_desc10, v_desc25, v_desc50):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)

    status_f = "Filiado" if filiado else "Não Filiado"
    pdf.cell(0, 10, f"Relatório de Simulação - {municipio} ({uf}) - {status_f}", 0, 1)
    pdf.ln(5)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Valor Integral: R$ {v_integral:,.2f}", 0, 1)
    pdf.cell(0, 8, f"Cenário Desconto 10%: R$ {v_desc10:,.2f} (Parcela Padrão: 12x)", 0, 1)
    pdf.cell(0, 8, f"Cenário Desconto 25%: R$ {v_desc25:,.2f} (Parcela Padrão: 10x)", 0, 1)
    pdf.cell(0, 8, f"Cenário Desconto 50%: R$ {v_desc50:,.2f} (Parcela Padrão: 10x)", 0, 1)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        temp_filename = tmp_file.name

    pdf.output(temp_filename)

    with open(temp_filename, "rb") as f:
        pdf_bytes = f.read()

    if os.path.exists(temp_filename):
        os.remove(temp_filename)

    return pdf_bytes

# -----------------------------------------------------------------------------
# 5. ESTRUTURA DO DASHBOARD (Conforme a referência)
# -----------------------------------------------------------------------------

# --- TOPO: LOGO E BOTÕES ---
header_col1, header_col2, header_col3 = st.columns([2, 2, 1])

with header_col1:
    # Insira o link da imagem do logo da FNP aqui ou carregue uma imagem local
    # Exemplo com placeholder ou link online (substitua se tiver o arquivo local)
    st.image("https://jornaldosmunicipios.com.br/wp-content/uploads/2021/04/logo-FNP-Prefeitos-Prefeitas.png", width=250)

# Simulação dos valores de desconto para Arapiraca para gerar o PDF antecipadamente (opcional)
v_int = 60728.00
v_d10 = v_int * 0.90
v_d25 = v_int * 0.75
v_d50 = v_int * 0.50

with header_col2:
    st.markdown("<br>", unsafe_allow_html=True) # Alinhamento vertical
    pdf_bytes = gerar_pdf_simulacao("Arapiraca", "AL", False, v_int, v_d10, v_d25, v_d50)
    st.download_button(
        label="📄 Baixar Simulação em PDF",
        data=pdf_bytes,
        file_name=f"simulacao_Arapiraca.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

with header_col3:
    st.markdown("<br>", unsafe_allow_html=True) # Alinhamento vertical
    if st.button("🔄 Atualização Base", use_container_width=True):
        st.success("Base atualizada!")

# --- TÍTULO PRINCIPAL ---
st.markdown("## Simulador de Contribuição e Parcelamento")

# --- LINHA 1: MÉTRICAS GERAIS (Cards Brancos com Ícones) ---
metric_col1, metric_col2, metric_col3 = st.columns(3)

# Exemplo de como adicionar ícones simulando a referência usando markdown dentro do st.metric
# (Ícones reais exigem CSS complexo ou st.image antes da métrica)
with metric_col1:
    st.metric(label="CAPITAIS", value="27", delta="Quantidade de capitais no Brasil")

with metric_col2:
    st.metric(label="MUNICÍPIOS ACIMA DE 80 MIL HABITANTES", value="1.227", delta="Municípios com mais de 80 mil habitantes")

with metric_col3:
    st.metric(label="POTENCIAL DE ARRECADAÇÃO", value="R$ 5,63 Bi", delta="Potencial total de arrecadação anual")

# --- LINHA 2: FILTROS E RANKING ---
st.markdown("#### 🔍 Consulta e Filtros")
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([1.5, 1, 3, 1])

with filter_col1:
    porte_options = df_base["Porte"].unique()
    porte_sel = st.selectbox("Porte", porte_options, index=list(porte_options).index("150 a 350mil hab.") if "150 a 350mil hab." in porte_options else 0)
    df_filtered_porte = df_base[df_base["Porte"] == porte_sel]

with filter_col2:
    uf_options = df_filtered_porte["UF"].unique()
    uf_sel = st.selectbox("UF", uf_options, index=list(uf_options).index("AL") if "AL" in uf_options else 0)
    df_filtered_uf = df_filtered_porte[df_filtered_porte["UF"] == uf_sel]

with filter_col3:
    mun_options = df_filtered_uf["Município"].unique()
    mun_sel = st.selectbox("Município", mun_options, index=list(mun_options).index("Arapiraca") if "Arapiraca" in mun_options else 0)
    # Seleção final dos dados do município
    data_sel = df_filtered_uf[df_filtered_uf["Município"] == mun_sel].iloc[0]

with filter_col4:
    # Mostra Classificação e Ranking
    st.markdown("**Classificação**")
    class_color = "🟢" if data_sel["Classificação"] == "Adimplente" else "🔴"
    st.markdown(f"{class_color} {data_sel['Classificação']}")
    
    st.markdown("**Ranking**")
    # Simulação do card de ranking da referência
    st.markdown(f"""
        <div style="background-color: white; color: #31333F; padding: 10px 15px; border-radius: 8px; font-weight: bold; text-align: center; font-size: 1.2rem;">
            {data_sel['Ranking']}%
        </div>
    """, unsafe_allow_html=True)

# --- LINHA 3: PAINEL DE SIMULAÇÃO ---
status_filiado_text = "(Filiado)" if data_sel["Filiado"] else "(Não Filiado)"
status_filiado_color = "🟢" if data_sel["Filiado"] else "🔴"
st.markdown(f"### Painel de Simulação — {mun_sel} {status_filiado_color} **{status_filiado_text}**")

# Cálculo dos valores baseados na seleção
valor_integral = data_sel["Valor_Integral"]
valor_d10 = valor_integral * 0.90
valor_d25 = valor_integral * 0.75
valor_d50 = valor_integral * 0.50

# Cards Brancos de Simulação (Estrutura da Referência)
sim_col1, sim_col2, sim_col3, sim_col4 = st.columns(4)

with sim_col1:
    st.markdown(f"""
        <div class="sim-card">
            <p class="caption">VALOR INTEGRAL</p>
            <h4>R$ {valor_integral:,.0f}</h4>
            <p class="caption">Sem Desconto</p>
        </div>
    """, unsafe_allow_html=True)

with sim_col2:
    st.markdown(f"""
        <div class="sim-card" style="border-left: 5px solid #1A4D96;">
            <p class="caption" style="color: #1A4D96 !important;">DESCONTO 10%</p>
            <h4>R$ {valor_d10:,.0f}</h4>
            <p class="caption">Parcela Padrão: 12x</p>
        </div>
    """, unsafe_allow_html=True)

with sim_col3:
    st.markdown(f"""
        <div class="sim-card" style="border-left: 5px solid #8E44AD;">
            <p class="caption" style="color: #8E44AD !important;">DESCONTO 25%</p>
            <h4>R$ {valor_d25:,.0f}</h4>
            <p class="caption">Parcela Padrão: 10x</p>
        </div>
    """, unsafe_allow_html=True)

with sim_col4:
    st.markdown(f"""
        <div class="sim-card" style="border-left: 5px solid #27AE60;">
            <p class="caption" style="color: #27AE60 !important;">DESCONTO 50%</p>
            <h4>R$ {valor_d50:,.0f}</h4>
            <p class="caption">Parcela Padrão: 10x</p>
        </div>
    """, unsafe_allow_html=True)

# --- LINHA 4: CALCULADORA DE PARCELAMENTO ---
st.markdown("#### ⚙️ Calculadora de parcelamento")
calc_col1, calc_col2 = st.columns(2)

with calc_col1:
    # Opções de cenário base baseadas nos cálculos acima
    cenario_options = {
        "Desconto 10%": valor_d10,
        "Desconto 25%": valor_d25,
        "Desconto 50%": valor_d50,
        "Valor Integral": valor_integral
    }
    cenario_sel = st.selectbox("1. Escolha o cenário de valor base:", list(cenario_options.keys()))
    valor_base_calculo = cenario_options[cenario_sel]

with calc_col2:
    num_parcelas = st.selectbox(
        "2. Escolha o número de parcelas desejado:",
        [12, 24, 36, 48],
        index=0,
        format_func=lambda x: f"{x}x ({x} parcelas)"
    )

# Cálculos da Calculadora
valor_parcela = valor_base_calculo / num_parcelas
economia_municipio = valor_integral - valor_base_calculo

# --- LINHA 5: RESULTADOS DA CALCULADORA (Cards Azul e Verde) ---
res_col1, res_col2, res_col3 = st.columns(3)

with res_col1:
    st.markdown(f"""
        <div class="result-card-blue">
            <p style="font-size: 0.8rem; font-weight: bold; opacity: 0.8;">VALOR DE CADA PARCELA</p>
            <h2 style="margin: 0.5rem 0;">R$ {valor_parcela:,.0f}</h2>
            <p style="font-size: 0.8rem; opacity: 0.8;">Plano em {num_parcelas} parcelas mensais</p>
        </div>
    """, unsafe_allow_html=True)

with res_col2:
    st.markdown(f"""
        <div class="result-card-blue">
            <p style="font-size: 0.8rem; font-weight: bold; opacity: 0.8;">VALOR TOTAL DA NEGOCIAÇÃO</p>
            <h2 style="margin: 0.5rem 0;">R$ {valor_base_calculo:,.0f}</h2>
            <p style="font-size: 0.8rem; opacity: 0.8;">Cenário: {cenario_sel}</p>
        </div>
    """, unsafe_allow_html=True)

with res_col3:
    st.markdown(f"""
        <div class="result-card-green">
            <p style="font-size: 0.8rem; font-weight: bold; opacity: 0.8;">ECONOMIA PARA O MUNICÍPIO</p>
            <h2 style="margin: 0.5rem 0;">R$ {economia_municipio:,.0f}</h2>
            <p style="font-size: 0.8rem; opacity: 0.8;">Em relação ao valor integral de R$ {valor_integral:,.0f}</p>
        </div>
    """, unsafe_allow_html=True)
