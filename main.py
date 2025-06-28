import os
import fitz
import inquirer
import re
from modules import read

def main():

    os.system('cls')

    print("""
     ____________________________________________________________________
    |--------------------------------------------------------------------|
    |      ██╗    ███████████╗     ██████╗██████╗███╗   ██████████╗      |
    |      ██║    ████╔════██║    ██╔════██╔═══██████╗ ██████╔════╝      |
    |      ██║ █╗ ███████╗ ██║    ██║    ██║   ████╔████╔███████╗        |
    |      ██║███╗████╔══╝ ██║    ██║    ██║   ████║╚██╔╝████╔══╝        |
    |      ╚███╔███╔██████████████╚██████╚██████╔██║ ╚═╝ █████████╗      |
    |       ╚══╝╚══╝╚══════╚══════╝╚═════╝╚═════╝╚═╝     ╚═╚══════╝      |
    |                                                                    |
    |----------------Anonimizador de Dados Pessoais----------------------|
    |--Este escript ele um arquivo em PDF e gera um novo                 | 
    |  arquivo sem os dados pessoais.                                    | 
    |                                                                    |
    |                                                                    |
    |--------------------------------------------------------------------|
    |____________________________________________________________________| 
  """) 

    # listar arquivos da pasta data
    caminhos = [os.path.join("data", nome) for nome in os.listdir("data")]
    arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
    pdfs = [arq[5:] for arq in arquivos if arq.lower().endswith(".pdf")]


    questions = [
        inquirer.List(
            'filename',
            message="Selecione o arquivo: ",
            choices=pdfs,
        )    
    ]

    answers = inquirer.prompt(questions)
    filename =  answers["filename"]

    if (os.path.exists('output') == False):
        try:
            os.mkdir('output')
        except:
            print("Não foi possível criar diretório") 

    cpfs_encontrados, telefones_encontrados, texto_tajado = read.read_pdf(filename=filename)


    # Criação do PDF com o texto tarjado
    create_pdf(texto_tajado, filename)

    confirm = {
        inquirer.Confirm(
            'confirmed',
            message="Deseja sair?" ,
            default=True),
    }
    confirmation = inquirer.prompt(confirm)

    if(confirmation["confirmed"]):
        quit()


def create_pdf(textos_tarjar, filename):
    caminho_arquivo = os.path.join('data', filename)
    nome_arquivo, ext = os.path.splitext(filename)
    caminho_saida = os.path.join('output', f"{nome_arquivo}_tarjado{ext}")

    doc = fitz.open(caminho_arquivo)


    padroes = [
        r'\d{3}\.\d{3}\.\d{3}-\d{2}',
        r'\(\d{2}\)\s?\d{4,5}-\d{4}',
    ]

    for pagina in doc:
        texto_pagina = pagina.get_text()
        for padrao in padroes:
            for match in re.findall(padrao, texto_pagina):
                areas = pagina.search_for(match)
                for area in areas:
                    pagina.add_redact_annot(area, fill=(0, 0, 0))
        pagina.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    doc.save(caminho_saida)
    print(f"Novo arquivo gerado: {caminho_saida}")

if __name__ == '__main__':
    while True:
        main()
