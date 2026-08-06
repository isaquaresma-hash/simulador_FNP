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
  """Converte valores em formato monetário BR ou números para float puro."""
  try:
    if valor is None:
      return 0.0

    if isinstance(valor, (int, float)):
      return float(valor)

    val_str = str(valor).strip()
    if val_str.lower() in ["nan", "none", "", "null", "-"]:
      return 0.0

    val_str = val_str.replace("R$", "").replace(" ", "")

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


def formatar_ranking(valor):
  """Formata os valores da coluna Ranking/Classificação."""
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


@st.cache_data
def carregar_dados():
  caminho_encontrado = None
  if os.path.exists(NOME_ARQUIVO_PLANILHA):
    caminho_encontrado = NOME_ARQUIVO_PLANILHA
  else:
    for f in os.listdir("."):
      if f.endswith(".xlsx") or f.endswith(".csv"):
        caminho_encontrado = f
        break

  if not caminho_encontrado:
    st.error("Erro: Nenhum arquivo Excel/CSV foi encontrado no repositório!")
    st.stop()

  try:
    if caminho_encontrado.endswith(".csv"):
      df = pd.read_csv(caminho_encontrado, dtype=str)
    else:
      df = pd.read_excel(caminho_encontrado, engine="openpyxl", dtype=str)
  except ImportError:
    st.error(
        "A biblioteca 'openpyxl' não está instalada no ambiente. Adicione"
        " 'openpyxl' ao seu requirements.txt."
    )
    st.stop()

  df.columns = df.columns.astype(str).str.strip()

  mapeamento = {}
  for col in df.columns:
    col_upper = col.upper()

    if "PARCELA" in col_upper:
      continue

    if "SITUAÇÃO" in col_upper or "SITUACAO" in col_upper:
      mapeamento[col] = "Situação"
    elif "PORTE" in col_upper:
      mapeamento[col] = "Porte"
    elif "UF" in col_upper:
      mapeamento[col] = "UF"
    elif "MUNICÍPIO" in col_upper or "MUNICIPIO" in col_upper:
      mapeamento[col] = "Município"
    elif "RANKING" in col_upper or "RANK" in col_upper or "CLASSIFICAÇÃO" in col_upper or "CLASSIFICACAO" in col_upper or "POSIÇÃO" in col_upper:
      mapeamento[col] = "Ranking"
    elif "10%" in col_upper and "Valor_D10" not in mapeamento.values():
      mapeamento[col] = "Valor_D10"
    elif (
        "50%" in col_upper or "60%" in col_upper
    ) and "Valor_D50" not in mapeamento.values():
      mapeamento[col] = "Valor_D50"
    elif "25%" in col_upper and "Valor_D25" not in mapeamento.values():
      mapeamento[col] = "Valor_D25"
    elif (
        "CONTRIBUIÇÃO 2027" in col_upper or "CONTRIBUICAO 2027" in col_upper
    ) and "Valor_Integral" not in mapeamento.values():
      mapeamento[col] = "Valor_Integral"

  df = df.rename(columns=mapeamento)
  df = df.loc[:, ~df.columns.duplicated()]

  if "Ranking" in df.columns:
    df["Ranking"] = [formatar_ranking(v) for v in df["Ranking"]]

  colunas_valor = ["Valor_Integral", "Valor_D10", "Valor_D50", "Valor_D25"]
  for col in colunas_valor:
    if col in df.columns:
      df[col] = [converter_valor_ptbr(v) for v in df[col]]
    else:
      df[col] = 0.0

  return df


df_base = carregar_dados()

