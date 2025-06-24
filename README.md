# 🔒 PDF Anonymizer

Este projeto tem como objetivo **analisar arquivos PDF e remover ou anonimizar dados pessoais sensíveis**. Ele é capaz de identificar se o PDF contém texto digital ou é um documento escaneado (imagem), aplicar técnicas de *OCR*, *regex* e *machine learning* para extrair e identificar informações pessoais como CPF, nomes e outros dados identificáveis, e gerar uma nova versão do PDF com essas informações removidas ou mascaradas.

## 🚀 Funcionalidades

* 📄 Leitura de arquivos PDF
* 🔍 Detecção automática do tipo de conteúdo (texto digital ou imagem escaneada)
* 🧠 Identificação de dados pessoais com:

  * Expressões regulares (regex) para dados como CPF
  * Modelos de machine learning para identificar nomes, endereços, e outros dados sensíveis
* 🖼️ Aplicação de OCR em PDFs escaneados (imagem)
* ✂️ Remoção ou anonimização de dados pessoais
* 📁 Geração de novo PDF com os dados anonimizados

## 📦 Tecnologias Utilizadas

* Python 3
* [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
* [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
* [Pytesseract](https://pypi.org/project/pytesseract/)
* [Scikit-learn](https://scikit-learn.org/)
* [spaCy](https://spacy.io/) ou outro modelo de NER para identificação de entidades
* Regex
* OpenCV (para pré-processamento de imagens)

## 🛠️ Como Usar

1. Clone o repositório:

```bash
git clone https://github.com/neves369/anonimizador-de-dados.git
cd anonimizador-de-dados
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Certifique-se de ter o Tesseract OCR instalado e configurado no PATH.

4. Execute o script:

```bash
python main.py caminho/para/arquivo.pdf
```

5. O novo arquivo PDF com os dados anonimizados será gerado na mesma pasta, com o sufixo `_anon.pdf`.

## 📁 Estrutura do Projeto

```
pdf-anonymizer/
│
├── main.py              # Script principal
├── requirements.txt     # Dependências do projeto
└── README.md
```

## ⚠️ Aviso Legal

**Não é recomendado para uso em produção sem auditoria de conformidade com leis como a LGPD ou GDPR**.

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---