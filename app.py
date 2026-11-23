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

from flask import Flask, Response, abort, render_template, url_for
from jinja2 import pass_context
from markupsafe import Markup, escape

BASE = Path(__file__).parent


GOATCOUNTER = ""
# Indirizzo completo del sito pubblicato (es. "https://nome.github.io/guida/").
# Serve per le anteprime nei social e per la sitemap; il workflow lo imposta da solo.
SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")
CONTENT = BASE / "content"

app = Flask(__name__)
app.config["FREEZER_RELATIVE_URLS"] = True
app.config["FREEZER_DESTINATION"] = "build"
app.config["FREEZER_REMOVE_EXTRA_FILES"] = True

# slug -> (titolo nel menu, titolo della pagina, descrizione per i motori di ricerca)
PAGES = {
    "cibo": ("Cibo", "Cibo", "La spesa di tutti i giorni in 25 voci: cosa guardare, dove comprare, a cosa fare attenzione."),
    "vestire": ("Vestire", "Vestire", "Fibre vegetali, marchi europei verificati, usato e riparazione."),
    "casa": ("Casa", "Casa e cura", "Pulizia, bucato, cucina e cura della persona con meno chimica."),
    "digitale": ("Digitale", "Digitale", "Alternative europee alle grandi piattaforme e i tuoi diritti."),
    "energia": ("Soldi ed energia", "Soldi ed energia", "Banche etiche, pagamenti europei, comunità energetiche."),
    "muoversi": ("Muoversi", "Muoversi", "Piedi, bici, treno, autobus e viaggi: cosa inquina meno e quali sono i tuoi diritti."),
    "rifiuti-acqua": ("Rifiuti e acqua", "Rifiuti e acqua", "Raccolta differenziata, imballaggi e acqua del rubinetto."),
    "bambini": ("Bambini", "Bambini", "Giocattoli, vestiti, cura e merende per i più piccoli."),
    "dove-comprare": ("Dove comprare", "Dove comprare", "GAS, CSA, mercati contadini e cooperative su una mappa."),
    "iniziare": (None, "Da dove iniziare", "Dieci cambiamenti della guida, dai più facili a quelli che capitano ogni tanto, ognuno con la sua fonte."),
    "perche": (None, "Perché ho fatto questo sito", "Chi scrive questa guida e con quali idee."),
    "metodo": (None, "Metodo e marchi", "Come scelgo le fonti e cosa garantiscono i marchi europei."),
    "conoscere": (None, "Conoscere la rete", "GAS, CSA, cooperative sociali e commercio equo spiegati in un minuto."),
    "glossario": (None, "Glossario", "Sigle e marchi della guida spiegati in una riga, con la fonte."),
    "lista": (None, "Lista della spesa", "Cosa guardare in etichetta per ogni voce della spesa, da stampare."),
    "cerca": (None, "Cerca", "Cerca tra voci, capitoli, glossario e fonti."),
    "novita": (None, "Cosa è cambiato", "Le modifiche alla guida, con la data."),
    "fonti": (None, "Tutte le fonti", "Ogni fonte della guida, con il link per verificarla."),
    "note": (None, "Note e privacy", "Chi sono, cosa raccolgo (niente), come contattarmi."),
}
# Numero e titolo dei capitoli, per i link "precedente / successivo"
CAPITOLI_INFO = {
    "cibo": ("Capitolo 1", "Cibo"), "vestire": ("Capitolo 2", "Vestire"), "casa": ("Capitolo 3", "Casa e cura"),
    "digitale": ("Capitolo 4", "Digitale"), "energia": ("Capitolo 5", "Soldi ed energia"),
    "muoversi": ("Capitolo 6", "Muoversi"), "rifiuti-acqua": ("Capitolo 7", "Rifiuti e acqua"),
    "bambini": ("Capitolo 8", "Bambini"), "dove-comprare": ("La rete", "Dove comprare"),
}
CAPITOLI_JSON = {"muoversi", "rifiuti-acqua", "bambini"}
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
    for ext in ("webp", "jpg"):
        if (BASE / "static" / "foto" / f"{pid}.{ext}").exists():
            return ctx["url_for"]("static", filename=f"foto/{pid}.{ext}")
    return FOTO_REMOTE.format(id=pid)
CODE_RE = re.compile(r"\b([CVKDSRMTWB]\d{1,2})\b")


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
    return {"NAV": NAV, "PAGES": PAGES, "FONTI": FONTI, "GOATCOUNTER": GOATCOUNTER.strip(), "SITE_URL": SITE_URL,
            "CAPITOLI_INFO": CAPITOLI_INFO, "N_LEGGI_UE": sum(1 for f in FONTI.values() if f["tipo"] == "Legge UE")}


# Apostrofi tipografici: "l'olio" diventa "l’olio" solo nel testo visibile,
# mai dentro tag, attributi, script o stili.
_BLOCCHI = re.compile(r"(<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)", re.S | re.I)
_APOSTROFO = re.compile(r"(?<=[A-Za-zÀ-ÿ])(?:'|&#39;|&#x27;)")


