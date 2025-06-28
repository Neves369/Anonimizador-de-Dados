import re
import fitz 


def verifica_cpf(strCPF: str) -> bool:
    strCPF = ''.join(filter(str.isdigit, strCPF))
    
    if len(strCPF) != 11:
        return False
    if len(set(strCPF)) == 1:
        return False

    Soma = 0
    Resto = 0

    for i in range(9):
        Soma = Soma + int(strCPF[i]) * (10 - i)
    Resto = (Soma * 10) % 11
    if (Resto == 10) or (Resto == 11):
        Resto = 0

    if Resto != int(strCPF[9]):
        return False

    Soma = 0
    for i in range(10):
        Soma = Soma + int(strCPF[i]) * (11 - i)
    Resto = (Soma * 10) % 11
    if (Resto == 10) or (Resto == 11):
        Resto = 0

    if Resto != int(strCPF[10]):
        return False

    return True

# Verificação simples de CPF e Telefone
def simple_find(filename):
    cpfs_encontrados = []
    telefones_encontrados = []
    regex_cpf = r'\b(?:\d{3}[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{2}|\d{11})\b'
    regex_telefone = r'\(?\d{2}\)?\s?-?\d{4,5}\s?-?\d{4}'
    
    try:
        caminho_completo = "data\\" + filename
        doc = fitz.open(caminho_completo)

        for pagina_num in range(doc.page_count):
            pagina = doc[pagina_num]
            texto_pagina = pagina.get_text("text")
            
            if texto_pagina:
                # Encontra CPFs e Telefones no texto
                cpfs_na_pagina = re.findall(regex_cpf, texto_pagina)
                telefones_na_pagina = re.findall(regex_telefone, texto_pagina)

                # Tarja os telefones encontrados
                for telefone in telefones_na_pagina:
                    telefone_limpo = re.sub(r'[\s().-]', '', telefone)
                    telefones_encontrados.append(telefone_limpo)
                    texto_pagina = re.sub(re.escape(telefone), "(XX) XXXXX-XXXX", texto_pagina)

                # Tarja os CPFs encontrados
                for cpf in cpfs_na_pagina:
                    cpf_limpo = re.sub(r'[\s.-]', '', cpf)
                    if len(cpf_limpo) == 11 and verifica_cpf(cpf_limpo):
                        cpfs_encontrados.append(cpf_limpo)
                        texto_pagina = re.sub(re.escape(cpf), "XXX.XXX.XXX-XX", texto_pagina)


        doc.close()
    
    except fitz.FileNotFoundError:
        print(f"Erro: O arquivo PDF '{filename}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao ler o PDF: {e}")
    
    return cpfs_encontrados, telefones_encontrados, texto_pagina

# Função principal para processar o texto do PDF
def process_text(filename):
    cpfs_encontrados, telefones_encontrados, texto_tajado = simple_find(filename)
    
    return cpfs_encontrados, telefones_encontrados, texto_tajado

