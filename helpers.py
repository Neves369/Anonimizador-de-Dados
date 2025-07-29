import os
import sys
import fitz

#retorna o caminho absoluto de um recurso (como uma imagem, arquivo etc.)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Função que converte cada página de um PDF em uma imagem PNG

def gerar_imagens_do_pdf(caminho_pdf, pasta_destino):
    os.makedirs(pasta_destino, exist_ok=True)
    doc = fitz.open(caminho_pdf)
    caminhos_imagens = []

    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        caminho_img = os.path.join(pasta_destino, f"pagina_{i+1}.png")
        pix.save(caminho_img)
        caminhos_imagens.append(caminho_img)

    doc.close()
    return caminhos_imagens
