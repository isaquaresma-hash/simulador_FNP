import streamlit as st
import pandas as pd
import re
import os
import base64
from fpdf import FPDF

# 1. Configuração Inicial da Página
st.set_page_config(
    page_title="Simulador de Contribuição e Parcelamento - FNP",
    layout="wide"
)

# 2. CAMINHO DA IMAGEM DE FUNDO
CAMINHO_IMAGEM_FUNDO = r"C:\Users\isa.quaresma\Pictures\Screenshots\simulador.png.jpeg"

def carregar_imagem_base64(caminho):
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        extensao = caminho.split(".")[-1].lower()
        mime = "image/png" if extensao in ["png"] else "image/jpeg"
        return f"data:{mime};base64,{encoded}"
    return None

img_fundo_b64 = carregar_imagem_base64(CAMINHO_IMAGEM_FUNDO)

# 3. ESTILIZAÇÃO VISUAL
if img_fundo_b64:
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("{img_fundo_b64}") !important;
            background-repeat: no-repeat !important;
            background-position: center top !important;
            background-size: cover !important;
            background-attachment: fixed !important;
            background-color: #0d233a !important;
        }}

        .stApp, .main, [data-testid="stHeader"] {{
            background-color: transparent !important;
            color: #1e293b;
        }}
        
        header, footer, #MainMenu {{ visibility: hidden; }}
        
        .block-container {{
            padding-top: 220px !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-bottom: 3rem !important;
        }}

        .app-header-title {{
            color: #002b49;
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: -0.3px;
            margin-top: 0px;
            margin-bottom: 6px;
            text-shadow: 0 2px 4px rgba(255,255,255,0.8);
        }}
        
        [data-testid="stWidgetLabel"] label, 
        [data-testid="stWidgetLabel"] p {{
            color: #ffffff !important;
            font-size: 1.05rem !important;
            font-weight: 800 !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.9) !important;
            background: rgba(0, 43, 73, 0.6) !important;
            padding: 2px 8px !important;
            border-radius: 4px !important;
            display: inline-block !important;
        }}

        .kpi-card {{
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid rgba(203, 213, 225, 0.8);
            border-radius: 10px;
            padding: 10px 14px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
            backdrop-filter: blur(6px);
        }}
        .kpi-icon-blue {{ background: #004b87; color: white; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }}
        .kpi-icon-green {{ background: #10b981; color: white; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }}
        .kpi-icon-purple {{ background: #8b5cf6; color: white; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }}
        .kpi-title {{ font-size: 0.68rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
        .kpi-value {{ font-size: 1.35rem; font-weight: 800; color: #0f172a; line-height: 1.1; }}
        .kpi-desc {{ font-size: 0.7rem; color: #64748b; margin-top: 1px; }}

        .sim-title {{
            color: #002b49;
            font-size: 1.3rem;
            font-weight: 800;
            margin-bottom: 2px;
            background: rgba(255, 255, 255, 0.95);
            padding: 6px 14px;
            border-radius: 8px;
            display: inline-block;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }}

        .filter-rank-box {{
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 0.95rem;
            font-weight: 800;
            color: #002b49;
            text-align: center;
            height: 38px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        .card-scen {{
            background: #ffffff;
            border-radius: 10px;
            padding: 10px 14px;
            border-left: 4px solid #cbd5e1;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }}
        .card-scen-full {{ border-left-color: #64748b; }}
        .card-scen-10 {{ border-left-color: #3b82f6; }}
        .card-scen-25 {{ border-left-color: #8b5cf6; }}
        .card-scen-50 {{ border-left-color: #10b981; }}
        
        .scen-tag {{ font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: #64748b; }}
        .scen-val {{ font-size: 1.15rem; font-weight: 800; color: #0f172a; margin: 2px 0; }}
        .scen-sub {{ font-size: 0.72rem; color: #475569; font-weight: 500; }}

        .res-box {{
            background: linear-gradient(135deg, #002b49 0%, #004b87 100%);
            color: #ffffff;
            border-radius: 10px;
            padding: 12px 16px;
            box-shadow: 0 6px 16px rgba(0, 43, 73, 0.15);
        }}
        .res-label {{ font-size: 0.75rem; color: #93c5fd; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }}
        .res-val {{ font-size: 1.5rem; font-weight: 900; color: #ffffff; line-height: 1.1; margin-top: 2px; }}
        .res-sub {{ font-size: 0.75rem; color: #e2e8f0; margin-top: 4px; }}

        div[data-baseweb="select"] > div {{ background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; }}
        .stButton>button, .stDownloadButton>button {{ border-radius: 8px !important; font-weight: 600 !important; }}
        </style>
    """, unsafe_allow_html=True)

# 4. CARREGAMENTO DA PLANILHA DO GOOGLE SHEETS
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1-FezkcudLwtZdPHMGPbFOJJ4ZGzxxpB1fxsWwbqQsDw/edit?gid=0#gid=0"

def obter_url_csv(url):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        doc_id = match.group(1)
        return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv"
    return url

def converter_para_int(texto):
    if pd.isna(texto) or str(texto).strip() == "":
        return 0
    val_str = str(texto).strip()
    val_limpo = re.sub(r'[^\d]', '', val_str)
    try:
        return int(val_limpo)
    except ValueError:
        return 0

def formatar_moeda(valor):
    try:
        val_int = int(round(float(valor)))
        return f"R$ {val_int:,}".replace(",", ".")
    except (ValueError, TypeError):
        return "R$ 0"

# FUNÇÃO PARA GERAR O PDF COM ACENTUAÇÃO CORRETA
def gerar_pdf_simulacao(municipio, uf, porte, rank, status_filiado, cenario, parcelas, valor_parcela, total_negociacao, economia, v_integral):
    pdf = FPDF()
    pdf.add_page()
    
    def txt(texto):
        return str(texto).encode('latin-1', 'replace').decode('latin-1')
    
    # Cabeçalho
    pdf.set_fill_color(0, 43, 73)
    pdf.rect(0, 0, 210, 35, 'F')
    
    pdf.set_font("Arial", "B", 15)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, txt("FNP - SIMULADOR DE CONTRIBUIÇÃO E PARCELAMENTO"), ln=True, align="C")
    
    pdf.ln(15)
    
    # Informações do Município
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(0, 43, 73)
    pdf.cell(0, 10, txt(f"RELATÓRIO DE SIMULAÇÃO - {municipio.upper()} ({uf})"), ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 7, txt(f"Porte: {porte}  |  Ranking: {rank}  |  Situação: {status_filiado}"), ln=True)
    
    pdf.ln(5)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Detalhes da Simulação
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(0, 43, 73)
    pdf.cell(0, 8, txt("DETALHES DO PARCELAMENTO SELECIONADO"), ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    
    pdf.cell(100, 8, txt("Cenário Selecionado:"), border=1)
    pdf.cell(90, 8, txt(f"{cenario}"), border=1, ln=True)
    
    pdf.cell(100, 8, txt("Número de Parcelas:"), border=1)
    pdf.cell(90, 8, txt(f"{parcelas}x"), border=1, ln=True)

    pdf.cell(100, 8, txt("Valor Integral (Sem Desconto):"), border=1)
    pdf.cell(90, 8, txt(f"{formatar_moeda(v_integral)}"), border=1, ln=True)
    
    pdf.cell(100, 8, txt("Valor Total da Negociação:"), border=1)
    pdf.cell(90, 8, txt(f"{formatar_moeda(total_negociacao)}"), border=1, ln=True)
    
    pdf.cell(100, 8, txt("Valor de Cada Parcela Mensal:"), border=1)
    pdf.cell(90, 8, txt(f"{formatar_moeda(valor_parcela)}"), border=1, ln=True)
    
    pdf.cell(100, 8, txt("Economia Gerada para o Município:"), border=1)
    pdf.cell(90, 8, txt(f"{formatar_moeda(economia)}"), border=1, ln=True)
    
    pdf.ln(15)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, txt("Este documento é apenas uma simulação baseada nas regras de contribuição da FNP."), align="C")

    return bytes(pdf.output())

@st.cache_data(ttl=30)
def carregar_dados():
    try:
        url_csv = obter_url_csv(URL_GOOGLE_SHEETS)
        df = pd.read_csv(url_csv, dtype=str)
        df = df.fillna("")
        df.columns = [str(col).strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a planilha: {e}")
        return None

df_dados = carregar_dados()

# Containers para gerenciamento dos botões no topo
col_top_vazio, col_btn_pdf, col_btn_top = st.columns([3.5, 1.3, 1.2])

with col_btn_top:
    if st.button("🔄 Atualização Base", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 5. TÍTULO DA APLICAÇÃO
st.markdown('<div class="app-header-title">Simulador de Contribuição e Parcelamento</div>', unsafe_allow_html=True)

# 6. CARDS DE KPI SUPERIORES
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown('<div class="kpi-card"><div class="kpi-icon-blue">🏛️</div><div><div class="kpi-title">Capitais</div><div class="kpi-value">27</div><div class="kpi-desc">Quantidade de capitais no Brasil</div></div></div>', unsafe_allow_html=True)
with k2:
    st.markdown('<div class="kpi-card"><div class="kpi-icon-green">👥</div><div><div class="kpi-title">Municípios Acima de 80 mil Habitantes</div><div class="kpi-value">1.227</div><div class="kpi-desc">Municípios com mais de 80 mil habitantes</div></div></div>', unsafe_allow_html=True)
with k3:
    st.markdown('<div class="kpi-card"><div class="kpi-icon-purple">💲</div><div><div class="kpi-title">Potencial de Arrecadação</div><div class="kpi-value">R$ 5,63 Bi</div><div class="kpi-desc">Potencial total de arrecadação anual</div></div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 7. FILTROS DE CONSULTA
if df_dados is not None:
    col_situacao = df_dados.columns[0]  # Coluna A
    col_porte = df_dados.columns[1]     # Coluna B
    col_uf = df_dados.columns[2]        # Coluna C
    col_mun = df_dados.columns[3]       # Coluna D
    col_rank = df_dados.columns[4]      # Coluna E

    portes_unicos = ["Todos"] + sorted([p.strip() for p in df_dados[col_porte].unique() if p.strip() != ""])
    ufs_unicas = ["Todas"] + sorted([u.strip() for u in df_dados[col_uf].unique() if u.strip() != ""])

    st.markdown("""
        <div style="font-weight: 800; font-size: 1.1rem; color: #ffffff; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.9); background: rgba(0, 43, 73, 0.7); padding: 4px 10px; border-radius: 6px; display: inline-block;">
            🔍 Consulta e Filtros
        </div>
    """, unsafe_allow_html=True)

    col_p, col_u, col_m, col_r = st.columns([1.2, 1, 2.8, 1])

    with col_p:
        porte_sel = st.selectbox("Porte", portes_unicos, key="select_porte")
    with col_u:
        uf_sel = st.selectbox("UF", ufs_unicas, key="select_uf")

    df_filtrado = df_dados.copy()
    if porte_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado[col_porte].str.strip() == porte_sel]
    if uf_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado[col_uf].str.strip() == uf_sel]

    muns_disponiveis = sorted([m.strip() for m in df_filtrado[col_mun].unique() if m.strip() != ""])
    lista_muns = ["Digite ou selecione um município"] + muns_disponiveis

    with col_m:
        mun_sel = st.selectbox("Município", lista_muns, key="select_mun")

    rank_exibicao = "-"
    if mun_sel != "Digite ou selecione um município":
        dados_temp = df_dados[df_dados[col_mun].str.strip() == mun_sel]
        if not dados_temp.empty:
            rank_exibicao = str(dados_temp.iloc[0][col_rank]).strip()

    with col_r:
        st.markdown('<div data-testid="stWidgetLabel"><label>Ranking</label></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="filter-rank-box">{rank_exibicao}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 8. PAINEL DE SIMULAÇÃO
    if mun_sel != "Digite ou selecione um município":
        dados_mun = df_dados[df_dados[col_mun].str.strip() == mun_sel].iloc[0]

        v_integral = converter_para_int(dados_mun.iloc[5])  # Coluna F
        v_10 = converter_para_int(dados_mun.iloc[6])        # Coluna G
        v_50 = converter_para_int(dados_mun.iloc[7])        # Coluna H
        v_25 = converter_para_int(dados_mun.iloc[8])        # Coluna I

        val_situacao = str(dados_mun[col_situacao]).strip().lower()
        eh_filiado = val_situacao in ["sim", "filiado", "s", "true", "1"]
        tag_filiado = "🟢 (Filiado)" if eh_filiado else "🔴 (Não Filiado)"

        st.markdown(f"""
            <div>
                <div class='sim-title'>Painel de Simulação — {mun_sel} &nbsp; <span style='font-size: 1rem;'>{tag_filiado}</span></div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if eh_filiado:
            sc0, sc1 = st.columns(2)
            with sc0:
                st.markdown(f"""
                    <div class="card-scen card-scen-full">
                        <div class="scen-tag">Valor Integral</div>
                        <div class="scen-val">{formatar_moeda(v_integral)}</div>
                        <div class="scen-sub">Sem Desconto</div>
                    </div>
                """, unsafe_allow_html=True)

            with sc1:
                st.markdown(f"""
                    <div class="card-scen card-scen-10">
                        <div class="scen-tag">Desconto 10%</div>
                        <div class="scen-val">{formatar_moeda(v_10)}</div>
                        <div class="scen-sub">Parcela Padrão: 12x</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            sc0, sc1, sc2, sc3 = st.columns(4)
            with sc0:
                st.markdown(f"""
                    <div class="card-scen card-scen-full">
                        <div class="scen-tag">Valor Integral</div>
                        <div class="scen-val">{formatar_moeda(v_integral)}</div>
                        <div class="scen-sub">Sem Desconto</div>
                    </div>
                """, unsafe_allow_html=True)

            with sc1:
                st.markdown(f"""
                    <div class="card-scen card-scen-10">
                        <div class="scen-tag">Desconto 10%</div>
                        <div class="scen-val">{formatar_moeda(v_10)}</div>
                        <div class="scen-sub">Parcela Padrão: 12x</div>
                    </div>
                """, unsafe_allow_html=True)

            with sc2:
                st.markdown(f"""
                    <div class="card-scen card-scen-25">
                        <div class="scen-tag">Desconto 25%</div>
                        <div class="scen-val">{formatar_moeda(v_25)}</div>
                        <div class="scen-sub">Parcela Padrão: 10x</div>
                    </div>
                """, unsafe_allow_html=True)

            with sc3:
                st.markdown(f"""
                    <div class="card-scen card-scen-50">
                        <div class="scen-tag">Desconto 50%</div>
                        <div class="scen-val">{formatar_moeda(v_50)}</div>
                        <div class="scen-sub">Parcela Padrão: 10x</div>
                    </div>
                """, unsafe_allow_html=True)

        # 9. CALCULADORA DE PARCELAMENTO
        st.markdown('<div class="sim-title" style="font-size: 1.1rem; margin-top: 15px;">⚙️ Calculadora de parcelamento</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        c_regra, c_parc = st.columns([1.2, 1])

        if eh_filiado:
            opcoes_cenario = ["Desconto 10%", "Integral (Sem Desconto)"]
        else:
            opcoes_cenario = ["Desconto 10%", "Desconto 25%", "Desconto 50%", "Integral (Sem Desconto)"]

        with c_regra:
            cenario_escolhido = st.selectbox(
                "1. Escolha o cenário de valor base:",
                opcoes_cenario,
                index=0,
                key="calc_cenario_select"
            )

        with c_parc:
            opcoes_parcelas = [f"{i}x ({i} parcelas)" for i in range(1, 25)]
            parcela_selecionada = st.selectbox(
                "2. Escolha o número de parcelas desejado:",
                opcoes_parcelas,
                index=11, # Padrão: 12x
                key="calc_parcela_select"
            )
            num_parcelas = int(parcela_selecionada.split("x")[0])

        if cenario_escolhido == "Desconto 10%":
            valor_base = v_10
        elif cenario_escolhido == "Desconto 25%":
            valor_base = v_25
        elif cenario_escolhido == "Desconto 50%":
            valor_base = v_50
        else:
            valor_base = v_integral

        valor_parcela = valor_base / num_parcelas if num_parcelas > 0 else 0
        economia = max(0, v_integral - valor_base)

        r_col1, r_col2, r_col3 = st.columns(3)

        with r_col1:
            st.markdown(f"""
                <div class="res-box">
                    <div class="res-label">Valor de Cada Parcela</div>
                    <div class="res-val">{formatar_moeda(valor_parcela)}</div>
                    <div class="res-sub">Plano em {num_parcelas} parcelas mensais</div>
                </div>
            """, unsafe_allow_html=True)

        with r_col2:
            st.markdown(f"""
                <div class="res-box" style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);">
                    <div class="res-label">Valor Total da Negociação</div>
                    <div class="res-val">{formatar_moeda(valor_base)}</div>
                    <div class="res-sub">Cenário: {cenario_escolhido}</div>
                </div>
            """, unsafe_allow_html=True)

        with r_col3:
            st.markdown(f"""
                <div class="res-box" style="background: linear-gradient(135deg, #065f46 0%, #10b981 100%);">
                    <div class="res-label">Economia para o Município</div>
                    <div class="res-val">{formatar_moeda(economia)}</div>
                    <div class="res-sub">Em relação ao valor integral de {formatar_moeda(v_integral)}</div>
                </div>
            """, unsafe_allow_html=True)

        # RENDERIZAÇÃO DO BOTÃO PDF NO TOPO
        pdf_bytes = gerar_pdf_simulacao(
            municipio=mun_sel,
            uf=str(dados_mun[col_uf]),
            porte=str(dados_mun[col_porte]),
            rank=rank_exibicao,
            status_filiado="Filiado" if eh_filiado else "Não Filiado",
            cenario=cenario_escolhido,
            parcelas=num_parcelas,
            valor_parcela=valor_parcela,
            total_negociacao=valor_base,
            economia=economia,
            v_integral=v_integral
        )

        with col_btn_pdf:
            st.download_button(
                label="📄 Baixar Simulação em PDF",
                data=pdf_bytes,
                file_name=f"Simulacao_FNP_{mun_sel.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )