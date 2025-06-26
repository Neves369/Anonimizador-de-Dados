import re
import fitz

# Verifica se é um CPF válido, de acordo com os cálculos da Receita Federal 
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

# Tarja o CPF  
def tarja_cpf(cpf: str) -> str:
    cpf_limpo = re.sub(r'[\s.-]', '', cpf)
    # print(f"CPF limpo: {cpf_limpo}")
    return f"**************"
  

# Usa Regex para uma verificação simples de CPF's e Telefones
def simple_find(filename):
    cpfs_encontrados = []
    telefones_encontrados = []
    regex_cpf = r'\b(?:\d{3}[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{2}|\d{11})\b'
    regex_telefone = r'\(?\d{2}\)?\s?-?\d{4,5}\s?-?\d{4}'
    texto_modificado = ""

    try:
        caminho_completo = "data\\" + filename
        doc = fitz.open(caminho_completo)
       
        for pagina_num in range(doc.page_count):
            pagina = doc[pagina_num]
            texto_pagina = pagina.get_text("text")
            texto_pagina_mod = texto_pagina

            if texto_pagina:
                cpfs_na_pagina = re.findall(regex_cpf, texto_pagina)
                telefones_na_pagina = re.findall(regex_telefone, texto_pagina)

                # for telefone in telefones_na_pagina:
                #     telefone_limpo = re.sub(r'[\s().-]', '', telefone)
                #     telefones_encontrados.append(telefone_limpo)

                for cpf in cpfs_na_pagina:
                    cpf_limpo = re.sub(r'[\s.-]', '', cpf)
                    if len(cpf_limpo) == 11 and verifica_cpf(cpf_limpo):
                        cpfs_encontrados.append(cpf_limpo)

                        texto_pagina_mod = re.sub(
                            re.escape(cpf),
                            tarja_cpf(cpf),
                            texto_pagina_mod
                        )
                        
                texto_modificado += texto_pagina_mod

        doc.close()
            
    except fitz.FileNotFoundError:
        print(f"Erro: O arquivo PDF '{filename}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao ler o PDF: {e}")

    return cpfs_encontrados, telefones_encontrados, texto_modificado

# Processa o texto buscando dados pressoais
def process_text(filename):
    cpfs_encontrados, telefones_encontrados, texto_modificado = simple_find(filename)

    print("cpfs encontrados: ", cpfs_encontrados)
    # print("telefones encontrados: ", telefones_encontrados)
    print("Texto modificado: ", texto_modificado[:10000])  

