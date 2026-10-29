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
# 2. CARREGAMENTO E LIMPEZA ROBUSTA DA PLANILHA EXCEL
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
# 3. ESTILOS CSS - CARREGAMENTO DA IMAGEM DE FUNDO
# -----------------------------------------------------------------------------
def set_bg_hack():
    bin_str = None
    mime_type = "image/jpeg"
    arquivo_fundo = "simulador.png.jpg"

    if os.path.exists(arquivo_fundo):
        try:
            with open(arquivo_fundo, "rb") as img_file:
                bin_str = base64.b64encode(img_file.read()).decode()
        except Exception:
            pass

    bg_css = f'background-image: url("data:{mime_type};base64,{bin_str}");' if bin_str else 'background-color: #0A3663;'

    page_bg_img = """
        <style>
        .stApp {
            BG_REPLACE
            background-size: cover;
            background-position: center top;
            background-repeat: no-repeat;
        }
        .block-container { padding-top: 180px !important; padding-bottom: 2rem !important; }
        #MainMenu, footer, header { visibility: hidden; }

        @media screen and (max-width: 768px) {
            .stApp {
                background-size: contain !important;
                background-position: center top !important;
                background-color: #0A3663 !important;
            }
            .block-container { padding-top: 100px !important; }
        }

        .page-title { color: #FFFFFF; font-size: 1.6rem; font-weight: 800; margin-bottom: 0.5rem; }
        .badge-main { background-color: #334155; color: #FFFFFF !important; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 0.95rem; display: inline-block; margin-bottom: 8px; }
        .badge-filter { background-color: #475569; color: #FFFFFF !important; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 0.85rem; display: block; margin-bottom: 6px; text-align: left; }
        .badge-light { background-color: #FFFFFF; color: #1A202C !important; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.95rem; vertical-align: middle; display: inline-flex; align-items: center; justify-content: center; }

        .stSelectbox div[data-baseweb="select"] > div {
            background-color: #F1F5F9 !important;
            color: #0F172A !important;
            border-radius: 6px !important;
            border: none !important;
            min-height: 38px !important;
            height: 38px !important;
        }
        .info-auto-box {
            background-color: #F1F5F9;
            color: #0F172A;
            font-weight: 800;
            text-align: center;
            height: 38px;
            min-height: 38px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            box-shadow: none;
            font-size: 0.88rem;
            box-sizing: border-box;
        }

        .top-card { background-color: #FFFFFF; padding: 6px 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.06); display: flex; align-items: center; gap: 10px; height: 60px; }
        .icon-circle { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 0.95rem; font-weight: bold; flex-shrink: 0; }
        .top-card-title { color: #718096 !important; font-size: 0.6rem; font-weight: 800; text-transform: uppercase; line-height: 1; }
        .top-card-value { color: #1A202C !important; font-size: 1.25rem; font-weight: 800; line-height: 1.1; margin: 2px 0; }
        .top-card-sub { color: #A0AEC0 !important; font-size: 0.58rem; font-weight: 600; line-height: 1; }

        .sim-card { background-color: #FFFFFF; padding: 0.7rem 0.9rem; border-radius: 6px; min-height: 85px; display: flex; flex-direction: column; justify-content: center; }
        .sim-title { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; margin-bottom: 0.1rem; }
        .sim-value { color: #1A202C !important; font-size: 1.3rem; font-weight: 800; margin: 0.1rem 0; }
        .sim-sub { color: #A0AEC0 !important; font-size: 0.65rem; min-height: 1rem; }

        .res-card-dark { background-color: #0A3663; color: #FFFFFF !important; padding: 0.7rem 0.9rem; border-radius: 6px; }
        .res-card-blue { background-color: #3B82F6; color: #FFFFFF !important; padding: 0.7rem 0.9rem; border-radius: 6px; }
        .res-card-green { background-color: #10B981; color: #FFFFFF !important; padding: 0.7rem 0.9rem; border-radius: 6px; }
        .res-title { font-size: 0.65rem; font-weight: 800; color: #FFFFFF !important; text-transform: uppercase; }
        .res-val { font-size: 1.3rem; font-weight: 800; color: #FFFFFF !important; margin: 0.1rem 0; }
        .res-sub { font-size: 0.65rem; color: rgba(255,255,255,0.85) !important; }

        .stButton button, .stDownloadButton button { background-color: #FFFFFF !important; color: #2D3748 !important; border: 1px solid #CBD5E0 !important; border-radius: 6px !important; font-size: 0.72rem !important; font-weight: 600 !important; padding: 0.2rem 0.3rem !important; min-height: 38px !important; text-align: center !important; }
        </style>
        """.replace("BG_REPLACE", bg_css)

    st.markdown(page_bg_img, unsafe_allow_html=True)


