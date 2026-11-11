# Guida alla vita sostenibile

Guida indipendente e senza scopo di lucro per mangiare, vestirsi e vivere in modo più sostenibile, con fonti verificabili.

Il sito è **statico**: Flask e Jinja servono solo a generare le pagine HTML (con Frozen-Flask). Online ci sono solo file, senza server, database o cookie.

## Avviare in locale

```bash
python3 -m venv .venv
source .venv/bin/activate        # su Windows: .venv\Scripts\activate
pip install -r requirements.txt

python app.py                    # anteprima su http://127.0.0.1:5000
python scarica_foto.py           # una volta: copia le foto in static/foto/
python freeze.py                 # genera il sito nella cartella build/
```

Le foto vengono da Unsplash (uso gratuito). Se non le scarichi, le pagine le prendono direttamente da Unsplash; su GitHub le scarica il workflow da solo.

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

Nei testi basta scrivere un codice fonte (per esempio `C5` o `R15`) dentro `{{ '...' | fonti }}` o nei campi `fonti` dei JSON: diventa un link alla pagina **Tutte le fonti**.

## Struttura

```
app.py              rotte e filtri (pagine, link alle fonti)
freeze.py           genera build/
content/            dati e testi
templates/          base.html, pagine, parti riutilizzate (partials/)
static/             css, js, caratteri (ospitati qui, niente Google Fonts), Leaflet, dati della mappa
```

## Pubblicare

Le due strade usano la stessa cartella `build/`: si può cambiare quando si vuole.

**GitHub Pages.** Crea un repository pubblico, carica il progetto, poi in *Settings > Pages > Source* scegli *GitHub Actions*. A ogni push su `main` il file `.github/workflows/pubblica.yml` genera e pubblica il sito su `https://TUONOME.github.io/NOME-REPO/`. GitHub Pages è gratuito per siti non commerciali: 1 GB di spazio, circa 100 GB di traffico al mese.

**Codeberg Pages** (associazione senza scopo di lucro, Berlino). Crea il repository su codeberg.org, aggiungi un webhook come spiegato in `pubblica-codeberg.sh`, poi lancia:

```bash
./pubblica-codeberg.sh
```

**Dominio proprio**: funziona con entrambi. Va impostata la variabile `SITE_BASE="/"` (serve solo alla pagina 404).

## Statistiche di visita

1. Crea un account gratuito su [goatcounter.com](https://www.goatcounter.com) e scegli un nome (diventa `nome.goatcounter.com`).
2. In `app.py` scrivi quel nome in `GOATCOUNTER = "nome"`.
3. Pubblica. La pagina Note e privacy si aggiorna da sola.

Le statistiche le vedi entrando in `https://nome.goatcounter.com`. Senza cookie, quindi niente banner.

## Prima di andare online

- [ ] **Dati della mappa.** e-circles, Rete italiana CSA e Slow Food non hanno una licenza aperta. Con un repository pubblico anche `static/data/rete.json` diventa pubblico: chiedi il permesso o lascia solo nome, comune e link. La Rete di economia solidale è CC BY-NC-ND.
- [ ] **Coordinate dei comuni.** Vengono da un dataset del 2018 senza licenza: sostituirle con dati ISTAT o OpenStreetMap.
- [ ] **Pagina Note e privacy.** Completa nome, email di contatto, host scelto e licenza dei testi.
- [ ] **Perché.** Scrivi la tua storia in `content/perche.md` e aggiungi la foto in `static/`.
- [ ] **Foto** dei capitoli: per ora ci sono riquadri segnaposto.
- [ ] **Fonti non lette in automatico** (EUR-Lex, Normattiva, EFSA, FAO): l'elenco è nel documento delle fonti.

## Idee per dopo

- Ricerca interna con [Pagefind](https://pagefind.app) (statica, funziona senza server).
- Mappa di base ospitata in proprio con [Protomaps](https://protomaps.com), così i visitatori non caricano niente da server esterni.
- Un file `.geojson` scaricabile della mappa, quando le licenze lo permettono.

## Licenze

- Codice: da scegliere (per esempio MIT o EUPL-1.2).
- Caratteri: Inter e Newsreader, SIL Open Font License (`static/fonts/`).
- Leaflet: BSD-2-Clause (`static/vendor/leaflet/`).
- Mappa: © contributori di OpenStreetMap, ODbL.
