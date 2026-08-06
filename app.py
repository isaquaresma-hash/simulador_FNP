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
        /* Reduzido o padding superior para a logo da imagem de fundo subir visualmente */
        .block-container {{ padding-top: 40px !important; padding-bottom: 2rem !important; }}
        #MainMenu, footer, header {{ visibility: hidden; }}

        .page-title {{
            color: #0A3663;
            font-size: 1.35rem;
            font-weight: 800;
            margin-top: 0.5rem; /* Ajuste para acompanhar o topo mais alto */
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
