import re
import os
import fitz
import pytesseract
from modules.log import log_mensagem
from PIL import Image, ImageDraw, ImageFont

def detectar_dados(filename):
    nome_base, _ = os.path.splitext(filename)
    caminho_imagens = os.path.join("data", "imagens", nome_base) 

    log_mensagem("Abrindo:", caminho_imagens)
    log_mensagem("Arquivo existe?", os.path.exists(caminho_imagens))
    
    # Define o caminho para o executável do Tesseract se necessário (principalmente no Windows)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\Tesseract-OCR\tesseract.exe'

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

    try:
        # Obtém uma lista ordenada dos arquivos de imagem no diretório
        image_files = sorted([f for f in os.listdir(caminho_imagens) 
                              if f.startswith(f"pagina") and f.endswith((".png", ".jpg", ".jpeg"))])

        if not image_files:
            log_mensagem(f"Atenção: Nenhuma imagem encontrada para o documento '{filename}' na pasta '{caminho_imagens}'.")
            log_mensagem(f"Certifique-se de que as imagens estão nomeadas como 'pagina_X.png' e estão no diretório correto.")
            return Exception("Nenhuma imagem encontrada para o documento.")

        for i, image_file in enumerate(image_files):
            image_path = os.path.join(caminho_imagens, image_file)
            
            try:
                pil_image = Image.open(image_path)
            except FileNotFoundError:
                log_mensagem(f"Erro: Imagem não encontrada: {image_path}. Pulando esta página.")
                continue
            except Exception as e:
                log_mensagem(f"Erro ao abrir a imagem {image_path}: {e}. Pulando esta página.")
                continue

            try:
                # Realiza OCR para obter texto e dados de caixa delimitadora (bounding box)
                data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT, lang='por')
            except pytesseract.TesseractNotFoundError:
                print("Erro: Executável do Tesseract não encontrado. Certifique-se de que o Tesseract está instalado e configurado no PATH.")
                print("Você pode precisar definir 'pytesseract.pytesseract.tesseract_cmd' manualmente.")
                return Exception("Tesseract não encontrado.")
            except Exception as e:
                print(f"Erro ao realizar OCR na imagem {image_path}: {e}. Pulando esta página.")
                continue
            
            page_words_info = []
            # 'data' pode conter listas vazias ou None se o OCR falhar completamente para uma palavra
            if 'text' in data and data['text'] is not None:
                for j in range(len(data['text'])):
                    word = data['text'][j].strip()
                    # Opcional: Adicionar um filtro de confiança do OCR, ex: int(data['conf'][j]) > 70
                    if word and data['left'][j] is not None and data['top'][j] is not None: 
                        x = data['left'][j]
                        y = data['top'][j]
                        w = data['width'][j]
                        h = data['height'][j]
                        page_words_info.append({
                            "text": word,
                            "bbox": [x, y, x + w, y + h]
                        })

            full_page_text = " ".join([word_info["text"] for word_info in page_words_info])
            # Normalizar espaços para evitar problemas com regex devido a múltiplos espaços do OCR
            full_page_text = re.sub(r'\s+', ' ', full_page_text).strip()


            for label, padrao in padroes:
                encontrados = set()
                # Usamos finditer para obter as posições de início e fim de cada correspondência
                for match in re.finditer(padrao, full_page_text):
                    matched_text = match.group(0)
                    start_char, end_char = match.span()

                    match_bbox = []
                    current_text_pos_in_full_page_text = 0
                    
                    for word_info in page_words_info:
                        word_text = word_info["text"]
                        
                        word_start_in_full_text = full_page_text.find(word_text, current_text_pos_in_full_page_text)
                        
                        if word_start_in_full_text != -1:
                            word_end_in_full_text = word_start_in_full_text + len(word_text)

                            if max(start_char, word_start_in_full_text) < min(end_char, word_end_in_full_text):
                                match_bbox.append(word_info["bbox"])
                            
                            current_text_pos_in_full_page_text = word_end_in_full_text

                    if match_bbox:
                        min_x0 = min(b[0] for b in match_bbox)
                        min_y0 = min(b[1] for b in match_bbox)
                        max_x1 = max(b[2] for b in match_bbox)
                        max_y1 = max(b[3] for b in match_bbox)
                        combined_bbox = [min_x0, min_y0, max_x1, max_y1]

                        # Corrected line: convert the list to a tuple before adding to the set
                        combined_bbox_tuple = tuple(combined_bbox) 
                        if (matched_text, combined_bbox_tuple) in encontrados:
                            continue
                        
                        encontrados.add((matched_text, combined_bbox_tuple)) # Add a tuple of (text, bbox) to the set
                        dados_detectados.append({
                            "pagina": i,
                            "texto": matched_text,
                            "label": label,
                            "bbox": combined_bbox
                        })

            return dados_detectados                    

    except FileNotFoundError as e:
        print(f"Erro: O diretório de imagens '{caminho_imagens}' não foi encontrado. Por favor, verifique o caminho. Detalhes: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao detectar dados: {e}")

def demarcar_dados(filename, dados_detectados):
    # Pega apenas o nome do arquivo, sem a extensão
    nome_base, _ = os.path.splitext(filename)

    # Constrói o caminho dos diretórios corretamente
    caminho_imagens_dir = os.path.join("data", "imagens", nome_base)
    caminho_saida_dir = os.path.join("data", "imagens", nome_base)
    os.makedirs(caminho_saida_dir, exist_ok=True)
    
    image_files = sorted([f for f in os.listdir(caminho_imagens_dir) 
                             if f.startswith("pagina") and f.endswith((".png", ".jpg", ".jpeg"))])
    
    if not image_files:
        print(f"Nenhuma imagem encontrada no diretório: {caminho_imagens_dir}")
        return None
        
    for i, image_file in enumerate(image_files):
        image_path = os.path.join(caminho_imagens_dir, image_file)
        output_image_path = os.path.join(caminho_saida_dir, image_file)
        
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
        except Exception as e:
            print(f"Erro ao abrir a imagem {image_path}: {e}")
            continue
        
        for dado in dados_detectados:
            if dado["pagina"] == i:
                bbox = dado["bbox"]
                x0, y0, x1, y1 = bbox
                
                # Desenha um retângulo na imagem
                draw.rectangle([x0, y0, x1, y1], outline="red", width=3)
                
                # Adiciona um texto de anotação
                draw.text((x0, y0 - 15), f"{dado['label']}: {dado['texto']}", fill="red", font=font)
                
        img.save(output_image_path)
        print(f"Imagem com demarcação salva em: {output_image_path}")
        
    return caminho_saida_dir

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