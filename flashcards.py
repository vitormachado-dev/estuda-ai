import csv
from pydantic import BaseModel
from busca import client, carregar_indice, criar_indice, buscar, ARQUIVO_INDICE, com_novas_tentativas

MODELO = "gemini-3.5-flash-lite"


class Flashcard(BaseModel):
    # o "molde" que a IA é obrigada a seguir
    pergunta: str
    resposta: str


def gerar_flashcards(tema, indice, quantidade=5):
    trechos = buscar(tema, indice, quantidade=4)
    if not trechos:   # tema não está no material: nem chama a IA
        return []

    contexto = "\n\n---\n\n".join(texto for _, texto in trechos)
    prompt = f"""Crie até {quantidade} flashcards de estudo sobre o tema "{tema}",
usando APENAS o material abaixo. Cada flashcard deve ter uma pergunta objetiva
e uma resposta curta (até 2 frases). Não invente informações.
Se o material não tiver relação com o tema, devolva uma lista vazia.

MATERIAL:
{contexto}"""

    resposta = com_novas_tentativas(
        lambda: client.models.generate_content(
            model=MODELO,
            contents=prompt,
            config={
                "response_mime_type": "application/json",   # responde em JSON
                "response_schema": list[Flashcard],          # no formato do molde
            },
        )
    )
    return resposta.parsed or []   # se vier vazio, devolve lista vazia


def salvar_csv(flashcards, caminho="flashcards.csv"):
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        for card in flashcards:
            escritor.writerow([card.pergunta, card.resposta])


if __name__ == "__main__":
    indice = carregar_indice() if ARQUIVO_INDICE.exists() else criar_indice("aula.pdf")

    tema = input("Tema dos flashcards: ")
    flashcards = gerar_flashcards(tema, indice)

    if not flashcards:
        print("\nNão encontrei conteúdo sobre esse tema no material.")
    else:
        for i, card in enumerate(flashcards, start=1):
            print(f"\n{i}. P: {card.pergunta}")
            print(f"   R: {card.resposta}")
        salvar_csv(flashcards)
        print("\nFlashcards salvos em flashcards.csv")