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
    # Substituído '•' por '-' para evitar a interrogação no FPDF
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

    # Substituído '•' por '-' para evitar a interrogação no FPDF
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
