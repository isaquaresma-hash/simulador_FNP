# --- FILTROS (ALINHAMENTO PERFEITO) ---
st.markdown(
    '<div class="badge-dark">🔍 Consulta e Filtros</div>',
    unsafe_allow_html=True,
)

f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 0.8, 3, 1.2])

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
  st.markdown(
      '<div style="text-align: center;"><span class="badge-dark"'
      ' style="margin-bottom: 6px;">Ranking</span></div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      f"""
        <div style="background-color: #FFFFFF; color: #1A202C; font-weight: 800; text-align: center; padding: 10px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); font-size: 0.95rem; line-height: 1;">
            {df_final['Ranking']}%
        </div>
    """,
      unsafe_allow_html=True,
  )
