import os
import flet as ft
import shutil
import subprocess
import fitz
import platform
from modules import read
from modules import processText 
from eventos.detectar_dados import detectar
from eventos.selecionar_arquivo import selecione_arquivo
from eventos.selecionar_arquivo import abrir_pdf
from filtros import aplicar_filtro, criar_dropdown_filtro
from eventos.anonimizar import anonimizar_selecionados
from ui_config import configurar_pagina, apply_theme_colors # Importe apply_theme_colors
from helpers import resource_path, gerar_imagens_do_pdf
from eventos.tela_config import mostrar_tela_configuracoes # Importe a tela_configuracoes (use o nome correto do arquivo)
from modules import log


import sys 

logo_img = ft.Ref[ft.Image]()





def resource_path(relative_path):
    return relative_path

# --- Mova a definição de mostrar_tela_principal para fora da função main ---
def mostrar_tela_principal(page: ft.Page, header_ref, corpo_ref, texto_ref, sidebar_ref, 
                           painel_dados_detectados_ref, painel_pdf_ref, status_ref, detalhes_anonimizacao_ref):
    
    # Aplica as cores do tema para garantir que todos os elementos usem o tema correto
    apply_theme_colors(page) 
    
    # Ao voltar para a tela principal, re-renderize os componentes
    page.controls.clear()

    # Atualize as cores dos componentes antes de adicioná-los
    header_ref.bgcolor = page.theme_mode_background_color
    # Atualiza as cores internas do header
    for control in header_ref.content.controls:
        if isinstance(control, ft.Text):
            control.color = page.theme_mode_text_color
        elif isinstance(control, ft.IconButton):
            control.icon_color = page.theme_mode_text_color # Para icon buttons no header

    sidebar_ref.bgcolor = page.theme_mode_background_color
    # Atualiza as cores internas do sidebar
    for control in sidebar_ref.content.controls:
        if isinstance(control, ft.Icon):
            control.color = page.theme_mode_text_color
        elif isinstance(control, ft.IconButton):
            control.icon_color = page.theme_mode_text_color
    
    painel_dados_detectados_ref.bgcolor = page.theme_mode_background_color
    # Atualiza as cores internas do painel_dados_detectados
    for control in painel_dados_detectados_ref.content.controls:
        if isinstance(control, ft.Text):
            control.color = page.theme_mode_text_color

    painel_pdf_ref.bgcolor = page.theme_mode_content_background_color
    # Atualiza as cores internas do painel_pdf
    if isinstance(detalhes_anonimizacao_ref.content, ft.Text):
        detalhes_anonimizacao_ref.content.color = page.theme_mode_text_color
    # A cor do texto "PDF" dentro do container do painel_pdf
    # Você precisará acessar o segundo controle do painel_pdf.content.controls
    # Isso pode ser um pouco frágil se a estrutura mudar.
    # Uma forma mais robusta é dar um ft.Ref a esse Text
    # Por enquanto, vou assumir a estrutura atual:
    if len(painel_pdf_ref.content.controls) > 1 and isinstance(painel_pdf_ref.content.controls[1], ft.Container):
        inner_pdf_container = painel_pdf_ref.content.controls[1]
        if isinstance(inner_pdf_container.content, ft.Text):
            inner_pdf_container.content.color = page.theme_mode_pdf_text_color
        inner_pdf_container.bgcolor = page.theme_mode_pdf_background_color

    status_ref.color = page.theme_mode_text_color
    texto_ref.color = page.theme_mode_text_color

    page.add(
        header_ref,
        ft.Divider(thickness=1, color=page.theme_mode_color, height=10),
        corpo_ref,
        ft.Divider(thickness=1, color=page.theme_mode_color, height=10),
        texto_ref
    )
    page.update()

    if logo_img.current:
        logo_img.current.src = resource_path("assets/logo_dark.png") if page.theme_mode == ft.ThemeMode.DARK else resource_path("assets/logo.png")
        logo_img.current.update()

