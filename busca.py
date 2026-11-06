import json
import math
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from chunks import extrair_texto, remover_repetidas, dividir_em_chunks

load_dotenv(Path(__file__).parent / ".env")
client = genai.Client()

MODELO_EMBEDDING = "gemini-embedding-001"
ARQUIVO_INDICE = Path(__file__).parent / "indice.json"


def gerar_embeddings(textos):
    # manda uma lista de textos e recebe uma lista de vetores (listas de números)
    resultado = client.models.embed_content(model=MODELO_EMBEDDING, contents=textos)
    return [e.values for e in resultado.embeddings]


def criar_indice(caminho_pdf):
    paginas = extrair_texto(caminho_pdf)
    texto = remover_repetidas(paginas)
    chunks = dividir_em_chunks(texto)

    vetores = gerar_embeddings(chunks)
    indice = [{"texto": c, "vetor": v} for c, v in zip(chunks, vetores)]

    # salva em arquivo pra não precisar gerar de novo toda vez
    ARQUIVO_INDICE.write_text(json.dumps(indice), encoding="utf-8")
    return indice


def carregar_indice():
    return json.loads(ARQUIVO_INDICE.read_text(encoding="utf-8"))


def similaridade(a, b):
    # similaridade de cosseno: perto de 1 = significados parecidos
    produto = sum(x * y for x, y in zip(a, b))
    norma_a = math.sqrt(sum(x * x for x in a))
    norma_b = math.sqrt(sum(y * y for y in b))
    return produto / (norma_a * norma_b)


def buscar(pergunta, indice, quantidade=3):
    vetor_pergunta = gerar_embeddings([pergunta])[0]
    pontuados = [
        (similaridade(vetor_pergunta, item["vetor"]), item["texto"])
        for item in indice
    ]
    pontuados.sort(reverse=True)   # maior similaridade primeiro
    return pontuados[:quantidade]


if __name__ == "__main__":
    if ARQUIVO_INDICE.exists():
        indice = carregar_indice()
        print("Índice carregado do arquivo.")
    else:
        print("Gerando embeddings, aguarde...")
        indice = criar_indice("aula.pdf")
        print("Índice criado com", len(indice), "chunks.")

    pergunta = input("\nSua pergunta: ")
    resultados = buscar(pergunta, indice)

    for pontuacao, texto in resultados:
        print(f"\n--- Similaridade: {pontuacao:.3f} ---")
        print(texto[:300])