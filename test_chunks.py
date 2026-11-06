from chunks import normalizar, remover_repetidas, dividir_em_chunks


def test_normalizar_remove_numeros():
    assert normalizar("Ronaldo C. Oliveira 3") == "Ronaldo C. Oliveira"


def test_remover_repetidas_tira_rodape_e_mantem_conteudo():
    paginas = [
        "Conteúdo A\nRodapé 1",
        "Conteúdo B\nRodapé 2",
        "Conteúdo C\nRodapé 3",
    ]
    texto = remover_repetidas(paginas)
    assert "Rodapé" not in texto       # o rodapé repetido tem que sair
    assert "Conteúdo A" in texto       # o conteúdo tem que ficar


def test_dividir_em_chunks_com_sobreposicao():
    texto = "a" * 1000 + "b" * 1000
    chunks = dividir_em_chunks(texto, tamanho=1000, sobreposicao=200)
    assert len(chunks) == 3
    assert chunks[0] == "a" * 1000
    assert chunks[1].startswith("a" * 200)   # os 200 finais do anterior se repetem


def test_dividir_texto_vazio():
    assert dividir_em_chunks("") == []