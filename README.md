# Estuda AI 📚🤖

Assistente de estudos que responde perguntas sobre o conteúdo de PDFs usando **RAG (Retrieval-Augmented Generation)** com a API do Google Gemini.

Criei este projeto para resolver um problema real meu: estudo para concursos de TI com muito material em PDF e queria uma forma rápida de tirar dúvidas e revisar o conteúdo.

## Como funciona

```
PDF → extração de texto → limpeza → chunks → embeddings → busca por similaridade → resposta da IA
```

1. **Extração e limpeza:** lê o texto do PDF e remove cabeçalhos e rodapés repetidos
2. **Chunks:** divide o texto em pedaços com sobreposição, para não perder contexto
3. **Embeddings:** transforma cada pedaço em um vetor que representa seu significado
4. **Busca:** compara a pergunta com os pedaços usando similaridade de cosseno
5. **Resposta:** envia apenas os trechos relevantes para o modelo, que responde com base neles

O modelo é instruído a responder **somente com base no material**. Se a informação não estiver no PDF, ele avisa em vez de inventar, o que reduz alucinações.

## Estrutura

| Arquivo | Responsabilidade |
|---|---|
| `chunks.py` | Extração, limpeza e divisão do texto |
| `busca.py` | Geração de embeddings, índice e busca por similaridade |
| `responder.py` | Montagem do prompt e geração da resposta |

## Tecnologias

- Python
- Google Gemini API (geração de texto e embeddings)
- pypdf

## Como rodar

```bash
git clone https://github.com/SEU_USUARIO/estuda-ai.git
cd estuda-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crie um arquivo `.env` com base no `.env.example` e coloque sua chave do [Google AI Studio](https://aistudio.google.com).

Coloque um PDF na pasta com o nome `aula.pdf` e execute:

```bash
python responder.py
```

## Próximos passos

- [ ] Geração automática de flashcards
- [ ] Novas tentativas automáticas em caso de instabilidade da API
- [ ] Suporte a vários PDFs