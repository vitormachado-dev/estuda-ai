import json
import math
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from chunks import extrair_texto, remover_repetidas, dividir_em_chunks

load_dotenv(Path(__file__).parent / ".env")
client = genai.Client()

MODELO_EMBEDDING = "gemini-embedding-001"
ARQUIVO_INDICE = Path(__file__).parent / "indice.json"
ERROS_TEMPORARIOS = (429, 500, 503)   # limite estourado ou servidor com problema
NOTA_MINIMA = 0.65                    # abaixo disso, o trecho não tem relação real com a pergunta


def com_novas_tentativas(funcao, tentativas=3, espera=2):
    # executa a função; se der erro temporário, espera e tenta de novo
    for tentativa in range(1, tentativas + 1):
        try:
            return funcao()
        except errors.APIError as erro:
            if erro.code not in ERROS_TEMPORARIOS or tentativa == tentativas:
                raise
            print(f"Erro {erro.code} (temporário). Tentando de novo em {espera}s...")
            time.sleep(espera)
            espera *= 2   # 2s, 4s, 8s


def gerar_embeddings(textos):
    resultado = com_novas_tentativas(
        lambda: client.models.embed_content(model=MODELO_EMBEDDING, contents=textos)
    )
    return [e.values for e in resultado.embeddings]


def criar_indice(caminho_pdf):
    paginas = extrair_texto(caminho_pdf)
    texto = remover_repetidas(paginas)
    chunks = dividir_em_chunks(texto)

    vetores = gerar_embeddings(chunks)
    indice = [{"texto": c, "vetor": v} for c, v in zip(chunks, vetores)]

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
    pontuados.sort(reverse=True)
    relevantes = [(nota, texto) for nota, texto in pontuados if nota >= NOTA_MINIMA]
    return relevantes[:quantidade]   # pode voltar vazia se nada for relevante


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

    if not resultados:
        print("\nNenhum trecho relevante encontrado.")
    for pontuacao, texto in resultados:
        print(f"\n--- Similaridade: {pontuacao:.3f} ---")
        print(texto[:300])