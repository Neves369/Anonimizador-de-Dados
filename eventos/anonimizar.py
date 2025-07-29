
import os
import shutil
import flet as ft
from modules import processText
from modules.log import log_mensagem

def anonimizar_selecionados(
    e,
    page: ft.Page,
    nome_arquivo_copiado: ft.Ref[str],
    checkboxes: list,
    status: ft.Text,
    btn_abrir_pdf: ft.IconButton,
    painel_direito: ft.Container,
    gerar_imagens_do_pdf,
    abrir_pdf,
):
    selecionados = [cb.data for cb in checkboxes if cb.value]
    
    if not selecionados:
        status.value = "Nenhum dado selecionado."
        page.update()
        return

    status.value = "Anonimizando..."
    page.update()

    # Aplica anonimização
    caminho_saida = processText.aplicar_anonimizacao(nome_arquivo_copiado.current, selecionados)

    # Excluir arquivos originais
    try:
        caminho_original = os.path.join("data", nome_arquivo_copiado.current)
        if os.path.exists(caminho_original):
            os.remove(caminho_original)

        nome_base_original, _ = os.path.splitext(nome_arquivo_copiado.current)
        pasta_imagens_original = os.path.join("data", "imagens", nome_base_original)
        if os.path.exists(pasta_imagens_original):
            shutil.rmtree(pasta_imagens_original)

        pasta_imagens_demarcadas = os.path.join("data", "imagens", f"{nome_base_original}-DETECTADO")
        if os.path.exists(pasta_imagens_demarcadas):
            shutil.rmtree(pasta_imagens_demarcadas)

        for nome_arquivo in os.listdir("data"):
            if nome_arquivo.lower().endswith((".png", ".jpg", ".jpeg")):
                caminho_img = os.path.join("data", nome_arquivo)
                os.remove(caminho_img)

    except Exception as erro:
        log_mensagem(f"[Erro ao limpar arquivos antigos] {erro}")

    status.value = "Anonimização concluída!"
    btn_abrir_pdf.visible = True
    btn_abrir_pdf.on_click = lambda _: abrir_pdf(caminho_saida)

    nome_arquivo_anonimizado = os.path.basename(caminho_saida)
    nome_base_anonimizado, _ = os.path.splitext(nome_arquivo_anonimizado)
    pasta_imagens_anonimizadas = os.path.join("data", "imagens", nome_base_anonimizado)

    if os.path.exists(pasta_imagens_anonimizadas):
        shutil.rmtree(pasta_imagens_anonimizadas)

    caminhos_imagens_anonimizadas = gerar_imagens_do_pdf(caminho_saida, pasta_imagens_anonimizadas)

    painel_direito.content.controls.clear()
    painel_direito.content.controls.append(
        ft.Text(
            f"Visualização do PDF Anonimizado ({len(caminhos_imagens_anonimizadas)} páginas)",
            size=20,
            weight="bold",
            color="#555555"
        )
    )

    for caminho in caminhos_imagens_anonimizadas:
        painel_direito.content.controls.append(
            ft.Container(
                content=ft.Image(src=caminho, width=600, fit=ft.ImageFit.CONTAIN),
                border=ft.border.all(2, "#cccccc"),
                border_radius=8,
                padding=10,
                margin=ft.Margin(0, 10, 0, 10),
                bgcolor="#fafafa"
            )
        )

    page.update()
