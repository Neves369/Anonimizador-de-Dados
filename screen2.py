import os
import flet as ft
import shutil
import subprocess
import fitz 
import platform
from modules import read
from modules import processText

import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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


def main(page: ft.Page):
    page.title = "Anonimizador"
    page.window_width = 1200
    page.window_height = 800
    page.bgcolor = "#ececec"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.window.maximized = True

    nome_arquivo_copiado = ft.Ref[str]()
    dados_detectados = []
    checkboxes = []

    lista_dados = ft.Column(scroll=ft.ScrollMode.AUTO, height=350)
    status = ft.Text(f"Selecione um arquivo para continuar...", color="#666666", weight='bold')
    
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
            original_abs = os.path.abspath(original_caminho)
            destino_abs = os.path.abspath(destino)

            if original_abs != destino_abs:
                shutil.copy(original_abs, destino_abs)
            else:
                print("O arquivo já está no diretório de destino. Nenhuma cópia necessária.")

            nome_arquivo_copiado.current = nome_arquivo
            status.value = "Arquivo carregado. Clique em 'Detectar Dados'."
            btn_detectar.visible= True

            # Gerar imagens de todas as páginas do PDF
            caminho_pdf = destino_abs
            pasta_imagens = os.path.join("data", "imagens")
            caminhos_imagens = gerar_imagens_do_pdf(caminho_pdf, pasta_imagens)

            # Atualizar painel direito com as imagens
            painel_direito.content.controls.clear()
            painel_direito.content.controls.append(
                ft.Text("Visualização do PDF", size=20, weight="bold", color="#555555")
            )
            for caminho in caminhos_imagens:
                painel_direito.content.controls.append(
                    ft.Image(src=caminho, width=600, fit=ft.ImageFit.CONTAIN)
                )
            page.update()


    def detectar(e):

        selecionar_tudo_cb = ft.Checkbox(label=ft.Text(f"SELECIONAR TUDO", color="#666666", weight='bold'), value=False)

        def selecionar_tudo_changed(e):
            for cb in checkboxes:
                cb.value = selecionar_tudo_cb.value
            page.update()

        selecionar_tudo_cb.on_change = selecionar_tudo_changed

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
            label = ft.Text(f"[{dado['label']}] {dado['texto']}", color="#666666", weight='bold')
            cb = ft.Checkbox(label=label, value=False)
            cb.data = dado
            checkboxes.append(cb)
            lista_dados.controls.append(cb)
        
        lista_dados.controls.insert(0, selecionar_tudo_cb)

        status.value = f"{len(checkboxes)} dados encontrados. \nSelecione as informações que deseja ocultar..."
        btn_anonimizar.visible= True
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

    # Container do cabeçalho
    logo_path = resource_path("assets/logo.png")

    header = ft.Container(
        content=ft.Row([
            ft.Image(
                src=logo_path,
                width=50,
                height=50,
                fit=ft.ImageFit.CONTAIN,
            ),
            ft.Text(
                "ANONIMIZADOR",
                size=28,
                weight=ft.FontWeight.BOLD,
                color="#666666"
            ),
            ft.Container(expand=True),
            ft.Text(
                "versão 1.0",
                size=14,
                color="#666666"
            )
        ]),
        bgcolor="#ffffff",
        padding=20,
        border_radius=12,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color="#00000020",
            offset=ft.Offset(0, 2)
        ),
    )
    
    abrir_picker = ft.FilePicker(on_result=selecione_arquivo)
    page.overlay.append(abrir_picker)

    # Botões do painel esquerdo
    btn_selecionar = ft.ElevatedButton("📂 Selecionar PDF", on_click=lambda _: abrir_picker.pick_files(
        dialog_title="Escolha um PDF", allow_multiple=False, allowed_extensions=["pdf"]
    ), width=400, color="white")
    btn_detectar = ft.ElevatedButton("🔍 Detectar Dados", visible=False, on_click=detectar, width=400, color="white")
    btn_anonimizar = ft.ElevatedButton("🔐 Anonimizar", visible=False, on_click=anonimizar_selecionados, width=400, color="white")
    botao_abrir_pdf = ft.ElevatedButton("📂 Abrir PDF", visible=False, width=400, color="white")
    
    # Painel esquerdo com botões
    painel_esquerdo = ft.Container(
        content=ft.Column([
            btn_selecionar,
            btn_detectar,
            # ft.Container(height=180),
            btn_anonimizar,
            botao_abrir_pdf
        ], 
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#ffffff",
        padding=25,
        border_radius=12,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color="#00000020",
            offset=ft.Offset(0, 2)
        ),
        width=200,
        height=550
    )

    # Painel central lista de dados
    painel_lista = ft.Container(
        content=ft.Column([
          lista_dados
        ], 
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#ffffff",
        padding=25,
        border_radius=12,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color="#00000020",
            offset=ft.Offset(0, 2)
        ),
        width=400,
        height=550
    )
    
   
    # Painel direito (área de trabalho)
    painel_direito = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text(
                    "Área de trabalho",
                    size=18,
                    color="#999999",
                    text_align=ft.TextAlign.CENTER
                ),
                alignment=ft.alignment.center
            )
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO
        ),
        bgcolor="#ffffff",
        padding=30,
        border_radius=12,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color="#00000020",
            offset=ft.Offset(0, 2)
        ),
        expand=True,
        height=840
    )

    texto = ft.Text(
        "Desenvolvido por: Douglas Brian - Ezequiel Pacheco - Gabriel Garcia",
        size=14,
                color="#666666"
            )

    
    # Agrupa os dois painéis em uma linha
    linha_coluna_esquerda = ft.Row([
        painel_esquerdo,
        painel_lista,
    ])

    # Painel inferior de Log
    painel_inferior = ft.Container(
        content=status,
        bgcolor="#ffffff",
        padding=20,
        border_radius=12,
        width=610,
        height=280
    )

    #  Coluna que agrupa os painéis
    coluna_esquerda = ft.Column([
      linha_coluna_esquerda,
      painel_inferior
    ])

    # Layout principal
    conteudo_principal = ft.Row([
        coluna_esquerda,
        painel_direito
    ],
    alignment=ft.MainAxisAlignment.START,
    vertical_alignment=ft.CrossAxisAlignment.START)
    
    # Adicionar todos os elementos à página
    page.add(
        header,
        conteudo_principal,
        texto
    )

ft.app(target=main)