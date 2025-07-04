import fitz  # PyMuPDF

doc = fitz.open("data/documento.pdf")
print("Páginas:", doc.page_count)
doc.close()