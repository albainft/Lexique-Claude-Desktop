#!/usr/bin/env python3
"""Génère docs/index.html depuis lexique.md.

Format d'une fiche :
  ## Terme
  - anglais: ...
  - catégorie: ...
  - définition: ...
  - voir: Terme lié, Autre terme lié   (facultatif)

--check : n'écrit rien, sort en 1 si docs/index.html diffère de la source.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "lexique.md"
TMPL = ROOT / "template.html"
OUT = ROOT / "docs" / "index.html"
FIELDS = {"anglais": "e", "catégorie": "c", "définition": "d", "voir": "v"}


def slug(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def parse(text):
    terms, note, cur, cats, in_cats = [], "", None, [], False
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip() == "# Catégories":
            in_cats = True
        elif in_cats and line.startswith("## "):
            in_cats = False
        if in_cats and (m := re.match(r"-\s*([^:]+):\s*(.*)$", line)):
            cats.append({"n": m.group(1).strip(), "d": m.group(2).strip()})
            continue
        if line.startswith("## "):
            cur = {"t": line[3:].strip(), "e": "", "c": "", "d": "", "v": [], "line": n}
            terms.append(cur)
        elif cur is None and line.startswith("> "):
            note = line[2:].strip()
        elif cur is not None and (m := re.match(r"-\s*([^:]+):\s*(.*)$", line)):
            key = FIELDS.get(m.group(1).strip().lower())
            if key is None:
                sys.exit(f"lexique.md:{n}: champ inconnu « {m.group(1).strip()} »")
            cur[key] = [s.strip() for s in m.group(2).split(",") if s.strip()] if key == "v" else m.group(2).strip()
    ids = {}
    for t in terms:
        t["id"] = slug(t["t"])
        if t["id"] in ids:
            sys.exit(f"lexique.md:{t['line']}: terme en double « {t['t']} »")
        ids[t["id"]] = t
        for field, label in (("e", "version anglaise"), ("c", "catégorie"), ("d", "définition")):
            if not t[field]:
                sys.exit(f"lexique.md:{t['line']}: « {t['t']} » n'a pas de {label}")
    declared = {c["n"] for c in cats}
    for t in terms:
        if cats and t["c"] not in declared:
            sys.exit(f"lexique.md:{t['line']}: catégorie « {t['c']} » non déclarée (ajouter « - {t['c']}: description » sous « # Catégories »)")
    for t in terms:
        for name in t["v"]:
            if slug(name) not in ids:
                sys.exit(f"lexique.md:{t['line']}: « {t['t']} » renvoie à « {name} », qui n'existe pas")
        t["v"] = [slug(name) for name in t["v"]]
        del t["line"]
    used = {t["c"] for t in terms}
    cats = [c for c in cats if c["n"] in used] or [{"n": n, "d": ""} for n in dict.fromkeys(t["c"] for t in terms)]
    return terms, note, cats


def render(terms, note, cats):
    data = json.dumps(terms, ensure_ascii=False).replace("</", "<\\/")
    return TMPL.read_text(encoding="utf-8").replace("__DATA__", data).replace("__NOTE__", json.dumps(note, ensure_ascii=False)).replace("__CATS__", json.dumps(cats, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="vérifie sans écrire")
    args = ap.parse_args()
    terms, note, cats = parse(SRC.read_text(encoding="utf-8"))
    html = render(terms, note, cats)
    if args.check:
        ok = OUT.exists() and OUT.read_text(encoding="utf-8") == html
        print(f"lexique : {len(terms)} termes, {'OK' if ok else 'docs/index.html périmé'}")
        sys.exit(0 if ok else 1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8", newline="\n")
    print(f"lexique : {len(terms)} termes, {OUT.relative_to(ROOT)} écrit")


if __name__ == "__main__":
    main()
