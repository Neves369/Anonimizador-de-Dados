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

    read.read_pdf(filename=filename)

    confirm = {
        inquirer.Confirm(
            'confirmed',
            message="Deseja sair?" ,
            default=True),
    }
    confirmation = inquirer.prompt(confirm)

    if(confirmation["confirmed"]):
        quit()




if __name__ == '__main__':
    while True:
        main()
