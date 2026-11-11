"""Genera il sito statico nella cartella build/.

    python freeze.py
"""
from flask_frozen import Freezer

from app import PAGES, app

freezer = Freezer(app)


@freezer.register_generator
def page():
    for slug in PAGES:
        yield {"slug": slug}


if __name__ == "__main__":
    freezer.freeze()
    # niente elaborazione Jekyll su GitHub Pages
    (freezer.root / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Sito generato in {freezer.root}")
