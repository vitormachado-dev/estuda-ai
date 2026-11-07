# Estuda AI 📚🤖

Assistente de estudos que responde perguntas e gera flashcards a partir do conteúdo de PDFs, usando **RAG (Retrieval-Augmented Generation)** com a API do Google Gemini.

Criei este projeto para resolver um problema real meu: estudo para concursos de TI com muito material em PDF e queria uma forma rápida de tirar dúvidas e revisar o conteúdo.

![Tela do Estuda AI](docs/tela.png)

## Funcionalidades

- **Interface web:** envie um PDF pelo navegador e use tudo sem precisar do terminal
- **Perguntas e respostas:** faça perguntas sobre o material e receba respostas baseadas apenas no conteúdo do PDF
- **Gerador de flashcards:** escolha um tema e gere flashcards prontos para importar no Anki
- **Recusa de temas fora do material:** se o assunto não estiver no PDF, o programa avisa em vez de inventar
- **Tolerância a falhas:** novas tentativas automáticas quando a API fica instável

## Como funciona

```
PDF → extração de texto → limpeza → chunks → embeddings → busca por similaridade → resposta da IA
```

1. **Extração e limpeza:** lê o texto do PDF e remove cabeçalhos e rodapés repetidos
2. **Chunks:** divide o texto em pedaços com sobreposição, para não perder contexto
3. **Embeddings:** transforma cada pedaço em um vetor que representa seu significado
4. **Busca:** compara a pergunta com os pedaços usando similaridade de cosseno e descarta trechos abaixo de uma nota mínima de relevância
5. **Resposta:** envia apenas os trechos relevantes para o modelo, que responde com base neles

### Decisões de projeto

- **Redução de alucinações:** o modelo é instruído a responder somente com base no material. Se nenhum trecho atingir a nota mínima de similaridade, o programa nem chama a IA, o que também economiza cota.
- **Saída estruturada:** os flashcards usam JSON com schema definido (Pydantic), garantindo que cada card tenha sempre pergunta e resposta no formato esperado pelo código.
- **Retry com backoff exponencial:** em erros temporários da API (429, 500, 503), o programa espera e tenta de novo (2s, 4s, 8s) antes de desistir.
- **Cache do índice:** os embeddings não são gerados de novo a cada execução (arquivo no terminal, `st.cache_data` na interface web).
- **Separação entre lógica e interface:** a interface web reaproveita as mesmas funções usadas no terminal, sem duplicar código.

## Estrutura

| Arquivo | Responsabilidade |
|---|---|
| `app.py` | Interface web com Streamlit (upload, chat e flashcards) |
| `chunks.py` | Extração, limpeza e divisão do texto |
| `busca.py` | Embeddings, índice, busca por similaridade e retry |
| `responder.py` | Montagem do prompt e geração da resposta |
| `flashcards.py` | Geração de flashcards por tema, com saída estruturada e exportação para CSV/Anki |
| `test_chunks.py` | Testes automatizados da limpeza e divisão do texto |

## Tecnologias

- Python
- Google Gemini API (geração de texto e embeddings)
- Streamlit
- pypdf
- Pydantic
- pytest

## Como rodar

```bash
git clone https://github.com/vitormachado-dev/estuda-ai.git
cd estuda-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crie um arquivo `.env` com base no `.env.example` e coloque sua chave do [Google AI Studio](https://aistudio.google.com).

**Interface web (recomendado):**

```bash
streamlit run app.py
```

A página abre no navegador. Envie um PDF e use as abas de perguntas e flashcards.

**Pelo terminal:** coloque um PDF na pasta com o nome `aula.pdf` e execute:

```bash
python responder.py      # perguntas e respostas
python flashcards.py     # flashcards (salvos em flashcards.csv, prontos para o Anki)
```

## Testes

```bash
pytest
```

Os testes cobrem a limpeza e a divisão do texto (`chunks.py`), sem depender da API. Eles já ajudaram a encontrar e corrigir um bug em que PDFs com poucas páginas perdiam todo o conteúdo na etapa de limpeza.

## Próximos passos

- [x] Geração automática de flashcards
- [x] Novas tentativas automáticas em caso de instabilidade da API
- [x] Interface web
- [ ] Suporte a vários PDFs