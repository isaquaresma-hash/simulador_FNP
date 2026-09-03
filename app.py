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
# 2. DADOS DA TABELA FNP 2027 (Fidelidade total à imagem)
# -----------------------------------------------------------------------------
DADOS_TABELA_FNP = [
    {"Faixa": 1, "De": "até", "Ate": "218.758.762", "D1": "40.000", "D2": "40.577", "D3": "44.951", "D4": "48.053", "D5": "65.590", "D6": "66.758", "D7": "67.752", "D8": "68.621", "D9": "69.396", "D10": "70.096"},
    {"Faixa": 2, "De": "218.758.762", "Ate": "313.554.225", "D1": "41.000", "D2": "41.707", "D3": "47.067", "D4": "50.870", "D5": "72.363", "D6": "73.795", "D7": "75.012", "D8": "76.077", "D9": "77.027", "D10": "77.886"},
    {"Faixa": 3, "De": "313.554.225", "Ate": "495.853.193", "D1": "42.000", "D2": "42.853", "D3": "49.326", "D4": "53.918", "D5": "79.871", "D6": "81.599", "D7": "83.070", "D8": "84.356", "D9": "85.502", "D10": "86.539"},
    {"Faixa": 4, "De": "495.853.193", "Ate": "667.214.224", "D1": "43.000", "D2": "48.906", "D3": "51.743", "D4": "57.223", "D5": "88.196", "D6": "90.259", "D7": "92.014", "D8": "93.549", "D9": "94.917", "D10": "96.154"},
    {"Faixa": 5, "De": "667.214.224", "Ate": "729.195.872", "D1": "44.000", "D2": "50.982", "D3": "54.336", "D4": "60.814", "D5": "97.431", "D6": "99.869", "D7": "101.944", "D8": "103.758", "D9": "105.376", "D10": "106.839"},
    {"Faixa": 6, "De": "729.195.872", "Ate": "783.885.562", "D1": "45.000", "D2": "53.190", "D3": "57.125", "D4": "64.723", "D5": "107.674", "D6": "110.535", "D7": "112.968", "D8": "115.097", "D9": "116.994", "D10": "118.710"},
    {"Faixa": 7, "De": "783.885.562", "Ate": "1.039.104.119", "D1": "48.000", "D2": "57.322", "D3": "66.644", "D4": "75.967", "D5": "119.339", "D6": "122.595", "D7": "125.365", "D8": "127.787", "D9": "129.947", "D10": "131.900"},
    {"Faixa": 8, "De": "1.039.104.119", "Ate": "1.294.322.674", "D1": "50.000", "D2": "60.728", "D3": "71.457", "D4": "82.185", "D5": "132.099", "D6": "135.846", "D7": "139.034", "D8": "141.822", "D9": "144.307", "D10": "146.555"},
    {"Faixa": 9, "De": "1.294.322.674", "Ate": "1.629.752.775", "D1": "60.000", "D2": "61.970", "D3": "82.853", "D4": "94.280", "D5": "147.442", "D6": "151.433", "D7": "154.828", "D8": "157.797", "D9": "160.444", "D10": "162.839"},
    {"Faixa": 10, "De": "1.629.752.775", "Ate": "1.968.828.856", "D1": "70.000", "D2": "72.125", "D3": "94.652", "D4": "106.977", "D5": "164.324", "D6": "168.629", "D7": "172.292", "D8": "175.494", "D9": "178.350", "D10": "180.932"},
    {"Faixa": 11, "De": "1.968.828.856", "Ate": "2.278.737.101", "D1": "75.000", "D2": "77.415", "D3": "95.732", "D4": "108.725", "D5": "182.166", "D6": "187.057", "D7": "191.219", "D8": "194.858", "D9": "198.102", "D10": "201.036"},
    {"Faixa": 12, "De": "2.278.737.101", "Ate": "2.588.645.348", "D1": "87.000", "D2": "89.613", "D3": "109.432", "D4": "123.491", "D5": "202.955", "D6": "208.247", "D7": "212.750", "D8": "216.688", "D9": "220.198", "D10": "223.373"},
    {"Faixa": 13, "De": "2.588.645.348", "Ate": "3.463.680.395", "D1": "100.000", "D2": "102.839", "D3": "124.376", "D4": "139.653", "D5": "226.005", "D6": "231.756", "D7": "236.649", "D8": "240.927", "D9": "244.742", "D10": "248.192"},
    {"Faixa": 14, "De": "3.463.680.395", "Ate": "4.375.175.234", "D1": "122.000", "D2": "173.256", "D3": "175.487", "D4": "274.089", "D5": "309.811", "D6": "311.640", "D7": "317.836", "D8": "320.152", "D9": "420.781", "D10": "435.769"},
    {"Faixa": 15, "De": "4.375.175.234", "Ate": "5.104.371.106", "D1": "128.000", "D2": "175.739", "D3": "180.359", "D4": "276.967", "D5": "318.414", "D6": "321.997", "D7": "328.666", "D8": "330.315", "D9": "447.167", "D10": "449.411"},
    {"Faixa": 16, "De": "5.104.371.106", "Ate": "5.833.566.978", "D1": "129.000", "D2": "176.842", "D3": "182.522", "D4": "280.084", "D5": "320.970", "D6": "327.610", "D7": "332.653", "D8": "335.486", "D9": "449.362", "D10": "452.456"},
    {"Faixa": 17, "De": "5.833.566.978", "Ate": "8.750.350.468", "D1": "145.000", "D2": "188.225", "D3": "189.015", "D4": "291.671", "D5": "325.660", "D6": "391.855", "D7": "410.531", "D8": "427.419", "D9": "452.549", "D10": "457.285"},
    {"Faixa": 18, "De": "8.750.350.468", "Ate": "11.758.283.441", "D1": "197.700", "D2": "197.700", "D3": "428.350", "D4": "461.300", "D5": "494.250", "D6": "593.100", "D7": "655.705", "D8": "657.682", "D9": "658.341", "D10": "659.000"},
    {"Faixa": 19, "De": "11.758.283.441", "Ate": "21.875.876.170", "D1": "204.125", "D2": "221.875", "D3": "576.875", "D4": "710.000", "D5": "754.375", "D6": "798.750", "D7": "883.063", "D8": "884.838", "D9": "886.613", "D10": "887.500"},
    {"Faixa": 20, "De": "21.875.876.170", "Ate": "50.000.000.000", "D1": "1.373.495", "D2": "1.450.875", "D3": "1.547.600", "D4": "1.683.015", "D5": "1.818.430", "D6": "1.837.775", "D7": "1.851.317", "D8": "1.886.138", "D9": "1.901.614", "D10": "1.934.500"},
    {"Faixa": 21, "De": "50.000.000.000", "Ate": "acima de 50.000.000.000", "D1": "3.692.000", "D2": "3.900.000", "D3": "4.160.000", "D4": "4.524.000", "D5": "4.888.000", "D6": "4.940.000", "D7": "4.976.400", "D8": "5.070.000", "D9": "5.111.600", "D10": "5.200.000"}
]

