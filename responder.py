from busca import client, carregar_indice, criar_indice, buscar, ARQUIVO_INDICE, com_novas_tentativas

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
    trechos = buscar(pergunta, indice)
    if not trechos:   # nada relevante: nem chama a IA
        return "Não encontrei essa informação no material."
    prompt = montar_prompt(pergunta, trechos)
    resposta = com_novas_tentativas(
        lambda: client.models.generate_content(model=MODELO_RESPOSTA, contents=prompt)
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