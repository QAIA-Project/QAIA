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
SCENARIO_RE = re.compile(r"^\s*(Scenario Outline|Scenario)\s*:\s*(.*)$")
STEP_RE = re.compile(r"^\s*(Given|When|Then|And|But|\*)\s+(.*)$")
BACKGROUND_RE = re.compile(r"^\s*Background\s*:")
EXAMPLES_RE = re.compile(r"^\s*Examples\s*:")
TABLE_RE = re.compile(r"^\s*\|(.*)\|\s*$")
FEATURE_RE = re.compile(r"^Feature\s*:")

# Intitules acceptes, par langue. Liste FERMEE : un intitule libre rendrait la verification
# impossible, et c'est la verification qui justifie l'existence du rendu.
LABELS = {
    "fr": {"pre": "Preconditions", "act": "Action", "exp": "Resultat attendu"},
    "en": {"pre": "Preconditions", "act": "Action", "exp": "Expected result"},
}

BLOCK_HEADER_RE = re.compile(r"^###\s+(QAIA-[A-Za-z0-9-]+)\s+·\s+(.*)$")
STEP_LINE_RE = re.compile(r"^\s*\d+\.\s+(.*)$")


def parse_feature(path):
    """Return [(scenario_id, title, [step_text, ...])], Outlines already expanded."""
    lines = io.open(path, encoding="utf-8").read().splitlines()
    background, scenarios = [], []
    current = None      # dict(id, title, steps, outline, headers, rows)
    in_background = False
    pending_tags = []
    in_examples = False

    def flush():
        if current is None:
            return
        if current["outline"] and current["rows"]:
            for index, row in enumerate(current["rows"], start=1):
                mapping = dict(zip(current["headers"], row))
                steps = [substitute(s, mapping) for s in current["steps"]]
                scenarios.append(("%s-e%d" % (current["id"], index),
                                  substitute(current["title"], mapping),
                                  background + steps))
        else:
            scenarios.append((current["id"], current["title"], background + current["steps"]))

    for line in lines:
        if FEATURE_RE.match(line):
            in_background = False
            continue
        if BACKGROUND_RE.match(line):
            flush()
            current, in_background, in_examples = None, True, False
            continue
        scenario = SCENARIO_RE.match(line)
        if scenario:
            flush()
            in_background, in_examples = False, False
            ids = [i for tag in pending_tags for i in ID_RE.findall(tag)]
            current = {"id": ids[0] if ids else None, "title": scenario.group(2).strip(),
                       "steps": [], "outline": scenario.group(1) == "Scenario Outline",
                       "headers": [], "rows": []}
            pending_tags = []
            continue
        if TAG_RE.match(line):
            pending_tags.append(line)
            continue
        if EXAMPLES_RE.match(line):
            in_examples = True
            continue
        table = TABLE_RE.match(line)
        if table and in_examples and current is not None:
            cells = [c.strip() for c in table.group(1).split("|")]
            if not current["headers"]:
                current["headers"] = cells
            else:
                current["rows"].append(cells)
            continue
        step = STEP_RE.match(line)
        if step:
            text = step.group(2).strip()
            if in_background:
                background.append(text)
            elif current is not None:
                current["steps"].append(text)
    flush()
    return scenarios


def substitute(text, mapping):
    for key, value in mapping.items():
        text = text.replace("<%s>" % key, value)
    return text


def parse_projection(path):
    """Return ([(scenario_id, title, [step_text, ...])], language)."""
    raw = io.open(path, encoding="utf-8").read().splitlines()
    language = None
    for line in raw[:12]:
        match = re.match(r"^language:\s*([a-z]{2})\s*$", line.strip())
        if match:
            language = match.group(1)
            break

    blocks, current = [], None
    for line in raw:
        header = BLOCK_HEADER_RE.match(line)
        if header:
            if current:
                blocks.append(current)
            current = (header.group(1), header.group(2).strip(), [])
            continue
        step = STEP_LINE_RE.match(line)
        if step and current:
            current[2].append(step.group(1).strip())
    if current:
        blocks.append(current)
    return blocks, language


def check_pair(feature_path, projection_path):
    problems = []
    expected = parse_feature(feature_path)
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
    for scenario_id, title, steps in expected:
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
        if len(features) != 1 or len(projections) != 1:
            pairs.append((dirpath, features, projections))
            continue
        pairs.append((os.path.join(dirpath, features[0]),
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
            failures.append((pair[0], ["un seul .feature et un seul testbook.<lang>.md par "
                                       "dossier sont supportes ; trouve %d / %d"
                                       % (len(pair[1]), len(pair[2]))]))
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
