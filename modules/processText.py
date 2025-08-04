import re
import os
import fitz 
from modules.log import log_mensagem

from PIL import Image


# def extrair_texto_ocr(caminho_imagem):
#     """Usa OCR para extrair texto de uma imagem"""
#     imagem = Image.open(caminho_imagem)
#     texto = pytesseract.image_to_string(imagem, lang='por')
#     return texto


# nlp = spacy.load("pt_core_news_lg")

def pdf_possui_texto(caminho_pdf):
    doc = fitz.open(caminho_pdf)
    for pagina in doc:
        texto = pagina.get_text().strip()
        if texto:
            return True  # Encontrou texto
    return False  # Nenhum texto encontrado

def detectar_dados(filename):
    global nlp
    caminho_arquivo = os.path.join("data", filename)
    doc = fitz.open(caminho_arquivo)

    log_mensagem("Abrindo:", caminho_arquivo)
    log_mensagem("Arquivo existe?", os.path.exists(caminho_arquivo))

    if pdf_possui_texto(caminho_arquivo):
        log_mensagem("📄 O PDF contém texto extraível.")
    else:
        log_mensagem("🖼️ O PDF é imagem (escaneado, sem texto).")

    log_mensagem("Modelo spaCy já carregado. Reutilizando.") 

    dados_detectados = []

    padroes = [
        ("CPF", r'\b\d{3}\.?\d{3}\.?\d{3}-?\s*\d{2}\b|\b\d{11}\b|\b\d{7}[\s\n]?\d{4}\b|\b\d{5}[\s\n]?\d{6}\b|\b\d{8}[\s\n]?\d{3}\b'),
        ("RG", r'\b(?:\d{3}[.\s]?\d{3}[.\s]?\d{3}|\d{2}\.\d{3,6}-\d{1,2}|\d{2}\.\d{3}\.\d{3}-\d{1}|\d{3}\.\d{3}\.\d{2}-\d{1}|\d{6,9}-\d{1}|\d{9,10}|\d{11}|\d{7})\b'),
        ("Telefone", r"\(\d{2}\)\s?\d{4,5}-\d{4}"),
        ("Email", r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b"),
        ("OAB", r"\b\d{3}\.?\d{3}[-/][A-Z]{2}\b"),
        ("CEP", r'\b\d{2}\.\d{3}-\d{3}\b'),
        ("Endereço", r'\b(?:Rua|Bairro|endereço|casa|Bloco|condomínio|Avenida|Av.|Travessa|Praça|Rodovia|Estrada|Alameda|Largo|Apto|apto.|Vila|Quadra|QD|Lote|lOTE|CEP:|CEP)\s+[A-Za-zÀ-ÿ0-9\s\.\-]+(?:,\s*\d{1,5})?\b')
    ]

    for i, pagina in enumerate(doc):
        texto = pagina.get_text()

        for label, padrao in padroes:
            encontrados = set()
            for match in re.findall(padrao, texto):
                bboxes = pagina.search_for(match)
                for bbox in bboxes:
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

    dados_texto = [d for d in dados_selecionados if d.get("tipo") == "texto"]
    dados_imagem = [d for d in dados_selecionados if d.get("tipo") == "imagem"]

    for dado in dados_selecionados:
        pagina = doc[dado["pagina"]]

        if "completa" in dado and dado ["completa"]:
            bbox =pagina.rect
            pagina.add_redact_annot(bbox, fill=(0, 0, 0), text="[OCULTO]")
        else:
            bbox = fitz.Rect(dado["bbox"])
            # bbox.y0 += 7
            # bbox.y1 -= 7
            pagina.add_redact_annot(bbox, fill=(0, 0, 0), text="[OCULTO]")

    for dado in [d for d in dados_selecionados if d.get("tipo") == "imagem"]:
        pagina = doc[dado["pagina"]]
        xrefs = dado.get("xrefs")  # obter lista de xrefs agrupados
        if not xrefs:
            # talvez tenha algum dado com 'xref' único — suporte legacy
            xref = dado.get("xref")
            if xref:
                xrefs = [xref]
            else:
                # nenhum xref disponível, ignora
                continue

        for xref in xrefs:
            try:
                bbox_imagem = pagina.get_image_bbox(xref)
                pagina.add_redact_annot(bbox_imagem, fill=(0, 0, 0))
            except Exception as e:
                log_mensagem(f"Erro ao ocultar imagem xref {xref} na página {dado['pagina']}: {e}")

    for pagina in doc:
        pagina.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    doc.save(caminho_saida)
    return caminho_saida

def caixas_sobrepostas(rect1, rect2, margem=5):
    # Expande rect1 em margem para tolerar pequenas diferenças
    rect1_expand = rect1 + (-margem, -margem, margem, margem)
    return rect1_expand.intersects(rect2)

def agrupar_bboxes_por_proximidade(bboxes):
    grupos = []
    for bbox in bboxes:
        adicionado = False
        for grupo in grupos:
            # Se bbox sobrepõe alguma caixa no grupo, adiciona ao grupo
            if any(caixas_sobrepostas(bbox, g) for g in grupo):
                grupo.append(bbox)
                adicionado = True
                break
        if not adicionado:
            grupos.append([bbox])
    # Agora juntar as caixas de cada grupo numa bbox única
    bboxes_agrupadas = []
    for grupo in grupos:
        x0 = min(r.x0 for r in grupo)
        y0 = min(r.y0 for r in grupo)
        x1 = max(r.x1 for r in grupo)
        y1 = max(r.y1 for r in grupo)
        bboxes_agrupadas.append(fitz.Rect(x0, y0, x1, y1))
    return bboxes_agrupadas

def demarcar_dados(filename, dados_detectados):
    """
    Abre o PDF, adiciona anotações (highlight) nas regiões dos dados detectados,
    e salva em output para visualização.
    NÃO faz anonimização, só demarca visualmente.
    """
    caminho = os.path.join("data", filename)
    nome_base, ext = os.path.splitext(filename)
    caminho_saida = os.path.join("output", f"{nome_base}-DETECTADO{ext}")

    doc = fitz.open(caminho)

    print(f"Demarcando dados detectados no arquivo: {caminho}")

    for dado in dados_detectados:
        pagina = doc[dado["pagina"]]
        bbox = fitz.Rect(dado["bbox"])
        highlight = pagina.add_highlight_annot(bbox)
        highlight.set_info(title="Detecção", content=f"{dado['label']}: {dado['texto']}")
        highlight.update()

    doc.save(caminho_saida)
    doc.close()
    log_mensagem(f"Arquivo com demarcação salvo em: {caminho_saida}")
    return caminho_saida

def detectar_imagens(caminho_pdf):
    doc = fitz.open(caminho_pdf)

    imagens = []
    for i, pagina in enumerate(doc):
        bboxes_por_xref = []  # lista de (bbox, xref)
        for img_index, img in enumerate(pagina.get_images(full=True)):
            xref = img[0]
            rects = pagina.get_image_rects(xref)
            if not rects:
                continue
            for r in rects:
                bboxes_por_xref.append((r, xref))

        # Função que agrupa as caixas, mantendo os xrefs do grupo
        grupos = []
        for bbox, xref in bboxes_por_xref:
            adicionado = False
            for grupo in grupos:
                # grupo é lista de (bbox, xref)
                if any(caixas_sobrepostas(bbox, g[0]) for g in grupo):
                    grupo.append((bbox, xref))
                    adicionado = True
                    break
            if not adicionado:
                grupos.append([(bbox, xref)])

        # Para cada grupo, juntar as caixas e juntar os xrefs únicos
        for grupo in grupos:
            x0 = min(b[0].x0 for b in grupo)
            y0 = min(b[0].y0 for b in grupo)
            x1 = max(b[0].x1 for b in grupo)
            y1 = max(b[0].y1 for b in grupo)
            bbox_agrupada = fitz.Rect(x0, y0, x1, y1)

            if bbox_agrupada.get_area() < 500:
                continue

            xrefs_unicos = list(set([b[1] for b in grupo]))

            imagens.append({
                "pagina": i,
                "bbox": list(bbox_agrupada),
                "xrefs": xrefs_unicos,
                "descricao": f"Imagem agrupada página {i+1}, xrefs {xrefs_unicos}",
                "label": "Imagem",
                "tipo": "imagem"
            })

    doc.close()
    return imagens


