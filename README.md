<p align="center"><sub>Cofre de Senhas</sub></p>

---

<p align="center">
  <img src="assets/banner.png" alt="Cofre de Senhas" width="100%">
</p>

<p align="center">
  Gerenciador de senhas no terminal com scrypt e criptografia autenticada (Fernet)
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-A855F7?style=for-the-badge&logo=python&logoColor=white">
  <img alt="cryptography" src="https://img.shields.io/badge/cryptography-Fernet%20%2B%20scrypt-242424?style=for-the-badge">
  <a href="https://github.com/arthurlynow098/cofre-de-senhas/actions/workflows/testes.yml"><img alt="Testes" src="https://img.shields.io/github/actions/workflow/status/arthurlynow098/cofre-de-senhas/testes.yml?style=for-the-badge&label=testes&color=242424"></a>
  <img alt="Licença MIT" src="https://img.shields.io/badge/licen%C3%A7a-MIT-242424?style=for-the-badge">
</p>

## Sobre o projeto

Eu sempre recomendava gerenciador de senha para todo mundo, mas não sabia explicar **por que** era seguro guardar tudo num lugar só. Então construí um.

O Cofre de Senhas roda no terminal e guarda tudo em um único arquivo JSON criptografado. A senha mestra nunca é salva em lugar nenhum. Sem ela o arquivo é só um monte de bytes aleatórios, e se alguém alterar um único caractere o cofre percebe e se recusa a abrir.

## Como funciona

```mermaid
flowchart LR
    A[senha mestra] --> C[scrypt n=2^15]
    B[salt aleatório de 16 bytes] --> C
    C --> D[chave de 256 bits]
    D --> E[Fernet]
    F[entradas em JSON] --> E
    E --> G[(cofre.json)]
```

## Tecnologias

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=flat-square&amp;logo=python&amp;logoColor=white">
  <img alt="cryptography" src="https://img.shields.io/badge/cryptography-2B2B2B?style=flat-square">
  <img alt="scrypt" src="https://img.shields.io/badge/scrypt-2B2B2B?style=flat-square">
</p>

## Executando o código

```bash
git clone https://github.com/arthurlynow098/cofre-de-senhas.git
cd cofre-de-senhas
pip install cryptography

python -m cofre criar
python -m cofre add github --usuario arthurlynow098 --gerar 24
python -m cofre add banco --usuario arthur
python -m cofre listar
python -m cofre ver github
python -m cofre auditar
python -m cofre gerar 32
```

O arquivo fica em `~/.cofre.json`. Dá para mudar com `--arquivo` ou com a variável `COFRE_ARQUIVO`.

Testes

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Os testes conferem, entre outras coisas, que nenhum nome ou senha aparece em texto puro no arquivo e que alterar um único caractere faz o cofre recusar a abertura.

## Exemplo

É assim que o arquivo fica no disco depois de salvar uma entrada. Repare que nem o nome "github" aparece.

```json
{
  "versao": 1,
  "kdf": {
    "nome": "scrypt",
    "n": 32768,
    "r": 8,
    "p": 1,
    "salt": "0elR2N4vj06tJEeedxXBqQ=="
  },
  "dados": "gAAAAABq-YjadYQFSlZbZ1Q4zJ2SI4bqhAv0-kbt--32rSXJk3Gx5Z6g5a2uxHYOj8W8..."
}
```

## Estudei por aqui

Segui essas aulas e materiais para entender e aplicar tudo que está aqui.

| Material | O que tirei dele |
|---|---|
| [Documentação do Fernet](https://cryptography.io/en/latest/fernet/) | Como usar e o que tem dentro de um token |
| [cryptography, Key Derivation Functions](https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/) | Parâmetros do scrypt |
| [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html) | Boas práticas de guardar dado sensível |
| [TryHackMe, Introduction to Cryptography](https://tryhackme.com/room/cryptographyintro) | Simétrica, assimétrica, hash e onde cada uma entra |

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).

<p align="center"><sub>A gravura do banner é o pangolim de Thomas Hardwicke, do século XIX, em domínio público no <a href="https://commons.wikimedia.org/wiki/File%3APangolin_Hardwicke_%28white_background%29.jpg">Wikimedia Commons</a>.</sub></p>