set_bg_hack()

# -----------------------------------------------------------------------------
# 4. REGRAS E AUXILIARES
# -----------------------------------------------------------------------------
def obter_grupo_rclpc(rcl_pc):
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


def txt_pdf(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

# -----------------------------------------------------------------------------
# 5. GERADOR DE PDF
# -----------------------------------------------------------------------------
class PDFSimulacao(FPDF):
    def header(self):
        img_path = "imagem.pdf.png"
        if os.path.exists(img_path):
            try:
                self.image(img_path, x=0, y=0, w=210)
            except Exception:
                self.set_fill_color(10, 54, 99)
                self.rect(0, 0, 210, 32, "F")
        else:
            self.set_fill_color(10, 54, 99)
            self.rect(0, 0, 210, 32, "F")

        self.set_y(6.0)
        self.set_x(62)
        self.set_font("Arial", "B", 12)
        self.set_text_color(255, 255, 255)
        self.cell(138, 10, txt_pdf("SIMULADOR DE CONTRIBUIÇÃO E PARCELAMENTO"), 0, 1, "L")
        self.set_y(40)


class PDFMemoria(FPDF):
    def header(self):
        img_path = "imagem.pdf.png"
        if os.path.exists(img_path):
            try:
                self.image(img_path, x=0, y=0, w=210)
            except Exception:
                self.set_fill_color(10, 54, 99)
                self.rect(0, 0, 210, 32, "F")
        else:
            self.set_fill_color(10, 54, 99)
            self.rect(0, 0, 210, 32, "F")

        self.set_y(6.0)
        self.set_x(62)
        self.set_font("Arial", "B", 13)
        self.set_text_color(255, 255, 255)
        self.cell(138, 10, txt_pdf("MEMÓRIA DE CÁLCULO DE CONTRIBUIÇÃO"), 0, 1, "L")
        self.set_y(40)


def gerar_pdf_simulacao(municipio, uf, porte, cenario, parcelas, val_integral, valor_total, valor_parcela, economia, mes_inicio="Janeiro", desc_50_prop=False):
    pdf = PDFSimulacao()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 8, txt_pdf(f"RELATÓRIO DE SIMULAÇÃO - {municipio.upper()} ({uf})"), 0, 1, "L")

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 6, txt_pdf(f"Porte: {porte}"), 0, 1, "L")

    pdf.ln(3)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 7, txt_pdf("DETALHES DO PARCELAMENTO SELECIONADO"), 0, 1, "L")
    pdf.ln(3)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.3)

    cenario_pdf = cenario
    if cenario in ["Desconto 25%", "Desconto 50%"]:
        cenario_pdf = f"{cenario} (Novo Filiado)"

    eh_proporcional = (mes_inicio != "Janeiro") or desc_50_prop

    # Se for proporcional, exibe detalhes da modalidade e oculta parcelas/mensalidade
    if eh_proporcional:
        prop_txt = f"Proporcional ({mes_inicio} a Dez/2027)"
        if desc_50_prop:
            prop_txt += " + Desconto 50%"

        dados = [
            ("Cenário Selecionado:", f"{cenario_pdf}"),
            ("Mês de Início da Adesão:", f"{mes_inicio}"),
            ("Modalidade Proporcional:", f"{prop_txt}"),
            ("Valor Integral Anual:", f"R$ {fmt_br(val_integral)}"),
            ("Valor Total da Negociação:", f"R$ {fmt_br(valor_total)}"),
            ("Desconto para o Município:", f"R$ {fmt_br(economia)}"),
        ]
    else:
        # Padrão normal (sem proporcionalidade)
        dados = [
            ("Cenário Selecionado:", f"{cenario_pdf}"),
            ("Mês de Início da Adesão:", f"{mes_inicio}"),
            ("Número de Parcelas:", f"{parcelas}x"),
            ("Valor Integral Anual:", f"R$ {fmt_br(val_integral)}"),
            ("Valor Total da Negociação:", f"R$ {fmt_br(valor_total)}"),
            ("Valor de Cada Parcela Mensal:", f"R$ {fmt_br(valor_parcela)}"),
            ("Desconto para o Município:", f"R$ {fmt_br(economia)}"),
        ]

    col_w1, col_w2, row_height = 95, 95, 8.5
    for rotulo, valor in dados:
        pdf.cell(col_w1, row_height, txt_pdf(f" {rotulo}"), 1, 0, "L")
        pdf.cell(col_w2, row_height, txt_pdf(f" {valor}"), 1, 1, "L")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        temp_filename = tmp_file.name

    pdf.output(temp_filename)
    with open(temp_filename, "rb") as f:
        pdf_bytes = f.read()

    if os.path.exists(temp_filename):
        os.remove(temp_filename)

    return pdf_bytes


