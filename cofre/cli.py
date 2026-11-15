from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

from .vault import Entry, Vault, WrongPassword, generate_password

DEFAULT_PATH = Path(os.environ.get("COFRE_ARQUIVO", Path.home() / ".cofre.json"))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cofre", description="Gerenciador de senhas no terminal.")
    p.add_argument("--arquivo", default=str(DEFAULT_PATH), help="onde fica o cofre (padrão ~/.cofre.json)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("criar", help="cria um cofre novo")
    a = sub.add_parser("add", help="adiciona uma entrada")
    a.add_argument("nome")
    a.add_argument("--usuario", default="")
    a.add_argument("--url", default="")
    a.add_argument("--gerar", type=int, metavar="TAMANHO", help="gera uma senha aleatória em vez de pedir")
    a.add_argument("--substituir", action="store_true")
    g = sub.add_parser("ver", help="mostra uma entrada")
    g.add_argument("nome")
    sub.add_parser("listar", help="lista os nomes")
    r = sub.add_parser("remover", help="apaga uma entrada")
    r.add_argument("nome")
    sub.add_parser("auditar", help="procura senhas repetidas")
    s = sub.add_parser("gerar", help="só gera uma senha, sem salvar")
    s.add_argument("tamanho", type=int, nargs="?", default=20)
    return p


def ask_master(confirm: bool = False) -> str:
    master = getpass.getpass("  senha mestra ")
    if confirm and getpass.getpass("  repita a senha mestra ") != master:
        raise SystemExit("  as senhas não batem")
    return master


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "gerar":
        print(f"\n  {generate_password(args.tamanho)}\n")
        return 0

    vault = Vault(args.arquivo)
    try:
        if args.cmd == "criar":
            vault.create(ask_master(confirm=True))
            print(f"\n  cofre criado em {args.arquivo}\n  não existe recuperação, se esquecer a senha mestra os dados se perdem\n")
            return 0
        vault.open(ask_master())
    except WrongPassword as exc:
        print(f"\n  {exc}\n", file=sys.stderr)
        return 1
    except (FileNotFoundError, FileExistsError, ValueError) as exc:
        print(f"\n  {exc}\n", file=sys.stderr)
        return 1

    if args.cmd == "add":
        pw = generate_password(args.gerar) if args.gerar else getpass.getpass(f"  senha de {args.nome} ")
        try:
            vault.add(Entry(args.nome, args.usuario, pw, args.url), overwrite=args.substituir)
        except KeyError as exc:
            print(f"\n  {exc.args[0]}, use --substituir\n", file=sys.stderr)
            return 1
        print(f"\n  {args.nome} salvo" + (" com senha gerada" if args.gerar else "") + "\n")
    elif args.cmd == "ver":
        try:
            e = vault.get(args.nome)
        except KeyError:
            print(f"\n  {args.nome} não existe\n", file=sys.stderr)
            return 1
        print(f"\n  nome     {e.name}\n  usuário  {e.user}\n  senha    {e.password}\n  url      {e.url}\n  alterado {e.updated}\n")
    elif args.cmd == "listar":
        names = vault.names()
        print("\n" + ("\n".join(f"  {n}" for n in names) if names else "  cofre vazio") + "\n")
    elif args.cmd == "remover":
        vault.remove(args.nome)
        print(f"\n  {args.nome} removido\n")
    elif args.cmd == "auditar":
        groups = vault.reused()
        if not groups:
            print("\n  nenhuma senha repetida\n")
        for g in groups:
            print(f"  senha repetida em {', '.join(g)}")
    return 0
