import re
from collections import Counter
from pypdf import PdfReader

def extrair_texto(caminho_pdf):
    leitor = PdfReader(caminho_pdf)
    paginas = [p.extract_text() or "" for p in leitor.pages]
    return paginas

def normalizar(linha):
    # tira os números pra comparar: "Ronaldo C. Oliveira 3" vira "Ronaldo C. Oliveira"
    return re.sub(r"\d+", "", linha).strip()

def remover_repetidas(paginas):
    contagem = Counter(
        normalizar(linha) for pagina in paginas for linha in pagina.splitlines()
    )
    limite = max(2, len(paginas) * 0.3)   # no mínimo 2: linha que aparece 1 vez nunca é cabeçalho

    texto_limpo = []
    for pagina in paginas:
        linhas_boas = [
            l for l in pagina.splitlines()
            if normalizar(l) and contagem[normalizar(l)] < limite
        ]
        texto_limpo.append("\n".join(linhas_boas))
    return "\n".join(texto_limpo)

def dividir_em_chunks(texto, tamanho=1000, sobreposicao=200):
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        chunks.append(texto[inicio:fim])
        inicio += tamanho - sobreposicao
    return chunks

if __name__ == "__main__":
    paginas = extrair_texto("aula.pdf")
    texto = remover_repetidas(paginas)
    chunks = dividir_em_chunks(texto)

    print("Páginas:", len(paginas))
    print("Caracteres depois da limpeza:", len(texto))
    print("Total de chunks:", len(chunks))
    print("\n--- Chunk 1 ---\n")
    print(chunks[0])