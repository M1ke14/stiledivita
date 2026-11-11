# Guida alla vita sostenibile

Guida indipendente e senza scopo di lucro per mangiare, vestirsi e vivere in modo più sostenibile, con fonti verificabili.

Il sito è **statico**. Online ci sono solo file, senza server, database o cookie.

## Avviare in locale

```bash
python3 -m venv .venv
source .venv/bin/activate        # su Windows: .venv\Scripts\activate
pip install -r requirements.txt

python app.py                    # anteprima su http://127.0.0.1:5000
python scarica_foto.py           # una volta: copia le foto in static/foto/
python freeze.py                 # genera il sito nella cartella build/
```

Le foto vengono da Unsplash (uso gratuito). 

## Dove si modifica cosa

| Cosa | File |
|---|---|
| La tua pagina "Perché" | `content/perche.md` (testo in Markdown, in alto sottotitolo e cinque idee) |
| Voci di Cibo e Casa | `content/cibo.json`, `content/casa.json` |
| Alternative digitali | `content/digitale.json` |
| Schede e approfondimenti della rete | `content/conoscere.json` |
| Tutte le fonti (codici C, V, K, D, S, R, M) | `content/fonti.json` |
| Marchi e servizi | `content/fonti_extra.json` |
| Foto e crediti | `content/foto.json` (poi `python scarica_foto.py`) |
| Punti della mappa | `static/data/rete.json` (campi: nome, tipo, comune, provincia, regione, lat, lon, sito, fonte, nome fonte, attivo) |
| Testi delle altre pagine | `templates/pages/*.html` |
| Colori, caratteri, stili comuni | `static/css/site.css` |


## Struttura

```
app.py              rotte e filtri (pagine, link alle fonti)
freeze.py           genera build/
content/            dati e testi
templates/          base.html, pagine, parti riutilizzate (partials/)
static/             css, js, caratteri , Leaflet, dati della mappa
```
