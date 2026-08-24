#!/usr/bin/env python3
"""Fail when a document claims a skill count that no longer matches the repository.

Why this exists, and it is not hypothetical. On 2026-08-08 a blank-context review panel found
**four different skill counts in four documents dated the same day** -- 30, 32, 33 and 35 -- while
the repository contained 35. Each had been correct when written; five skills were added over the
course of the day and each document was updated at a different moment, or not at all. The count had
already been corrected four times by hand before this file existed. The fifth correction was the
point at which correcting it again stopped being the right answer.

## What is checked, and what is deliberately not

**Total claims** -- a number presented as *the catalogue's size*: `35 skills across 4 plugins`,
`all 35 skills`, `**35 skills**`, `des 35 skills`. These must equal the real total.

**Per-plugin claims** in the README -- `qaia-core 0.2.34, 17 skills`. These must equal that
plugin's real count. They drift independently of the total and were stale on their own.

Not checked, on purpose:

- **`docs/STATUS.md`** is a dated, chronological log. `29 skills` in a Sprint-26 entry is *correct*
  -- it records what was true then. Checking it would demand rewriting history to keep a linter
  quiet, which is the opposite of what the file is for.
- **Another project's catalogue.** QASkills' ~380 skills are theirs to be wrong about. Recognised
  by a marker on the line.
- **Bare counts in prose** (`12 skills renvoient à docs/`). They describe a subset, not the total.
  Only the shapes listed above are read as a total claim.

The first version of this file checked every `<n> skills` occurrence and produced **35 findings of
which 33 were false positives** -- the same failure that made nine linter warnings sit ignored for
three sprints. A check that cries wolf is a check nobody runs.

Run: python eval/tools/check_skill_counts.py
Exit 0 all claims current, 1 at least one is stale, 2 nothing to count.
"""
import io
import json
import os
import glob
import re
import sys

# Le README de CHAQUE plugin annonce sa propre version et son nombre de skills. Le controle
# de CI qui verifie le README principal ne les couvrait pas : le 2026-08-08 une revue les a
# trouves perimes de 6 a 20 versions correctifs -- 0.2.14 pour 0.2.34, 0.1.8 pour 0.1.27.
# Un README de plugin est LIVRE a l'utilisateur : il est plus visible que le README racine.
PLUGIN_README = "plugins/%s/README.md"
# `skill` au singulier accepte : la fusion du 2026-08-24 a ramene `qaia-score` a UNE skill, et
# le motif n'acceptait que « skills ». Un controle qui impose une faute de grammaire pour se
# taire finit par etre contourne plutot que corrige.
PLUGIN_STATUS = re.compile(
    r"\*\*Status:\s*([0-9]+\.[0-9]+\.[0-9]+),\s*(\d{1,3})\s+skills?\.\*\*")

TOTAL_SCANNED = [
    "README.md",
    # Ajoute le 2026-08-10, dans le meme commit que sa creation. Le README bilingue a ete scinde
    # en README.md (EN) + README.fr.md (FR) ; la moitie francaise porte les memes comptes et les
    # memes versions de plugin. L'inscrire ici au moment de la scission plutot qu'apres la
    # premiere derive : un fichier hors perimetre est un angle mort qu'on cree soi-meme.
    "README.fr.md",
    "docs/TEST-COVERAGE-MAP.md",
    "docs/ACTION-PLAN.md",
    "plugins/qaia-core/CATALOGUE.md",
    "site/index.html",
    "site/compare.html",
    "site/walkthrough.html",
    "site/llms.txt",
]