# -----------------------------------------------------------------------------
# 3. CARREGAMENTO E LIMPEZA ROBUSTA DA PLANILHA EXCEL
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
        "Situação",
        "Porte",
        "UF",
        "Município",
        "Ranking",
        "Valor_Integral",
        "Valor_D10",
        "Valor_D50",
        "Valor_D25",
        "Parcela_12x",
        "Parcela_D50_x",
        "Parcela_D25_x",
        "População",
        "RCL",
        "Receita per capita",
        "Decil"
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
# 4. ESTILOS CSS
# -----------------------------------------------------------------------------
def set_bg_hack():
    bin_str = None
    mime_type = "image/png"
    
    # Busca especificamente pela imagem informada nos arquivos
    imagem_fundo = "simulador.png.jpg" if os.path.exists("simulador.png.jpg") else "Tabela de contribuição 2027.png"
    
    for f in os.listdir("."):
        if f == imagem_fundo or f.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                if f.lower().endswith(('.jpg', '.jpeg')):
                    mime_type = "image/jpeg"
                else:
                    mime_type = "image/png"
                    
                with open(f, "rb") as img_file:
                    bin_str = base64.b64encode(img_file.read()).decode()
                break
            except Exception:
                pass

    bg_css = f'background-image: url("data:{mime_type};base64,{bin_str}");' if bin_str else 'background-color: #F8FAFC;'

    page_bg_img = f"""
        <style>
        .stApp {{
            {bg_css}
            background-size: cover;
            background-position: center top;
            background-repeat: no-repeat;
        }}
        .block-container {{ padding-top: 180px !important; padding-bottom: 2rem !important; }}
        #MainMenu, footer, header {{ visibility: hidden; }}

        @media screen and (max-width: 768px) {{
            .stApp {{
                background-size: contain !important;
                background-position: center top !important;
                background-color: #0A3663 !important;
            }}
            .block-container {{ padding-top: 100px !important; }}
        }}

        .page-title {{ color: #FFFFFF; font-size: 1.6rem; font-weight: 800; margin-bottom: 0.5rem; }}
        .badge-main {{ background-color: #334155; color: #FFFFFF !important; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 0.95rem; display: inline-block; margin-bottom: 8px; }}
        .badge-filter {{ background-color: #475569; color: #FFFFFF !important; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 0.85rem; display: block; margin-bottom: 6px; text-align: left; }}
        .badge-light {{ background-color: #FFFFFF; color: #1A202C !important; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.95rem; vertical-align: middle; display: inline-flex; align-items: center; justify-content: center; }}
        
        .stSelectbox div[data-baseweb="select"] > div {{ 
            background-color: #F1F5F9 !important; 
            color: #0F172A !important; 
            border-radius: 6px !important; 
            border: none !important; 
            min-height: 38px !important; 
            height: 38px !important; 
        }}
        .info-auto-box {{ 
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
        }}
        
        .top-card {{ background-color: #FFFFFF; padding: 6px 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.06); display: flex; align-items: center; gap: 10px; height: 60px; }}
        .icon-circle {{ width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 0.95rem; font-weight: bold; flex-shrink: 0; }}
        .top-card-title {{ color: #718096 !important; font-size: 0.6rem; font-weight: 800; text-transform: uppercase; line-height: 1; }}
        .top-card-value {{ color: #1A202C !important; font-size: 1.25rem; font-weight: 800; line-height: 1.1; margin: 2px 0; }}
        .top-card-sub {{ color: #A0AEC0 !important; font-size: 0.58rem; font-weight: 600; line-height: 1; }}

        .sim-card {{ background-color: #FFFFFF; padding: 0.7rem 0.9rem; border-radius: 6px; min-height: 85px; display: flex; flex-direction: column; justify-content: center; }}
        .sim-title {{ font-size: 0.65rem; font-weight: 800; text-transform: uppercase; margin-bottom: 0.1rem; }}
        .sim-value {{ color: #1A202C !important; font-size: 1.3rem; font-weight: 800; margin: 0.1rem 0; }}
        .sim-sub {{ color: #A0AEC0 !important; font-size: 0.65rem; min-height: 1rem; }}

        .res-card-dark {{ background-color: #0A3663; color: #FFFFFF !important; padding: 0.7rem 0.9rem; border-radius: 6px; }}
        .res-card-blue {{ background-color: #3B82F6; color: #FFFFFF !important; padding: 0.7rem 0.9rem; border-radius: 6px; }}
        .res-card-green {{ background-color: #10B981; color: #FFFFFF !important; padding: 0.7rem 0.9rem; border-radius: 6px; }}
        .res-title {{ font-size: 0.65rem; font-weight: 800; color: #FFFFFF !important; text-transform: uppercase; }}
        .res-val {{ font-size: 1.3rem; font-weight: 800; color: #FFFFFF !important; margin: 0.1rem 0; }}
        .res-sub {{ font-size: 0.65rem; color: rgba(255,255,255,0.85) !important; }}

        .explicacao-card {{ background-color: #FFFFFF; padding: 1rem 1.2rem; border-radius: 8px; border-left: 5px solid #0A3663; margin-top: 1rem; color: #1E293B; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}

        .stButton button, .stDownloadButton button {{ background-color: #FFFFFF !important; color: #2D3748 !important; border: 1px solid #CBD5E0 !important; border-radius: 6px !important; font-size: 0.72rem !important; font-weight: 600 !important; padding: 0.2rem 0.3rem !important; min-height: 38px !important; text-align: center !important; }}
        
        .tabela-fnp-container {{ overflow-x: auto; margin-top: 15px; font-size: 0.75rem; }}
        .tabela-fnp {{ width: 100%; border-collapse: collapse; text-align: center; }}
        .tabela-fnp th {{ background-color: #0A3663; color: white; padding: 4px; border: 1px solid #CBD5E0; font-size: 0.7rem; }}
        .tabela-fnp td {{ padding: 3px; border: 1px solid #CBD5E0; color: #1E293B; }}
        .tabela-fnp tr:nth-child(even) {{ background-color: #F8FAFC; }}
        </style>
        """
    st.markdown(page_bg_img, unsafe_allow_html=True)