def apostrofi(html):
    parti = _BLOCCHI.split(html)
    for i in range(0, len(parti), 2):
        parti[i] = _APOSTROFO.sub("\u2019", parti[i])
    return "".join(parti)


@app.after_request
def tipografia(resp):
    if resp.mimetype == "text/html" and not resp.direct_passthrough:
        resp.set_data(apostrofi(resp.get_data(as_text=True)))
    return resp


@app.route("/")
def index():
    return render_template("pages/index.html", slug="index")


@app.route("/<slug>/")
def page(slug):
    if slug not in PAGES:
        abort(404)
    ctx = {"slug": slug, "page_title": PAGES[slug][1], "description": PAGES[slug][2]}
    template = f"pages/{slug}.html"
    if slug in CAPITOLI_JSON:
        ctx["cap"] = load_json(f"capitoli/{slug}.json")
        template = "pages/capitolo.html"
    elif slug == "perche":
        ctx["meta"], ctx["body"] = load_markdown("perche.md")
    elif slug in ("cibo", "lista"):
        ctx["data"] = load_json("cibo.json")
        ctx["stagioni"] = load_json("stagioni.json")
    elif slug == "casa":
        ctx["data"] = load_json("casa.json")
    elif slug == "digitale":
        ctx["data"] = load_json("digitale.json")
    elif slug == "conoscere":
        ctx["data"] = load_json("conoscere.json")["D"]
    elif slug == "iniziare":
        ctx["data"] = load_json("iniziare.json")
    elif slug == "glossario":
        ctx["voci"] = load_json("glossario.json")
    elif slug == "novita":
        ctx["voci"] = load_json("novita.json")
    elif slug == "fonti":
        ctx["extra"] = load_json("fonti_extra.json")
        ctx["foto_crediti"] = FOTO
        groups = {}
        for f in FONTI.values():
            groups.setdefault(f["gruppo"], []).append(f)
        ctx["groups"] = groups
    return render_template(template, **ctx)


def _testo(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(s))).strip()


@app.route("/cerca.json")
def indice_ricerca():
    """Indice per la ricerca, generato con il sito: titolo, testo, link."""
    voci = []
    for slug, (_, titolo, desc) in PAGES.items():
        if slug in ("cerca",):
            continue
        voci.append({"t": titolo, "x": desc, "u": url_for("page", slug=slug), "g": "Pagina"})
    for slug, nome in (("cibo", "Cibo"), ("casa", "Casa e cura")):
        for v in load_json(f"{slug}.json")["VOCI"]:
            testo = " ".join([v.get("intro", "")] + v.get("guarda", v.get("fare", [])) + v.get("dove", v.get("cerca", [])) + [v.get("attenzione", "")])
            voci.append({"t": v["nome"], "x": testo, "u": url_for("page", slug=slug) + "#" + v["id"], "g": nome})
    for a in load_json("digitale.json").get("ALT", []):
        voci.append({"t": f"{a.get('al', '')}: {a.get('nome', '')}", "x": a.get("desc", ""), "u": url_for("page", slug="digitale"), "g": "Digitale"})
    for slug in sorted(CAPITOLI_JSON):
        cap = load_json(f"capitoli/{slug}.json")
        for s in cap["sezioni"]:
            for p in s["punti"]:
                voci.append({"t": p["t"], "x": p["d"], "u": url_for("page", slug=slug), "g": cap["titolo"]})
    for g in load_json("iniziare.json")["gruppi"]:
        for p in g["passi"]:
            voci.append({"t": p["t"], "x": p["d"] + " " + p["come"], "u": url_for("page", slug="iniziare") + "#" + slugify(p["t"]), "g": "Da dove iniziare"})
    for g in load_json("glossario.json"):
        voci.append({"t": g["t"], "x": g["d"], "u": url_for("page", slug="glossario") + "#" + slugify(g["t"]), "g": "Glossario"})
    for f in FONTI.values():
        voci.append({"t": f"{f['codice']} {f['titolo']}", "x": f.get("sostiene", ""), "u": url_for("page", slug="fonti") + "#" + f["codice"], "g": "Fonti"})
    for v in voci:
        v["x"] = _testo(v["x"])[:400]
        # link relativi alla pagina /cerca/, così funzionano anche in una sottocartella
        v["u"] = "../" + v["u"].lstrip("/")
    return Response(json.dumps(voci, ensure_ascii=False), mimetype="application/json")


@app.template_filter("slug")
def slugify(s):
    s = s.lower()
    for a, b in (("à", "a"), ("è", "e"), ("é", "e"), ("ì", "i"), ("ò", "o"), ("ù", "u")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


@app.route("/sitemap.xml")
def sitemap():
    base = SITE_URL or ""
    urls = [base + "/"] + [base + url_for("page", slug=s) for s in PAGES]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += [f"  <url><loc>{escape(u)}</loc></url>" for u in urls]
    xml.append("</urlset>")
    return Response("\n".join(xml) + "\n", mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    righe = ["User-agent: *", "Allow: /"]
    if SITE_URL:
        righe.append(f"Sitemap: {SITE_URL}/sitemap.xml")
    return Response("\n".join(righe) + "\n", mimetype="text/plain")


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