# A total claim, in the shapes this project actually writes.
TOTAL_CLAIM = [
    re.compile(r"(\d{1,4})\s+skills\s+across\s+\d+\s+plugins", re.I),
    re.compile(r"\ball\s+(\d{1,4})\s+skills", re.I),
    re.compile(r"\*\*(\d{1,4})\s+skills\*\*"),
    re.compile(r"\bdes\s+(\d{1,4})\s+skills", re.I),
    re.compile(r"(\d{1,4})\s+skills,\s+\d+\s+plugins", re.I),
    re.compile(r"\bThe\s+(\d{1,4})\s+skills\s+are\b", re.I),
    re.compile(r"\bSur\s+les\s+(\d{1,4})\s+skills", re.I),

    # --- Les trois formes que ce controle a laissees passer, trouvees le 2026-08-10 ------
    #
    # Le fichier scannait deja `site/compare.html` et `site/llms.txt` et rendait OK pendant
    # qu ils annoncaient 35, 30 et 30 pour un depot a 37. Le perimetre etait bon ; c est la
    # FORME des affirmations qui n etait pas prevue. Un controle qui vise la bonne page et
    # rate la phrase porte la meme garantie fausse qu un compte juste au-dessus d une table
    # fausse -- le defaut que `unlisted_skills()` documente un etage plus bas.
    #
    # 1. Un adjectif glisse entre le nombre et « skills » : « 30 Markdown skills across
    #    4 plugins ». La forme `across N plugins` reste ce qui en fait un total.
    re.compile(r"(\d{1,4})\s+(?:\w+\s+){1,2}skills\s+across\s+\d+\s+plugins", re.I),

    # 2. Une cellule de tableau dont le contenu ENTIER est « N skills » : dans une ligne
    #    « Catalogue size », c est un total par construction. Exiger `<td>` colle aux
    #    chiffres protege les catalogues des autres, ecrits en approximation (`~380`) --
    #    un `~` suffit a ne pas matcher, et c est voulu, pas un accident heureux.
    re.compile(r"<td>\s*(\d{1,4})\s+skills\s*</td>", re.I),

    # 3. Le comparatif sans le mot : « ~380 skills over there, 30 here ». Le nombre nu ne
    #    peut etre lu comme un total que par ce qui le precede, donc la regle porte la
    #    phrase entiere plutot que le nombre.
    re.compile(r"skills\s+over\s+there,\s*(\d{1,4})\s+here", re.I),
]

# Un chiffre PERIME mais DATE n'est pas une erreur : c'est de l'histoire.
#
# Ce controle conseillait deja, dans son message d'echec, de « reecrire la phrase pour qu'elle
# porte sa date au lieu de se lire comme actuelle » -- et se declenchait quand meme, parce que
# rien n'implementait cette echappatoire. **Son conseil n'etait pas applicable.** Un controle qui
# demande une chose impossible apprend a son lecteur a le contourner, pas a lui obeir. Releve le
# 2026-08-24 en essayant de suivre le conseil.
#
# La date doit SUIVRE le nombre de pres (40 caracteres) : « 37 skills du 2026-08-11 » passe,
# « 37 skills [...trois lignes...] mis a jour le 2026-08-11 » non. Sans cette proximite,
# n'importe quelle date presente dans le document couvrirait n'importe quel chiffre perime.
_DATE_NEAR = re.compile(r"\b(?:du|le|on|as of|au)?\s*\(?\d{4}-\d{2}-\d{2}", re.I)


def _dated(line, pos):
    return bool(_DATE_NEAR.search(line[pos:pos + 40]))


# Deux formes reelles : "`qaia-core` 0.2.34, 17 skills" dans le bandeau de statut, et
# "plugins/qaia-core/ | Core plugin: ... (17 skills," dans la carte du depot. La seconde a ete
# oubliee par la premiere version resserree de ce controle, et elle etait perimee.
PER_PLUGIN = [
    re.compile(r"`(qaia-[a-z]+)`\s+[\d.]+,\s*(\d{1,3})\s+skills", re.I),
    re.compile(r"plugins/(qaia-[a-z]+)/.{0,160}?\((\d{1,3})\s+skills", re.I),
]

EXTERNAL = re.compile(r"qaskills|qa[- ]orchestra|agentic[- ]qe|neonwatty|ClaudeCodeAgents", re.I)


def count_skills(root):
    n = 0
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "node_modules"]
        n += sum(1 for f in files if f == "SKILL.md")
    return n


