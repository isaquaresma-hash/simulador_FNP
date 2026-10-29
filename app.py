import base64
import os
import tempfile
import pandas as pd
import streamlit as st
from fpdf import FPDF

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Simulador FNP 2027",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp { background-color: #0A3663; }
.block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
#MainMenu, footer, header { visibility: hidden; }
.page-title { color: #FFFFFF; font-size: 1.8rem; font-weight: 800; margin-bottom: 1rem; }
.badge-main { background-color: #334155; color: #FFFFFF !important; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 0.95rem; display: inline-block; margin-bottom: 8px; }
.badge-filter { background-color: #475569; color: #FFFFFF !important; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 0.85rem; display: block; margin-bottom: 6px; text-align: left; }
.badge-light { background-color: #FFFFFF; color: #1A202C !important; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.95rem; vertical-align: middle; display: inline-flex; align-items: center; justify-content: center; }
.stSelectbox div[data-baseweb="select"] > div { background-color: #F1F5F9 !important; color: #0F172A !important; border-radius: 6px !important; border: none !important; min-height: 38px !important; height: 38px !important; }
.info-auto-box { background-color: #F1F5F9; color: #0F172A; font-weight: 800; text-align: center; height: 38px; min-height: 38px; display: flex; align-items: center; justify-content: center; border-radius: 6px; font-size: 0.88rem; }
.top-card { background-color: #FFFFFF; padding: 6px 12px; border-radius: 8px; display: flex; align-items: center; gap: 10px; height: 60px; }
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
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CARREGAMENTO DE DADOS E CONVERSÕES
# -----------------------------------------------------------------------------
def converter_valor_ptbr(valor):
    try:
        if valor is None or pd.isna(valor):
            return 0.0
        if isinstance(valor, (int, float)):
            return float(valor)
        val_str = str(valor).strip().replace("R$", "").replace(" ", "")
        if "," in val_str:
            val_str = val_str.replace(".", "").replace(",", ".")
        return float(val_str)
    except Exception:
        return 0.0

def formatar_inteiro_ptbr(valor):
    if pd.isna(valor) or str(valor).strip().lower() in ["nan", "none", "", "-"]:
        return "-"
    try:
        val_num = int(float(str(valor).replace("R$", "").replace(".", "").replace(",", ".").strip()))
        return f"{val_num:,}".replace(",", ".")
    except Exception:
        return str(valor)

def formatar_ranking(valor):
    if pd.isna(valor) or str(valor).strip().lower() in ["nan", "none", "", "-"]:
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
        return f"R$ {valor / 1_000_000_000:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".") + " bilhões"
    elif valor >= 1_000_000:
        return f"R$ {valor / 1_000_000:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " milhões"
    return f"R$ {fmt_br(valor)}"

@st.cache_data
def carregar_dados():
    caminho = None
    for f in os.listdir("."):
        if f.endswith(".xlsx") or f.endswith(".csv"):
            caminho = f
            break
    if not caminho:
        st.error("Nenhum arquivo de dados (.xlsx/.csv) foi encontrado!")
        st.stop()
    try:
        if caminho.endswith(".csv"):
            df = pd.read_csv(caminho, header=2, dtype=str)
        else:
            df = pd.read_excel(caminho, header=2, engine="openpyxl", dtype=str)
    except Exception as e:
        st.error(f"Erro ao carregar ficheiro: {e}")
        st.stop()

    cols = ["Situação", "Porte", "UF", "Município", "Ranking", "Valor_Integral", "Valor_D10", "Valor_D50", "Valor_D25", "Parcela_12x", "Parcela_D50_x", "Parcela_D25_x", "População", "RCL", "Receita per capita", "Decil"]
    renames = {df.columns[i]: cols[i] for i in range(min(len(cols), len(df.columns)))}
    df = df.rename(columns=renames).loc[:, ~df.columns.duplicated()]

    if "Município" in df.columns:
        df = df.dropna(subset=["Município"])
        df = df[df["Município"].astype(str).str.strip() != ""]
    if "Ranking" in df.columns:
        df["Ranking"] = [formatar_ranking(v) for v in df["Ranking"]]

    for col in ["Valor_Integral", "Valor_D10", "Valor_D25", "Valor_D50", "RCL", "Receita per capita"]:
        df[col] = [converter_valor_ptbr(v) for v in df[col]] if col in df.columns else 0.0

    return df

df_base = carregar_dados()

# -----------------------------------------------------------------------------
# 3. GERADOR DE PDF E AUXILIARES
# -----------------------------------------------------------------------------
def obter_grupo_rclpc(rcl_pc):
    limites = [4832.71, 5354.64, 5846.24, 6295.10, 6787.76, 7421.25, 8275.17, 8454.71, 11968.65]
    for i, lim in enumerate(limites, start=1):
        if rcl_pc <= lim:
            return i
    return 10

def obter_valores_validados(row_or_df):
    v_int = row_or_df["Valor_Integral"].sum()
    v_d10 = row_or_df["Valor_D10"].sum()
    v_d25 = row_or_df["Valor_D25"].sum()
    v_d50 = row_or_df["Valor_D50"].sum()
    v_d10 = v_int * 0.90 if v_d10 <= 0 or v_d10 >= v_int else v_d10
    v_d25 = v_int * 0.75 if v_d25 <= 0 or v_d25 >= v_int else v_d25
    v_d50 = v_int * 0.50 if v_d50 <= 0 or v_d50 >= v_int else v_d50
    return v_int, v_d10, v_d25, v_d50

def txt_pdf(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

class PDFSimulacao(FPDF):
    def header(self):
        self.set_fill_color(10, 54, 99)
        self.rect(0, 0, 210, 32, "F")
        self.set_y(10)
        self.set_font("Arial", "B", 12)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, txt_pdf("SIMULADOR DE CONTRIBUIÇÃO E PARCELAMENTO"), 0, 1, "C")
        self.set_y(40)

def gerar_pdf_simulacao(municipio, uf, porte, cenario, parcelas, val_integral, valor_total, valor_parcela, economia, mes_inicio="Janeiro", desc_50_prop=False, eh_filiado=True):
    pdf = PDFSimulacao()
    pdf.add_page()
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(10, 54, 99)
    pdf.cell(0, 8, txt_pdf(f"RELATÓRIO DE SIMULAÇÃO - {municipio.upper()} ({uf})"), 0, 1, "L")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, txt_pdf(f"Porte: {porte}"), 0, 1, "L")
    pdf.ln(5)

    eh_proporcional = (not eh_filiado) and ((mes_inicio != "Janeiro") or desc_50_prop)
    if eh_proporcional:
        prop_txt = f"Proporcional ({mes_inicio} a Dez/2027)" + (" + Desconto 50%" if desc_50_prop else "")
        dados = [
            ("Cenário Selecionado:", f"{cenario}"),
            ("Mês de Início da Adesão:", f"{mes_inicio}"),
            ("Modalidade Proporcional:", f"{prop_txt}"),
            ("Valor Integral Anual:", f"R$ {fmt_br(val_integral)}"),
            ("Valor Total da Negociação:", f"R$ {fmt_br(valor_total)}"),
            ("Desconto para o Município:", f"R$ {fmt_br(economia)}"),
        ]
    else:
        dados = [
            ("Cenário Selecionado:", f"{cenario}"),
            ("Número de Parcelas:", f"{parcelas}x"),
            ("Valor Integral Anual:", f"R$ {fmt_br(val_integral)}"),
            ("Valor Total da Negociação:", f"R$ {fmt_br(valor_total)}"),
            ("Valor de Cada Parcela Mensal:", f"R$ {fmt_br(valor_parcela)}"),
            ("Desconto para o Município:", f"R$ {fmt_br(economia)}"),
        ]

    for rotulo, valor in dados:
        pdf.cell(95, 8, txt_pdf(f" {rotulo}"), 1, 0, "L")
        pdf.cell(95, 8, txt_pdf(f" {valor}"), 1, 1, "L")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        temp_name = tmp.name
    pdf.output(temp_name)
    with open(temp_name, "rb") as f:
        bytes_data = f.read()
    if os.path.exists(temp_name):
        os.remove(temp_name)
    return bytes_data

# -----------------------------------------------------------------------------
# 4. GESTÃO DE FILTROS E SESSÃO
# -----------------------------------------------------------------------------
for key in ["porte_sel", "uf_sel", "mun_sel"]:
    if key not in st.session_state:
        st.session_state[key] = "-"

def on_porte_change():
    st.session_state.uf_sel = "-"
    st.session_state.mun_sel = "-"

def on_uf_change():
    st.session_state.mun_sel = "-"

def on_mun_change():
    mun = st.session_state.mun_sel
    if mun != "-":
        match = df_base[df_base["Município"] == mun]
        if not match.empty:
            st.session_state.uf_sel = str(match["UF"].iloc[0])
            st.session_state.porte_sel = str(match["Porte"].iloc[0])

df_filtrado = pd.DataFrame()
has_data = False
if st.session_state.mun_sel != "-":
    df_filtrado = df_base[df_base["Município"] == st.session_state.mun_sel]
    has_data = not df_filtrado.empty

MESES_ANO = [("Janeiro", 12), ("Fevereiro", 11), ("Março", 10), ("Abril", 9), ("Maio", 8), ("Junho", 7), ("Julho", 6), ("Agosto", 5), ("Setembro", 4), ("Outubro", 3), ("Novembro", 2), ("Dezembro", 1)]

# -----------------------------------------------------------------------------
# 5. CABEÇALHO E TOP CARDS
# -----------------------------------------------------------------------------
h_col1, h_col2 = st.columns([6, 4])
with h_col1:
    st.markdown('<div class="page-title">Simulador de Contribuição e Parcelamento</div>', unsafe_allow_html=True)

with h_col2:
    if has_data:
        situacao_m = str(df_filtrado["Situação"].iloc[0]).strip()
        eh_filiado_m = "filiado" in situacao_m.lower() and "não" not in situacao_m.lower()
        val_int, val_10, val_25, val_50 = obter_valores_validados(df_filtrado)
        
        cenario_m = st.session_state.get("cenario_calc", "Desconto 10%")
        parcelas_m = st.session_state.get("num_parcelas_calc", 12)
        mes_ini_m = st.session_state.get("mes_inicio_calc", "Janeiro") if not eh_filiado_m else "Janeiro"
        desc_50_m = st.session_state.get("aplicar_50_prop_sel", "Não") if not eh_filiado_m else "Não"
        
        meses_v = dict(MESES_ANO).get(mes_ini_m, 12) if not eh_filiado_m else 12
        v_base = val_10 if cenario_m == "Desconto 10%" else (val_25 if cenario_m == "Desconto 25%" else (val_50 if cenario_m == "Desconto 50%" else val_int))
        
        v_neg = (v_base / 12 * meses_v) * 0.50 if (not eh_filiado_m and desc_50_m == "Sim") else ((v_base / 12 * meses_v) if not eh_filiado_m else v_base)
        e_econ = val_int - v_neg
        v_parc = v_neg / parcelas_m if parcelas_m > 0 else 0.0

        pdf_data = gerar_pdf_simulacao(st.session_state.mun_sel, st.session_state.uf_sel, str(df_filtrado["Porte"].iloc[0]), cenario_m, parcelas_m, val_int, v_neg, v_parc, e_econ, mes_ini_m, desc_50_m == "Sim", eh_filiado_m)
        st.download_button("📄 PDF Simulação", data=pdf_data, file_name=f"simulacao_{st.session_state.mun_sel}.pdf", mime="application/pdf", use_container_width=True)

st.markdown('<div class="badge-main">🔍 Consulta e Filtros</div>', unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns([2.5, 1.2, 3.8, 2.5])

p_opts = ["-"] + sorted([str(x) for x in df_base["Porte"].dropna().unique()])
with f1:
    st.markdown('<div class="badge-filter">Porte</div>', unsafe_allow_html=True)
    st.selectbox("", p_opts, key="porte_sel", on_change=on_porte_change, label_visibility="collapsed")

u_opts = ["-"] + sorted([str(x) for x in df_base["UF"].dropna().unique()])
with f2:
    st.markdown('<div class="badge-filter">UF</div>', unsafe_allow_html=True)
    st.selectbox("", u_opts, key="uf_sel", on_change=on_uf_change, label_visibility="collapsed")

m_opts = ["-"] + sorted([str(x) for x in df_base["Município"].dropna().unique()])
with f3:
    st.markdown('<div class="badge-filter">Município</div>', unsafe_allow_html=True)
    st.selectbox("", m_opts, key="mun_sel", on_change=on_mun_change, label_visibility="collapsed")

rank_val = str(df_filtrado["Ranking"].iloc[0]) if has_data and "Ranking" in df_filtrado.columns else "-"
with f4:
    st.markdown('<div class="badge-filter">Classificação</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-auto-box">{rank_val}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. PAINEL DE SIMULAÇÃO
# -----------------------------------------------------------------------------
if has_data:
    st.markdown("<hr style='margin: 1rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
    sit = str(df_filtrado["Situação"].iloc[0]).strip()
    filiado = "filiado" in sit.lower() and "não" not in sit.lower()
    
    st.markdown(f'<div style="font-size: 1.3rem; font-weight: 800; color: #FFF;">Painel de Simulação — {st.session_state.mun_sel} <span class="badge-light">{"🟢" if filiado else "🔴"}({sit})</span></div>', unsafe_allow_html=True)

    v_int, v_10, v_25, v_50 = obter_valores_validados(df_filtrado)

    if filiado:
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="sim-card"><div class="sim-title">VALOR INTEGRAL</div><div class="sim-value">R$ {fmt_br(v_int)}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="sim-card"><div class="sim-title">DESCONTO 10%</div><div class="sim-value">R$ {fmt_br(v_10)}</div></div>', unsafe_allow_html=True)
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="sim-card"><div class="sim-title">VALOR INTEGRAL</div><div class="sim-value">R$ {fmt_br(v_int)}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="sim-card"><div class="sim-title">DESCONTO 10%</div><div class="sim-value">R$ {fmt_br(v_10)}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="sim-card"><div class="sim-title">DESCONTO 25%</div><div class="sim-value">R$ {fmt_br(v_25)}</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="sim-card"><div class="sim-title">DESCONTO 50%</div><div class="sim-value">R$ {fmt_br(v_50)}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="badge-main">⚙️ Calculadora de parcelamento</div>', unsafe_allow_html=True)

    if not filiado:
        cc1, cc2, cc3, cc4 = st.columns([2.5, 2.2, 2.5, 2.8])
        with cc1:
            st.markdown('<div class="badge-filter">1. Cenário:</div>', unsafe_allow_html=True)
            cenario = st.selectbox("", ["Desconto 10%", "Desconto 25%", "Desconto 50%", "Valor Integral"], key="cenario_calc", label_visibility="collapsed")
        
        opts_p = list(range(1, 11)) if cenario in ["Desconto 25%", "Desconto 50%"] else list(range(1, 13))
        with cc2:
            st.markdown('<div class="badge-filter">2. Parcelas:</div>', unsafe_allow_html=True)
            num_parc = st.selectbox("", opts_p, format_func=lambda x: f"{x}x", key="num_parcelas_calc", label_visibility="collapsed")
        with cc3:
            st.markdown('<div class="badge-filter">3. Mês de início:</div>', unsafe_allow_html=True)
            mes_ini = st.selectbox("", [m[0] for m in MESES_ANO], key="mes_inicio_calc", label_visibility="collapsed")
        with cc4:
            st.markdown('<div class="badge-filter">4. Desc. 50% proporcional:</div>', unsafe_allow_html=True)
            desc_50 = st.selectbox("", ["Não", "Sim"], key="aplicar_50_prop_sel", label_visibility="collapsed")
            app_50 = (desc_50 == "Sim")
    else:
        cc1, cc2 = st.columns([1, 1])
        with cc1:
            st.markdown('<div class="badge-filter">1. Cenário:</div>', unsafe_allow_html=True)
            cenario = st.selectbox("", ["Desconto 10%", "Valor Integral"], key="cenario_calc", label_visibility="collapsed")
        with cc2:
            st.markdown('<div class="badge-filter">2. Parcelas:</div>', unsafe_allow_html=True)
            num_parc = st.selectbox("", list(range(1, 13)), format_func=lambda x: f"{x}x", key="num_parcelas_calc", label_visibility="collapsed")
        mes_ini = "Janeiro"
        app_50 = False

    meses_v = dict(MESES_ANO).get(mes_ini, 12) if not filiado else 12
    v_base = v_10 if cenario == "Desconto 10%" else (v_25 if cenario == "Desconto 25%" else (v_50 if cenario == "Desconto 50%" else v_int))

    v_neg = (v_base / 12 * meses_v) * 0.50 if (not filiado and app_50) else ((v_base / 12 * meses_v) if not filiado else v_base)
    economia = v_int - v_neg
    v_parc = v_neg / num_parc if num_parc > 0 else 0.0

    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    with r1: st.markdown(f'<div class="res-card-dark"><div class="res-title">VALOR PARCELA</div><div class="res-val">R$ {fmt_br(v_parc)}</div><div class="res-sub">{num_parc} parcelas</div></div>', unsafe_allow_html=True)
    with r2: st.markdown(f'<div class="res-card-blue"><div class="res-title">VALOR TOTAL</div><div class="res-val">R$ {fmt_br(v_neg)}</div><div class="res-sub">Adesão em {mes_ini} ({meses_v} meses)</div></div>', unsafe_allow_html=True)
    with r3: st.markdown(f'<div class="res-card-green"><div class="res-title">DESCONTO MUNICÍPIO</div><div class="res-val">R$ {fmt_br(economia)}</div><div class="res-sub">Economia gerada</div></div>', unsafe_allow_html=True)
