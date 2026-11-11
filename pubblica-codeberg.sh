#!/usr/bin/env bash
# Pubblica il sito su Codeberg Pages: genera build/ e lo carica sul ramo "pages".
# Prima volta: in Codeberg, Impostazioni del repository > Webhook > Forgejo,
# URL https://TUONOME.codeberg.page/radici/ e filtro ramo "pages".
# Guida: https://docs.codeberg.org/codeberg-pages/
set -euo pipefail

SITE_BASE="${SITE_BASE:-/radici/}" python3 freeze.py

tmp="$(mktemp -d)"
git worktree add -f "$tmp" pages 2>/dev/null || git worktree add -f --orphan -b pages "$tmp"
find "$tmp" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -R build/. "$tmp"/
(
  cd "$tmp"
  git add -A
  git commit -m "Pubblica il sito $(date +%Y-%m-%d)" || echo "Nessuna modifica da pubblicare"
  git push origin pages
)
git worktree remove --force "$tmp"
echo "Fatto. Il sito si aggiorna appena Codeberg riceve il webhook."
