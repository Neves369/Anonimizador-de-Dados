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

def gerar_caminhos_imagens_existentes(pasta_destino):
    """
    Lista todos os arquivos de imagem em um diretório específico.
    
    Args:
        pasta_destino (str): O caminho do diretório onde as imagens estão salvas.
    
    Returns:
        list: Uma lista de strings com os caminhos completos para as imagens.
    """
    caminhos_imagens = []
    
    # Verifica se a pasta existe antes de tentar listar o conteúdo
    if not os.path.isdir(pasta_destino):
        print(f"Erro: O diretório '{pasta_destino}' não foi encontrado.")
        return []
    
    # Lista todos os arquivos na pasta
    for nome_arquivo in os.listdir(pasta_destino):
        # Filtra apenas os arquivos que são imagens
        if nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            caminho_completo = os.path.join(pasta_destino, nome_arquivo)
            caminhos_imagens.append(caminho_completo)
            
    # Ordena a lista para garantir que as páginas estejam na ordem correta (1, 2, 3...)
    caminhos_imagens.sort()

    return caminhos_imagens
