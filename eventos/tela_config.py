import flet as ft

def mostrar_tela_configuracoes(page: ft.Page, voltar_callback):

    def toggle_theme(e):
        # Alterna entre tema claro e escuro
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        page.update() # Atualiza a página para aplicar o novo tema

    preferencias_menu = ft.Container(
        width=200,
        bgcolor="#21282B",
        content=ft.Column(
            controls=[
                ft.Text("Preferências", color="white", size=16)
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=20,
    )

    area_configuracoes = ft.Container(
        expand=True,
        bgcolor="#21282B",
        content=ft.Column(
            controls=[
                ft.Text("Tela de Configurações", color="white", size=20),
                ft.ElevatedButton(
                    text="Voltar",
                    on_click=lambda e: voltar_callback()
                ),
                ft.ElevatedButton( # Novo botão para alternar tema
                    text="Alternar Tema (Claro/Escuro)",
                    on_click=toggle_theme
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=20
        ),
        padding=30
    )

    conteudo = ft.Row(
        controls=[preferencias_menu, area_configuracoes],
        expand=True
    )

    page.controls.clear()
    page.add(conteudo)
    page.update()