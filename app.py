import csv
import io
import streamlit as st
from chunks import extrair_texto, remover_repetidas, dividir_em_chunks
from busca import gerar_embeddings
from responder import responder
from flashcards import gerar_flashcards

TAMANHO_LOTE = 50   # quantos chunks mandar por vez pra API de embeddings

st.set_page_config(page_title="Estuda AI", page_icon="📚")
st.title("📚 Estuda AI")
st.caption("Faça perguntas e gere flashcards a partir dos seus PDFs")


@st.cache_data(show_spinner="Lendo e indexando o PDF...")
def montar_indice(conteudo):
    # o cache evita reprocessar o mesmo PDF a cada clique na página
    paginas = extrair_texto(io.BytesIO(conteudo))
    texto = remover_repetidas(paginas)
    chunks = dividir_em_chunks(texto)

    vetores = []
    for i in range(0, len(chunks), TAMANHO_LOTE):   # manda em lotes, pra PDFs grandes
        vetores += gerar_embeddings(chunks[i:i + TAMANHO_LOTE])
    return [{"texto": c, "vetor": v} for c, v in zip(chunks, vetores)]


def flashcards_para_csv(flashcards):
    # monta o CSV na memória, sem salvar arquivo no disco
    saida = io.StringIO()
    escritor = csv.writer(saida, delimiter=";")
    for card in flashcards:
        escritor.writerow([card.pergunta, card.resposta])
    return saida.getvalue()


# ---------- Upload do PDF ----------
arquivo = st.file_uploader("Envie um PDF", type="pdf")
if arquivo is None:
    st.info("Envie um PDF para começar.")
    st.stop()

indice = montar_indice(arquivo.getvalue())
if not indice:
    st.error("Não consegui extrair texto deste PDF. Ele pode ser escaneado (só imagem).")
    st.stop()

# se trocou de PDF, limpa o histórico e os flashcards anteriores
if st.session_state.get("arquivo_atual") != arquivo.name:
    st.session_state.arquivo_atual = arquivo.name
    st.session_state.historico = []
    st.session_state.flashcards = None

st.success(f"PDF processado: {len(indice)} trechos indexados.")

aba_perguntas, aba_flashcards = st.tabs(["💬 Perguntas", "🃏 Flashcards"])

# ---------- Aba de perguntas ----------
with aba_perguntas:
    for papel, texto in st.session_state.historico:
        with st.chat_message(papel):
            st.markdown(texto)

    pergunta = st.chat_input("Pergunte algo sobre o material")
    if pergunta:
        with st.chat_message("user"):
            st.markdown(pergunta)
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                resposta = responder(pergunta, indice)
            st.markdown(resposta)
        st.session_state.historico += [("user", pergunta), ("assistant", resposta)]

# ---------- Aba de flashcards ----------
with aba_flashcards:
    tema = st.text_input("Tema dos flashcards", placeholder="ex: modelo espiral")
    quantidade = st.slider("Quantidade", min_value=3, max_value=10, value=5)

    if st.button("Gerar flashcards", disabled=not tema):
        with st.spinner("Gerando flashcards..."):
            st.session_state.flashcards = gerar_flashcards(tema, indice, quantidade)

    cards = st.session_state.flashcards
    if cards == []:
        st.warning("Não encontrei conteúdo sobre esse tema no material.")
    elif cards:
        for i, card in enumerate(cards, start=1):
            with st.expander(f"{i}. {card.pergunta}"):
                st.write(card.resposta)
        st.download_button(
            "⬇️ Baixar CSV para o Anki",
            data=flashcards_para_csv(cards),
            file_name="flashcards.csv",
            mime="text/csv",
        )