def unlisted_skills():
    """Les skills absentes de la table du README de leur propre plugin.

    Trouve par un audit INDEPENDANT le 2026-08-09, et c'est le constat le plus severe qu'on
    puisse faire a ce fichier : les README annoncaient le bon NOMBRE -- ce controle le
    verifiait, et passait -- pendant que leur table en listait moins.

    **Neuf skills etaient invisibles dans leur propre documentation**, dont `qaia`, la
    meta-skill que le README racine dit d'utiliser en premier, absente depuis son ajout.

    Autrement dit : le controle certifiait l'affirmation et ignorait le contenu -- exactement
    le mode d'echec qu'il avait ete ecrit pour empecher un etage plus haut. Un compte juste
    au-dessus d'une table fausse est pire qu'un compte faux : il porte une garantie.
    """
    out = []
    for plugin_dir in sorted(glob.glob(os.path.join("plugins", "*"))):
        if not os.path.isdir(os.path.join(plugin_dir, "skills")):
            continue
        readme = os.path.join(plugin_dir, "README.md")
        if not os.path.isfile(readme):
            continue
        text = io.open(readme, encoding="utf-8").read()
        listed = set(re.findall(r"`([a-z][a-z0-9-]+)`", text))
        for d in sorted(glob.glob(os.path.join(plugin_dir, "skills", "*"))):
            name = os.path.basename(d)
            if os.path.isdir(d) and name not in listed:
                out.append((readme, name))
    return out


def main():
    total = count_skills("plugins")
    if total == 0:
        print("BROKEN: no SKILL.md under plugins/ -- run from the repository root.")
        return 2
    per_plugin = {p: count_skills(os.path.join("plugins", p))
                  for p in sorted(os.listdir("plugins"))
                  if os.path.isdir(os.path.join("plugins", p))}

    stale, checked = [], 0
    for path in TOTAL_SCANNED:
        if not os.path.isfile(path):
            continue
        for i, line in enumerate(io.open(path, encoding="utf-8", errors="replace"), 1):
            if EXTERNAL.search(line):
                continue
            for rx in TOTAL_CLAIM:
                for m in rx.finditer(line):
                    checked += 1
                    if int(m.group(1)) != total and not _dated(line, m.end()):
                        stale.append((path, i, "total", m.group(0).strip(), total))
            for rx in PER_PLUGIN:
                for m in rx.finditer(line):
                    plugin, claimed = m.group(1), int(m.group(2))
                    if plugin not in per_plugin:
                        continue
                    checked += 1
                    if claimed != per_plugin[plugin]:
                        stale.append((path, i, plugin, m.group(0).strip()[:70], per_plugin[plugin]))

    # --- les README de plugin : version ET nombre de skills -------------------------
    import json as _json
    for p, n in per_plugin.items():
        path = PLUGIN_README % p
        if not os.path.isfile(path):
            continue
        manifest = os.path.join("plugins", p, ".claude-plugin", "plugin.json")
        if not os.path.isfile(manifest):
            continue
        ver = _json.load(io.open(manifest, encoding="utf-8"))["version"]
        body = io.open(path, encoding="utf-8", errors="replace").read()
        m = PLUGIN_STATUS.search(body)
        checked += 1
        if not m:
            stale.append((path, 0, p, "aucune ligne **Status: <version>, <n> skills.**",
                          "%s / %d" % (ver, n)))
        elif m.group(1) != ver or int(m.group(2)) != n:
            stale.append((path, body[:m.start()].count(chr(10)) + 1, p,
                          m.group(0), "%s / %d skills" % (ver, n)))

    missing = unlisted_skills()
    if missing:
        print("SKILL ABSENTE DE LA TABLE DE SON PROPRE README -- %d cas.\n" % len(missing))
        for readme, name in missing:
            print("  %-34s ne liste pas `%s`" % (readme, name))
        print("\nUn compte juste au-dessus d'une table fausse est pire qu'un compte faux :")
        print("il porte une garantie. Ajouter la ligne, ou retirer la skill.")
        return 1

    if stale:
        print("STALE SKILL COUNT -- the repository has %d skills (%s).\n"
              % (total, ", ".join("%s %d" % (k, v) for k, v in per_plugin.items())))
        for path, i, what, claim, real in stale:
            # `real` est un entier pour un compte, une chaine pour un README de plugin
            # (« 0.2.34 / 17 skills »). La premiere version de ce message plantait sur le
            # second cas : le controle detectait la derive et s ecrasait en la rapportant.
            print("  %s:%s  claims \"%s\"  ->  %s is %s" % (path, i or "?", claim, what, real))
        print("\nUpdate the claim, or -- if the number is deliberately historical -- rewrite it so it")
        print("carries its date (\"30 le matin du 2026-08-08\") instead of reading as current.")
        return 1

    print("OK: %d skill-count claim(s) match the repository, et chaque skill figure dans la "
          "table de son README (%d skills; %s)."
          % (checked, total, ", ".join("%s %d" % (k, v) for k, v in per_plugin.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
