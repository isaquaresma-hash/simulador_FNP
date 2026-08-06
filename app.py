# -----------------------------------------------------------------------------
# 4. GERADOR DE PDF (FORMATADO CONFORME O MODELO)
# -----------------------------------------------------------------------------
class PDF(FPDF):

  def header(self):
    # Título principal em Caixa Alta
    self.set_font("Arial", "B", 14)
    self.set_text_color(10, 54, 99)  # Cor Azul FNP (#0A3663)
    self.cell(
        0, 10, "FNP - SIMULADOR DE CONTRIBUIÇÃO E PARCELAMENTO", 0, 1, "C"
    )
    self.ln(2)

  def footer(self):
    self.set_y(-20)
    self.set_font("Arial", "I", 8)
    self.set_text_color(128, 128, 128)
    self.cell(
        0,
        5,
        "Este documento é apenas uma simulação baseada nas regras de"
        " contribuição da FNP.",
        0,
        1,
        "C",
    )
    self.cell(0, 5, f"Página {self.page_no()}", 0, 0, "C")


def gerar_pdf_simulacao(
    municipio,
    uf,
    porte,
    ranking,
    situacao,
    cenario,
    parcelas,
    val_integral,
    valor_total,
    valor_parcela,
    economia,
):
  pdf = PDF()
  pdf.add_page()

  # Subtítulo do Município
  pdf.set_font("Arial", "B", 12)
  pdf.set_text_color(15, 23, 42)
  pdf.cell(
      0, 8, f"RELATÓRIO DE SIMULAÇÃO - {municipio.upper()} ({uf})", 0, 1, "L"
  )

  # Linha de Metadados (Porte | Ranking | Situação)
  pdf.set_font("Arial", "", 10)
  pdf.set_text_color(71, 85, 105)
  pdf.cell(
      0,
      6,
      f"Porte: {porte}  |  Ranking: {ranking}  |  Situação: {situacao}",
      0,
      1,
      "L",
  )
  pdf.ln(6)

  # Seção de Detalhes
  pdf.set_font("Arial", "B", 11)
  pdf.set_text_color(10, 54, 99)
  pdf.cell(0, 8, "DETALHES DO PARCELAMENTO SELECIONADO", 0, 1, "L")
  pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha divisória
  pdf.ln(4)

  # Itens detalhados do parcelamento
  itens = [
      ("Cenário Selecionado:", f"{cenario}"),
      ("Número de Parcelas:", f"{parcelas}x"),
      ("Valor Integral (Sem Desconto):", f"R$ {fmt_br(val_integral)}"),
      ("Valor Total da Negociação:", f"R$ {fmt_br(valor_total)}"),
      ("Valor de Cada Parcela Mensal:", f"R$ {fmt_br(valor_parcela)}"),
      ("Economia Gerada para o Município:", f"R$ {fmt_br(economia)}"),
  ]

  for rotulo, valor in itens:
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, rotulo, 0, 1, "L")

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, f" | {valor}", 0, 1, "L")
    pdf.ln(2)

  with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
    temp_filename = tmp_file.name

  pdf.output(temp_filename)
  with open(temp_filename, "rb") as f:
    pdf_bytes = f.read()

  if os.path.exists(temp_filename):
    os.remove(temp_filename)
  return pdf_bytes