set_bg_hack()

# -----------------------------------------------------------------------------
# 5. ENQUADRAMENTO DA TABELA MANUAL FNP 2027 (RCL X RCLpc)
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

# -----------------------------------------------------------------------------
# 6. GERADOR DE PDF
# -----------------------------------------------------------------------------
class PDFSimulacao(FPDF):
    def header(self):
        self.set_fill_color(10, 54, 99)
        self.rect(0, 0, 210, 32, "F")
        self.set_y(10)
        self.set_font("Arial", "B", 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "FNP - SIMULADOR DE CONTRIBUICAO E PARCELAMENTO", 0, 1, "C")
        self.set_y(40)


class PDFMemoria(FPDF):
    def header(self):
        self.set_fill_color(10, 54, 99)
        self.rect(0, 0, 210, 32, "F")
        self.set_y(10)
        self.set_font("Arial", "B", 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "MEMORIA DE CALCULO DE CONTRIBUICAO", 0, 1, "C")
        self.set_y(40)


def gerar_pdf_simulacao(municipio, uf, porte, cenario, parcelas, val_integral, valor_total, valor_parcela, economia):
    pdf = PDFSimulacao()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 8, f"RELATORIO DE SIMULACAO - {municipio.upper()} ({uf})", 0, 1, "L")

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 6, f"Porte: {porte}", 0, 1, "L")

    pdf.ln(3)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 7, "DETALHES DO PARCELAMENTO SELECIONADO", 0, 1, "L")
    pdf.ln(3)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.3)

    cenario_pdf = cenario
    if cenario in ["Desconto 25%", "Desconto 50%"]:
        cenario_pdf = f"{cenario} (Novo Filiado)"

    dados = [
        ("Cenario Selecionado:", f"{cenario_pdf}"),
        ("Numero de Parcelas:", f"{parcelas}x"),
        ("Valor Integral:", f"R$ {fmt_br(val_integral)}"),
        ("Valor Total da Negociacao:", f"R$ {fmt_br(valor_total)}"),
        ("Valor de Cada Parcela Mensal:", f"R$ {fmt_br(valor_parcela)}"),
        ("Desconto para o Municipio:", f"R$ {fmt_br(economia)}"),
    ]

    col_w1, col_w2, row_height = 95, 95, 9
    for rotulo, valor in dados:
        pdf.cell(col_w1, row_height, f" {rotulo}", 1, 0, "L")
        pdf.cell(col_w2, row_height, f" {valor}", 1, 1, "L")

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

    # Subtítulo com formato Município/UF
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 8, f"{municipio}/{uf}", 0, 1, "L")

    pdf.ln(2)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # Formatação de dados
    pop_fmt = formatar_inteiro_ptbr(populacao)
    rcl_fmt = f"R$ {fmt_br(rcl)}" if isinstance(rcl, (int, float)) and rcl > 0 else str(rcl)
    receita_per_capita_fmt = f"R$ {fmt_br(receita_per_capita)}" if isinstance(receita_per_capita, (int, float)) else str(receita_per_capita)
    rcl_descritiva = formatar_bilhoes_milhoes(rcl)

    # Bloco 1: Dados do município
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 6, "Dados do municipio:", 0, 1, "L")
    pdf.ln(1)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 5, f"Populacao (IBGE): {pop_fmt} habitantes", 0, 1, "L")
    pdf.cell(0, 5, f"RCL 2025: {rcl_fmt}", 0, 1, "L")
    pdf.cell(0, 5, f"RCL per capita: {receita_per_capita_fmt}", 0, 1, "L")
    pdf.cell(0, 5, f"Grupo de RCLpc: Decil {grupo_rclpc}", 0, 1, "L")

    pdf.ln(4)

    # Bloco 2: Metodologia
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 6, "Metodologia", 0, 1, "L")
    pdf.ln(1)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 5, "O valor da contribuicao e definido a partir do cruzamento de dois indicadores:", 0, 1, "L")
    pdf.ln(1)

    pdf.cell(0, 5, f"- RCL: determina a faixa de receita do municipio na tabela;", 0, 1, "L")
    pdf.cell(0, 5, f"- RCL per capita (RCL / populacao): determina o grupo de RCLpc.", 0, 1, "L")

    pdf.ln(4)

    # Bloco 3: Aplicação Específica para o Município
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 6, f"Para {municipio}:", 0, 1, "L")
    pdf.ln(1)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 5, f"{rcl_fmt} / {pop_fmt} = {receita_per_capita_fmt} de RCL per capita", 0, 1, "L")
    
    texto_enquadramento = f"Com a RCL de {rcl_descritiva} e a RCLpc de {receita_per_capita_fmt} (Decil {grupo_rclpc}), o municipio e enquadrado na tabela da FNP."
    pdf.multi_cell(0, 5, texto_enquadramento)

    pdf.ln(3)

    # Destaque do Valor da Contribuição
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 6, f"Contribuicao Anual Integral 2027: R$ {fmt_br(val_contribuicao)}", 0, 1, "L")

    pdf.ln(5)

    # Bloco 4: Tabela FNP 2027 no PDF
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 6, "TABELA DE CONTRIBUICAO FNP 2027", 0, 1, "C")
    pdf.ln(2)

    pdf.set_font("Arial", "B", 5)
    pdf.set_fill_color(10, 54, 99)
    pdf.set_text_color(255, 255, 255)

    col_w = [8, 18, 18, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14]
    headers = ["FX", "De (R$)", "Ate (R$)", "1 (D1)", "2", "3", "4", "5", "6", "7", "8", "9", "10 (D10)"]

    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 5, h, 1, 0, "C", True)
    pdf.ln()

    pdf.set_font("Arial", "", 5)
    pdf.set_text_color(0, 0, 0)

    for row in DADOS_TABELA_FNP:
        pdf.cell(col_w[0], 4, str(row["Faixa"]), 1, 0, "C")
        pdf.cell(col_w[1], 4, str(row["De"]), 1, 0, "R")
        pdf.cell(col_w[2], 4, str(row["Ate"]), 1, 0, "R")
        pdf.cell(col_w[3], 4, str(row["D1"]), 1, 0, "R")
        pdf.cell(col_w[4], 4, str(row["D2"]), 1, 0, "R")
        pdf.cell(col_w[5], 4, str(row["D3"]), 1, 0, "R")
        pdf.cell(col_w[6], 4, str(row["D4"]), 1, 0, "R")
        pdf.cell(col_w[7], 4, str(row["D5"]), 1, 0, "R")
        pdf.cell(col_w[8], 4, str(row["D6"]), 1, 0, "R")
        pdf.cell(col_w[9], 4, str(row["D7"]), 1, 0, "R")
        pdf.cell(col_w[10], 4, str(row["D8"]), 1, 0, "R")
        pdf.cell(col_w[11], 4, str(row["D9"]), 1, 0, "R")
        pdf.cell(col_w[12], 4, str(row["D10"]), 1, 1, "R")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        temp_filename = tmp_file.name

    pdf.output(temp_filename)
    with open(temp_filename, "rb") as f:
        pdf_bytes = f.read()

    if os.path.exists(temp_filename):
        os.remove(temp_filename)

    return pdf_bytes

