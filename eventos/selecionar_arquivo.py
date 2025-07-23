import os
import shutil
import platform
import subprocess
import flet as ft  # necessário para tipos como FilePickerResultEvent

def abrir_pdf(filepath):
    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":
        subprocess.run(["open", filepath])
    else:
        subprocess.run(["xdg-open", filepath])


def selecione_arquivo(
    e: ft.FilePickerResultEvent,
    page: ft.Page,
    lista_dados: ft.ListView,
    dados_detectados: list,
    checkboxes: list,
    btn_anonimizar: ft.ElevatedButton,
    botao_abrir_pdf: ft.ElevatedButton,
    painel_direito: ft.Container,
    nome_arquivo_copiado: ft.Ref[str],
    status: ft.Text,
    btn_detectar: ft.ElevatedButton,
    gerar_imagens_do_pdf
):
    if e.files:
        original_caminho = e.files[0].path
        nome_arquivo = os.path.basename(original_caminho)

        # Limpa o estado da UI
        lista_dados.controls.clear()
        dados_detectados.clear()
        checkboxes.clear()
        btn_anonimizar.visible = False
        botao_abrir_pdf.visible = False
        painel_direito.content.controls.clear()

        destino = os.path.join("data", nome_arquivo)
        os.makedirs("data", exist_ok=True)
        original_abs = os.path.abspath(original_caminho)
        destino_abs = os.path.abspath(destino)

        if original_abs != destino_abs:
            shutil.copy(original_abs, destino_abs)
        else:
            print("O arquivo já está no diretório de destino.")

        nome_arquivo_copiado.current = nome_arquivo
        status.value = "Arquivo carregado. Clique em 'Detectar Dados'."
        btn_detectar.visible = True

        nome_base_arquivo, _ = os.path.splitext(nome_arquivo)
        pasta_imagens = os.path.join("data", "imagens", nome_base_arquivo)

        if os.path.exists(pasta_imagens):
            shutil.rmtree(pasta_imagens)

        caminhos_imagens = gerar_imagens_do_pdf(destino_abs, pasta_imagens)

        painel_direito.content.controls.append(
            ft.Text(f"Visualização do PDF ({len(caminhos_imagens)} páginas)", size=20, weight="bold", color="#555555")
        )

        for caminho in caminhos_imagens:
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
