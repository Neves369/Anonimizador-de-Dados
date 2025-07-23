import re
import os
import fitz
import spacy
import pytesseract
from PIL import Image

def detectar_dados(filename):
    nome_base, _ = os.path.splitext(filename)
    caminho_imagens = os.path.join("data", "imagens") 
    
    # Define o caminho para o executável do Tesseract se necessário (principalmente no Windows)
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 

    nlp = spacy.load("pt_core_news_lg")

    sessoes = {
        "CPF": [],
        "RG": [],
        "Telefone": [],
        "Email": [],
        "OAB": [],
        "Outros": []
    }

    padroes = [
        ("CPF", r"\d{3}\.\d{3}\.\d{3}-\d{2}"),
        ("RG", r"\d{2}\.\d{3}\.\d{3}-\d{1}"),
        ("Telefone", r"\(\d{2}\)\s?\d{4,5}-\d{4}"),
        ("Email", r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b"),
        ("OAB", r"\d{3}\.\d{2}") 
    ]

    try:
        # Obtém uma lista ordenada dos arquivos de imagem no diretório
        image_files = sorted([f for f in os.listdir(caminho_imagens) 
                              if f.startswith(f"{nome_base}_page_") and f.endswith((".png", ".jpg", ".jpeg"))])

        if not image_files:
            print(f"Atenção: Nenhuma imagem encontrada para o documento '{filename}' na pasta '{caminho_imagens}'.")
            print(f"Certifique-se de que as imagens estão nomeadas como '{nome_base}_page_X.png' e estão no diretório correto.")
            return sessoes

        for i, image_file in enumerate(image_files):
            image_path = os.path.join(caminho_imagens, image_file)
            
            try:
                pil_image = Image.open(image_path)
            except FileNotFoundError:
                print(f"Erro: Imagem não encontrada: {image_path}. Pulando esta página.")
                continue
            except Exception as e:
                print(f"Erro ao abrir a imagem {image_path}: {e}. Pulando esta página.")
                continue

            try:
                # Realiza OCR para obter texto e dados de caixa delimitadora (bounding box)
                data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT, lang='por')
            except pytesseract.TesseractNotFoundError:
                print("Erro: Executável do Tesseract não encontrado. Certifique-se de que o Tesseract está instalado e configurado no PATH.")
                print("Você pode precisar definir 'pytesseract.pytesseract.tesseract_cmd' manualmente.")
                return sessoes # Retorna sessoes vazias ou levanta o erro, dependendo do comportamento desejado
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
            
            # --- DEBUG: Imprima o texto para ver o que o OCR detectou ---
            # print(f"\n--- Texto OCR da Página {i} ({image_file}) ---")
            # print(full_page_text)
            # print("------------------------------------------")
            # --- FIM DEBUG ---
            
            # spacy_doc = nlp(full_page_text) # Esta linha não está sendo usada para detecção direta dos padrões definidos

            for label, padrao in padroes:
                # Usamos finditer para obter as posições de início e fim de cada correspondência
                for match in re.finditer(padrao, full_page_text):
                    matched_text = match.group(0)
                    start_char, end_char = match.span()

                    match_bbox = []
                    current_text_pos_in_full_page_text = 0 # Posição atual no texto completo reconstruído
                    
                    for word_info in page_words_info:
                        word_text = word_info["text"]
                        
                        # Calcula a posição de início e fim da palavra no 'full_page_text'
                        # Isso é mais robusto do que apenas somar 'len(word)' se houver espaços variáveis
                        word_start_in_full_text = full_page_text.find(word_text, current_text_pos_in_full_page_text)
                        
                        # Se a palavra foi encontrada e está dentro da seção atual do texto
                        if word_start_in_full_text != -1:
                            word_end_in_full_text = word_start_in_full_text + len(word_text)

                            # Verifica se o span da palavra se sobrepõe ao span do match do regex
                            if max(start_char, word_start_in_full_text) < min(end_char, word_end_in_full_text):
                                match_bbox.append(word_info["bbox"])
                            
                            # Atualiza a posição para a próxima busca, evitando encontrar a mesma palavra
                            current_text_pos_in_full_page_text = word_end_in_full_text 
                            # Se adicionamos espaços entre as palavras, precisamos contabilizá-los
                            # A forma mais segura é buscar a próxima palavra.

                    if match_bbox:
                        # Combina as caixas delimitadoras individuais em uma única maior
                        min_x0 = min(b[0] for b in match_bbox)
                        min_y0 = min(b[1] for b in match_bbox)
                        max_x1 = max(b[2] for b in match_bbox)
                        max_y1 = max(b[3] for b in match_bbox)
                        combined_bbox = [min_x0, min_y0, max_x1, max_y1]

                        dado = {
                            "pagina": i,
                            "texto": matched_text,
                            "label": label,
                            "bbox": combined_bbox
                        }
                        if label in sessoes:
                            sessoes[label].append(dado)
                        else:
                            sessoes["Outros"].append(dado)

    except FileNotFoundError as e:
        print(f"Erro: O diretório de imagens '{caminho_imagens}' não foi encontrado. Por favor, verifique o caminho. Detalhes: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao detectar dados: {e}")
        # print(f"Detalhamento: {traceback.format_exc()}") # Descomente para ver o stack trace completo para depuração

    print("\n--- Resultado Final da Detecção ---")
    print(sessoes) 
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