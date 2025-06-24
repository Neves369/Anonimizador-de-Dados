def verify_pdf(filename):
    caminho_completo = "data\\" + filename
    try:
        doc = fitz.open(caminho_completo)
        
        # Verifica se o PDF está vazio
        if doc.page_count == 0:
            print(f"'{filename}' é um PDF vazio.")
            doc.close()
            return "vazio"

        # Variáveis para rastrear o tipo
        contem_texto_selecionavel = False
        contem_imagens_rasterizadas = False

        # Itera sobre as primeiras 3 páginas para uma análise rápida
        num_paginas_para_analise = min(doc.page_count, 3) 

        for i in range(num_paginas_para_analise):
            pagina = doc[i]

            # 1. Tenta extrair texto: Se conseguir, é um PDF de texto
            texto = pagina.get_text("text")
            if texto and texto.strip():
                contem_texto_selecionavel = True
                break 

            # 2. Se não encontrar texto selecionável, verifica se há imagens rasterizadas
            imagens = pagina.get_images(full=False) 
            if len(imagens) > 0:
                # Filtrar por imagens que não são máscaras ou artefatos minúsculos
                imagens_reais = [img for img in imagens if img[2] > 50 and img[3] > 50] # Largura e altura > 50 pixels
                if len(imagens_reais) > 0:
                    contem_imagens_rasterizadas = True

        doc.close()

        if contem_texto_selecionavel:
            return "texto"
        elif contem_imagens_rasterizadas:
            return "escaneado"
        else:
            return "indefinido"

    except fitz.FileDataError:
        print(f"Erro: '{filename}' não é um arquivo PDF válido ou está corrompido.")
        return "invalido"
    except Exception as e:
        print(f"Erro inesperado ao processar '{filename}': {e}")
        return "erro"

# Lê o pdf e segue a melhor abordagem para processamento do mesmo
def read_pdf(filename):
    typePDF = verify_pdf(filename)

    try:
        match typePDF:
        case "texto":
            # aqui entra o processamento de texto
        case "escaneado":
            
        case "indefinido":
            
        case _:  # Default case
            
    except:


