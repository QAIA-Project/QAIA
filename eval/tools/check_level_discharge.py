#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Une condition de refus est-elle couverte AU NIVEAU ou sa promesse est faite ? (#107)

ADR 0001 exige un scenario pour chaque condition `[req-neg]` ; ADR 0008 precise qu'une condition
marquee `[level: api]` n'est acquittee que par un scenario `@api` -- un ecran qui affiche un
message d'erreur ne verifie pas le 400 du contrat. La regle est ecrite a quatre endroits de
`generate` (04-choosing-techniques, 07-emitting-the-test-book, api-steps, negative-ratio) et,
avant ce fichier, aucun controle ne la verifiait.

Le controle apparie la conception (`03-design.md`) et le cahier (`.feature`) :

- conception : chaque condition (ligne de tableau ou puce dont le premier element est un
  identifiant `...-C<n>`), son marqueur `[req-neg]` (ou une colonne `[req-neg]` non vide), son
  niveau `[level: e2e|api]` -- sur la ligne, ou par une declaration globale du document
  (« Toutes les conditions sont `[level: api]` ») ;
- cahier : les commentaires `# condition: ID[, ID...]`. Un tel commentaire place APRES la ligne
  `Scenario` et avant toute etape appartient a ce scenario ; place ailleurs, il appartient au
  scenario suivant.

Verdict, pour chaque condition `[req-neg]` de niveau connu :

- ACQUITTEE   un scenario lie porte `@negative` ET le tag de son niveau ;
- VIOLATION   des scenarios lies existent, aucun ne porte les deux -- c'est le cas que la regle
              existe pour interdire (un refus de contrat « couvert » par un ecran) ;
- NON LIEE    aucun scenario ne la cite : le lien est un commentaire en texte libre, et ce
              controle n'est jamais plus solide que lui. Dit, jamais compte comme acquitte.

Une condition sans niveau declare est comptee a part et n'est pas jugee : on ne devine pas un
niveau que la conception n'a pas decide.

Usage : python3 check_level_discharge.py [<03-design.md> <cahier.feature> ...]
Sans argument : les paires de reference de PAIRS. Sortie non nulle sur VIOLATION ou NON LIEE.
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Les paires ou la conception declare ses niveaux ET ou le cahier lie ses scenarios a ses
# conditions. Les autres exemples du depot ne le font pas encore (voir le rapport de #107).
PAIRS = [
    ("eval/reverse-engineering-2026-08-11/10-saucedemo-03-design.md",
     ["eval/reverse-engineering-2026-08-11/11-saucedemo.feature"]),
    ("eval/reverse-engineering-2026-08-11/20-restfulbooker-03-design.md",
     ["eval/reverse-engineering-2026-08-11/21-restfulbooker.feature"]),
]

# Exceptions CONNUES, chacune avec sa raison. Une exception qui ne se produit plus fait echouer le
# controle : une dispense perimee est une regle qui ne garde plus rien sans que personne le voie.
KNOWN = {
    "SD03-C13": "conception du 2026-08-11 prise entre deux pages de `generate` qui se "
                "contredisaient (coverage-expansion.md contre negative-ratio.md) ; contradiction "
                "levee le 2026-11-23 en faveur de la definition fermee. L'artefact date est garde "
                "tel quel, comme preuve.",
}

COND_ID = r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-C\d+"
ROW_ID = re.compile(r"^\s*(?:\|\s*|[-*]\s+)\**`?(" + COND_ID + r")`?\**\s*(?:\||—|-|:|\s)")
LEVEL = re.compile(r"\[level:\s*(e2e|api)\s*\]")
GLOBAL_LEVEL = re.compile(
    r"(toutes les conditions|les \d+ conditions|every (?:derived )?condition|all conditions)"
    r"[^\n]*?\[level:\s*(e2e|api)\s*\]", re.I)
REQNEG_MARK = re.compile(r"\[req-neg\]")
NEGATED_REQNEG = re.compile(r"\b(?:pas|not|non|no)\s+[*`]*\[req-neg\][*`]*", re.I)
COND_COMMENT = re.compile(r"^\s*#.*?\bconditions?\s*:\s*(.*)$", re.I)
SCENARIO = re.compile(r"^\s*(Scenario|Scenario Outline|Example|Scenario Template)\s*:")
STEP = re.compile(r"^\s*(Given|When|Then|And|But|\*)\s")
TAG_LINE = re.compile(r"^\s*@")


def parse_design(text):
    """Rend {id: {"reqneg": bool, "level": str|None}}."""
    glob = GLOBAL_LEVEL.search(text)
    global_level = glob.group(2) if glob else None
    conds = {}
    reqneg_col = None
    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if any("req-neg" in c for c in cells) and not ROW_ID.match(line):
                # En-tete : retient la colonne `[req-neg]`, s'il y en a une.
                reqneg_col = next(i for i, c in enumerate(cells) if "req-neg" in c)
                continue
        else:
            if not line.strip():
                reqneg_col = None if not line.strip() and reqneg_col is None else reqneg_col
        m = ROW_ID.match(line)
        if not m:
            continue
        cid = m.group(1)
        # « **Pas `[req-neg]`** : ... » est une conception qui ECARTE le marqueur, en le citant.
        # Lu naivement, il comptait comme marque : sept des huit premieres « violations » sur les
        # paires de reference venaient de la (premiere execution, 2026-11-23).
        # Une negation explicite l'emporte sur toute autre mention de la ligne : « Pas `[req-neg]`
        # en l'etat... si Q7 est tranchee, cette condition DEVIENT `[req-neg]` » decrit un futur
        # conditionnel, pas la marque d'aujourd'hui.
        reqneg = bool(REQNEG_MARK.search(line)) and not NEGATED_REQNEG.search(line)
        if not reqneg and reqneg_col is not None and line.lstrip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if reqneg_col < len(cells):
                # La colonne `[req-neg]` porte aussi d'autres marques (`[open] Q9`) : seule une
                # affirmation explicite compte, jamais une cellule simplement non vide.
                cell = cells[reqneg_col].strip("*` ").lower()
                reqneg = cell in ("oui", "yes", "x", "✓", "✔")
        lv = LEVEL.search(line)
        conds[cid] = {"reqneg": reqneg, "level": lv.group(1) if lv else global_level}
    return conds


def parse_feature(text):
    """Rend [(titre, tags:set, conditions:set)] ; les conditions viennent des commentaires."""
    scenarios = []
    pending_tags, pending_conds = set(), set()
    current, current_has_step = None, False
    for line in text.splitlines():
        cm = COND_COMMENT.match(line)
        if cm:
            ids = set(re.findall(COND_ID, cm.group(1)))
            if current is not None and not current_has_step:
                current[2].update(ids)
            else:
                pending_conds.update(ids)
            continue
        if TAG_LINE.match(line):
            pending_tags.update(t.lower() for t in re.findall(r"@[\w-]+", line))
            continue
        if SCENARIO.match(line):
            current = (line.strip(), pending_tags, set(pending_conds))
            scenarios.append(current)
            pending_tags, pending_conds, current_has_step = set(), set(), False
            continue
        if STEP.match(line) and current is not None:
            current_has_step = True
    return scenarios


def check(design_path, feature_paths):
    conds = parse_design(open(design_path, encoding="utf-8").read())
    scenarios = []
    for fp in feature_paths:
        scenarios += parse_feature(open(fp, encoding="utf-8").read())
    out = {"discharged": [], "violation": [], "unlinked": [], "no_level": []}
    for cid, c in sorted(conds.items()):
        if not c["reqneg"]:
            continue
        if c["level"] is None:
            out["no_level"].append(cid)
            continue
        linked = [s for s in scenarios if cid in s[2]]
        if not linked:
            out["unlinked"].append(cid)
        elif any("@negative" in s[1] and "@" + c["level"] in s[1] for s in linked):
            out["discharged"].append(cid)
        else:
            out["violation"].append((cid, c["level"], [sorted(s[1]) for s in linked]))
    return conds, out


def main(argv):
    pairs = PAIRS
    if argv:
        pairs = [(argv[0], argv[1:])]
    bad = 0
    known_seen = set()
    for design, feats in pairs:
        d = design if os.path.isabs(design) else os.path.join(ROOT, design)
        fs = [f if os.path.isabs(f) else os.path.join(ROOT, f) for f in feats]
        conds, out = check(d, fs)
        n_reqneg = sum(1 for c in conds.values() if c["reqneg"])
        print("%s : %d conditions, %d [req-neg] -- %d acquittee(s) a leur niveau"
              % (os.path.basename(design), len(conds), n_reqneg, len(out["discharged"])))
        if not argv:
            for v in [v for v in out["violation"] if v[0] in KNOWN]:
                known_seen.add(v[0])
                print("  CONNUE     %s : %s" % (v[0], KNOWN[v[0]]))
            out["violation"] = [v for v in out["violation"] if v[0] not in KNOWN]
        for cid, lvl, tagsets in out["violation"]:
            print("  VIOLATION  %s [level: %s] : aucun scenario lie ne porte @negative et @%s -- %s"
                  % (cid, lvl, lvl, "; ".join(" ".join(t) for t in tagsets)))
        for cid in out["unlinked"]:
            print("  NON LIEE   %s : aucun scenario ne la cite (# condition: %s)" % (cid, cid))
        if out["no_level"]:
            print("  sans niveau declare, non jugees : " + ", ".join(out["no_level"]))
        if n_reqneg == 0:
            print("  AUCUNE condition [req-neg] lue : un controle qui ne lit rien ne rend pas vert")
            bad += 1
        bad += len(out["violation"]) + len(out["unlinked"])
    if not argv:
        for stale in sorted(set(KNOWN) - known_seen):
            print("  DISPENSE PERIMEE  %s ne se produit plus : retirer l'entree de KNOWN" % stale)
            bad += 1
    print("OK" if not bad else "%d probleme(s)" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
