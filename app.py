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
            df = pd.read_csv(caminho_encontrado, dtype=str)
        else:
            df = pd.read_excel(caminho_encontrado, engine="openpyxl", dtype=str)
    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")
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
        elif any(k in col_upper for k in ["RANKING", "RANK", "CLASSIFICAÇÃO", "CLASSIFICACAO", "POSIÇÃO"]):
            mapeamento[col] = "Ranking"
        elif "10%" in col_upper and "Valor_D10" not in mapeamento.values():
            mapeamento[col] = "Valor_D10"
        elif ("50%" in col_upper or "60%" in col_upper) and "Valor_D50" not in mapeamento.values():
            mapeamento[col] = "Valor_D50"
        elif "25%" in col_upper and "Valor_D25" not in mapeamento.values():
            mapeamento[col] = "Valor_D25"
        elif ("CONTRIBUIÇÃO" in col_upper or "INTEGRAL" in col_upper) and "Valor_Integral" not in mapeamento.values():
            mapeamento[col] = "Valor_Integral"

    df = df.rename(columns=mapeamento)
    df = df.loc[:, ~df.columns.duplicated()]

    if "Ranking" in df.columns:
        df["Ranking"] = [formatar_ranking(v) for v in df["Ranking"]]

    for col in ["Valor_Integral", "Valor_D10", "Valor_D25", "Valor_D50"]:
        if col in df.columns:
            df[col] = [converter_valor_ptbr(v) for v in df[col]]
        else:
            df[col] = 0.0

    return df


df_base = carregar_dados()