def main(page: ft.Page):

    log_ref = ft.Ref[ft.ListView]()

    log.set_log_ref(log_ref)

    # Remova o 'if page.theme_mode is None:' daqui,
    # pois configurar_pagina já lida com a inicialização do tema
    configurar_pagina(page) # Chame sua função de configuração da página

    # Remova o page.update() duplicado
    # page.update() 
    
    # Definição das referências para os controles da UI
    # Isso é necessário para que mostrar_tela_principal possa manipulá-los
    # Se você não usar ft.Ref para um controle específico, passe o próprio objeto
    nome_arquivo_copiado = ft.Ref[str]()

    dados_detectados = []
    checkboxes = []

    lista_dados = ft.ListView(expand=True, spacing=10, padding=10)

    # Use a cor do tema para o texto de status
    status = ft.Text(f"Selecione um arquivo para continuar...", color=page.theme_mode_text_color, weight='bold')

    dropdown_filtro = criar_dropdown_filtro(
        lambda e: aplicar_filtro(e, dropdown_filtro, lista_dados, checkboxes)
    )

    btn_abrir_pdf = ft.IconButton(icon=ft.Icons.DOWNLOAD, visible=False, icon_color=page.theme_mode_text_color)

    btn_detectar = ft.IconButton(
        icon=ft.Icons.SEARCH,
        visible=False,
        icon_color=page.theme_mode_text_color,
        tooltip="Detectar Dados",
        on_click=lambda e: detectar(
            e,
            page,
            dropdown_filtro,
            lista_dados,
            painel_pdf,
            btn_anonimizar,
            status,
            nome_arquivo_copiado,
            dados_detectados,
            checkboxes,
            gerar_imagens_do_pdf,
        ),
    )

    btn_selecionar_pdf = ft.IconButton(
        icon=ft.Icons.FOLDER_OPEN,
        icon_color=page.theme_mode_text_color,
        tooltip="Selecionar PDF",
        on_click=lambda _: abrir_picker.pick_files(
            dialog_title="Escolha um PDF",
            allow_multiple=False,
            allowed_extensions=["pdf"]
        )
    )

    btn_anonimizar = ft.IconButton(
        icon=ft.Icons.LOCK,
        icon_color=page.theme_mode_text_color,
        visible=False,
        on_click=lambda e: anonimizar_selecionados(
            e,
            page,
            nome_arquivo_copiado,
            checkboxes,
            status,
            btn_abrir_pdf,
            painel_pdf,
            gerar_imagens_do_pdf,
            abrir_pdf
        ),
    )

    # Header
    logo_path = resource_path("assets/logo.png") if page.theme_mode == ft.ThemeMode.DARK else resource_path("assets/logo_dark.png")
    header = ft.Container(
        height=50,
        bgcolor=page.theme_mode_background_color, # Use cor do tema
        content=ft.Row(
            controls=[
                ft.Image(ref=logo_img, src=logo_path, width=40, height=40),
                btn_selecionar_pdf,
                btn_detectar,
                btn_anonimizar,
                btn_abrir_pdf,
                ft.Container(expand=True),
                ft.Text("versão 1.0", size=12, color=page.theme_mode_text_color), # Cor do texto da versão
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=40,
        ),
        margin=ft.margin.only(left=20),
    )    

    # Menu lateral esquerdo
    sidebar = ft.Container(
        width=60,
        height=900,
        bgcolor=page.theme_mode_background_color, # Use cor do tema
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.PERSON_3, color=page.theme_mode_text_color), # Cor do ícone
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    icon_color=page.theme_mode_text_color, # Cor do ícone do botão
                    tooltip="Configurações",
                    on_click=lambda e: mostrar_tela_configuracoes(
                        page, 
                        lambda: mostrar_tela_principal(page, header, corpo, texto, sidebar, 
                                                       painel_dados_detectados, painel_pdf, status, 
                                                       detalhes_anonimizacao) # Passa todos os componentes necessários
                    )
                )
            ],
            spacing=25,
            alignment=ft.MainAxisAlignment.END,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=15,
        alignment=ft.alignment.top_center,
    )

    # Lista de dados detectados
    painel_dados_detectados = ft.Container(
        width=300,
        height=900,
        bgcolor=page.theme_mode_background_color, # Use cor do tema
        content=ft.Column([
            ft.Text("Dados detectados", color=page.theme_mode_text_color, size=18, weight=ft.FontWeight.BOLD), # Cor do texto
            dropdown_filtro,
            lista_dados
        ],
        scroll=ft.ScrollMode.AUTO),
        padding=20
    )

    log_painel = ft.ExpansionTile(
        title=ft.Text("Logs", color="white"),
        subtitle=ft.Text("Clique para expandir ou recolher", color="#bbbbbb", size=12),
        bgcolor="#1e1e1e",
        initially_expanded=False,
        controls=[
            ft.Container(
                height=150,
                content=ft.ListView(
                    ref=log_ref,
                    spacing=5,
                    padding=10,
                    expand=True,
                    auto_scroll=True
                ),
                padding=10
            )
        ]
    )


    # Título da área de trabalho
    detalhes_anonimizacao = ft.Container(
        content=ft.Text("Detalhes da anonimização", color=page.theme_mode_text_color, size=16), # Cor do texto
        padding=10,
        height=869,
    )

    # Área de visualização PDF (painel direito)
    painel_pdf = ft.Container(
        bgcolor=page.theme_mode_content_background_color, # Use cor do tema
        expand=True,
        content=ft.Column([
            detalhes_anonimizacao,
            ft.Container(
                alignment=ft.alignment.center,
                content=ft.Text("PDF", size=15, color=page.theme_mode_pdf_text_color), # Cor do texto do PDF
                bgcolor=page.theme_mode_pdf_background_color, # Cor de fundo do PDF
                expand=True
            )
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO
        ),
        padding=30,
        border_radius=12,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color="#00000020",
            offset=ft.Offset(0, 2)
        ),
        height=840
    )

    abrir_picker = ft.FilePicker(
        on_result=lambda e: selecione_arquivo(
            e,
            page,
            lista_dados,
            dados_detectados,
            checkboxes,
            btn_anonimizar,
            btn_selecionar_pdf,
            painel_pdf,
            nome_arquivo_copiado,
            status,
            btn_detectar,
            gerar_imagens_do_pdf
        )
    )

    page.overlay.append(abrir_picker)

    # Rodapé
    texto = ft.Text(
        "Desenvolvido por: Douglas Brian - Ezequiel Pacheco - Gabriel Garcia",
        size=12,
        color=page.theme_mode_text_color # Use cor do tema
    )

    # Corpo principal da página
    corpo = ft.Row([
        sidebar,
        painel_dados_detectados,
        painel_pdf
    ],
    expand=True)

    # Adicionar tudo à página
    page.add(
        header,
        ft.Divider(thickness=1, color=page.theme_mode_color, height=10),
        corpo,
        ft.Divider(thickness=1, color=page.theme_mode_color, height=10),
        log_painel,
        texto
    )
    
ft.app(target=main)