def gerar_pdf_memoria_calculo(uf, municipio, populacao, rcl, receita_per_capita, grupo_rclpc, val_contribuicao):
    pdf = PDFMemoria()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 8, txt_pdf(f"{municipio}/{uf}"), 0, 1, "L")

    pdf.ln(2)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    pop_fmt = formatar_inteiro_ptbr(populacao)
    rcl_fmt = f"R$ {fmt_br(rcl)}" if isinstance(rcl, (int, float)) and rcl > 0 else str(rcl)
    receita_per_capita_fmt = f"R$ {fmt_br(receita_per_capita)}" if isinstance(receita_per_capita, (int, float)) else str(receita_per_capita)
    rcl_descritiva = formatar_bilhoes_milhoes(rcl)

    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 6, txt_pdf("Dados do município:"), 0, 1, "L")
    pdf.ln(1)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 5, txt_pdf(f"- População (IBGE): {pop_fmt} habitantes"), 0, 1, "L")
    pdf.cell(0, 5, txt_pdf(f"- RCL 2025: {rcl_fmt}"), 0, 1, "L")
    pdf.cell(0, 5, txt_pdf(f"- RCL per capita: {receita_per_capita_fmt}"), 0, 1, "L")
    pdf.cell(0, 5, txt_pdf(f"- Grupo de RCLpc: Decil {grupo_rclpc}"), 0, 1, "L")

    pdf.ln(4)

    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 6, txt_pdf("Metodologia:"), 0, 1, "L")
    pdf.ln(1)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 5, txt_pdf("O valor da contribuição é definido a partir do cruzamento de dois indicadores:"), 0, 1, "L")
    pdf.ln(1)

    pdf.cell(0, 5, txt_pdf("- RCL: determina a faixa de receita do município na tabela;"), 0, 1, "L")
    pdf.cell(0, 5, txt_pdf("- RCL per capita (RCL / população): determina o grupo de RCLpc."), 0, 1, "L")

    pdf.ln(4)

    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 6, txt_pdf(f"Para {municipio}:"), 0, 1, "L")
    pdf.ln(1)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 5, txt_pdf(f"{rcl_fmt} / {pop_fmt} = {receita_per_capita_fmt} de RCL per capita"), 0, 1, "L")

    texto_enquadramento = f"Com a RCL de {rcl_descritiva} e a RCLpc de {receita_per_capita_fmt} (Decil {grupo_rclpc}), o município é enquadrado na tabela da FNP."
    pdf.multi_cell(0, 5, txt_pdf(texto_enquadramento))

    pdf.ln(3)

    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 6, txt_pdf(f"Contribuição Anual Integral 2027: R$ {fmt_br(val_contribuicao)}"), 0, 1, "L")

    pdf.ln(5)

    caminho_imagem_tabela = "Tabela de contribuição 2027.png"
    if os.path.exists(caminho_imagem_tabela):
        pdf.image(caminho_imagem_tabela, x=10, w=190)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        temp_filename = tmp_file.name

    pdf.output(temp_filename)
    with open(temp_filename, "rb") as f:
        pdf_bytes = f.read()

    if os.path.exists(temp_filename):
        os.remove(temp_filename)

    return pdf_bytes

