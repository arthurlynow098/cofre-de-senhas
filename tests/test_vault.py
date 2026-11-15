import json

import pytest

from cofre.vault import Entry, Vault, WrongPassword, generate_password

MESTRA = "uma frase mestra bem comprida"
N_TESTE = 2**10  # scrypt mais leve só para os testes rodarem rápido


@pytest.fixture
def cofre(tmp_path):
    v = Vault(tmp_path / "cofre.json", n=N_TESTE)
    v.create(MESTRA)
    return v


def test_salva_e_reabre(cofre):
    cofre.add(Entry("github", "arthur", "s3gredo-forte"))
    outro = Vault(cofre.path)
    outro.open(MESTRA)
    assert outro.get("github").password == "s3gredo-forte"


def test_senha_errada(cofre):
    with pytest.raises(WrongPassword):
        Vault(cofre.path).open("senha errada qualquer")


def test_arquivo_nao_tem_nada_em_texto_puro(cofre):
    cofre.add(Entry("banco", "arthur", "senha-super-secreta"))
    conteudo = cofre.path.read_text(encoding="utf-8")
    assert "senha-super-secreta" not in conteudo and "banco" not in conteudo


def test_adulteracao_e_detectada(cofre):
    cofre.add(Entry("email", "arthur", "abc"))
    doc = json.loads(cofre.path.read_text(encoding="utf-8"))
    token = doc["dados"]
    doc["dados"] = token[:-6] + ("A" if token[-6] != "A" else "B") + token[-5:]
    cofre.path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(WrongPassword):
        Vault(cofre.path).open(MESTRA)


def test_senha_mestra_curta_e_recusada(tmp_path):
    with pytest.raises(ValueError):
        Vault(tmp_path / "x.json", n=N_TESTE).create("curta")


def test_detecta_senha_repetida(cofre):
    cofre.add(Entry("a", "u", "mesma"))
    cofre.add(Entry("b", "u", "mesma"))
    cofre.add(Entry("c", "u", "diferente"))
    assert cofre.reused() == [["a", "b"]]


def test_gerador_tem_todos_os_grupos():
    pw = generate_password(16)
    assert len(pw) == 16
    assert any(c.islower() for c in pw) and any(c.isupper() for c in pw)
    assert any(c.isdigit() for c in pw) and any(not c.isalnum() for c in pw)