# -----------------------------------------------------------------------------
# 3. ESTILOS CSS E DETECÇÃO DE IMAGEM DE FUNDO
# -----------------------------------------------------------------------------
def set_bg_hack():
    bin_str = None
    mime_type = "image/png"
    
    for f in os.listdir("."):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
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
        .badge-filter {{ background-color: #475569; color: #FFFFFF !important; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 0.9rem; display: inline-block; margin-bottom: 6px; }}
        .badge-light {{ background-color: #FFFFFF; color: #1A202C !important; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.95rem; vertical-align: middle; display: inline-flex; align-items: center; justify-content: center; }}
        
        .stSelectbox div[data-baseweb="select"] > div {{ background-color: #F1F5F9 !important; color: #0F172A !important; border-radius: 6px !important; border: none !important; min-height: 34px !important; height: 34px !important; }}
        .info-auto-box {{ background-color: #FFFFFF; color: #0F172A; font-weight: 800; text-align: center; height: 34px; display: flex; align-items: center; justify-content: center; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); font-size: 0.82rem; }}
        
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

        .stButton button, .stDownloadButton button {{ background-color: #FFFFFF !important; color: #2D3748 !important; border: 1px solid #CBD5E0 !important; border-radius: 6px !important; font-size: 0.75rem !important; font-weight: 600 !important; padding: 0.2rem 0.6rem !important; min-height: 34px !important; }}
        </style>
        """
    st.markdown(page_bg_img, unsafe_allow_html=True)


set_bg_hack()


def fmt_br(valor):
    return f"{valor:,.0f}".replace(",", ".")

# -----------------------------------------------------------------------------
# 4. REGRAS DE NEGÓCIO
# -----------------------------------------------------------------------------
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
# 5. GERADOR DE PDF
# -----------------------------------------------------------------------------
class PDF(FPDF):
    def header(self):
        self.set_fill_color(10, 54, 99)
        self.rect(0, 0, 210, 32, "F")
        self.set_y(10)
        self.set_font("Arial", "B", 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "FNP - SIMULADOR DE CONTRIBUIÇÃO E PARCELAMENTO", 0, 1, "C")
        self.set_y(40)


def gerar_pdf_simulacao(municipio, uf, porte, ranking, situacao, cenario, parcelas, val_integral, valor_total, valor_parcela, economia):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 8, f"RELATÓRIO DE SIMULAÇÃO - {municipio.upper()} ({uf})", 0, 1, "L")

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 6, f"Porte: {porte}   |   Ranking: {ranking}   |   Situação: {situacao}", 0, 1, "L")

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

    dados = [
        ("Cenário Selecionado:", f"{cenario}"),
        ("Número de Parcelas:", f"{parcelas}x"),
        ("Valor Integral (Sem Desconto):", f"R$ {fmt_br(val_integral)}"),
        ("Valor Total da Negociação:", f"R$ {fmt_br(valor_total)}"),
        ("Valor de Cada Parcela Mensal:", f"R$ {fmt_br(valor_parcela)}"),
        ("Economia Gerada para o Município:", f"R$ {fmt_br(economia)}"),
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

# -----------------------------------------------------------------------------
# 6. CABEÇALHO E TOP CARDS
# -----------------------------------------------------------------------------
header_title_col, header_actions_col = st.columns([5.5, 4.5])

with header_title_col:
    st.markdown('<div class="page-title">Simulador de Contribuição e Parcelamento</div>', unsafe_allow_html=True)

with header_actions_col:
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        pdf_placeholder = st.empty()

    with b_col2:
        if st.button("🔄 Atualização Base", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

m_col1, m_col2 = st.columns(2)
with m_col1:
    st.markdown('<div class="top-card"><div class="icon-circle" style="background-color: #1E40AF;">🏛️</div><div><div class="top-card-title">CAPITAIS</div><div class="top-card-value">27</div><div class="top-card-sub">Quantidade de capitais no Brasil</div></div></div>', unsafe_allow_html=True)
with m_col2:
    st.markdown('<div class="top-card"><div class="icon-circle" style="background-color: #059669;">👥</div><div><div class="top-card-title">MUNICÍPIOS ACIMA DE 80 MIL HABITANTES</div><div class="top-card-value">435</div><div class="top-card-sub">Municípios recorte FNP</div></div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 7. FILTROS AUTOMÁTICOS (UF -> MUNICÍPIO -> PORTE AUTOMÁTICO)
# -----------------------------------------------------------------------------
st.markdown('<div class="badge-main">🔍 Consulta e Filtros</div>', unsafe_allow_html=True)
f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 3.5, 2.5, 2.5])

# 1. Escolhe a UF
uf_opcoes = ["-"] + sorted(df_base["UF"].dropna().unique().tolist()) if "UF" in df_base.columns else ["-"]
with f_col1:
    st.markdown('<div class="badge-filter">UF</div>', unsafe_allow_html=True)
    uf_sel = st.selectbox("", uf_opcoes, key="uf_sel", label_visibility="collapsed")

# 2. Carrega Municípios da UF escolhida
if uf_sel != "-":
    df_uf = df_base[df_base["UF"] == uf_sel]
    mun_opcoes = ["-"] + sorted(df_uf["Município"].dropna().unique().tolist())
else:
    mun_opcoes = ["-"]

with f_col2:
    st.markdown('<div class="badge-filter">Município</div>', unsafe_allow_html=True)
    mun_sel = st.selectbox("", mun_opcoes, key="mun_sel", label_visibility="collapsed")

# 3. Busca automática de Porte e Ranking do Município
if mun_sel != "-" and uf_sel != "-":
    df_filtrado = df_base[(df_base["UF"] == uf_sel) & (df_base["Município"] == mun_sel)]
    porte_val = df_filtrado["Porte"].iloc[0] if "Porte" in df_filtrado.columns and not df_filtrado.empty else "-"
    ranking_val = df_filtrado["Ranking"].iloc[0] if "Ranking" in df_filtrado.columns and not df_filtrado.empty else "-"
else:
    df_filtrado = pd.DataFrame()
    porte_val = "-"
    ranking_val = "-"

# 4. Exibe o Porte carregado automaticamente
with f_col3:
    st.markdown('<div class="badge-filter">Porte</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-auto-box">{porte_val}</div>', unsafe_allow_html=True)

# 5. Exibe a Classificação/Ranking carregada automaticamente
with f_col4:
    st.markdown('<div class="badge-filter">Classificação</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-auto-box">{ranking_val}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. SIMULADOR E CALCULADORA
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
            st.markdown(f'<div class="sim-card" style="border-left: 4px solid #1E3A8A;"><div class="sim-title" style="color: #4A5568;">VALOR INTEGRAL</div><div class="sim-value">R$ {fmt_br(val_integral)}</div><div class="sim-sub">Sem Desconto</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="sim-card" style="border-left: 4px solid #2563EB;"><div class="sim-title" style="color: #2563EB;">DESCONTO 10%</div><div class="sim-value">R$ {fmt_br(val_d10)}</div><div class="sim-sub"></div></div>', unsafe_allow_html=True)
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="sim-card" style="border-left: 4px solid #1E3A8A;"><div class="sim-title" style="color: #4A5568;">VALOR INTEGRAL</div><div class="sim-value">R$ {fmt_br(val_integral)}</div><div class="sim-sub">Sem Desconto</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="sim-card" style="border-left: 4px solid #2563EB;"><div class="sim-title" style="color: #2563EB;">DESCONTO 10%</div><div class="sim-value">R$ {fmt_br(val_d10)}</div><div class="sim-sub"></div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="sim-card" style="border-left: 4px solid #7C3AED;"><div class="sim-title" style="color: #7C3AED;">DESCONTO 25%</div><div class="sim-value">R$ {fmt_br(val_d25)}</div><div class="sim-sub"></div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="sim-card" style="border-left: 4px solid #10B981;"><div class="sim-title" style="color: #10B981;">DESCONTO 50%</div><div class="sim-value">R$ {fmt_br(val_d50)}</div><div class="sim-sub"></div></div>', unsafe_allow_html=True)

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
        st.markdown(f'<div class="res-card-blue"><div class="res-title">VALOR TOTAL DA NEGOCIAÇÃO</div><div class="res-val">R$ {fmt_br(valor_negociado)}</div><div class="res-sub">Cenário: {cenario}</div></div>', unsafe_allow_html=True)
    with res3:
        st.markdown(f'<div class="res-card-green"><div class="res-title">ECONOMIA PARA O MUNICÍPIO</div><div class="res-val">R$ {fmt_br(economia)}</div><div class="res-sub">Em relação ao valor integral de R$ {fmt_br(val_integral)}</div></div>', unsafe_allow_html=True)

    # Gera o PDF dinâmico
    pdf_bytes_topo = gerar_pdf_simulacao(
        municipio=mun_sel,
        uf=uf_sel,
        porte=porte_val,
        ranking=ranking_val,
        situacao=situacao_municipio,
        cenario=cenario,
        parcelas=num_parcelas,
        val_integral=val_integral,
        valor_total=valor_negociado,
        valor_parcela=valor_parcela,
        economia=economia
    )

    pdf_placeholder.download_button("📄 Baixar Simulação em PDF", data=pdf_bytes_topo, file_name=f"simulacao_{mun_sel}.pdf", mime="application/pdf", use_container_width=True)
else:
    pdf_placeholder.button("📄 Baixar Simulação em PDF", disabled=True, use_container_width=True)
