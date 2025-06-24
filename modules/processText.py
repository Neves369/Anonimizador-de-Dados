# Verifica se é um CPF válido, de acordo com os cálculos da Receita Federal 
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

# Usa Regex para uma verificação simples de CPF's (encontra CPF's)
def simple_find_cpfs(filename):
    cpfs_encontrados = []
    regex_cpf = r'\b(?:\d{3}[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{2}|\d{11})\b'

    try:
        caminho_completo = "data\\" + filename
        doc = fitz.open(caminho_completo)
        
        for pagina_num in range(doc.page_count):
            pagina = doc[pagina_num]
            texto_pagina = pagina.get_text("text")
            
            if texto_pagina:
                cpfs_na_pagina = re.findall(regex_cpf, texto_pagina)
                for cpf in cpfs_na_pagina:
                    cpf_limpo = re.sub(r'[\s.-]', '', cpf)
                    if len(cpf_limpo) == 11 and verifica_cpf(cpf_limpo):
                        cpfs_encontrados.append(cpf_limpo)
        
        doc.close()
            
    except fitz.FileNotFoundError:
        print(f"Erro: O arquivo PDF '{filename}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao ler o PDF: {e}")

    return cpfs_encontrados

# Processa o texto buscando dados pressoais
def process_text(filename):
    cpfs = simple_find_cpfs(filename)

    print("cpfs encontrados: ", cpfs)


