import os
import flet as ft
import shutil
import fitz
import helpers
from modules import processText
from modules import processImage
from collections import defaultdict
from functools import partial

teste = 'escaneado'  # ou 'texto', dependendo do tipo de processamento

def detectar(
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
    gerar_imagens_do_pdf
):
    # Exibe o dropdown de filtro
    dropdown_filtro.visible = True
    dropdown_filtro.value = "Todos"
    dropdown_filtro.update()

    selecionar_tudo_cb = ft.Checkbox(label=ft.Text("SELECIONAR TODOS OS DADOS", color="#ffffff", weight='bold'), value=False)

    def selecionar_tudo_changed(e):
        for cb in checkboxes:
            cb.value = selecionar_tudo_cb.value
        page.update()

    selecionar_tudo_cb.on_change = selecionar_tudo_changed

    if not nome_arquivo_copiado.current:
        status.value = "Nenhum arquivo selecionado."
        return

    status.value = "Detectando dados..."
    page.update()

    if teste == 'texto':
        dados = processText.detectar_dados(nome_arquivo_copiado.current)
    elif teste == 'escaneado':
        dados = processImage.detectar_dados(nome_arquivo_copiado.current)

    dados_detectados.clear()
    dados_detectados.extend(dados)

    caminho_pdf_original = os.path.join("data", nome_arquivo_copiado.current)
    
    if teste == 'texto':
        caminho_pdf_demarcado = processText.demarcar_dados(nome_arquivo_copiado.current, dados_detectados)
    elif teste == 'escaneado':
        caminho_pdf_demarcado = processImage.demarcar_dados(nome_arquivo_copiado.current, dados_detectados)

    nome_base, _ = os.path.splitext(nome_arquivo_copiado.current)
    pasta_imagens_demarcadas = os.path.join("data", "imagens", f"{nome_base}-DETECTADO")
    if os.path.exists(pasta_imagens_demarcadas):
        shutil.rmtree(pasta_imagens_demarcadas)

    if teste == 'texto':
        caminhos_imagens = gerar_imagens_do_pdf(caminho_pdf_demarcado, pasta_imagens_demarcadas)
    elif teste == 'escaneado':
        caminhos_imagens = helpers.gerar_caminhos_imagens_existentes(os.path.join("data", "imagens", f"{nome_base}"))


    painel_pdf.content.controls.clear()
    painel_pdf.content.controls.append(
        ft.Text(f"Visualização do PDF Demarcado ({len(caminhos_imagens)} páginas)", size=20, weight="bold", color="#555555")
    )
    for caminho in caminhos_imagens:
        painel_pdf.content.controls.append(
            ft.Container(
                content=ft.Image(src=caminho, width=600, fit=ft.ImageFit.CONTAIN),
                border=ft.border.all(2, "#cccccc"),
                border_radius=8,
                padding=10,
                margin=ft.Margin(0, 10, 0, 10),
                bgcolor="#fafafa"
            )
        )

    if teste == 'texto':
        imagens_detectadas = processText.detectar_imagens(caminho_pdf_original)

    checkboxes.clear()
    lista_dados.controls.clear()

    agrupado = defaultdict(list)
    for dado in dados_detectados:
        agrupado[dado["label"]].append(dado)

    for tipo, lista in agrupado.items():
        grupo_checkboxes = []

        selecionar_categoria_cb = ft.Checkbox(
            label=ft.Text(f"Selecionar todos [{tipo.upper()}]", color=page.theme_mode_text_color, weight="bold"),
            value=False
        )

        def toggle_grupo_checkbox(e, grupo):
            for cb in grupo:
                cb.value = e.control.value
            page.update()

        lista_dados.controls.append(ft.Divider(thickness=1, color=page.theme_mode_text_color))
        lista_dados.controls.append(selecionar_categoria_cb)

        for dado in lista:
            label = ft.Text(f"[{dado['label']}] {dado['texto']}", color=page.theme_mode_text_color, weight='bold')
            cb = ft.Checkbox(label=label, value=False)
            cb.data = dado
            grupo_checkboxes.append(cb)
            checkboxes.append(cb)
            lista_dados.controls.append(cb)

        selecionar_categoria_cb.on_change = partial(toggle_grupo_checkbox, grupo=grupo_checkboxes)
        lista_dados.controls.append(ft.Divider(thickness=1, color=page.theme_mode_text_color))

    # --- IMAGENS DETECTADAS ---
    if imagens_detectadas:
        grupo_imgs = []
        selecionar_imgs_cb = ft.Checkbox(
            label=ft.Text("Selecionar todas as IMAGENS", color=page.theme_mode_text_color, weight='bold'),
            value=False
        )

        def toggle_imgs(e):
            for cb in grupo_imgs:
                cb.value = e.control.value
            page.update()

        selecionar_imgs_cb.on_change = toggle_imgs
        lista_dados.controls.append(selecionar_imgs_cb)

        for img in imagens_detectadas:
            descricao = f"Imagem na página {img['pagina'] + 1} - ids {img['xrefs']}"
            cb = ft.Checkbox(label=ft.Text(descricao, color="#666666", weight='bold'), value=False)
            cb.data = {"label": "Imagem", "tipo": "imagem", **img}
            grupo_imgs.append(cb)
            checkboxes.append(cb)
            lista_dados.controls.append(cb)

        lista_dados.controls.append(ft.Divider(thickness=1, color=page.theme_mode_text_color))

    # --- PÁGINAS INTEIRAS ---
    doc = fitz.open(caminho_pdf_original)
    grupo_paginas = []

    selecionar_paginas_cb = ft.Checkbox(
        label=ft.Text("Selecionar TODAS as PÁGINAS INTEIRAS", color=page.theme_mode_text_color, weight='bold'),
        value=False
    )

    def toggle_paginas(e):
        for cb in grupo_paginas:
            cb.value = e.control.value
        page.update()

    selecionar_paginas_cb.on_change = toggle_paginas
    lista_dados.controls.append(selecionar_paginas_cb)

    for i in range(len(doc)):
        cb_pagina = ft.Checkbox(
            label=ft.Text(f"Página {i + 1} inteira", color=page.theme_mode_text_color, weight='bold'),
            value=False
        )
        cb_pagina.data = {"pagina": i, "completa": True}
        grupo_paginas.append(cb_pagina)
        checkboxes.append(cb_pagina)
        lista_dados.controls.append(cb_pagina)

    doc.close()

    lista_dados.controls.insert(0, selecionar_tudo_cb)

    resumo = [f"{tipo.upper()}: {len(lista)}" for tipo, lista in agrupado.items()]
    resumo_texto = " | ".join(resumo)

    status.value = (
        f"{len(checkboxes)} dados encontrados.\n"
        f"{resumo_texto}\n"
        f"Selecione as informações que deseja ocultar..."
    )

    btn_anonimizar.visible = True
    page.update()
