import csv
import io
import streamlit as st
from chunks import extrair_texto, remover_repetidas, dividir_em_chunks
from busca import gerar_embeddings
from responder import responder
from flashcards import gerar_flashcards

TAMANHO_LOTE = 50        # quantos chunks mandar por vez pra API de embeddings
ALTURA_CONVERSA = 500    # altura da área de respostas, em pixels (depois disso, aparece o scroll)

st.set_page_config(page_title="Estuda AI", page_icon="📚")
st.title("📚 Estuda AI")
st.caption("Faça perguntas e gere flashcards a partir dos seus PDFs")


@st.cache_data(show_spinner="Lendo e indexando o PDF...")
def montar_indice(conteudo, nome_arquivo):
    # cada PDF tem seu próprio cache: adicionar um novo não reprocessa os antigos
    paginas = extrair_texto(io.BytesIO(conteudo))
    texto = remover_repetidas(paginas)
    chunks = dividir_em_chunks(texto)

    # marca cada trecho com o nome do arquivo, para a IA saber de onde ele veio
    chunks = [f"[Fonte: {nome_arquivo}]\n{c}" for c in chunks]

    vetores = []
    for i in range(0, len(chunks), TAMANHO_LOTE):
        vetores += gerar_embeddings(chunks[i:i + TAMANHO_LOTE])
    return [{"texto": c, "vetor": v} for c, v in zip(chunks, vetores)]


def flashcards_para_csv(flashcards):
    saida = io.StringIO()
    escritor = csv.writer(saida, delimiter=";")
    for card in flashcards:
        escritor.writerow([card.pergunta, card.resposta])
    return saida.getvalue()


# ---------- Upload dos PDFs ----------
arquivos = st.file_uploader("Envie um ou mais PDFs", type="pdf", accept_multiple_files=True)
if not arquivos:
    st.info("Envie pelo menos um PDF para começar.")
    st.stop()

indice = []
for arquivo in arquivos:
    indice_arquivo = montar_indice(arquivo.getvalue(), arquivo.name)
    if not indice_arquivo:
        st.warning(f"Não consegui extrair texto de **{arquivo.name}**. Ele pode ser escaneado (só imagem).")
    indice += indice_arquivo

if not indice:
    st.error("Nenhum dos PDFs enviados tem texto que eu consiga ler.")
    st.stop()

# se mudou a lista de PDFs, limpa o histórico e os flashcards anteriores
nomes = sorted(a.name for a in arquivos)
if st.session_state.get("arquivos_atuais") != nomes:
    st.session_state.arquivos_atuais = nomes
    st.session_state.historico = []      # lista de pares (pergunta, resposta)
    st.session_state.flashcards = None

st.success(f"{len(arquivos)} PDF(s) processado(s): {len(indice)} trechos indexados.")

aba_perguntas, aba_flashcards = st.tabs(["💬 Perguntas", "🃏 Flashcards"])

# ---------- Aba de perguntas ----------
with aba_perguntas:
    # 1. o campo de pergunta fica no topo
    pergunta = st.chat_input("Pergunte algo sobre o material")
    if pergunta:
        with st.spinner("Pensando..."):
            resposta = responder(pergunta, indice)
        st.session_state.historico.append((pergunta, resposta))

    # 2. as respostas ficam numa área com altura fixa e scroll
    with st.container(height=ALTURA_CONVERSA):
        if not st.session_state.historico:
            st.caption("As respostas vão aparecer aqui.")
        # mais recente primeiro, logo abaixo do campo de pergunta
        for pergunta_antiga, resposta_antiga in reversed(st.session_state.historico):
            with st.chat_message("user"):
                st.markdown(pergunta_antiga)
            with st.chat_message("assistant"):
                st.markdown(resposta_antiga)

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