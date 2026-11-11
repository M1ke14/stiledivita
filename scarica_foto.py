"""Scarica le foto elencate in content/foto.json dentro static/foto/.

Così il sito pubblicato non carica immagini da server esterni.
Se una foto manca, la pagina usa il link originale su Unsplash.

    python scarica_foto.py
"""
import json
import urllib.request
from pathlib import Path

BASE = Path(__file__).parent
DEST = BASE / "static" / "foto"
URL = "https://images.unsplash.com/{id}?w=2000&q=80&fm=jpg&fit=crop"


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    foto = json.loads((BASE / "content" / "foto.json").read_text(encoding="utf-8"))
    for f in foto:
        out = DEST / f"{f['id']}.jpg"
        if out.exists():
            print("già presente:", out.name)
            continue
        req = urllib.request.Request(URL.format(id=f["id"]), headers={"User-Agent": "guida-sostenibile"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                out.write_bytes(r.read())
            print("scaricata:", out.name, "foto di", f["autore"])
        except OSError as e:
            print("non riuscita:", f["id"], e)


if __name__ == "__main__":
    main()
