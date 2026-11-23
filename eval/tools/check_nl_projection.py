#!/usr/bin/env python3
"""Fail when a natural-language test book diverges from the Gherkin it projects.

## Pourquoi ce fichier existe

Le rendu en langage naturel (`testbook.<lang>.md`, sprint S40) est le document que des humains
vont LIRE -- un metier, un responsable de test, quelqu'un qui ne lit pas de Gherkin. C'est
exactement le genre de document que personne ne re-verifie jamais contre sa source.

`testbook-export` porte deja la regle : *« Export is a projection, never a second source »*. Sans
controle, cette regle tient par l'intention -- et ce depot a mesure sept fois en une session ce
que valent les regles tenues par l'intention (CLAUDE.md, « Ne jamais faire passer du Markdown par
le shell »). Un rendu qui derive devient un mensonge a retardement : plus lu que le Gherkin,
jamais confronte a lui.

## Ce qui est verifie

Pour chaque paire `<dossier>/*.feature` + `<dossier>/testbook.<lang>.md` :

1. **Aucun scenario omis** -- chaque identifiant `@QAIA-...` du Gherkin a son bloc.
2. **Aucun bloc en trop** -- pas d'identifiant que le Gherkin ne porte pas.
3. **Aucune etape inventee, aucune etape perdue** : les etapes du bloc sont celles du scenario,
   dans le meme ordre, texte VERBATIM. Le mot-cle Gherkin est remplace par un intitule
   (Preconditions / Action / Resultat attendu), le texte de l'etape ne bouge pas d'un caractere.
4. **Les `Scenario Outline` sont eclates** : un bloc par ligne d'`Examples`, identifiant suffixe
   `-eN`, chaque `<parametre>` remplace par la valeur de SA ligne -- substitution deterministe,
   donc verifiable.
5. **Les etapes de `Background`** apparaissent en tete des preconditions de chaque bloc.

Ce qui n'est PAS verifie : le style, la fluidite, l'utilite du rendu pour un lecteur. Ce controle
garantit que le rendu ne MENT pas, pas qu'il est bon. La seconde question demande un humain.

Run: python eval/tools/check_nl_projection.py
Exit 0 conforme, 1 divergence, 2 perimetre casse.
"""
import io
import os
import re
import sys

TAG_RE = re.compile(r"^\s*@")
ID_RE = re.compile(r"@(QAIA-[A-Za-z0-9-]+)")
# `Example` et `Scenario Template` sont des synonymes anglais de `Scenario` / `Scenario Outline`
# (dialecte `en` du Gherkin officiel), `Scenarios` un synonyme d'`Examples`.
SCENARIO_RE = re.compile(r"^\s*(Scenario Outline|Scenario Template|Scenario|Example)\s*:\s*(.*)$")
STEP_RE = re.compile(r"^\s*(Given|When|Then|And|But|\*)\s+(.*)$")
BACKGROUND_RE = re.compile(r"^\s*Background\s*:")
RULE_RE = re.compile(r"^\s*Rule\s*:")
EXAMPLES_RE = re.compile(r"^\s*(Examples|Scenarios)\s*:")
TABLE_RE = re.compile(r"^\s*\|(.*)\|\s*$")
FEATURE_RE = re.compile(r"^\s*Feature\s*:")
DOCSTRING_RE = re.compile(r'^\s*("""|```)')
LANGUAGE_RE = re.compile(r"^\s*#\s*language\s*:\s*([A-Za-z-]+)\s*$")

# Categorie de chaque etape, deduite de son mot-cle. `And`, `But` et `*` heritent de l'etape
# precedente -- c'est la semantique du Gherkin, et c'est ce que le rendu doit respecter.
CATEGORY = {"Given": "pre", "When": "act", "Then": "exp"}

# Intitules acceptes, par langue. Liste FERMEE : un intitule libre rendrait la verification
# impossible, et c'est la verification qui justifie l'existence du rendu.
LABELS = {
    "fr": {"pre": "Preconditions", "act": "Action", "exp": "Resultat attendu"},
    "en": {"pre": "Preconditions", "act": "Action", "exp": "Expected result"},
}

BLOCK_HEADER_RE = re.compile(r"^###\s+(QAIA-[A-Za-z0-9-]+)\s+·\s+(.*)$")
STEP_LINE_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
LABEL_LINE_RE = re.compile(r"^\s*\*\*(.+?)\*\*\s*$")


def parse_feature(path, problems=None):
    """Return [(scenario_id, title, [step_text, ...], [category, ...])], Outlines expanded.

    Le parseur suit les blocs du Gherkin (Feature, Rule, Background, Scenario, Examples,
    docstring) au lieu de lire chaque ligne isolement : un scanner sans etat lisait le contenu
    d'un docstring comme des etapes, fusionnait deux blocs `Examples`, faisait heriter les tags de
    `Feature:` au premier scenario, et sortait vert a vide sur un dialecte qu'il ne connaissait
    pas (#106). Ce que le rendu en langage naturel ne sait pas exprimer -- un docstring, une
    table de donnees de pas -- est SIGNALE dans `problems`, jamais ignore : un controle qui ne
    sait pas doit le dire.
    """
    if problems is None:
        problems = []
    name = os.path.basename(path)
    lines = io.open(path, encoding="utf-8").read().splitlines()

    for line in lines[:5]:
        match = LANGUAGE_RE.match(line)
        if match and match.group(1).lower() not in ("en", "en-us", "en-gb"):
            problems.append("%s : dialecte Gherkin `%s` non pris en charge -- seul l'anglais "
                            "est lu ; aucun scenario ne serait reconnu et le controle sortirait "
                            "vert a vide" % (name, match.group(1)))
            return []

    state = {"feature_bg": [], "rule_bg": None}
    scenarios = []
    current = None      # dict(id, title, steps, cats, outline, rows)
    in_background = False
    pending_tags = []
    in_examples = False
    headers = None      # en-tete du bloc `Examples` en cours ; None = la prochaine ligne en est un
    in_docstring = None
    last_category = None
    content_lines = 0

    def active_background():
        return state["rule_bg"] if state["rule_bg"] is not None else state["feature_bg"]

    def flush():
        if current is None:
            return
        bg_steps = [s for s, _ in active_background()]
        bg_cats = [c for _, c in active_background()]
        if current["outline"] and current["rows"]:
            for index, mapping in enumerate(current["rows"], start=1):
                steps = [substitute(s, mapping) for s in current["steps"]]
                scenarios.append(("%s-e%d" % (current["id"], index),
                                  substitute(current["title"], mapping),
                                  bg_steps + steps, bg_cats + current["cats"]))
        elif current["outline"]:
            problems.append("%s : %s est un `Scenario Outline` sans aucune ligne d'`Examples` "
                            "-- rien a projeter, et ses `<parametres>` resteraient litteraux"
                            % (name, current["id"]))
        else:
            scenarios.append((current["id"], current["title"], bg_steps + current["steps"],
                              bg_cats + current["cats"]))

    for line in lines:
        if in_docstring:
            if line.strip().startswith(in_docstring):
                in_docstring = None
            continue
        docstring = DOCSTRING_RE.match(line)
        if docstring:
            in_docstring = docstring.group(1)
            owner = current["id"] if current is not None else "Background"
            problems.append("%s : %s porte un docstring -- le rendu en langage naturel ne sait "
                            "pas l'exprimer, son contenu ne serait verifie contre rien"
                            % (name, owner))
            continue
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            content_lines += 1
        if FEATURE_RE.match(line):
            # Les tags de `Feature:` portent sur la feature, pas sur le premier scenario.
            pending_tags = []
            in_background = False
            continue
        if RULE_RE.match(line):
            flush()
            current, in_background, in_examples = None, False, False
            state["rule_bg"] = list(state["feature_bg"])
            pending_tags = []
            continue
        if BACKGROUND_RE.match(line):
            flush()
            current, in_background, in_examples = None, True, False
            last_category = None
            continue
        scenario = SCENARIO_RE.match(line)
        if scenario:
            flush()
            in_background, in_examples = False, False
            last_category = None
            ids = [i for tag in pending_tags for i in ID_RE.findall(tag)]
            current = {"id": ids[0] if ids else None, "title": scenario.group(2).strip(),
                       "steps": [], "cats": [],
                       "outline": scenario.group(1) in ("Scenario Outline", "Scenario Template"),
                       "rows": []}
            pending_tags = []
            continue
        if TAG_RE.match(line):
            pending_tags.append(line)
            continue
        if EXAMPLES_RE.match(line):
            # Chaque bloc `Examples` a son propre en-tete : un second bloc ne prolonge pas le
            # premier, et sa ligne d'en-tete n'est pas une donnee.
            in_examples, headers = True, None
            continue
        table = TABLE_RE.match(line)
        if table:
            cells = [c.strip() for c in table.group(1).split("|")]
            if in_examples and current is not None:
                if headers is None:
                    headers = cells
                else:
                    current["rows"].append(dict(zip(headers, cells)))
            else:
                owner = current["id"] if current is not None else "Background"
                problems.append("%s : %s porte une table de donnees de pas -- le rendu en "
                                "langage naturel ne sait pas l'exprimer, son contenu pourrait "
                                "etre omis ou inverse sans que rien ne le voie" % (name, owner))
            continue
        step = STEP_RE.match(line)
        if step:
            in_examples = False
            keyword, text = step.group(1), step.group(2).strip()
            category = CATEGORY.get(keyword, last_category or "pre")
            last_category = category
            if in_background:
                active_background().append((text, category))
            elif current is not None:
                current["steps"].append(text)
                current["cats"].append(category)
    flush()

    if not scenarios and content_lines and not problems:
        problems.append("%s : aucun scenario reconnu dans un fichier non vide -- mot-cle ou "
                        "dialecte inconnu ; un controle qui ne lit rien ne peut pas sortir vert"
                        % name)
    return scenarios


def substitute(text, mapping):
    for key, value in mapping.items():
        text = text.replace("<%s>" % key, value)
    return text


def parse_projection(path):
    """Return ([(scenario_id, title, [step_text, ...], [label, ...])], language)."""
    raw = io.open(path, encoding="utf-8").read().splitlines()
    language = None
    for line in raw[:12]:
        match = re.match(r"^language:\s*([a-z]{2})\s*$", line.strip())
        if match:
            language = match.group(1)
            break

    blocks, current, label = [], None, None
    for line in raw:
        header = BLOCK_HEADER_RE.match(line)
        if header:
            if current:
                blocks.append(current)
            current = (header.group(1), header.group(2).strip(), [], [])
            label = None
            continue
        heading = LABEL_LINE_RE.match(line)
        if heading and current:
            label = heading.group(1).strip()
            continue
        step = STEP_LINE_RE.match(line)
        if step and current:
            current[2].append(step.group(1).strip())
            current[3].append(label)
    if current:
        blocks.append(current)
    return blocks, language


def check_pair(feature_paths, projection_path):
    """`feature_paths` : un chemin, ou la liste des .feature du dossier (l'ordre fixe l'ordre
    attendu des blocs). Un cahier reel porte plusieurs fichiers pour une meme US -- exiger un
    seul serait une limite de l'outil imposee au produit."""
    if isinstance(feature_paths, str):
        feature_paths = [feature_paths]
    problems = []
    expected = []
    for path in feature_paths:
        expected.extend(parse_feature(path, problems))
    blocks, language = parse_projection(projection_path)

    if language not in LABELS:
        problems.append("en-tete `language:` absent ou hors de la liste fermee %s"
                        % sorted(LABELS))

    expected_ids = [s[0] for s in expected]
    seen_ids = [b[0] for b in blocks]

    for scenario_id in expected_ids:
        if seen_ids.count(scenario_id) == 0:
            problems.append("scenario %s absent du rendu" % scenario_id)
        elif seen_ids.count(scenario_id) > 1:
            problems.append("scenario %s rendu %d fois" % (scenario_id, seen_ids.count(scenario_id)))
    for scenario_id in seen_ids:
        if scenario_id not in expected_ids:
            problems.append("le rendu porte %s, que le Gherkin ne contient pas" % scenario_id)

    by_id = {b[0]: b for b in blocks}
    labels = LABELS.get(language, {})
    for scenario_id, title, steps, categories in expected:
        block = by_id.get(scenario_id)
        if block is None:
            continue
        if block[1] != title:
            problems.append("%s : titre rendu %r, Gherkin %r" % (scenario_id, block[1], title))
        if block[2] != steps:
            extra = [s for s in block[2] if s not in steps]
            missing = [s for s in steps if s not in block[2]]
            if extra:
                problems.append("%s : etape(s) INVENTEE(S), absente(s) du Gherkin : %r"
                                % (scenario_id, extra[:3]))
            if missing:
                problems.append("%s : etape(s) PERDUE(S), presente(s) dans le Gherkin : %r"
                                % (scenario_id, missing[:3]))
            if not extra and not missing:
                problems.append("%s : memes etapes, ordre different" % scenario_id)
        elif labels:
            # Les etapes sont les bonnes : encore faut-il qu'elles soient rangees sous le bon
            # intitule. Un `Then` sous « Preconditions » se lit comme un etat de depart.
            for index, (category, label) in enumerate(zip(categories, block[3]), start=1):
                if label != labels[category]:
                    problems.append("%s : etape %d rangee sous %r, son mot-cle Gherkin la "
                                    "place sous %r" % (scenario_id, index, label,
                                                       labels[category]))
                    break
    return problems, len(expected)


def find_pairs(root="."):
    pairs = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", "export")]
        features = sorted(f for f in filenames if f.endswith(".feature"))
        projections = sorted(f for f in filenames
                             if re.match(r"^testbook\.[a-z]{2}\.md$", f))
        if not features or not projections:
            continue
        # Un seul rendu par dossier : il projette TOUS les .feature de l'US, dans l'ordre
        # alphabetique des fichiers. Deux rendus concurrents seraient deux sources.
        if len(projections) != 1:
            pairs.append((dirpath, features, projections))
            continue
        pairs.append(([os.path.join(dirpath, f) for f in features],
                      os.path.join(dirpath, projections[0])))
    return pairs


def main(argv):
    root = argv[1] if len(argv) > 1 else "."
    pairs = find_pairs(root)
    if not pairs:
        print("ERREUR : perimetre casse -- aucune paire .feature / testbook.<lang>.md trouvee, "
              "alors que ce depot en contient au moins une. Un controle sans paire passerait "
              "vert sans rien verifier.", file=sys.stderr)
        return 2

    failures, total_scenarios = [], 0
    for pair in pairs:
        if len(pair) == 3:
            failures.append((pair[0], ["un seul testbook.<lang>.md par dossier ; trouve %d "
                                       "rendu(s) pour %d fichier(s) .feature"
                                       % (len(pair[2]), len(pair[1]))]))
            continue
        feature_path, projection_path = pair
        problems, count = check_pair(feature_path, projection_path)
        total_scenarios += count
        if problems:
            failures.append((projection_path, problems))

    print("Perimetre rendu naturel : %d paire(s), %d scenario(s) projete(s)."
          % (len(pairs), total_scenarios))

    if failures:
        print("::error::%d rendu(s) divergent(s) de leur Gherkin." % len(failures))
        for path, problems in failures:
            print("  %s" % path)
            for problem in problems:
                print("      %s" % problem)
        print("\nLe rendu est une PROJECTION, jamais une seconde source : corriger le rendu, "
              "ou corriger le Gherkin puis re-projeter -- jamais laisser les deux dire deux "
              "choses.")
        return 1

    print("OK: chaque scenario a exactement un bloc, aux memes etapes, dans le meme ordre.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