# -----------------------------------------------------------------------------
# 7. CABEÇALHO E TOP CARDS
# -----------------------------------------------------------------------------
header_title_col, header_actions_col = st.columns([6.3, 3.7])

with header_title_col:
    st.markdown('<div class="page-title">Simulador de Contribuição e Parcelamento</div>', unsafe_allow_html=True)

with header_actions_col:
    b_col1, b_col2, b_col3 = st.columns([1, 1, 1])
    with b_col1:
        pdf_placeholder = st.empty()

    with b_col2:
        pdf_memoria_placeholder = st.empty()

    with b_col3:
        if st.button("🔄 Atualizar Base", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

m_col1, m_col2 = st.columns(2)
with m_col1:
    st.markdown('<div class="top-card"><div class="icon-circle" style="background-color: #1E40AF;">🏛️</div><div><div class="top-card-title">CAPITAIS</div><div class="top-card-value">27</div><div class="top-card-sub">Quantidade de capitais no Brasil</div></div></div>', unsafe_allow_html=True)
with m_col2:
    st.markdown('<div class="top-card"><div class="icon-circle" style="background-color: #059669;">👥</div><div><div class="top-card-title">MUNICÍPIOS ACIMA DE 80 MIL HABITANTES</div><div class="top-card-value">435</div><div class="top-card-sub">Municípios recorte FNP</div></div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. FILTROS INTEGRADOS
# -----------------------------------------------------------------------------
st.markdown('<div class="badge-main">🔍 Consulta e Filtros</div>', unsafe_allow_html=True)

f_col1, f_col2, f_col3, f_col4 = st.columns([2.5, 1.2, 3.8, 2.5])

if "porte_sel" not in st.session_state:
    st.session_state.porte_sel = "-"
if "uf_sel" not in st.session_state:
    st.session_state.uf_sel = "-"
if "mun_sel" not in st.session_state:
    st.session_state.mun_sel = "-"

porte_opcoes = ["-"] + sorted([str(x) for x in df_base["Porte"].dropna().unique().tolist()]) if "Porte" in df_base.columns else ["-"]

def on_porte_change():
    st.session_state.uf_sel = "-"
    st.session_state.mun_sel = "-"

def on_uf_change():
    st.session_state.mun_sel = "-"

def on_mun_change():
    mun = st.session_state.mun_sel
    uf = st.session_state.uf_sel
    if mun != "-" and uf != "-":
        match = df_base[(df_base["UF"] == uf) & (df_base["Município"] == mun)]
        if not match.empty and "Porte" in match.columns:
            st.session_state.porte_sel = str(match["Porte"].iloc[0])

idx_porte = porte_opcoes.index(st.session_state.porte_sel) if st.session_state.porte_sel in porte_opcoes else 0

with f_col1:
    st.markdown('<div class="badge-filter">Porte</div>', unsafe_allow_html=True)
    porte_sel = st.selectbox("", porte_opcoes, index=idx_porte, key="porte_sel", on_change=on_porte_change, label_visibility="collapsed")

df_temp = df_base.copy()
if porte_sel != "-":
    df_temp = df_temp[df_temp["Porte"] == porte_sel]

uf_opcoes = ["-"] + sorted([str(x) for x in df_temp["UF"].dropna().unique().tolist()]) if "UF" in df_temp.columns else ["-"]
idx_uf = uf_opcoes.index(st.session_state.uf_sel) if st.session_state.uf_sel in uf_opcoes else 0

with f_col2:
    st.markdown('<div class="badge-filter">UF</div>', unsafe_allow_html=True)
    uf_sel = st.selectbox("", uf_opcoes, index=idx_uf, key="uf_sel", on_change=on_uf_change, label_visibility="collapsed")

if uf_sel != "-":
    df_temp = df_temp[df_temp["UF"] == uf_sel]

mun_opcoes = ["-"] + sorted([str(x) for x in df_temp["Município"].dropna().unique().tolist()]) if "Município" in df_temp.columns else ["-"]
idx_mun = mun_opcoes.index(st.session_state.mun_sel) if st.session_state.mun_sel in mun_opcoes else 0

with f_col3:
    st.markdown('<div class="badge-filter">Município</div>', unsafe_allow_html=True)
    mun_sel = st.selectbox("", mun_opcoes, index=idx_mun, key="mun_sel", on_change=on_mun_change, label_visibility="collapsed")

if mun_sel != "-" and uf_sel != "-":
    df_filtrado = df_base[(df_base["UF"] == uf_sel) & (df_base["Município"] == mun_sel)]
    if not df_filtrado.empty:
        porte_val = str(df_filtrado["Porte"].iloc[0]) if "Porte" in df_filtrado.columns else "-"
        ranking_val = str(df_filtrado["Ranking"].iloc[0]) if "Ranking" in df_filtrado.columns else "-"
        pop_val = str(df_filtrado["População"].iloc[0]) if "População" in df_filtrado.columns else "-"
        rcl_val = df_filtrado["RCL"].iloc[0] if "RCL" in df_filtrado.columns else "-"
        receita_per_capita_val = df_filtrado["Receita per capita"].iloc[0] if "Receita per capita" in df_filtrado.columns else "-"
        decil_val = str(df_filtrado["Decil"].iloc[0]) if "Decil" in df_filtrado.columns else "-"
    else:
        porte_val, ranking_val, pop_val, rcl_val, receita_per_capita_val, decil_val = "-", "-", "-", "-", "-", "-"
else:
    df_filtrado = pd.DataFrame()
    porte_val = porte_sel if porte_sel != "-" else "-"
    ranking_val, pop_val, rcl_val, receita_per_capita_val, decil_val = "-", "-", "-", "-", "-"

with f_col4:
    st.markdown('<div class="badge-filter">Classificação</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-auto-box">{ranking_val}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. SIMULADOR E CALCULADORA
# -----------------------------------------------------------------------------
has_data = not df_filtrado.empty

if has_data:
    st.markdown("<hr style='margin: 1rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

    situacao_municipio = str(df_filtrado["Situação"].iloc[0]).strip() if "Situação" in df_filtrado.columns else "Filiado"
    eh_filiado = "filiado" in situacao_municipio.lower() and "não" not in situacao_municipio.lower()
    status_color = "🟢" if eh_filiado else "🔴"

    st.markdown(f'<div style="margin-bottom: 0.6rem; font-size: 1.4rem; font-weight: 800; color: #FFFFFF;">Painel de Simulação — {mun_sel} <span class="badge-light">{status_color}({situacao_municipio})</span></div>', unsafe_allow_html=True)

    val_integral, val_d10, val_d25, val_d50 = obter_valores_validados(df_filtrado)

    if eh_filiado:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="sim-card" style="border-left: 4px solid #1E3A8A;"><div class="sim-title" style="color: #4A5568;">VALOR INTEGRAL</div><div class="sim-value">R$ {fmt_br(val_integral)}</div><div class="sim-sub"></div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="sim-card" style="border-left: 4px solid #2563EB;"><div class="sim-title" style="color: #2563EB;">DESCONTO 10%</div><div class="sim-value">R$ {fmt_br(val_d10)}</div><div class="sim-sub"></div></div>', unsafe_allow_html=True)
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="sim-card" style="border-left: 4px solid #1E3A8A;"><div class="sim-title" style="color: #4A5568;">VALOR INTEGRAL</div><div class="sim-value">R$ {fmt_br(val_integral)}</div><div class="sim-sub"></div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="sim-card" style="border-left: 4px solid #2563EB;"><div class="sim-title" style="color: #2563EB;">DESCONTO 10%</div><div class="sim-value">R$ {fmt_br(val_d10)}</div><div class="sim-sub"></div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="sim-card" style="border-left: 4px solid #7C3AED;"><div class="sim-title" style="color: #7C3AED;">DESCONTO 25%</div><div class="sim-value">R$ {fmt_br(val_d25)}</div><div class="sim-sub">Para novo filiado</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="sim-card" style="border-left: 4px solid #10B981;"><div class="sim-title" style="color: #10B981;">DESCONTO 50%</div><div class="sim-value">R$ {fmt_br(val_d50)}</div><div class="sim-sub">Para novo filiado</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="badge-main">⚙️ Calculadora de parcelamento</div>', unsafe_allow_html=True)

    calc_col1, calc_col2 = st.columns(2)

    with calc_col1:
        st.markdown('<div class="badge-filter">1. Escolha o cenário de valor base:</div>', unsafe_allow_html=True)
        opcoes_cenario = ["Desconto 10%", "Valor Integral"] if eh_filiado else ["Desconto 10%", "Desconto 25%", "Desconto 50%", "Valor Integral"]
        cenario = st.selectbox("", opcoes_cenario, key="cenario_calc", label_visibility="collapsed")

    opcoes_parcelas = list(range(1, 11)) if cenario in ["Desconto 25%", "Desconto 50%"] else list(range(1, 13))

    with calc_col2:
        st.markdown('<div class="badge-filter">2. Escolha o número de parcelas desejado:</div>', unsafe_allow_html=True)
        num_parcelas = st.selectbox("", opcoes_parcelas, index=len(opcoes_parcelas) - 1, format_func=lambda x: f"{x}x", key="num_parcelas_calc", label_visibility="collapsed")

    valor_negociado = val_d10 if cenario == "Desconto 10%" else (val_d25 if cenario == "Desconto 25%" else (val_d50 if cenario == "Desconto 50%" else val_integral))
    economia = val_integral - valor_negociado
    valor_parcela = valor_negociado / num_parcelas if num_parcelas > 0 else 0.0

    res1, res2, res3 = st.columns(3)
    with res1:
        st.markdown(f'<div class="res-card-dark"><div class="res-title">VALOR DE CADA PARCELA</div><div class="res-val">R$ {fmt_br(valor_parcela)}</div><div class="res-sub">Plano em {num_parcelas} parcelas mensais</div></div>', unsafe_allow_html=True)
    with res2:
        sub_cenario = f"Cenário: {cenario} (Novo Filiado)" if cenario in ["Desconto 25%", "Desconto 50%"] else f"Cenário: {cenario}"
        st.markdown(f'<div class="res-card-blue"><div class="res-title">VALOR TOTAL DA NEGOCIAÇÃO</div><div class="res-val">R$ {fmt_br(valor_negociado)}</div><div class="res-sub">{sub_cenario}</div></div>', unsafe_allow_html=True)
    with res3:
        st.markdown(f'<div class="res-card-green"><div class="res-title">DESCONTO PARA O MUNICÍPIO</div><div class="res-val">R$ {fmt_br(economia)}</div><div class="res-sub">Em relação ao valor integral de R$ {fmt_br(val_integral)}</div></div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # 10. SEÇÃO DE EXPLICAÇÃO DO CÁLCULO E TABELA
    # -----------------------------------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="badge-main">📘 Memória de Cálculo</div>', unsafe_allow_html=True)

    pop_fmt = formatar_inteiro_ptbr(pop_val)
    rcl_fmt = f"R$ {fmt_br(rcl_val)}" if isinstance(rcl_val, (int, float)) and rcl_val > 0 else str(rcl_val)
    receita_per_capita_fmt = f"R$ {fmt_br(receita_per_capita_val)}" if isinstance(receita_per_capita_val, (int, float)) else str(receita_per_capita_val)
    grupo_rclpc_val = obter_grupo_rclpc(receita_per_capita_val) if isinstance(receita_per_capita_val, (int, float)) else "-"
    rcl_descritiva = formatar_bilhoes_milhoes(rcl_val)

    # Geração da tabela em HTML para visualização em tela
    linhas_tabela_html = ""
    for r in DADOS_TABELA_FNP:
        linhas_tabela_html += f"""
        <tr>
            <td><b>{r['Faixa']}</b></td>
            <td>{r['De']}</td>
            <td>{r['Ate']}</td>
            <td>{r['D1']}</td>
            <td>{r['D2']}</td>
            <td>{r['D3']}</td>
            <td>{r['D4']}</td>
            <td>{r['D5']}</td>
            <td>{r['D6']}</td>
            <td>{r['D7']}</td>
            <td>{r['D8']}</td>
            <td>{r['D9']}</td>
            <td>{r['D10']}</td>
        </tr>
        """

    st.markdown(f"""
    <div class="explicacao-card">
        <h3 style="margin-top: 0; color: #0A3663;">{mun_sel}/{uf_sel}</h3>
        <p><b>Dados do município:</b></p>
        <ul>
            <li><b>População (IBGE):</b> {pop_fmt} habitantes</li>
            <li><b>RCL 2025:</b> {rcl_fmt}</li>
            <li><b>RCL per capita:</b> {receita_per_capita_fmt}</li>
            <li><b>Grupo de RCLpc:</b> Decil {grupo_rclpc_val}</li>
        </ul>
        <p><b>Metodologia</b><br>
        O valor da contribuição é definido a partir do cruzamento de dois indicadores:</p>
        <ul>
            <li><b>RCL:</b> determina a faixa de receita do município na tabela;</li>
            <li><b>RCL per capita (RCL ÷ população):</b> determina o grupo de RCLpc.</li>
        </ul>
        <p><b>Para {mun_sel}:</b><br>
        {rcl_fmt} ÷ {pop_fmt} = {receita_per_capita_fmt} de RCL per capita<br>
        Com a RCL de {rcl_descritiva} e a RCLpc de {receita_per_capita_fmt} (Decil {grupo_rclpc_val}), o município é enquadrado na tabela da FNP.</p>
        <p style="font-size: 1.1rem; font-weight: bold; color: #0A3663; margin-top: 10px;">
            Contribuição Anual Integral 2027: R$ {fmt_br(val_integral)}
        </p>
        <hr style="margin: 15px 0; border: 0; border-top: 1px solid #CBD5E0;">
        <h4 style="color: #0A3663; margin-bottom: 5px;">TABELA DE CONTRIBUIÇÃO FNP 2027: Valor Anual das Contribuições em R$</h4>
        <p style="font-size: 0.8rem; color: #64748B;">Apuracão (R$) com base no cruzamento entre RCL e RCLpc 2025</p>
        <div class="tabela-fnp-container">
            <table class="tabela-fnp">
                <thead>
                    <tr>
                        <th>Faixas de RCL (2025)</th>
                        <th>De</th>
                        <th>Até</th>
                        <th>1 (10% com menor RCL pc)</th>
                        <th>2</th>
                        <th>3</th>
                        <th>4</th>
                        <th>5</th>
                        <th>6</th>
                        <th>7</th>
                        <th>8</th>
                        <th>9</th>
                        <th>10 (10% com maior RCL pc)</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas_tabela_html}
                </tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # 11. PREPARAÇÃO DOS BOTÕES DE DOWNLOAD DO PDF
    # -----------------------------------------------------------------------------
    pdf_bytes_topo = gerar_pdf_simulacao(
        municipio=mun_sel,
        uf=uf_sel,
        porte=porte_val,
        cenario=cenario,
        parcelas=num_parcelas,
        val_integral=val_integral,
        valor_total=valor_negociado,
        valor_parcela=valor_parcela,
        economia=economia
    )

    pdf_placeholder.download_button("📄 PDF Simulação", data=pdf_bytes_topo, file_name=f"simulacao_{mun_sel}.pdf", mime="application/pdf", use_container_width=True)

    pdf_memoria_bytes = gerar_pdf_memoria_calculo(
        uf=uf_sel,
        municipio=mun_sel,
        populacao=pop_val,
        rcl=rcl_val,
        receita_per_capita=receita_per_capita_val,
        grupo_rclpc=grupo_rclpc_val,
        val_contribuicao=val_integral
    )

    pdf_memoria_placeholder.download_button("📊 Memória de Cálculo", data=pdf_memoria_bytes, file_name=f"memoria_calculo_{mun_sel}.pdf", mime="application/pdf", use_container_width=True)
else:
    pdf_placeholder.button("📄 PDF Simulação", disabled=True, use_container_width=True)
    pdf_memoria_placeholder.button("📊 Memória de Cálculo", disabled=True, use_container_width=True)
