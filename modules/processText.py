import re
import os
import fitz 
import spacy
import sys

nlp = spacy.load("pt_core_news_lg")
def detectar_dados(filename):
    global nlp
    caminho_arquivo = os.path.join("data", filename)
    doc = fitz.open(caminho_arquivo)

    
    # nlp = spacy.load("pt_core_news_lg") 

    print("Abrindo:", caminho_arquivo)
    print("Arquivo existe?", os.path.exists(caminho_arquivo))
    print("Modelo spaCy já carregado. Reutilizando.") # Mensagem para confirmar

def detectar_dados(filename):
    global nlp
    caminho_arquivo = os.path.join("data", filename)
    doc = fitz.open(caminho_arquivo)

    print("Abrindo:", caminho_arquivo)
    print("Arquivo existe?", os.path.exists(caminho_arquivo))
    print("Modelo spaCy já carregado. Reutilizando.") 

    dados_detectados = []

    padroes = [
        ("CPF", r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'),
        ("RG", r'\b(?:\d{2}\.\d{3}\.\d{3}-\d{1}|\d{6,9}-\d{1}|\d{9,10})\b'),
        ("Telefone", r"\(\d{2}\)\s?\d{4,5}-\d{4}"),
        ("Email", r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b"),
        ("OAB", r"\b\d{3}\.?\d{3}[-/][A-Z]{2}\b"),
        ("Endereço", r'\b(?:Rua|Avenida|Travessa|Praça|Rodovia|Estrada|Alameda|Largo|CEP|Vila)\s+[A-Za-zÀ-ÿ0-9\s\.\-]+(?:,\s*\d{1,5})?\b')

    ]

    for i, pagina in enumerate(doc):
        texto = pagina.get_text()

        for label, padrao in padroes:
            encontrados = set()  # para evitar repetir o mesmo bbox
            for match in re.findall(padrao, texto):
                bboxes = pagina.search_for(match)
                for bbox in bboxes:
                    # criar uma chave única para o dado (texto + bbox)
                    chave = (match, tuple(bbox))
                    if chave in encontrados:
                        continue
                    encontrados.add(chave)
                    dados_detectados.append({
                        "pagina": i,
                        "texto": match,
                        "label": label,
                        "bbox": list(bbox)
                    })

    return dados_detectados


def aplicar_anonimizacao(filename, dados_selecionados):
    caminho = os.path.join("data", filename)
    nome_base, ext = os.path.splitext(filename)
    caminho_saida = os.path.join("output", f"{nome_base}-ANONIMIZADO{ext}")
    
    doc = fitz.open(caminho)

    for dado in dados_selecionados:
        pagina = doc[dado["pagina"]]
        bbox = fitz.Rect(dado["bbox"])
        bbox.y0 += 5
        bbox.y1 -= 5
        pagina.add_redact_annot(bbox, fill=(0, 0, 0), text="[OCULTO]")

    for pagina in doc:
        pagina.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    doc.save(caminho_saida)
    return caminho_saida