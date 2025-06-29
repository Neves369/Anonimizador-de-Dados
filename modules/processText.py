import re
import os
import fitz 


# Verificação simples de CPF e Telefone
def simple_find(filename):
    caminho_arquivo = os.path.join('data', filename)
    nome_arquivo, ext = os.path.splitext(filename)
    caminho_saida = os.path.join('output', f"{nome_arquivo}_tarjado{ext}")

    doc = fitz.open(caminho_arquivo)

    padroes = [
        (r'\d{3}\.\d{3}\.\d{3}-\d{2}', "XXX.XXX.XXX-XX"),  # CPF
        (r'\d{2}\.\d{3}\.\d{3}-\d{1}', "XX.XXX.XXX-X"),  # RG
        (r'\(\d{2}\)\s?\d{4,5}-\d{4}', "(XX) XXXXX-XXXX"), # Telefone
    ]

    for pagina in doc:
        texto_pagina = pagina.get_text()
        for padrao, texto_substituto in padroes:
            for match in re.findall(padrao, texto_pagina):
                areas = pagina.search_for(match)
                for area in areas:
                    # Aplica a tarja e substitui o texto por texto genérico
                    pagina.add_redact_annot(area, fill=(0, 0, 0), text=texto_substituto)
        pagina.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    doc.save(caminho_saida)
    print(f"Novo arquivo gerado: {caminho_saida}")

# Função principal para processar o texto do PDF
def process_text(filename):
    simple_find(filename)

