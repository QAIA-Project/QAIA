#!/bin/sh
# Assemble l'arbre publie sur GitHub Pages. UNE seule definition, appelee par
# `.github/workflows/pages.yml` (pour publier) et par le job `shipped-suites` de `ci.yml` (pour
# tester ce qui est publie). Avant le 2026-11-23, la regle vivait en double : dans `pages.yml` et
# dans `site-qa/tests/serve.js`, et la suite du site pouvait rester verte avec une production
# cassee (quatre contre-exemples ecrits dans `serve.js`, #108).
#
#   /       <- site/
#   /demo/  <- examples/expense-demo/static-demo/
#
# Usage : sh .github/scripts/assemble-site.sh <dossier-de-sortie>
set -eu
out="${1:-_site}"
rm -rf "$out"
mkdir -p "$out/demo"
cp -r site/. "$out/"
cp -r examples/expense-demo/static-demo/. "$out/demo/"
test -f "$out/index.html"
test -f "$out/demo/index.html"
test -f "$out/llms.txt"
echo "--- published tree:"
find "$out" -type f | sort
