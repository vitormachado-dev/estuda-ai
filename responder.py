from busca import client, carregar_indice, criar_indice, buscar, ARQUIVO_INDICE

MODELO_RESPOSTA = "gemini-3.5-flash-lite"


def montar_prompt(pergunta, trechos):
    contexto = "\n\n---\n\n".join(texto for _, texto in trechos)
    return f"""Você é um assistente de estudos. Responda à pergunta usando APENAS
o conteúdo do material abaixo. Se a resposta não estiver no material,
diga que não encontrou essa informação no material.

MATERIAL:
{contexto}

PERGUNTA: {pergunta}

RESPOSTA:"""


def responder(pergunta, indice):
    trechos = buscar(pergunta, indice)          # 1. busca os trechos mais parecidos
    prompt = montar_prompt(pergunta, trechos)    # 2. monta o prompt com os trechos
    resposta = client.models.generate_content(   # 3. manda pra IA responder
        model=MODELO_RESPOSTA, contents=prompt
    )
    return resposta.text


if __name__ == "__main__":
    indice = carregar_indice() if ARQUIVO_INDICE.exists() else criar_indice("aula.pdf")

    print("Faça perguntas sobre o material. Digite 'sair' para encerrar.")
    while True:
        pergunta = input("\nPergunta: ")
        if pergunta.lower() == "sair":
            break
        print("\n" + responder(pergunta, indice))