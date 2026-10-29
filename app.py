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
# 2. CARREGAMENTO E LIMPEZA DA PLANILHA
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
        st.error("Erro: Nenhum arquivo Excel ou CSV foi encontrado no diretório!")
        st.stop()

    try:
        if caminho_encontrado.endswith(".csv"):
            df = pd.read_csv(caminho_encontrado, header=2, dtype=str)
        else:
            df = pd.read_excel(caminho_encontrado, header=2, engine="openpyxl", dtype=str)
    except Exception:
        st.error("Erro ao carregar a planilha de dados.")
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
# 3. ESTILOS CSS CONCATENADOS
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

    bg_css = f"background-image: url('data:{mime_type};base64,{bin_str}');" if bin_str else "background-color: #0A3663;"

    css_lines = [
        "<style>",
        ".stApp { " + bg_css + " background-size: cover; background-position: center top; background-repeat: no-repeat; }",
        ".block-container { padding-top: 180px !important; padding-bottom: 2rem !important; }",
        "#MainMenu, footer, header { visibility: hidden; }",
        "@media screen and (max-width: 768px) { .stApp { background-size: contain !important; background-position: center top !important; background-color: #0A3663 !important; } .block-container { padding-top: 100px !important; } }",
        ".page-title { color: #FFFFFF; font-size: 1.6rem; font-weight: 800; margin-bottom: 0.5rem; }",
        ".badge-main { background-color: #334155; color: #FFFFFF !important; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 0.95rem; display: inline-block; margin-bottom: 8px; }",
        ".badge-filter { background-color: #475569; color: #FFFFFF !important; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 0.85rem; display: block; margin-bottom: 6px; text-align: left; }",
        ".badge-light { background-color: #FFFFFF; color: #1A202C !important; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.95rem; vertical-align: middle; display: inline-flex; align-items: center; justify-content: center; }",
        ".stSelectbox div[data-baseweb='select'] > div { background-color: #F1F5F9 !important; color: #0F172A !important; border-radius: 6px !important; border: none !important; min-height: 38px !important; height: 38px !important; }",
        ".info-auto-box { background-color: #F1F5F9; color: #0F172A; font-weight: 800; text-align: center; height: 38px; min-height: 38px; display: flex; align-items: center; justify-content: center; border-radius: 6px; box-shadow: none; font-size: 0.88rem; box-sizing: border-box; }",
        ".top-card { background-color: #FFFFFF; padding: 6px 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.06); display: flex; align-items: center; gap: 10px; height: 60px; }",
        ".icon-circle { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 0.95rem; font-weight: bold; flex-shrink: 0; }",
        ".top-card-title { color: #718096 !important; font-size: 0.6rem; font-weight: 800; text-transform: uppercase; line-height: 1; }",
        ".top-card-value { color: #1A202C !important; font-size: 1.25rem; font-weight: 800; line-height: 1.1; margin: 2px 0; }",
        ".top-card-sub { color: #A0AEC0 !important; font-size: 0.58rem; font-weight: 600; line-height: 1; }",
        ".sim-card { background-color: #FFFFFF; padding: 0.7rem 0.9rem; border-radius: 6px; min-height: 85px; display: flex; flex-direction: column; justify-content: center; }",
        ".sim-title { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; margin-bottom: 0.1rem; }",
        ".sim-value { color: #1A202C !important; font-size: 1.3rem; font-weight: 800; margin: 0.1rem 0; }",
        ".sim-sub { color: #A0AEC0 !important; font-size: 0.65rem; min-height: 1rem; }",
        ".res-card-dark { background-color: #0A3663; color: #FFFFFF !important; padding: 0.7rem 0.9rem; border-radius: 6px; }",
        ".res-card-blue { background-color: #3B82F6; color: #FFFFFF !important; padding: 0.7rem 0.9rem; border-radius: 6px; }",
        ".res-card-green { background-color: #10B981; color: #FFFFFF !important; padding: 0.7rem 0.9rem; border-radius: 6px; }",
        ".res-title { font-size: 0.65rem; font-weight: 800; color: #FFFFFF !important; text-transform: uppercase; }",
        ".res-val { font-size: 1.3rem; font-weight: 800; color: #FFFFFF !important; margin: 0.1rem 0; }",
        ".res-sub { font-size: 0.65rem; color: rgba(255,255,255,0.85) !important; }",
        ".stButton button, .stDownloadButton button { background-color: #FFFFFF !important; color: #2D3748 !important; border: 1px solid #CBD5E0 !important; border-radius: 6px !important; font-size: 0.72rem !important; font-weight: 600 !important; padding: 0.2rem 0.3rem !important; min-height: 38px !important; text-align: center !important; }",
        "</style>"
    ]
    st.markdown("".join(css_lines), unsafe_allow_html=True)


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


def gerar_pdf_simulacao(municipio, uf, porte, cenario, parcelas, val_integral, valor_total, valor_parcela, economia, mes_inicio="Janeiro", desc_50_prop=False, eh_filiado=True):
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