# -----------------------------------------------------------------------------
# 3. ESTILOS CSS E IMAGEM DE FUNDO
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
            background-position: top center;
            background-repeat: no-repeat;
            background-attachment: scroll;
        }}
        /* Padding alterado para 350px para descer bem mais o conteúdo */
        .block-container {{ padding-top: 350px !important; padding-bottom: 2rem !important; }}
        #MainMenu, footer, header {{ visibility: hidden; }}

        .page-title {{
            color: #0A3663;
            font-size: 1.35rem;
            font-weight: 800;
            margin-top: 2rem;
            margin-bottom: 0.8rem;
        }}

        .badge-main {{
            background-color: #334155; color: #FFFFFF !important; padding: 6px 14px;
            border-radius: 6px; font-weight: bold; font-size: 0.85rem; display: inline-block; margin-bottom: 12px;
        }}
        .badge-filter {{
            background-color: #475569; color: #FFFFFF !important; padding: 3px 10px;
            border-radius: 4px; font-weight: 700; font-size: 0.78rem; display: inline-block; margin-bottom: 6px;
        }}
        .badge-light {{
            background-color: #FFFFFF; color: #1A202C !important; padding: 4px 10px;
            border-radius: 12px; font-weight: bold; font-size: 0.8rem;
        }}
        .stSelectbox div[data-baseweb="select"] > div {{
            background-color: #F1F5F9 !important; color: #0F172A !important;
            border-radius: 6px !important; border: none !important; min-height: 42px !important;
        }}
        .ranking-box {{
            background-color: #FFFFFF; color: #0F172A; font-weight: 800; text-align: center;
            height: 42px; display: flex; align-items: center; justify-content: center;
            border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); font-size: 0.9rem;
        }}
        .top-card {{
            background-color: #FFFFFF; padding: 12px 18px; border-radius: 10px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.08); display: flex; align-items: center; gap: 15px;
            height: 85px;
        }}
        .icon-circle {{
            width: 42px; height: 42px; border-radius: 50%; display: flex;
            align-items: center; justify-content: center; color: white; font-size: 1.2rem; font-weight: bold; flex-shrink: 0;
        }}
        .top-card-title {{ color: #718096 !important; font-size: 0.68rem; font-weight: 800; text-transform: uppercase; }}
        .top-card-value {{ color: #1A202C !important; font-size: 1.7rem; font-weight: 800; line-height: 1.1; }}
        .top-card-sub {{ color: #A0AEC0 !important; font-size: 0.65rem; font-weight: 600; }}

        .sim-card {{ background-color: #FFFFFF; padding: 1rem 1.2rem; border-radius: 8px; height: 100%; }}
        .sim-title {{ font-size: 0.72rem; font-weight: 800; text-transform: uppercase; margin-bottom: 0.2rem; }}
        .sim-value {{ color: #1A202C !important; font-size: 1.6rem; font-weight: 800; margin: 0.2rem 0; }}
        .sim-sub {{ color: #A0AEC0 !important; font-size: 0.72rem; }}

        .res-card-dark {{ background-color: #0A3663; color: #FFFFFF !important; padding: 1rem 1.2rem; border-radius: 8px; }}
        .res-card-blue {{ background-color: #3B82F6; color: #FFFFFF !important; padding: 1rem 1.2rem; border-radius: 8px; }}
        .res-card-green {{ background-color: #10B981; color: #FFFFFF !important; padding: 1rem 1.2rem; border-radius: 8px; }}
        .res-title {{ font-size: 0.72rem; font-weight: 800; color: #FFFFFF !important; text-transform: uppercase; }}
        .res-val {{ font-size: 1.7rem; font-weight: 800; color: #FFFFFF !important; margin: 0.2rem 0; }}
        .res-sub {{ font-size: 0.72rem; color: rgba(255,255,255,0.85) !important; }}

        .stButton button, .stDownloadButton button {{
            background-color: #FFFFFF !important; color: #2D3748 !important;
            border: 1px solid #CBD5E0 !important; border-radius: 6px !important;
            font-size: 0.8rem !important; font-weight: 600 !important; padding: 0.3rem 0.8rem !important;
        }}
        </style>
        """
    st.markdown(page_bg_img, unsafe_allow_html=True)


set_bg_hack(CAMINHO_IMAGEM_FUNDO)


def fmt_br(valor):
  return f"{valor:,.0f}".replace(",", ".")


# -----------------------------------------------------------------------------
# 4. GERADOR DE PDF
# -----------------------------------------------------------------------------
class PDF(FPDF):

  def header(self):
    self.set_font("Arial", "B", 13)
    self.set_text_color(10, 54, 99)
    self.cell(
        0, 8, "FNP - SIMULADOR DE CONTRIBUIÇÃO E PARCELAMENTO", 0, 1, "L"
    )
    self.ln(2)

  def footer(self):
    self.set_y(-18)
    self.set_font("Arial", "", 8)
    self.set_text_color(100, 116, 139)
    self.cell(
        0,
        5,
        "Este documento é apenas uma simulação baseada nas regras de"
        " contribuição da FNP.",
        0,
        1,
        "L",
    )


def gerar_pdf_simulacao(
    municipio,
    uf,
    porte,
    ranking,
    situacao,
    cenario,
    parcelas,
    val_integral,
    valor_total,
    valor_parcela,
    economia,
):
  pdf = PDF()
  pdf.add_page()

  pdf.set_font("Arial", "B", 11)
  pdf.set_text_color(15, 23, 42)
  pdf.cell(
      0, 6, f"RELATÓRIO DE SIMULAÇÃO - {municipio.upper()} ({uf})", 0, 1, "L"
  )

  pdf.set_font("Arial", "", 9)
  pdf.set_text_color(71, 85, 105)
  pdf.cell(
      0,
      5,
      f"Porte: {porte}  |  Ranking: {ranking}  |  Situação: {situacao}",
      0,
      1,
      "L",
  )
  pdf.ln(5)

  pdf.set_font("Arial", "B", 10)
  pdf.set_text_color(10, 54, 99)
  pdf.cell(0, 6, "DETALHES DO PARCELAMENTO SELECIONADO", 0, 1, "L")
  pdf.ln(2)

  itens = [
      ("Cenário Selecionado:", f"{cenario}"),
      ("Número de Parcelas:", f"{parcelas}x"),
      ("Valor Integral (Sem Desconto):", f"R$ {fmt_br(val_integral)}"),
      ("Valor Total da Negociação:", f"R$ {fmt_br(valor_total)}"),
      ("Valor de Cada Parcela Mensal:", f"R$ {fmt_br(valor_parcela)}"),
      ("Economia Gerada para o Município:", f"R$ {fmt_br(economia)}"),
  ]

  for rotulo, valor in itens:
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(0, 5, rotulo, 0, 1, "L")

    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, f" | {valor}", 0, 1, "L")
    pdf.ln(2)

  with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
    temp_filename = tmp_file.name

  pdf.output(temp_filename)
  with open(temp_filename, "rb") as f:
    pdf_bytes = f.read()

  if os.path.exists(temp_filename):
    os.remove(temp_filename)
  return pdf_bytes


# -----------------------------------------------------------------------------
# 5. ESTRUTURA DO TOPO (TÍTULO À ESQUERDA E BOTÕES À DIREITA)
# -----------------------------------------------------------------------------
porte_opcoes = ["Todos"] + sorted(df_base["Porte"].dropna().unique().tolist())

porte_sel = st.session_state.get("porte_sel", "Todos")
uf_sel = st.session_state.get("uf_sel", "Todas")
mun_sel = st.session_state.get("mun_sel", "Digite ou selecione um município")

df_porte = (
    df_base.copy()
    if porte_sel == "Todos"
    else df_base[df_base["Porte"] == porte_sel]
)
df_uf = df_porte.copy() if uf_sel == "Todas" else df_porte[df_porte["UF"] == uf_sel]

if mun_sel in ["Digite ou selecione um município", "None", None]:
  df_filtrado = pd.DataFrame()
elif mun_sel == "Todos":
  df_filtrado = df_uf.copy()
else:
  df_filtrado = df_uf[df_uf["Município"] == mun_sel]

has_data = not df_filtrado.empty
pdf_bytes_topo = None
nome_exibicao = (
    mun_sel if mun_sel != "Todos" else f"Todos ({len(df_filtrado)} municípios)"
)

if has_data:
  if "Situação" in df_filtrado.columns:
    situacoes = df_filtrado["Situação"].astype(str).tolist()
    filiados_count = sum(
        1
        for s in situacoes
        if "filiado" in s.lower() and "não" not in s.lower()
    )
    if len(df_filtrado) == 1:
      situacao_municipio = situacoes[0]
      eh_filiado = (
          "filiado" in situacao_municipio.lower()
          and "não" not in situacao_municipio.lower()
      )
      status_text = situacao_municipio
    else:
      eh_filiado = filiados_count == len(df_filtrado)
      status_text = f"{filiados_count} de {len(df_filtrado)} filiados"
  else:
    eh_filiado = True
    status_text = "Filiado"

  val_integral_t = df_filtrado["Valor_Integral"].sum()
  val_d10_t = df_filtrado["Valor_D10"].sum()
  if val_d10_t <= 0:
    val_d10_t = val_integral_t * 0.90

  val_neg_t = val_d10_t
  econ_t = val_integral_t - val_neg_t
  val_parc_t = val_neg_t / 12

  ranking_val = (
      df_filtrado["Ranking"].iloc[0]
      if len(df_filtrado) == 1 and "Ranking" in df_filtrado.columns
      else ("Vários" if len(df_filtrado) > 1 else "-")
  )

  pdf_bytes_topo = gerar_pdf_simulacao(
      municipio=nome_exibicao,
      uf=uf_sel,
      porte=porte_sel,
      ranking=ranking_val,
      situacao=status_text,
      cenario="Desconto 10%",
      parcelas=12,
      val_integral=val_integral_t,
      valor_total=val_neg_t,
      valor_parcela=val_parc_t,
      economia=econ_t,
  )

# Cabeçalho Principal
header_title_col, header_actions_col = st.columns([5.5, 4.5])

with header_title_col:
  st.markdown(
      '<div class="page-title">Simulador de Contribuição e Parcelamento</div>',
      unsafe_allow_html=True,
  )

with header_actions_col:
  b_col1, b_col2 = st.columns(2)
  with b_col1:
    if has_data and pdf_bytes_topo:
      st.download_button(
          label="📄 Baixar Simulação em PDF",
          data=pdf_bytes_topo,
          file_name=f"simulacao_{nome_exibicao}.pdf",
          mime="application/pdf",
          use_container_width=True,
      )
    else:
      st.button(
          "📄 Baixar Simulação em PDF",
          disabled=True,
          use_container_width=True,
          help="Selecione um município para habilitar o PDF.",
      )

  with b_col2:
    if st.button("🔄 Atualização Base", use_container_width=True):
      st.cache_data.clear()
      st.rerun()

# CARDS INFORMATIVOS SUPERIORES
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
  st.markdown("""
        <div class="top-card">
            <div class="icon-circle" style="background-color: #1E40AF;">🏛️</div>
            <div>
                <div class="top-card-title">CAPITAIS</div>
                <div class="top-card-value">27</div>
                <div class="top-card-sub">Quantidade de capitais no Brasil</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with m_col2:
  st.markdown("""
        <div class="top-card">
            <div class="icon-circle" style="background-color: #059669;">👥</div>
            <div>
                <div class="top-card-title">MUNICÍPIOS ACIMA DE 80 MIL HABITANTES</div>
                <div class="top-card-value">1.227</div>
                <div class="top-card-sub">Municípios com mais de 80 mil habitantes</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with m_col3:
  st.markdown("""
        <div class="top-card">
            <div class="icon-circle" style="background-color: #7C3AED;">💲</div>
            <div>
                <div class="top-card-title">POTENCIAL DE ARRECADAÇÃO</div>
                <div class="top-card-value">R$ 5,63 Bi</div>
                <div class="top-card-sub">Potencial total de arrecadação anual</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# CONSULTA E FILTROS
st.markdown(
    '<div class="badge-main">🔍 Consulta e Filtros</div>',
    unsafe_allow_html=True,
)

f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1.5, 4.5, 2])

# 1. Porte
with f_col1:
  st.markdown(
      '<div class="badge-filter">Porte</div>', unsafe_allow_html=True
  )
  porte_sel = st.selectbox(
      "", porte_opcoes, key="porte_sel", label_visibility="collapsed"
  )

df_porte = (
    df_base.copy()
    if porte_sel == "Todos"
    else df_base[df_base["Porte"] == porte_sel]
)

# 2. UF
with f_col2:
  st.markdown('<div class="badge-filter">UF</div>', unsafe_allow_html=True)
  uf_opcoes = ["Todas"] + sorted(df_porte["UF"].dropna().unique().tolist())
  uf_sel = st.selectbox(
      "", uf_opcoes, key="uf_sel", label_visibility="collapsed"
  )

df_uf = df_porte.copy() if uf_sel == "Todas" else df_porte[df_porte["UF"] == uf_sel]

# 3. Município
SELECIONE_MUN_TEXT = "Digite ou selecione um município"
lista_municipios = sorted(df_uf["Município"].dropna().unique().tolist())
eh_porte_capital = "CAPITAL" in str(porte_sel).upper()

if eh_porte_capital:
  mun_opcoes = [SELECIONE_MUN_TEXT] + lista_municipios
else:
  mun_opcoes = [SELECIONE_MUN_TEXT, "Todos"] + lista_municipios

with f_col3:
  st.markdown(
      '<div class="badge-filter">Município</div>', unsafe_allow_html=True
  )
  mun_sel = st.selectbox(
      "", mun_opcoes, key="mun_sel", label_visibility="collapsed"
  )

if mun_sel == SELECIONE_MUN_TEXT:
  df_filtrado = pd.DataFrame()
elif mun_sel == "Todos":
  df_filtrado = df_uf.copy()
else:
  df_filtrado = df_uf[df_uf["Município"] == mun_sel]

# 4. Classificação / Ranking
with f_col4:
  st.markdown(
      '<div class="badge-filter">Classificação</div>', unsafe_allow_html=True
  )
  if len(df_filtrado) == 1 and "Ranking" in df_filtrado.columns:
    ranking_val = df_filtrado["Ranking"].iloc[0]
  elif len(df_filtrado) > 1:
    ranking_val = "Vários"
  else:
    ranking_val = "-"

  st.markdown(
      f"""
        <div class="ranking-box">
            {ranking_val}
        </div>
    """,
      unsafe_allow_html=True,
  )

# -----------------------------------------------------------------------------
# EXPANSÃO DINÂMICA DA SIMULAÇÃO E CALCULADORA
# -----------------------------------------------------------------------------
has_data = not df_filtrado.empty

if has_data:
  st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

  if "Situação" in df_filtrado.columns:
    situacoes = df_filtrado["Situação"].astype(str).tolist()
    filiados_count = sum(
        1
        for s in situacoes
        if "filiado" in s.lower() and "não" not in s.lower()
    )

    if len(df_filtrado) == 1:
      situacao_municipio = situacoes[0]
      eh_filiado = (
          "filiado" in situacao_municipio.lower()
          and "não" not in situacao_municipio.lower()
      )
      status_text = situacao_municipio
      status_color = "🟢" if eh_filiado else "🔴"
    else:
      eh_filiado = filiados_count == len(df_filtrado)
      status_text = f"{filiados_count} de {len(df_filtrado)} filiados"
      status_color = "🔵"
  else:
    eh_filiado = True
    status_text = "Filiado"
    status_color = "🟢"

  nome_exibicao = (
      mun_sel if mun_sel != "Todos" else f"Todos ({len(df_filtrado)} municípios)"
  )

  st.markdown(
      f"""
      <div style="margin-bottom: 0.8rem; font-size: 1.2rem; font-weight: 800; color: #0F172A;">
          Painel de Simulação — {nome_exibicao} <span class="badge-light">{status_color} ({status_text})</span>
      </div>
  """,
      unsafe_allow_html=True,
  )

  val_integral = df_filtrado["Valor_Integral"].sum()
  val_d10 = df_filtrado["Valor_D10"].sum()
  val_d25 = df_filtrado["Valor_D25"].sum()
  val_d50 = df_filtrado["Valor_D50"].sum()

  if val_d10 <= 0:
    val_d10 = val_integral * 0.90
  if val_d25 <= 0:
    val_d25 = val_integral * 0.75
  if val_d50 <= 0:
    val_d50 = val_integral * 0.50

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
                  <div class="sim-sub">Pacote: 12x</div>
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
                  <div class="sim-sub">Pacote: 12x</div>
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
                  <div class="sim-sub">Pacote: 10x</div>
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
                  <div class="sim-sub">Pacote: 10x</div>
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
        '<div class="badge-filter" style="margin-bottom: 6px;">1. Escolha o'
        " cenário de valor base:</div>",
        unsafe_allow_html=True,
    )

    if eh_filiado:
      opcoes_cenario = ["Desconto 10%", "Valor Integral"]
    else:
      opcoes_cenario = [
          "Desconto 10%",
          "Desconto 25%",
          "Desconto 50%",
          "Valor Integral",
      ]

    cenario = st.selectbox("", opcoes_cenario, label_visibility="collapsed")

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
