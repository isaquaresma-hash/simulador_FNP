import base64
import os
import tempfile
from fpdf import FPDF
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Simulador FNP",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA IMAGEM DE FUNDO (Base64)
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
        /* Fundo semi-transparente nos cards para melhorar leitura sobre a imagem */
        div[data-testid="stMetricValue"], div[data-testid="stMetric"] {{
            background-color: rgba(255, 255, 255, 0.85);
            padding: 10px;
            border-radius: 8px;
        }}
        </style>
        """
    st.markdown(page_bg_img, unsafe_allow_html=True)


set_bg_hack(CAMINHO_IMAGEM_FUNDO)

# -----------------------------------------------------------------------------
# 2. BASE DE DADOS (Exemplo / Mock Data)
# -----------------------------------------------------------------------------
data = {
    "Porte": ["Capital", "Capital", "Grande", "Médio"],
    "UF": ["AM", "SP", "RJ", "MG"],
    "Município": ["Manaus", "São Paulo", "Rio de Janeiro", "Belo Horizonte"],
    "Classificação": ["Adimplente", "Adimplente", "Inadimplente", "Adimplente"],
    "Filiado": [True, True, False, True],
    "Valor_Integral": [197700.00, 500000.00, 350000.00, 250000.00],
}
df_base = pd.DataFrame(data)


# -----------------------------------------------------------------------------
# 3. FUNÇÃO PARA GERAR O PDF (Via Arquivo Temporário)
# -----------------------------------------------------------------------------
class PDF(FPDF):

  def header(self):
    self.set_font("Arial", "B", 14)
    self.cell(
        0, 10, "FNP - Simulador de Contribuicao e Parcelamento", 0, 1, "C"
    )
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
  pdf.cell(0, 8, f"Valor Total da Negociacao: R$ {valor_total:,.2f}", 0, 1)
  pdf.cell(0, 8, f"Valor de Cada Parcela: R$ {valor_parcela:,.2f}", 0, 1)
  pdf.cell(0, 8, f"Economia para o Municipio: R$ {economia:,.2f}", 0, 1)

  # Salva em arquivo temporário para garantir compatibilidade
  with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
    temp_filename = tmp_file.name

  pdf.output(temp_filename)

  with open(temp_filename, "rb") as f:
    pdf_bytes = f.read()

  if os.path.exists(temp_filename):
    os.remove(temp_filename)

  return pdf_bytes


# -----------------------------------------------------------------------------
# 4. DASHBOARD INTERFACE
# -----------------------------------------------------------------------------
st.title("Simulador de Contribuição e Parcelamento")

# Top Metrics
col1, col2, col3 = st.columns(3)
with col1:
  st.metric("Capitais", "27", "Quantidade de capitais no Brasil")
with col2:
  st.metric(
      "Municípios Acima de 80 mil Habitantes",
      "1,227",
      "Municípios com mais de 80 mil hab",
  )
with col3:
  st.metric(
      "Potencial de Arrecadação",
      "R$ 5,63 Bi",
      "Potencial total de arrecadação anual",
  )

st.write("---")

# Filtros
st.subheader("🔍 Consulta e Filtros")
f_col1, f_col2, f_col3, f_col4 = st.columns(4)

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
  st.markdown("**Classificação**")
  st.write(df_final["Classificação"])

# Painel de Resultados
status_filiado = "🟢 (Filiado)" if df_final["Filiado"] else "🔴 (Não Filiado)"
st.subheader(f"Painel de Simulação — {mun_sel} {status_filiado}")

val_integral = df_final["Valor_Integral"]
val_desc10 = val_integral * 0.90

c1, c2 = st.columns(2)
with c1:
  st.markdown("**Valor Integral**")
  st.write(f"R$ {val_integral:,.2f}")
  st.caption("Sem Desconto")

with c2:
  st.markdown("**Desconto 10%**")
  st.write(f"R$ {val_desc10:,.2f}")
  st.caption("Parcela Padrão: 12x")

st.write("---")

# Calculadora de Parcelamento
st.subheader("⚙️ Calculadora de parcelamento")

calc_col1, calc_col2 = st.columns(2)

with calc_col1:
  cenario = st.selectbox(
      "1. Escolha o cenário de valor base:", ["Desconto 10%", "Valor Integral"]
  )

with calc_col2:
  num_parcelas = st.selectbox(
      "2. Escolha o número de parcelas desejado:",
      [12, 24, 36, 48],
      format_func=lambda x: f"{x}x ({x} parcelas)",
  )

# Cálculos
if cenario == "Desconto 10%":
  valor_negociado = val_desc10
  economia = val_integral - val_desc10
else:
  valor_negociado = val_integral
  economia = 0.00

valor_parcela = valor_negociado / num_parcelas

# Resultados do Calculador
res1, res2, res3 = st.columns(3)

with res1:
  st.markdown("**Valor de Cada Parcela**")
  st.write(f"### R$ {valor_parcela:,.2f}")
  st.caption(f"Plano em {num_parcelas} parcelas mensais")

with res2:
  st.markdown("**Valor Total da Negociação**")
  st.write(f"### R$ {valor_negociado:,.2f}")
  st.caption(f"Cenário: {cenario}")

with res3:
  st.markdown("**Economia para o Município**")
  st.write(f"### R$ {economia:,.2f}")
  st.caption(f"Em relação ao valor integral de R$ {val_integral:,.2f}")

st.write("---")

# Botões Superiores / Download PDF
top_b1, top_b2 = st.columns(2)

with top_b1:
  pdf_bytes = gerar_pdf_simulacao(
      mun_sel,
      uf_sel,
      cenario,
      num_parcelas,
      valor_negociado,
      valor_parcela,
      economia,
  )
  st.download_button(
      label="📄 Baixar Simulação em PDF",
      data=pdf_bytes,
      file_name=f"simulacao_{mun_sel}.pdf",
      mime="application/pdf",
      use_container_width=True,
  )

with top_b2:
  if st.button("🔄 Atualização Base", use_container_width=True):
    st.success("Base atualizada com sucesso!")
