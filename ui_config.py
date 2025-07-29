# ui_config.py
import flet as ft

def apply_theme_colors(page: ft.Page):
    """Aplica as cores do tema à página com base no theme_mode atual."""
    if page.theme_mode == ft.ThemeMode.DARK:
        page.theme_mode_background_color = "#21282B"
        page.theme_mode_content_background_color = "#232D31"
        page.theme_mode_text_color = "white"
        page.theme_mode_color = ft.Colors.WHITE
        page.theme_mode_pdf_text_color = "#1e1e1e"  # Texto do PDF no tema escuro
        page.theme_mode_pdf_background_color = "#cccccc"  # Fundo do PDF no tema escuro
    else:  # ft.ThemeMode.LIGHT
        page.theme_mode_background_color = "#ffffff"
        page.theme_mode_content_background_color = "#B3B3B3"
        page.theme_mode_text_color = "#000000"
        page.theme_mode_color = ft.Colors.BLACK
        page.theme_mode_pdf_text_color = "#000000"  # Texto do PDF no tema claro
        page.theme_mode_pdf_background_color = "#838383"  # Fundo do PDF no tema claro
        page.theme_mode_image_color = "#000000"
    
    # Atualiza o background da página principal
    page.bgcolor = page.theme_mode_background_color
    page.update()

def configurar_pagina(page: ft.Page):
    page.title = "Anonimizador"
    page.window_width = 1200
    page.window_height = 900 # Usando o valor mais alto definido
    page.padding = 0
    page.spacing = 0
    page.window.maximized = True # Maximiza a janela ao iniciar

    page.theme_mode = ft.ThemeMode.DARK  # Tema padrão inicial
    
    # Chama a função para aplicar as cores do tema na inicialização
    apply_theme_colors(page)
    
    page.update()