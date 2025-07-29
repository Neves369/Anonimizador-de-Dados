# modules/log.py

import flet as ft

log_ref = None  # Essa referência será definida externamente (em main.py)

def set_log_ref(ref):
    global log_ref
    log_ref = ref

def log_mensagem(msg: str, tipo="info"):
    cor = {
        "info": "white",
        "erro": "#ff4c4c",
        "sucesso": "#4caf50"
    }.get(tipo, "white")

    if log_ref and log_ref.current:
        log_ref.current.controls.append(ft.Text(msg, color=cor, size=12))
        log_ref.current.update()
