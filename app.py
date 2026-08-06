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
# 2. IMAGEM DE FUNDO E ESTILOS CSS
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
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }}

        #MainMenu, footer, header {{ visibility: hidden; }}

        .badge-main {{
            background-color: #334155;
            color: #FFFFFF !important;
            padding: 6px 14px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 0.85rem;
            display: inline-block;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        }}

        .badge-filter {{
            background-color: #475569;
            color: #FFFFFF !important;
            padding: 3px 10px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 0.78rem;
            display: inline-block;
            margin-bottom: 6px;
        }}

        .badge-light {{
            background-color: #FFFFFF;
            color: #1A202C !important;
            padding: 4px 10px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 0.8rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .stSelectbox div[data-baseweb="select"] > div {{
            background-color: #F1F5F9 !important;
            color: #0F172A !important;
            border-radius: 6px !important;
            border: none !important;
            min-height: 42px !important;
        }}

        .ranking-box {{
            background-color: #FFFFFF;
            color: #0F172A;
            font-weight: 800;
            text-align: center;
            height: 42px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            font-size: 0.9rem;
        }}

        .top-card {{
            background-color: #FFFFFF;
            padding: 12px 18px;
            border-radius: 10px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.08);
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .icon-circle {{
            width: 42px;
            height: 42px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.2rem;
            font-weight: bold;
        }}
        .top-card-title {{
            color: #718096 !important;
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
        }}
        .top-card-value {{
            color: #1A202C !important;
            font-size: 1.8rem;
            font-weight: 800;
            line-height: 1.1;
        }}
        .top-card-sub {{
            color: #38A169 !important;
            font-size: 0.7rem;
            font-weight: 600;
        }}

        .sim-card {{
            background-color: #FFFFFF;
            padding: 1rem 1.2rem;
            border-radius: 8px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.08);
            height: 100%;
        }}
        .sim-title {{
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 0.2rem;
        }}
        .sim-value {{
            color: #1A202C !important;
            font-size: 1.6rem;
            font-weight: 800;
            margin: 0.2rem 0;
        }}
        .sim-sub {{
            color: #A0AEC0 !important;
            font-size: 0.72rem;
        }}

        .res-card-dark {{
            background-color: #0A3663;
            color: #FFFFFF !important;
            padding: 1rem 1.2rem;
            border-radius: 8px;
        }}
        .res-card-blue {{
            background-color: #3B82F6;
            color: #FFFFFF !important;
            padding: 1rem 1.2rem;
            border-radius: 8px;
        }}
        .res-card-green {{
            background-color: #10B981;
            color: #FFFFFF !important;
            padding: 1rem 1.2rem;
            border-radius: 8px;
        }}
        .res-title {{
            font-size: 0.72rem;
            font-weight: 800;
            color: #FFFFFF !important;
            text-transform: uppercase;
        }}
        .res-val {{
            font-size: 1.7rem;
            font-weight: 800;
            color: #FFFFFF !important;
            margin: 0.2rem 0;
        }}
        .res-sub {{
            font-size: 0.72rem;
            color: rgba(255,255,255,0.85) !important;
        }}

        .stButton button, .stDownloadButton button {{
            background-color: #FFFFFF !important;
            color: #2D3748 !important;
            border: 1px solid #CBD5E0 !important;
            border-radius: 6px !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            padding: 0.3rem 0.8rem !important;
        }}
        </style>
        """
    st.markdown(page_bg_img, unsafe_allow_html=True)


set_bg_hack(CAMINHO_IMAGEM_FUNDO)


def fmt_br(valor):
  return f"{valor:,.0f}".replace(",", ".")


# -----------------------------------------------------------------------------
# 3. BASE DE DADOS REAIS EXTRAÍDA DA PLANILHA
# -----------------------------------------------------------------------------
data = {
    "Situação": [
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
        "Filiado",
    ],
    "Porte": [
        "Capital",
        "Capital",
        "Capital",
        "80 a 150mil hab.",
        "Capital",
        "Capital",
        "Capital",
        "Capital",
        "Capital",
        "350 a 500mil hab.",
        "Capital",
        "+500mil hab.",
        "350 a 500mil hab.",
        "150 a 350mil hab.",
        "Capital",
        "80 a 150mil hab.",
        "Capital",
        "+500mil hab.",
        "Capital",
        "350 a 500mil hab.",
        "+500mil hab.",
        "+500mil hab.",
        "+500mil hab.",
        "350 a 500mil hab.",
        "até 80mil hab.",
        "+500mil hab.",
        "+500mil hab.",
        "até 80mil hab.",
        "350 a 500mil hab.",
        "350 a 500mil hab.",
        "Capital",
    ],
    "UF": [
        "SP",
        "RJ",
        "DF",
        "MG",
        "MG",
        "PR",
        "BA",
        "AM",
        "RS",
        "SP",
        "PB",
        "GO",
        "PR",
        "MA",
        "PA",
        "AM",
        "SC",
        "RJ",
        "AP",
        "PB",
        "RJ",
        "RJ",
        "SP",
        "SP",
        "MG",
        "PE",
        "BA",
        "SP",
        "PE",
        "PE",
        "MT",
    ],
    "Município": [
        "São Paulo",
        "Rio de Janeiro",
        "Brasília",
        "Muriaé",
        "Belo Horizonte",
        "Curitiba",
        "Salvador",
        "Manaus",
        "Porto Alegre",
        "Santos",
        "João Pessoa",
        "Aparecida de Goiânia",
        "Ponta Grossa",
        "Imperatriz",
        "Belém",
        "Parintins",
        "Florianópolis",
        "São Gonçalo",
        "Macapá",
        "Campina Grande",
        "Duque de Caxias",
        "Nova Iguaçu",
        "São Bernardo do Campo",
        "Mauá",
        "Mateus Leme",
        "Jaboatão dos Guararapes",
        "Feira de Santana",
        "Jarinu",
        "Petrolina",
        "Caruaru",
        "Cuiabá",
    ],
    "Ranking": [
        "Adimplente",
        "Adimplente",
        "70%",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "90%",
        "Adimplente",
        "90%",
        "Adimplente",
        "70%",
        "90%",
        "Adimplente",
        "70%",
        "30%",
        "70%",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "Adimplente",
        "70%",
    ],
    "Valor_Integral": [
        5070000.00,
        1547600.00,
        1934500.00,
        110535.00,
        883063.00,
        798750.00,
        197700.00,
        197700.00,
        593100.00,
        447167.00,
        173256.00,
        87000.00,
        70000.00,
        61970.00,
        129000.00,
        51743.00,
        309811.00,
        87000.00,
        70000.00,
        70000.00,
        180359.00,
        87000.00,
        320970.00,
        70000.00,
        50870.00,
        75000.00,
        75000.00,
        83070.00,
        60000.00,
        60000.00,
        274089.00,
    ],
}
df_base = pd.DataFrame(data)


# -----------------------------------------------------------------------------
# 4. FUNÇÃO GERAR PDF
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


def gerar_pdf_simulacao(
    municipio, uf, cenario, parcelas, valor_total, valor_parcela, economia
):
  pdf = PDF()
  pdf.add_page()
  pdf.set_font("Arial", "B", 12)

  pdf.cell(0, 10, f"Relatorio de Simulacao - {municipio} ({uf})", 0, 1)
  pdf.ln(5)

  pdf.set_font("Arial", "", 11)
  pdf.cell(0, 8, f"Cenario Selecionado: {cenario}", 0, 1)
  pdf.cell(0, 8, f"Numero de Parcelas: {parcelas}x", 0, 1)
  pdf.cell(0, 8, f"Valor Total da Negociacao: R$ {fmt_br(valor_total)}", 0, 1)
  pdf.cell(0, 8, f"Valor de Cada Parcela: R$ {fmt_br(valor_parcela)}", 0, 1)
  pdf.cell(0, 8, f"Economia para o Municipio: R$ {fmt_br(economia)}", 0, 1)

  with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
    temp_filename = tmp_file.name

  pdf.output(temp_filename)

  with open(temp_filename, "rb") as f:
    pdf_bytes = f.read()

  if os.path.exists(temp_filename):
    os.remove(temp_filename)

  return pdf_bytes


# -----------------------------------------------------------------------------
# 5. INTERFACE DASHBOARD
# -----------------------------------------------------------------------------

# Topo: Botões
btn_col1, btn_col2, btn_col3 = st.columns([4, 1.3, 1.3])

with btn_col1:
  st.write("")

pdf_bytes = gerar_pdf_simulacao(
    "Manaus", "AM", "Desconto 10%", 12, 177930.00, 14827.50, 19770.00
)

with btn_col2:
  st.download_button(
      label="📄 Baixar Simulação em PDF",
      data=pdf_bytes,
      file_name="simulacao_FNP.pdf",
      mime="application/pdf",
      use_container_width=True,
  )

with btn_col3:
  if st.button("🔄 Atualização Base", use_container_width=True):
    st.success("Base atualizada!")

st.markdown(
    """
    <h2 style='color: #0F172A; font-weight: 800; font-size: 1.6rem; margin-top: 1rem; margin-bottom: 1rem;'>
        Simulador de Contribuição e Parcelamento
    </h2>
""",
    unsafe_allow_html=True,
)

# Métricas
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
  st.markdown(
      """
        <div class="top-card">
            <div class="icon-circle" style="background-color: #1E40AF;">🏛️</div>
            <div>
                <div class="top-card-title">CAPITAIS</div>
                <div class="top-card-value">27</div>
                <div class="top-card-sub">↑ Quantidade de capitais no Brasil</div>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

with m_col2:
  st.markdown(
      """
        <div class="top-card">
            <div class="icon-circle" style="background-color: #059669;">👥</div>
            <div>
                <div class="top-card-title">MUNICÍPIOS ACIMA DE 80 MIL HABITANTES</div>
                <div class="top-card-value">1.227</div>
                <div class="top-card-sub">↑ Municípios com mais de 80 mil habitantes</div>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

with m_col3:
  st.markdown(
      """
        <div class="top-card">
            <div class="icon-circle" style="background-color: #7C3AED;">💲</div>
            <div>
                <div class="top-card-title">POTENCIAL DE ARRECADAÇÃO</div>
                <div class="top-card-value">R$ 5,63 Bi</div>
                <div class="top-card-sub">↑ Potencial total de arrecadação anual</div>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SEÇÃO DE FILTROS DINÂMICOS E CORRIGIDOS
# -----------------------------------------------------------------------------
st.markdown(
    '<div class="badge-main">🔍 Consulta e Filtros</div>',
    unsafe_allow_html=True,
)

f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1.5, 4.5, 2])

# 1. Filtro Porte
with f_col1:
  st.markdown(
      '<div class="badge-filter">Porte</div>', unsafe_allow_html=True
  )
  porte_opcoes = sorted(df_base["Porte"].unique().tolist())
  porte_sel = st.selectbox("", porte_opcoes, label_visibility="collapsed")

df_porte = df_base[df_base["Porte"] == porte_sel]

# 2. Filtro UF (filtrado pelo Porte)
with f_col2:
  st.markdown('<div class="badge-filter">UF</div>', unsafe_allow_html=True)
  uf_opcoes = sorted(df_porte["UF"].unique().tolist())
  uf_sel = st.selectbox("", uf_opcoes, label_visibility="collapsed")

df_uf = df_porte[df_porte["UF"] == uf_sel]

# 3. Filtro Município
with f_col3:
  st.markdown(
      '<div class="badge-filter">Município</div>', unsafe_allow_html=True
  )
  mun_opcoes = sorted(df_uf["Município"].unique().tolist())
  mun_sel = st.selectbox("", mun_opcoes, label_visibility="collapsed")

df_final = df_uf[df_uf["Município"] == mun_sel].iloc[0]

# 4. Exibição do Ranking Exato
with f_col4:
  st.markdown(
      '<div class="badge-filter">Ranking</div>', unsafe_allow_html=True
  )
  st.markdown(
      f"""
        <div class="ranking-box">
            {df_final['Ranking']}
        </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown("<br>", unsafe_allow_html=True)

# Painel de Simulação
status_text = (
    f"({df_final['Situação']})"
    if "Situação" in df_final
    else "(Filiado)"
)
status_color = "🟢" if "Filiado" in status_text else "🔴"

st.markdown(
    f"""
    <div style="margin-bottom: 0.8rem; font-size: 1.2rem; font-weight: 800; color: #0F172A;">
        Painel de Simulação — {mun_sel} <span class="badge-light">{status_color} {status_text}</span>
    </div>
""",
    unsafe_allow_html=True,
)

val_integral = df_final["Valor_Integral"]
val_d10 = val_integral * 0.90
val_d25 = val_integral * 0.75
val_d50 = val_integral * 0.50

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
            <div class="sim-sub">Parcela Padrão: 12x</div>
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
            <div class="sim-sub">Parcela Padrão: 10x</div>
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
            <div class="sim-sub">Parcela Padrão: 10x</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown("<br>", unsafe_allow_html=True)

# Calculadora de Parcelamento
st.markdown(
    '<div class="badge-main">⚙️ Calculadora de parcelamento</div>',
    unsafe_allow_html=True,
)

calc_col1, calc_col2 = st.columns(2)

with calc_col1:
  st.markdown(
      '<div class="badge-filter" style="margin-bottom: 6px;">1. Escolha o'
      " cenário de valor base:</div>",
      unsafe_allow_html=True,
  )
  cenario = st.selectbox(
      "",
      ["Desconto 10%", "Desconto 25%", "Desconto 50%", "Valor Integral"],
      label_visibility="collapsed",
  )

with calc_col2:
  st.markdown(
      '<div class="badge-filter" style="margin-bottom: 6px;">2. Escolha o'
      " número de parcelas desejado:</div>",
      unsafe_allow_html=True,
  )
  num_parcelas = st.selectbox(
      "",
      [12, 24, 36, 48],
      format_func=lambda x: f"{x}x ({x} parcelas)",
      label_visibility="collapsed",
  )

# Cálculos
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

# Resultados Inferiores
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
