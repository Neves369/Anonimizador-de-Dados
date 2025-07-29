import flet as ft

def main(page: ft.Page):
    page.title = "Configurações"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1e1e1e"  # Cor de fundo escura

    # Título da janela
    title = ft.Text("Configurações", size=20, weight=ft.FontWeight.BOLD)

    # Menu lateral com uma aba chamada "Preferências"
    menu = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Preferências", size=16, weight=ft.FontWeight.NORMAL)
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        width=200,
        padding=10,
        border=ft.border.all(1, "#444444"),
    )

    # Conteúdo vazio da direita (pode ser preenchido com futuras opções)
    content_area = ft.Container(
        content=None,
        expand=True,
        bgcolor="#1e1e1e"
    )

    # Layout principal
    layout = ft.Row(
        controls=[
            menu,
            content_area
        ],
        expand=True
    )

    # Adicionando tudo na página
    page.add(title, layout)

ft.app(target=main)
