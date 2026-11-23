#!/usr/bin/env python3
"""Prove check_nl_projection.py catches every way a natural-language rendering can drift.

## Pourquoi ce fichier existe

Le rendu en langage naturel n'a de valeur que si l'on peut affirmer qu'il ne ment pas. Cette
affirmation vaut ce que vaut son controle -- et un controle qui n'a jamais ete vu rouge ne prouve
rien. Ce depot a eu deux portes de CI vertes a vide en douze jours (2026-07-30, 2026-08-10) : les
deux fois, rien n'exercait la panne que la cible pretendait attraper.

Huit divergences injectees, une par facon dont une projection peut trahir sa source, plus le cas
conforme qui doit rester silencieux. Le neuvieme cas compte autant que les huit autres : un
controle qui signalerait tout serait inutilisable, et son rouge ne voudrait rien dire.

| Fixture | Ce qu'elle injecte | Attendu |
|---|---|---|
| `conforme.md` | rien | silence |
| `divergence-etape-inventee.md` | une etape absente du Gherkin | INVENTEE |
| `divergence-etape-perdue.md` | une etape du Gherkin non rendue | PERDUE |
| `divergence-scenario-omis.md` | un exemple d'`Outline` saute | absent du rendu |
| `divergence-bloc-en-trop.md` | un identifiant que le Gherkin ne porte pas | inconnu |
| `divergence-ordre.md` | memes etapes, ordre change | ordre different |
| `divergence-valeur-example.md` | une valeur d'`Examples` modifiee d'un caractere | INVENTEE + PERDUE |
| `divergence-titre.md` | un titre reecrit | titre divergent |
| `divergence-langue.md` | en-tete `language:` absent | langue hors liste fermee |

`divergence-valeur-example.md` est la plus importante : c'est la derive qu'un relecteur humain ne
verra jamais -- « 998 » au lieu de « 999 » dans un document de vingt pages.

Run: python eval/tools/selfcheck_nl_projection.py
Exit 0 conforme, 1 le controle ne detecte pas ce qu'il promet, 2 fixtures introuvables.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_nl_projection as C

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "nl-projection-red")
FEATURE = os.path.join(FIXTURES, "base.feature")

# (fichier, fragment attendu dans AU MOINS un probleme signale)
CASES = [
    ("divergence-etape-inventee.md", "INVENTEE"),
    ("divergence-etape-perdue.md", "PERDUE"),
    ("divergence-scenario-omis.md", "absent du rendu"),
    ("divergence-bloc-en-trop.md", "que le Gherkin ne contient pas"),
    ("divergence-ordre.md", "ordre different"),
    ("divergence-valeur-example.md", "INVENTEE"),
    ("divergence-titre.md", "titre rendu"),
    ("divergence-langue.md", "language"),
]

# Les sept formes Gherkin valides que l'ancien scanner ligne a ligne lisait de travers (#106).
# Ecrites a l'execution dans un dossier temporaire plutot que versionnees sous fixtures/ : elles
# n'ont pas de rendu, et le perimetre de `make lint` balaie tout `.feature` du depot.
# (nom, contenu, verification) -- verification(scenarios, problems) rend None ou un message.
FORMS = [
    ("docstring", (
        "Feature: F\n"
        "  @QAIA-X-001\n"
        "  Scenario: A docstring\n"
        "    Given a payload:\n"
        '      """\n'
        "      When the moon is full\n"
        "      Then nothing happens\n"
        '      """\n'
        "    Then it works\n"),
     lambda s, p: None if (any("docstring" in x for x in p)
                           and all("moon" not in step for sc in s for step in sc[2]))
     else "le contenu du docstring est lu comme des etapes, ou le docstring n'est pas signale"),
    ("table de pas", (
        "Feature: F\n"
        "  @QAIA-X-002\n"
        "  Scenario: A data table\n"
        "    Given these users:\n"
        "      | name  |\n"
        "      | alice |\n"
        "    Then they exist\n"),
     lambda s, p: None if any("table de donnees" in x for x in p)
     else "une table de donnees de pas est perdue en silence"),
    ("deux blocs Examples", (
        "Feature: F\n"
        "  @QAIA-X-003\n"
        "  Scenario Outline: Size <size>\n"
        "    When they send size <size>\n"
        "    Then status is <code>\n"
        "    Examples:\n"
        "      | size | code |\n"
        "      | 0    | 400  |\n"
        "    Examples:\n"
        "      | code | size |\n"
        "      | 201  | 5    |\n"),
     lambda s, p: None if ([sc[0] for sc in s] == ["QAIA-X-003-e1", "QAIA-X-003-e2"]
                           and s[1][2] == ["they send size 5", "status is 201"])
     else "le second bloc `Examples` est fusionne au premier : %r" % [sc[:3] for sc in s]),
    ("Outline sans Examples", (
        "Feature: F\n"
        "  @QAIA-X-004\n"
        "  Scenario Outline: Size <size>\n"
        "    When they send size <size>\n"
        "    Then it is refused\n"),
     lambda s, p: None if any("sans aucune ligne" in x for x in p)
     else "un Outline sans Examples passe, `<size>` exige litteralement"),
    ("tags de Feature", (
        "@QAIA-FEATURE-999\n"
        "Feature: F\n"
        "  Scenario: Untagged\n"
        "    Then it works\n"),
     lambda s, p: None if s and s[0][0] is None
     else "le premier scenario non tague herite des tags de Feature : %r" % [sc[0] for sc in s]),
    ("Rule et Background multiples", (
        "Feature: F\n"
        "  Background:\n"
        "    Given the system is up\n"
        "  Rule: one\n"
        "    Background:\n"
        "      Given rule one context\n"
        "    @QAIA-X-006\n"
        "    Scenario: In one\n"
        "      Then a\n"
        "  Rule: two\n"
        "    Background:\n"
        "      Given rule two context\n"
        "    @QAIA-X-007\n"
        "    Scenario: In two\n"
        "      Then b\n"),
     lambda s, p: None if (len(s) == 2 and s[1][2] == ["the system is up", "rule two context", "b"])
     else "le Background d'une Rule fuit dans la suivante : %r" % [sc[2] for sc in s]),
    ("dialecte francais", (
        "# language: fr\n"
        "Fonctionnalité: F\n"
        "  @QAIA-X-008\n"
        "  Scénario: Un cas\n"
        "    Alors ça marche\n"),
     lambda s, p: None if any("dialecte" in x for x in p)
     else "un dialecte non lu sort vert a vide"),
    ("mot-cle inconnu sans en-tete de langue", (
        "Fonctionnalité: F\n"
        "  Scénario: Un cas\n"
        "    Alors ça marche\n"),
     lambda s, p: None if any("aucun scenario reconnu" in x for x in p)
     else "un fichier dont rien n'est reconnu sort vert a vide"),
]


