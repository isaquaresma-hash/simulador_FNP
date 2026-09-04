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
# 3. ESTILOS CSS - CARREGAMENTO DA IMAGEM DE FUNDO (simulador.png.jpg)
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

        .stButton button, .stDownloadButton button {{ background-color: #FFFFFF !important; color: #2D3748 !important; border: 1px solid #CBD5E0 !important; border-radius: 6px !important; font-size: 0.72rem !important; font-weight: 600 !important; padding: 0.2rem 0.3rem !important; min-height: 38px !important; text-align: center !important; }}
        </style>
        """
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
# 5. GERADOR DE PDF COM CABEÇALHO DA IMAGEM "imagem.pdf.png"
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
            
        self.set_y(8.5)   # Subiu de 11 para 8.5
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

        self.set_y(8.5)   # Subiu de 11.5 para 8.5
        self.set_x(62)
        self.set_font("Arial", "B", 13)
        self.set_text_color(255, 255, 255)
        self.cell(138, 10, txt_pdf("MEMÓRIA DE CÁLCULO DE CONTRIBUIÇÃO"), 0, 1, "L")
        self.set_y(40)


def gerar_pdf_simulacao(municipio, uf, porte, cenario, parcelas, val_integral, valor_total, valor_parcela, economia):
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

    meses_nomes = ["Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    if parcelas == 1:
        vencimento_txt = "Março de 2027"
    else:
        mes_final = meses_nomes[min(parcelas - 1, len(meses_nomes) - 1)]
        vencimento_txt = f"Março a {mes_final} de 2027"

    dados = [
        ("Cenário Selecionado:", f"{cenario_pdf}"),
        ("Número de Parcelas:", f"{parcelas}x"),
        ("Mês Inicial / Vencimento:", f"{vencimento_txt}"),
        ("Valor Integral:", f"R$ {fmt_br(val_integral)}"),
        ("Valor Total da Negociação:", f"R$ {fmt_br(valor_total)}"),
        ("Valor de Cada Parcela Mensal:", f"R$ {fmt_br(valor_parcela)}"),
        ("Desconto para o Município:", f"R$ {fmt_br(economia)}"),
    ]

    col_w1, col_w2, row_height = 95, 95, 9
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

    pdf.cell(0, 5, txt_pdf(f"- RCL: determina a faixa de receita do município na tabela;"), 0, 1, "L")
    pdf.cell(0, 5, txt_pdf(f"- RCL per capita (RCL / população): determina o grupo de RCLpc."), 0, 1, "L")

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

df_filtrado = pd.DataFrame()
has_data = False

if st.session_state.mun_sel != "-" and st.session_state.uf_sel != "-":
    df_filtrado = df_base[(df_base["UF"] == st.session_state.uf_sel) & (df_base["Município"] == st.session_state.mun_sel)]
    has_data = not df_filtrado.empty

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
        
        valor_negociado_h = val_d10_h if cenario_h == "Desconto 10%" else (val_d25_h if cenario_h == "Desconto 25%" else (val_d50_h if cenario_h == "Desconto 50%" else val_integral_h))
        economia_h = val_integral_h - valor_negociado_h
        valor_parcela_h = valor_negociado_h / parcelas_h if parcelas_h > 0 else 0.0

        pop_val_h = str(df_filtrado["População"].iloc[0]) if "População" in df_filtrado.columns else "-"
        rcl_val_h = df_filtrado["RCL"].iloc[0] if "RCL" in df_filtrado.columns else 0.0
        receita_per_capita_val_h = df_filtrado["Receita per capita"].iloc[0] if "Receita per capita" in df_filtrado.columns else 0.0
        grupo_rclpc_val_h = obter_grupo_rclpc(receita_per_capita_val_h) if isinstance(receita_per_capita_val_h, (int, float)) else "-"

        pdf_bytes_topo = gerar_pdf_simulacao(
            municipio=st.session_state.mun_sel,
            uf=st.session_state.uf_sel,
            porte=str(df_filtrado["Porte"].iloc[0]) if "Porte" in df_filtrado.columns else "-",
            cenario=cenario_h,
            parcelas=parcelas_h,
            val_integral=val_integral_h,
            valor_total=valor_negociado_h,
            valor_parcela=valor_parcela_h,
            economia=economia_h
        )

        pdf_memoria_bytes = gerar_pdf_memoria_calculo(
            uf=st.session_state.uf_sel,
            municipio=st.session_state.mun_sel,
            populacao=pop_val_h,
            rcl=rcl_val_h,
            receita_per_capita=receita_per_capita_val_h,
            grupo_rclpc=grupo_rclpc_val_h,
            val_contribuicao=val_integral_h
        )

        with b_col1:
            st.download_button("📄 PDF Simulação", data=pdf_bytes_topo, file_name=f"simulacao_{st.session_state.mun_sel}.pdf", mime="application/pdf", use_container_width=True)

        with b_col2:
            st.download_button("📊 Memória de Cálculo", data=pdf_memoria_bytes, file_name=f"memoria_calculo_{st.session_state.mun_sel}.pdf", mime="application/pdf", use_container_width=True)
    else:
        with b_col1:
            st.button("📄 PDF Simulação", disabled=True, use_container_width=True)
        with b_col2:
            st.button("📊 Memória de Cálculo", disabled=True, use_container_width=True)

    with b_col3:
        if st.button("🔄 Atualizar Base", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

# -----------------------------------------------------------------------------
# 8. TOP CARDS
# -----------------------------------------------------------------------------
m_col1, m_col2 = st.columns(2)
with m_col1:
    st.markdown('<div class="top-card"><div class="icon-circle" style="background-color: #1E40AF;">🏛️</div><div><div class="top-card-title">CAPITAIS</div><div class="top-card-value">27</div><div class="top-card-sub">Quantidade de capitais no Brasil</div></div></div>', unsafe_allow_html=True)
with m_col2:
    st.markdown('<div class="top-card"><div class="icon-circle" style="background-color: #059669;">👥</div><div><div class="top-card-title">MUNICÍPIOS ACIMA DE 80 MIL HABITANTES</div><div class="top-card-value">435</div><div class="top-card-sub">Municípios recorte FNP</div></div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. FILTROS INTEGRADOS
# -----------------------------------------------------------------------------
st.markdown('<div class="badge-main">🔍 Consulta e Filtros</div>', unsafe_allow_html=True)

f_col1, f_col2, f_col3, f_col4 = st.columns([2.5, 1.2, 3.8, 2.5])

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

if has_data:
    porte_val = str(df_filtrado["Porte"].iloc[0]) if "Porte" in df_filtrado.columns else "-"
    ranking_val = str(df_filtrado["Ranking"].iloc[0]) if "Ranking" in df_filtrado.columns else "-"
    pop_val = str(df_filtrado["População"].iloc[0]) if "População" in df_filtrado.columns else "-"
    rcl_val = df_filtrado["RCL"].iloc[0] if "RCL" in df_filtrado.columns else "-"
    receita_per_capita_val = df_filtrado["Receita per capita"].iloc[0] if "Receita per capita" in df_filtrado.columns else "-"
    decil_val = str(df_filtrado["Decil"].iloc[0]) if "Decil" in df_filtrado.columns else "-"
else:
    porte_val = porte_sel if porte_sel != "-" else "-"
    ranking_val, pop_val, rcl_val, receita_per_capita_val, decil_val = "-", "-", "-", "-", "-"

with f_col4:
    st.markdown('<div class="badge-filter">Classificação</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-auto-box">{ranking_val}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 10. PAINEL DE SIMULAÇÃO E CALCULADORA
# -----------------------------------------------------------------------------
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
        num_parcelas_atual = st.session_state.get("num_parcelas_calc", len(opcoes_parcelas))
        idx_parcela = opcoes_parcelas.index(num_parcelas_atual) if num_parcelas_atual in opcoes_parcelas else (len(opcoes_parcelas) - 1)
        num_parcelas = st.selectbox("", opcoes_parcelas, index=idx_parcela, format_func=lambda x: f"{x}x", key="num_parcelas_calc", label_visibility="collapsed")

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
