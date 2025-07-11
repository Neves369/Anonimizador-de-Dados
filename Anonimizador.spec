# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files
import pt_core_news_lg  # necessário para pegar o caminho do modelo

def collect_folder(folder_path, target_folder):
    datas = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, folder_path)
            datas.append((full_path, os.path.join(target_folder, rel_path)))
    return datas

# Caminho do modelo spaCy
model_dir = pt_core_news_lg.__path__[0]
datas = collect_folder(model_dir, 'pt_core_news_lg')

# Outros recursos
datas.append(('assets/logo.png', 'assets'))
datas += collect_folder(os.path.abspath('data'), 'data')
datas += collect_folder(os.path.abspath('output'), 'output')
datas += collect_data_files('spacy')
datas += collect_data_files('spacy.lang.pt')

a = Analysis(
    ['screen2.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'modules.read',
        'modules.processText',
        'modules.processImage',
        'spacy.lang.pt',
        'spacy.lang.en',
        'spacy.vocab',
        'spacy.tokenizer',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Anonimizador',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Anonimizador'
)