def check_forms():
    import tempfile
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, content, verify in FORMS:
            path = os.path.join(tmp, "form.feature")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(content)
            problems = []
            scenarios = C.parse_feature(path, problems)
            verdict = verify(scenarios, problems)
            if verdict:
                failures.append("forme %s : %s" % (name, verdict))
    return failures


def check_labels():
    """Un `Then` range sous « Preconditions » : memes etapes, meme ordre, mauvais intitule."""
    import tempfile
    text = open(os.path.join(FIXTURES, "conforme.md"), encoding="utf-8").read()
    swapped = text.replace("**Expected result**", "**Preconditions**", 1)
    if swapped == text:
        return ["la fixture conforme ne porte plus d'intitule **Expected result** a deplacer"]
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "labels.md")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(swapped)
        problems, _ = C.check_pair(FEATURE, path)
    if not any("rangee sous" in p for p in problems):
        return ["intitules : un `Then` range sous Preconditions passe vert : %r" % problems]
    return []


def main():
    if not os.path.exists(FEATURE):
        print("::error::fixture introuvable : %s" % FEATURE, file=sys.stderr)
        return 2

    failures = []

    clean, count = C.check_pair(FEATURE, os.path.join(FIXTURES, "conforme.md"))
    if clean:
        failures.append("le rendu CONFORME est signale -- faux positif : %s" % clean)
    if count != 3:
        failures.append("la fixture devrait porter 3 scenarios (1 + un Outline a 2 exemples), "
                        "%d comptes" % count)

    for name, fragment in CASES:
        path = os.path.join(FIXTURES, name)
        if not os.path.exists(path):
            failures.append("fixture manquante : %s" % name)
            continue
        problems, _ = C.check_pair(FEATURE, path)
        if not problems:
            failures.append("%s : divergence NON detectee -- le controle est aveugle a ce cas"
                            % name)
        elif not any(fragment in p for p in problems):
            failures.append("%s : detectee, mais aucun message ne porte %r ; obtenu %r"
                            % (name, fragment, problems[:2]))

    failures.extend(check_forms())
    failures.extend(check_labels())

    # Les fixtures rouges doivent rester HORS du perimetre du controle lui-meme, sinon `make check`
    # serait rouge en permanence et la preuve deviendrait une panne.
    in_scope = [p for p in C.find_pairs(".")
                if "nl-projection-red" in str(p)]
    if in_scope:
        failures.append("les fixtures rouges sont dans le perimetre du controle : %s" % in_scope)

    # LE PERIMETRE, garde comme dans selfcheck_test_levels.py. Toutes les verifications
    # ci-dessus passent par `check_pair` avec des chemins explicites : elles resteraient vertes
    # si `find_pairs` cessait de trouver quoi que ce soit. C'est la panne du 2026-08-11 sur le
    # controle jumeau, ou deux cahiers livres le soir etaient hors du garde-fou du matin.
    pairs = C.find_pairs(".")
    # Une paire VALIDE est un couple (liste de .feature, chemin du rendu). Les triplets sont des
    # signalements d'erreur, pas des paires -- verifier la seule presence d'une chaine dans la
    # liste laissait passer une mutation qui transformait toutes les paires en erreurs, tout en
    # gardant les chemins visibles (mesure le 2026-08-11 : mutation survivante).
    valid = {}
    for pair in pairs:
        if len(pair) == 2 and str(pair[1]).endswith(".md"):
            valid[str(pair[1])] = pair
    for witness in ("site-qa", "booking-api-demo"):
        if not any(witness in path for path in valid):
            failures.append("perimetre : aucune paire VALIDE pour %s -- son rendu n'est compare "
                            "a rien" % witness)
    if len(valid) < 2:
        failures.append("perimetre : %d paire(s) VALIDE(S) -- ce depot en contient au moins "
                        "deux, un balayage qui n'en voit presque aucune passe vert sans rien "
                        "verifier" % len(valid))

    if failures:
        print("::error::l'auto-verification du rendu en langage naturel echoue.")
        for line in failures:
            print("  " + line)
        return 1

    print("OK: les 8 divergences injectees et les %d formes Gherkin de #106 sont detectees, un "
          "intitule faux est signale, le rendu conforme reste silencieux, et les fixtures sont "
          "hors perimetre du controle." % len(FORMS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
