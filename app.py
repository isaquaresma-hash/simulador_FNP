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

    # Se for proporcional (Desconto 50% extra / proporcional)
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
        # Padrão normal: a linha ("Mês de Início da Adesão") foi removida para
        # Desconto 10%, Desconto 25% e Valor Integral
        dados = [
            ("Cenário Selecionado:", f"{cenario_pdf}"),
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
