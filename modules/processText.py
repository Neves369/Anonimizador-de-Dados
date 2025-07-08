import re
import os
import fitz 
import spacy

def detectar_dados(filename):
    caminho_arquivo = os.path.join("data", filename)
    doc = fitz.open(caminho_arquivo)
    nlp = spacy.load("pt_core_news_lg")

    sessoes = {
        "CPF": [],
        "RG": [],
        "OAB": [],
        "Email": [],
        "Outros": []
    }

    padroes = [
        ("CPF", r"\d{3}\.\d{3}\.\d{3}-\d{2}"),
        ("RG", r"\d{2}\.\d{3}\.\d{3}-\d{1}"),
        ("Telefone", r"\(\d{2}\)\s?\d{4,5}-\d{4}"),
        ("Email", r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b"),
        ("OAB", r"\d{3}\.\d{2}")
    ]

    for i, pagina in enumerate(doc):
        texto = pagina.get_text()
        spacy_doc = nlp(texto)

        for label, padrao in padroes:
            for match in re.findall(padrao, texto):
                for bbox in pagina.search_for(match):
                    dado = {
                        "pagina": i,
                        "texto": match,
                        "label": label,
                        "bbox": list(bbox)
                    }
                    if label in sessoes:
                        sessoes[label].append(dado)
                    else:
                        sessoes["Outros"].append(dado)

    return sessoes

def aplicar_anonimizacao(filename, dados_selecionados):
    caminho = os.path.join("data", filename)
    nome_base, ext = os.path.splitext(filename)
    caminho_saida = os.path.join("output", f"{nome_base}_customizado{ext}")

    doc = fitz.open(caminho)

    for dado in dados_selecionados:
        pagina = doc[dado["pagina"]]
        bbox = fitz.Rect(dado["bbox"])
        bbox.y0 += 5
        bbox.y1 -= 5
        pagina.add_redact_annot(bbox, fill=(0, 0, 0), text="[OCULTO]")
        # texto_substituto = f"[{dado['label']} OCULTO]"

        # pagina.add_redact_annot(
        #     bbox,
        #     fill=(1, 1, 1),
        #     text=texto_substituto,
        #     fontname="helv",
        #     fontsize=8,
        #     text_color=(0, 0, 0)
        # )

    for pagina in doc:
        pagina.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    doc.save(caminho_saida)
    return caminho_saida