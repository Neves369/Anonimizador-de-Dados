import flet as ft

def aplicar_filtro(e, dropdown_filtro, lista_dados, checkboxes):
    filtro = dropdown_filtro.value
    lista_dados.controls.clear()

    if filtro == "Todos":
        for cb in checkboxes:
            lista_dados.controls.append(cb)
    else:
        for cb in checkboxes:
            if cb.data.get("label") == filtro:
                lista_dados.controls.append(cb)

    lista_dados.update()

def criar_dropdown_filtro(callback):
    return ft.Dropdown(
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("RG"),
            ft.dropdown.Option("CPF"),
            ft.dropdown.Option("Endereço"),
            ft.dropdown.Option("OAB"),
            ft.dropdown.Option("Email"),
            ft.dropdown.Option("Imagem"),
            ft.dropdown.Option("Telefone"),
        ],
        value="Todos",
        on_change=callback,
        width=160,
        visible=False
    )