# -----------------------------------------------------------------------------
# 6. GESTÃO DE ESTADO DOS FILTROS
# -----------------------------------------------------------------------------
if "porte_sel" not in st.session_state:
    st.session_state.porte_sel = "-"
if "uf_sel" not in st.session_state:
    st.session_state.uf_sel = "-"
if "mun_sel" not in st.session_state:
    st.session_state.mun_sel = "-"

if "porte_manual" not in st.session_state:
    st.session_state.porte_manual = False
if "uf_manual" not in st.session_state:
    st.session_state.uf_manual = False

def on_porte_change():
    st.session_state.porte_manual = (st.session_state.porte_sel != "-")
    st.session_state.uf_sel = "-"
    st.session_state.mun_sel = "-"
    st.session_state.uf_manual = False

def on_uf_change():
    st.session_state.uf_manual = (st.session_state.uf_sel != "-")
    st.session_state.mun_sel = "-"

def on_mun_change():
    mun = st.session_state.mun_sel
    if mun != "-":
        match = df_base[df_base["Município"] == mun]
        if not match.empty:
            if "UF" in match.columns:
                st.session_state.uf_sel = str(match["UF"].iloc[0])
            if "Porte" in match.columns:
                st.session_state.porte_sel = str(match["Porte"].iloc[0])
            st.session_state.porte_manual = False
            st.session_state.uf_manual = False

df_filtrado = pd.DataFrame()
has_data = False

if st.session_state.mun_sel != "-":
    df_filtrado = df_base[df_base["Município"] == st.session_state.mun_sel]
    if st.session_state.uf_sel != "-":
        df_filtrado = df_filtrado[df_filtrado["UF"] == st.session_state.uf_sel]
    has_data = not df_filtrado.empty

MESES_ANO = [
    ("Janeiro", 12), ("Fevereiro", 11), ("Março", 10), ("Abril", 9),
    ("Maio", 8), ("Junho", 7), ("Julho", 6), ("Agosto", 5),
    ("Setembro", 4), ("Outubro", 3), ("Novembro", 2), ("Dezembro", 1)
]

# -----------------------------------------------------------------------------
# 7. CABEÇALHO COM BOTÕES DE DOWNLOAD
# -----------------------------------------------------------------------------
header_title_col, header_actions_col = st.columns([6.3, 3.7])

with header_title_col:
    st.markdown('<div class="page-title">Simulador de Contribuição e Parcelamento</div>', unsafe_allow_html=True)

with header_actions_col:
    b_col1, b_col2, b_col3 = st.columns([1, 1, 1])

    if has_data:
        val_integral_h, val_d10_h, val_d25_h, val_d50_h = obter_valores_validados(df_filtrado)

        cenario_h = st.session_state.get("cenario_calc", "Desconto 10%")
        parcelas_h = st.session_state.get("num_parcelas_calc", 12)
        mes_inicio_nome_h = st.session_state.get("mes_inicio_calc", "Janeiro")

        desc_50_str_h = st.session_state.get("aplicar_50_prop_sel", "Não")
        aplicar_50_prop_h = (desc_50_str_h == "Sim")

        meses_vigentes_h = dict(MESES_ANO).get(mes_inicio_nome_h, 12)

        val_base_h = val_d10_h if cenario_h == "Desconto 10%" else (val_d25_h if cenario_h == "Desconto 25%" else (val_d50_h if cenario_h == "Desconto 50%" else val_integral_h))

        mensalidade_base_h = val_base_h / parcelas_h if parcelas_h > 0 else 0.0

        if aplicar_50_prop_h:
            valor_negociado_h = (mensalidade_base_h * meses_vigentes_h) * 0.50
        else:
            valor_negociado_h = (val_base_h / 12) * meses_vigentes_h

        economia_h = val_integral_h - valor_negociado_h
        valor_parcela_h = valor_negociado_h / parcelas_h if parcelas_h > 0 else 0.0
