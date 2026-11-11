"""Guida alla vita sostenibile: sito statico.

Il sito è statico: Flask serve solo a generarlo. In locale:
    python app.py            # anteprima su http://127.0.0.1:5000
    python freeze.py         # genera i file HTML nella cartella build/
"""
import json
import re
from pathlib import Path

import markdown
import yaml
import os

from flask import Flask, abort, render_template
from jinja2 import pass_context
from markupsafe import Markup, escape

BASE = Path(__file__).parent


GOATCOUNTER = ""
CONTENT = BASE / "content"

app = Flask(__name__)
app.config["FREEZER_RELATIVE_URLS"] = True
app.config["FREEZER_DESTINATION"] = "build"
app.config["FREEZER_REMOVE_EXTRA_FILES"] = True

# slug -> (titolo nel menu, titolo della pagina, descrizione per i motori di ricerca)
PAGES = {
    "perche": ("Perché", "Perché ho fatto questo sito", "Chi scrive questa guida e con quali idee."),
    "metodo": ("Metodo", "Metodo e marchi", "Come scelgo le fonti e cosa garantiscono i marchi europei."),
    "cibo": ("Cibo", "Cibo", "La spesa di tutti i giorni in 25 voci: cosa guardare, dove comprare, a cosa fare attenzione."),
    "vestire": ("Vestire", "Vestire", "Fibre vegetali, marchi europei verificati, usato e riparazione."),
    "casa": ("Casa e cura", "Casa e cura", "Pulizia, bucato, cucina e cura della persona con meno chimica."),
    "digitale": ("Digitale", "Digitale", "Alternative europee alle grandi piattaforme e i tuoi diritti."),
    "energia": ("Soldi ed energia", "Soldi ed energia", "Banche etiche, pagamenti europei, comunità energetiche."),
    "dove-comprare": ("Dove comprare", "Dove comprare", "GAS, CSA, mercati contadini e cooperative su una mappa."),
    "conoscere": (None, "Conoscere la rete", "GAS, CSA, cooperative sociali e commercio equo spiegati in un minuto."),
    "fonti": (None, "Tutte le fonti", "Ogni fonte della guida, con il link per verificarla."),
    "note": (None, "Note e privacy", "Chi sono, cosa raccolgo (niente), come contattarmi."),
}
NAV = [s for s, (label, _, _) in PAGES.items() if label]


def load_json(name):
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


def load_markdown(name):
    """Legge un file .md con intestazione YAML tra due righe '---'."""
    text = (CONTENT / name).read_text(encoding="utf-8")
    meta, body = {}, text
    m = re.match(r"\A---[ \t]*\n(.*?)\n---[ \t]*\n(.*)\Z", text, re.S)
    if m:
        meta = yaml.safe_load(m.group(1)) or {}
        body = m.group(2)
    html = markdown.markdown(body, extensions=["extra", "smarty"])
    return meta, Markup(html)


FONTI = load_json("fonti.json")
FOTO = load_json("foto.json")
FOTO_REMOTE = "https://images.unsplash.com/{id}?w=2400&q=80&auto=format&fit=crop"


@app.template_global()
@pass_context
def foto(ctx, pid):
    """Usa la copia in static/foto/ se c'è (vedi scarica_foto.py), altrimenti il link originale."""
    if (BASE / "static" / "foto" / f"{pid}.jpg").exists():
        return ctx["url_for"]("static", filename=f"foto/{pid}.jpg")
    return FOTO_REMOTE.format(id=pid)
CODE_RE = re.compile(r"\b([CVKDSRM]\d{1,2})\b")


@app.template_filter("fonti")
@pass_context
def fonti_links(ctx, text, link=True):
    """Trasforma 'C5, C6' in link alla pagina delle fonti.
    Con link=False lascia il testo com'è (serve dentro altri link)."""
    if not link:
        return text
    base = ctx["url_for"]("page", slug="fonti")

    def repl(m):
        code = m.group(1)
        if code not in FONTI:
            return code
        title = escape(FONTI[code]["titolo"])
        return f'<a class="fonte" href="{base}#{code}" title="{title}">{code}</a>'

    return Markup(CODE_RE.sub(repl, str(escape(text))))


@app.context_processor
def inject_globals():
    return {"NAV": NAV, "PAGES": PAGES, "FONTI": FONTI, "GOATCOUNTER": GOATCOUNTER.strip()}


@app.route("/")
def index():
    return render_template("pages/index.html", slug="index")


@app.route("/<slug>/")
def page(slug):
    if slug not in PAGES:
        abort(404)
    ctx = {"slug": slug, "page_title": PAGES[slug][1], "description": PAGES[slug][2]}
    if slug == "perche":
        ctx["meta"], ctx["body"] = load_markdown("perche.md")
    elif slug == "cibo":
        ctx["data"] = load_json("cibo.json")
    elif slug == "casa":
        ctx["data"] = load_json("casa.json")
    elif slug == "digitale":
        ctx["data"] = load_json("digitale.json")
    elif slug == "conoscere":
        ctx["data"] = load_json("conoscere.json")["D"]
    elif slug == "fonti":
        ctx["extra"] = load_json("fonti_extra.json")
        ctx["foto_crediti"] = FOTO
        groups = {}
        for f in FONTI.values():
            groups.setdefault(f["gruppo"], []).append(f)
        ctx["groups"] = groups
    return render_template(f"pages/{slug}.html", **ctx)


# Indirizzo di base del sito pubblicato, serve solo alla pagina 404
# (es. "/" per un dominio proprio, "/guida/" per utente.github.io/guida/).
SITE_BASE = os.environ.get("SITE_BASE", "/")


@app.route("/404.html")
def pagina_404():
    return render_template("pages/404.html", slug="404", page_title="Pagina non trovata", site_base=SITE_BASE)


@app.errorhandler(404)
def not_found(_):
    return render_template("pages/404.html", slug="404", page_title="Pagina non trovata"), 404


if __name__ == "__main__":
    app.run(debug=True)
