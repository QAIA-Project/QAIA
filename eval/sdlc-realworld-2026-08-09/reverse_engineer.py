# -*- coding: utf-8 -*-
"""Retro-ingenierie : deriver l'exigence des artefacts observables, puis la confronter a la
specification publiee. Tout ecart est un constat de la phase Discovery.

Sources OBSERVABLES (ce qu'un testeur voit sans lire la spec) :
  - specs/e2e/SELECTORS.md : le contrat d'interface que toute implementation doit fournir
  - specs/e2e/*.spec.ts    : les comportements attendus, un par titre de test
Source de VERITE a confronter :
  - specs/api/openapi.yml
"""
import io, os, re, sys, yaml, collections

E2E = sys.argv[1]
SPEC = sys.argv[2]

sel = io.open(os.path.join(E2E, "SELECTORS.md"), encoding="utf-8").read()

# --- 1. les routes API que l'IHM utilise, d'apres le contrat -----------------------------
ui_api = sorted(set(re.findall(r"`(/api/[^`]+)`", sel)) | set(re.findall(r"\*\*(/api/[^*]+)\*\*", sel)))
# --- 2. les routes de pages ---------------------------------------------------------------
ui_pages = sorted(set(re.findall(r"`(/(?!api)[a-z0-9:{}/@-]*)`", sel)))

d = yaml.safe_load(io.open(SPEC, encoding="utf-8"))
spec_paths = sorted((d.get("paths") or {}).keys())

def norm(p):
    p = re.sub(r"^/api", "", p)
    p = re.sub(r"\{[^}]+\}", "{}", p)
    p = re.sub(r":[a-zA-Z_]+", "{}", p)
    return p.rstrip("/") or "/"

spec_norm = {norm(p) for p in spec_paths}
ui_norm = {norm(p) for p in ui_api}

print("=== INVENTAIRE OBSERVABLE ===")
print("  endpoints API cites par le contrat UI : %d" % len(ui_api))
print("  chemins declares par openapi.yml      : %d" % len(spec_paths))
print("  routes de page citees par le contrat  : %d" % len(ui_pages))
print()
print("=== CONFRONTATION ===")
only_ui = sorted(ui_norm - spec_norm)
only_spec = sorted(spec_norm - ui_norm)
print("  utilises par l'IHM, ABSENTS de la spec : %d" % len(only_ui))
for p in only_ui:
    print("      %s" % p)
print("  declares par la spec, JAMAIS cites par l'IHM : %d" % len(only_spec))
for p in only_spec:
    print("      %s" % p)

# --- 3. comportements observables, par domaine ------------------------------------------
titles = []
for f in sorted(os.listdir(E2E)):
    if not f.endswith(".spec.ts"):
        continue
    txt = io.open(os.path.join(E2E, f), encoding="utf-8").read()
    for m in re.finditer(r"^\s*test\s*(?:\.\s*\w+\s*)?\(\s*(['\"`])((?:\\.|(?!\1).)*)\1", txt, re.M):
        titles.append((f.replace(".spec.ts", ""), m.group(2)))
print()
print("=== COMPORTEMENTS OBSERVABLES : %d ===" % len(titles))
by = collections.Counter(d for d, _ in titles)
for k, v in by.most_common():
    print("   %-24s %3d" % (k, v))

# --- 4. ce que la spec promet et qu'aucun comportement observable ne couvre --------------
METHODS = ("get", "post", "put", "delete", "patch")
codes = collections.Counter()
for p, item in (d.get("paths") or {}).items():
    for m, op in (item or {}).items():
        if m in METHODS:
            for c in (op.get("responses") or {}):
                codes[str(c)] += 1
blob = " ".join(t.lower() for _, t in titles)
print()
print("=== CODES PROMIS PAR LA SPEC vs TRACE DANS LES COMPORTEMENTS ===")
HINTS = {"401": ["unauthor", "not logged", "logged out", "auth"], "403": ["forbidden", "not the author", "other user"],
         "404": ["not found", "404", "missing", "nonexistent", "unknown"], "409": ["conflict", "duplicate", "already"],
         "422": ["validation", "invalid", "error", "required"], "204": ["delete", "remove"]}
for c, n in sorted(codes.items()):
    if c.startswith("2") and c != "204":
        continue
    seen = any(h in blob for h in HINTS.get(c, []))
    print("   %-4s declare %2d fois   trace dans un titre de test : %s" % (c, n, "oui" if seen else "NON"))
