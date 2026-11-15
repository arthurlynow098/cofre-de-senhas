"""O cofre em si.

Formato do arquivo (JSON)
  versao    número do formato
  kdf       parâmetros do scrypt e o salt
  dados     um token Fernet com todas as entradas criptografadas

A senha mestra nunca é salva. Ela passa pelo scrypt junto com o salt e
vira a chave do Fernet (AES-128-CBC com HMAC-SHA256). Se alguém mexer em
um único byte do arquivo, o HMAC falha e o cofre se recusa a abrir.
"""
from __future__ import annotations

import base64
import json
import os
import secrets
import string
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

DEFAULT_N, DEFAULT_R, DEFAULT_P = 2**15, 8, 1


class WrongPassword(Exception):
    pass


def derive_key(master: str, salt: bytes, n: int = DEFAULT_N, r: int = DEFAULT_R, p: int = DEFAULT_P) -> bytes:
    kdf = Scrypt(salt=salt, length=32, n=n, r=r, p=p)
    return base64.urlsafe_b64encode(kdf.derive(master.encode("utf-8")))


def generate_password(length: int = 20, symbols: bool = True) -> str:
    alphabet = string.ascii_letters + string.digits + ("!@#$%&*-_=+?" if symbols else "")
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
        # garante pelo menos um de cada grupo, sem viciar a distribuição
        if (any(c.islower() for c in pw) and any(c.isupper() for c in pw) and any(c.isdigit() for c in pw)
                and (not symbols or any(not c.isalnum() for c in pw))):
            return pw


@dataclass
class Entry:
    name: str
    user: str
    password: str
    url: str = ""
    notes: str = ""
    updated: str = ""


class Vault:
    def __init__(self, path: str | Path, n: int = DEFAULT_N):
        self.path = Path(path)
        self.n = n
        self._entries: dict[str, Entry] = {}
        self._key: bytes | None = None
        self._salt: bytes | None = None

    # ciclo de vida -------------------------------------------------------
    def create(self, master: str) -> None:
        if self.path.exists():
            raise FileExistsError(f"já existe um cofre em {self.path}")
        if len(master) < 12:
            raise ValueError("a senha mestra precisa de pelo menos 12 caracteres")
        self._salt = os.urandom(16)
        self._key = derive_key(master, self._salt, self.n)
        self._entries = {}
        self.save()

    def open(self, master: str) -> None:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        kdf = raw["kdf"]
        self._salt = base64.b64decode(kdf["salt"])
        self.n = kdf["n"]
        self._key = derive_key(master, self._salt, kdf["n"], kdf["r"], kdf["p"])
        try:
            plain = Fernet(self._key).decrypt(raw["dados"].encode())
        except InvalidToken as exc:
            self._key = None
            raise WrongPassword("senha mestra errada ou arquivo adulterado") from exc
        self._entries = {e["name"]: Entry(**e) for e in json.loads(plain)}

    def save(self) -> None:
        if self._key is None:
            raise RuntimeError("cofre fechado")
        plain = json.dumps([e.__dict__ for e in self._entries.values()], ensure_ascii=False).encode()
        doc = {
            "versao": 1,
            "kdf": {"nome": "scrypt", "n": self.n, "r": DEFAULT_R, "p": DEFAULT_P,
                    "salt": base64.b64encode(self._salt).decode()},
            "dados": Fernet(self._key).encrypt(plain).decode(),
        }
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        tmp.replace(self.path)  # troca atômica, não corrompe o cofre se cair a energia no meio

    # operações -----------------------------------------------------------
    def add(self, entry: Entry, overwrite: bool = False) -> None:
        if entry.name in self._entries and not overwrite:
            raise KeyError(f"{entry.name} já existe")
        entry.updated = datetime.now().isoformat(timespec="seconds")
        self._entries[entry.name] = entry
        self.save()

    def get(self, name: str) -> Entry:
        return self._entries[name]

    def remove(self, name: str) -> None:
        del self._entries[name]
        self.save()

    def names(self) -> list[str]:
        return sorted(self._entries)

    def search(self, term: str) -> list[Entry]:
        term = term.lower()
        return [e for e in self._entries.values() if term in e.name.lower() or term in e.url.lower()]

    def reused(self) -> list[list[str]]:
        """Agrupa entradas que usam a mesma senha, um problema clássico."""
        groups: dict[str, list[str]] = {}
        for e in self._entries.values():
            groups.setdefault(e.password, []).append(e.name)
        return [sorted(v) for v in groups.values() if len(v) > 1]
