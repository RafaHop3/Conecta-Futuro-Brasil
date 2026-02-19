from fpdf import FPDF

def gerar_certificado(nome_aluno, nome_curso):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 24)
    pdf.cell(190, 40, "CERTIFICADO DE CONCLUSAO", ln=True, align="C")
    pdf.set_font("Arial", "", 16)
    pdf.cell(190, 20, f"O Protocolo Conecta Futuro Brasil confere a:", ln=True, align="C")
    pdf.set_font("Arial", "B", 20)
    pdf.cell(190, 20, nome_aluno.upper(), ln=True, align="C")
    pdf.set_font("Arial", "", 16)
    pdf.multi_cell(190, 10, f"A especializacao em {nome_curso}\nvalidada pelo ecossistema MoneyLayer 2.0.", align="C")
    
    file_name = f"Certificado_{nome_aluno.replace(' ', '_')}.pdf"
    pdf.output(file_name)
    return file_name

print(f" > [SUCESSO]: {gerar_certificado('Rafael Machado Gomes Machado', 'Cyber Safety Senior')}")
