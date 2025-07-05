import os
import flet as ft
import shutil
import subprocess
import platform
from modules import read
from modules import processText

def main(page: ft.Page):
    page.title = "Anonimizador"
    page.window_width = 1200
    page.window_height = 800
    page.bgcolor = "#f5f5f5"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    nome_arquivo_copiado = ft.Ref[str]()
    dados_detectados = []
    checkboxes = []

    lista_dados = ft.Column(scroll=ft.ScrollMode.AUTO, height=350)
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
            label = ft.Text(f"[{dado['label']}] {dado['texto']}", color="#666666", weight='bold')
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

    # Container do cabeçalho
    header = ft.Container(
        content=ft.Row([
            ft.Text(
                "ANONIMIZADOR",
                size=28,
                weight=ft.FontWeight.BOLD,
                color="#000000"
            ),
            ft.Container(expand=True),  # Espaçador
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
        # margin=ft.margin.only(bottom=10)
    )
    
    abrir_picker = ft.FilePicker(on_result=selecione_arquivo)
    page.overlay.append(abrir_picker)

    # Botões do painel esquerdo
    btn_selecionar = ft.ElevatedButton("📂 Selecionar PDF", on_click=lambda _: abrir_picker.pick_files(
        dialog_title="Escolha um PDF", allow_multiple=False, allowed_extensions=["pdf"]
    ), width=400)
    btn_detectar = ft.ElevatedButton("🔍 Detectar Dados", on_click=detectar, width=400)
    btn_anonimizar = ft.ElevatedButton("🔐 Anonimizar", on_click=anonimizar_selecionados, width=400)
    botao_abrir_pdf = ft.ElevatedButton("📂 Abrir PDF", visible=False, width=400)
    
    # Painel esquerdo com botões
    painel_esquerdo = ft.Container(
        content=ft.Column([
            btn_selecionar,
            btn_detectar,
            ft.Container(height=180),
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
        height=400
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
        height=400
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
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
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
        height=550
    )
    
    # Layout principal
    conteudo_principal = ft.Row([
        painel_esquerdo,
        painel_lista,
        painel_direito
    ],
    alignment=ft.MainAxisAlignment.START,
    vertical_alignment=ft.CrossAxisAlignment.START)
    
    # Adicionar todos os elementos à página
    page.add(
        header,
        status,
        conteudo_principal
    )

ft.app(target=main)