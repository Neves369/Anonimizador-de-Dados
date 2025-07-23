
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
from ui_config import configurar_pagina
from helpers import resource_path, gerar_imagens_do_pdf


import sys 


def main(page: ft.Page):

    configurar_pagina(page)

    nome_arquivo_copiado = ft.Ref[str]()
    dados_detectados = []
    checkboxes = []


    lista_dados = ft.ListView(expand=True, spacing=10, padding=10)

    status = ft.Text(f"Selecione um arquivo para continuar...", color="#666666", weight='bold')

    dropdown_filtro = criar_dropdown_filtro(
        lambda e: aplicar_filtro(e, dropdown_filtro, lista_dados, checkboxes)
    )


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
    
    abrir_picker = ft.FilePicker(
        on_result=lambda e: selecione_arquivo(
            e,
            page,
            lista_dados,
            dados_detectados,
            checkboxes,
            btn_anonimizar,
            botao_abrir_pdf,
            painel_direito,
            nome_arquivo_copiado,
            status,
            btn_detectar,
            gerar_imagens_do_pdf
        )
    )

    page.overlay.append(abrir_picker)

    # Botões do painel esquerdo
    btn_selecionar = ft.ElevatedButton("📂 Selecionar PDF", on_click=lambda _: abrir_picker.pick_files(
        dialog_title="Escolha um PDF", allow_multiple=False, allowed_extensions=["pdf"]
    ), width=400, color="white")
    btn_detectar = ft.ElevatedButton(
        "🔍 Detectar Dados",
        visible=False,
        width=400,
        color="white",
        on_click=lambda e: detectar(
            e,
            page,
            dropdown_filtro,
            lista_dados,
            painel_direito,
            btn_anonimizar,
            status,
            nome_arquivo_copiado,
            dados_detectados,
            checkboxes,
            gerar_imagens_do_pdf
        )
    )
    btn_anonimizar = ft.ElevatedButton(
    "🔐 Anonimizar",
    visible=False,
    on_click=lambda e: anonimizar_selecionados(
        e,
        page,
        nome_arquivo_copiado,
        checkboxes,
        status,
        botao_abrir_pdf,
        painel_direito,
        gerar_imagens_do_pdf,
        abrir_pdf  # essa função deve estar definida ou importada no main.py
    ),
    width=400,
    color="white"
    )

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
            ft.Text(
                "Dados Detectados",
                size=18,
                color="#999999",
                text_align=ft.TextAlign.CENTER
            ),
            dropdown_filtro,
            status,
            lista_dados
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