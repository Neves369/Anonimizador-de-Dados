# import os
# import flet as ft
# import shutil
# import subprocess
# import platform
# from modules import read  # ou qualquer que seja o módulo que tenha `process_text`
# from modules import processText

# def main(page: ft.Page):
#     page.title = "Anonimizador de Dados Pessoais"
#     page.theme_mode = "light"
#     page.scroll = ft.ScrollMode.AUTO

#     dados_detectados = processText.detectar_dados(nome_arquivo_copiado.current)

#     nome_arquivo_copiado = ft.Ref[str]()

#     arquivo = ft.Text("Nenhum arquivo selecionado", size=14)
#     status = ft.Text("", size=14, color="green")

#     botao_abrir_pdf = ft.ElevatedButton("📂 Abrir PDF", visible=False)

#     def abrir_pdf(filepath):
#         if platform.system() == "Windows":
#             os.startfile(filepath)
#         elif platform.system() == "Darwin":
#             subprocess.run(["open", filepath])
#         else:
#             subprocess.run(["xdg-open", filepath])

#     def selecione_arquivo(e: ft.FilePickerResultEvent):
#         if e.files:
#             original_caminho = e.files[0].path
#             nome_arquivo = os.path.basename(original_caminho)
#             pasta_destino = "data"
#             os.makedirs(pasta_destino, exist_ok=True)
#             destino_caminho = os.path.join(pasta_destino, nome_arquivo)
#             try:
#                 shutil.copy(original_caminho, destino_caminho)
#                 nome_arquivo_copiado.current = nome_arquivo
#                 arquivo.value = f"Selecionado: {nome_arquivo} (copiado para '{pasta_destino}/')"
#                 status.value = ""
#                 botao_abrir_pdf.visible = False
#                 botao_abrir_pdf.on_click = None
#                 page.update()
#             except Exception as err:
#                 status.value = f"Erro ao copiar arquivo: {err}"
#                 page.update()

#     abrir_geren = ft.FilePicker(on_result=selecione_arquivo)
#     page.overlay.append(abrir_geren)

    

#     checkboxes = []
#     for dado in dados_detectados:
#         check = ft.Checkbox(label=f"[{dado['label']}] {dado['texto']}")
#         check.data = dado  # salva info completa
#         checkboxes.append(check)

#     page.add(ft.Column(checkboxes))

#     def anonimizar_pdf(e):
#         if not nome_arquivo_copiado.current:
#             status.value = "Nenhum arquivo selecionado para anonimizar."
#             page.update()
#             return

#         try:
#             status.value = "Anonimizando... aguarde."
#             page.update()
#             os.makedirs("output", exist_ok=True)

#             read.read_pdf(nome_arquivo_copiado.current)


#             # CORREÇÃO: Cria nome de saída dinâmico
#             nome_base, extensao = os.path.splitext(nome_arquivo_copiado.current)
#             nome_arquivo_saida = f"{nome_base}_tarjado{extensao}"
#             caminho_saida = os.path.join("output", nome_arquivo_saida)

#             if os.path.exists(caminho_saida):
#                 status.value = "Anonimização concluída! Clique em 'Abrir PDF'."
#                 botao_abrir_pdf.visible = True
#                 botao_abrir_pdf.on_click = lambda _, path=caminho_saida: abrir_pdf(path)
#             else:
#                 status.value = f"Erro: o PDF '{nome_arquivo_saida}' não foi gerado."
#                 botao_abrir_pdf.visible = False
#                 botao_abrir_pdf.on_click = None
#             page.update()

#         except Exception as err:
#             status.value = f"Erro na anonimização: {err}"
#             page.update()

#     header = ft.Text("ANONIMIZADOR DE DADOS PESSOAIS", size=24, weight="bold", color="blue")
#     descricao = ft.Text("Este programa lê um arquivo PDF e remove dados sensíveis.", size=16)

#     botao_importar = ft.ElevatedButton(
#         "Importar PDF",
#         on_click=lambda _: abrir_geren.pick_files(
#             dialog_title="Selecione um arquivo PDF",
#             allow_multiple=False,
#             allowed_extensions=["pdf"]
#         )
#     )
#     botao_anonimizar = ft.ElevatedButton("🔐 Anonimizar", on_click=anonimizar_pdf)

#     page.add(
#         header,
#         descricao,
#         arquivo,
#         status,
#         ft.Row([botao_importar, botao_anonimizar, botao_abrir_pdf]),
#     )

# ft.app(target=main)

import os
import flet as ft
import shutil
import subprocess
import platform
from modules import read
from modules import processText

def main(page: ft.Page):
    page.title = "Anonimizador Interativo"
    page.theme_mode = "light"
    page.scroll = ft.ScrollMode.AUTO

    nome_arquivo_copiado = ft.Ref[str]()
    dados_detectados = []
    checkboxes = []

    lista_dados = ft.Column(scroll=ft.ScrollMode.AUTO, height=300)
    status = ft.Text()

    def abrir_pdf(filepath):
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":
            subprocess.run(["open", filepath])
        else:
            subprocess.run(["xdg-open", filepath])

    def selecione_arquivo(e: ft.FilePickerResultEvent):
        if e.files:
            original_caminho = e.files[0].path
            nome_arquivo = os.path.basename(original_caminho)
            destino = os.path.join("data", nome_arquivo)
            os.makedirs("data", exist_ok=True)
            shutil.copy(original_caminho, destino)
            nome_arquivo_copiado.current = nome_arquivo
            status.value = "Arquivo carregado. Clique em 'Detectar Dados'."
            page.update()

    def detectar(e):
        nonlocal dados_detectados, checkboxes
        if not nome_arquivo_copiado.current:
            status.value = "Nenhum arquivo selecionado."
            return

        status.value = "Detectando dados..."
        page.update()

        dados_detectados = processText.detectar_dados(nome_arquivo_copiado.current)
        checkboxes.clear()
        lista_dados.controls.clear()

        for dado in dados_detectados:
            label = f"[{dado['label']}] {dado['texto']}"
            cb = ft.Checkbox(label=label, value=False)
            cb.data = dado
            checkboxes.append(cb)
            lista_dados.controls.append(cb)

        status.value = f"{len(checkboxes)} dados encontrados."
        page.update()

    def anonimizar_selecionados(e):
        selecionados = [cb.data for cb in checkboxes if cb.value]
        if not selecionados:
            status.value = "Nenhum dado selecionado."
            page.update()
            return

        status.value = "Anonimizando..."
        page.update()

        caminho_saida = processText.aplicar_anonimizacao(nome_arquivo_copiado.current, selecionados)

        status.value = f"Anonimização concluída!"
        botao_abrir_pdf.visible = True
        botao_abrir_pdf.on_click = lambda _: abrir_pdf(caminho_saida)
        page.update()

    abrir_picker = ft.FilePicker(on_result=selecione_arquivo)
    page.overlay.append(abrir_picker)

    botao_abrir_pdf = ft.ElevatedButton("📂 Abrir PDF", visible=False)

    page.add(
        ft.Text("ANONIMIZADOR INTERATIVO", size=24, weight="bold", color="blue"),
        ft.ElevatedButton("Selecionar PDF", on_click=lambda _: abrir_picker.pick_files(
            dialog_title="Escolha um PDF", allow_multiple=False, allowed_extensions=["pdf"]
        )),
        ft.ElevatedButton("🔍 Detectar Dados", on_click=detectar),
        lista_dados,
        ft.ElevatedButton("🔐 Anonimizar Selecionados", on_click=anonimizar_selecionados),
        botao_abrir_pdf,
        status
    )

ft.app(target=main)
