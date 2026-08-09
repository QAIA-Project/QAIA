#!/usr/bin/env python3
"""Garde le tier d'agents opt-in : hors des plugins, outils bornes, et jamais humain.

## Pourquoi ce fichier existe

Trois promesses sont faites dans `agents-tier/README.md`, et les trois sont le genre de promesse
qui s'erode en silence a la premiere reecriture :

1. **Le tier reste dehors.** Le garde-fou CI refuse `agents/` dans `plugins/` -- ecrit contre les
   hooks et MCP, dont le danger est du shell auto-execute. Un agent n'en porte pas, mais il
   **elargit ce que le modele peut atteindre** via sa liste `tools:`. Plus petit qu'un hook, pas
   nul : le tier reste separe et explicite plutot que glisse dans le coeur en relisant la regle
   jusqu'a ce qu'elle autorise ce qu'on veut.

2. **Les juges sont en lecture seule.** Un juge capable d'editer l'artefact qu'il note n'est pas
   un juge. La regle 3 du projet (« un producteur ne note jamais sa propre sortie ») ne tient que
   si l'outillage l'empeche, pas s'il le deconseille.

3. **Aucun agent ne se fait passer pour une personne.** Ils portent un prenom parce qu'un delegue
   nomme se manipule mieux -- mais un verdict qualite signe d'un nom humain sur un produit
   reglemente pourrait se lire comme une signature. Chaque agent doit le dire lui-meme.

Run: python eval/tools/check_agents_tier.py
Exit 0 conforme, 1 une promesse n'est plus tenue, 2 arborescence introuvable.
"""
import io
import os
import re
import sys

NL = chr(10)
TIER = os.path.join("agents-tier", "agents")
READ_ONLY = {"Read", "Glob", "Grep"}
JUDGES = {"camille-judge", "elian-refuter"}
# Un agent qui peut lancer un shell est un choix, pas un accident : la liste est explicite ici
# pour qu'un ajout silencieux echoue.
MAY_RUN_COMMANDS = {"marek-automation", "yuki-triage"}

NOT_A_PERSON = re.compile(r"is an automated agent, not a person", re.I)
FM = re.compile(r"^---\s*$(.*?)^---\s*$", re.S | re.M)


def main():
    if not os.path.isdir(TIER):
        print("BROKEN: %s introuvable -- lancer depuis la racine du depot." % TIER)
        return 2

    # 1. le tier reste hors des plugins
    bad = []
    for root, dirs, _ in os.walk("plugins"):
        for d in dirs:
            if d == "agents":
                bad.append(("emplacement", os.path.join(root, d),
                            "un repertoire agents/ est apparu dans plugins/"))

    files = sorted(f for f in os.listdir(TIER) if f.endswith(".md"))
    if not files:
        bad.append(("tier", TIER, "aucun agent -- le controle porterait sur du vide"))

    seen = set()
    for f in files:
        path = os.path.join(TIER, f)
        text = io.open(path, encoding="utf-8").read()
        m = FM.match(text)
        if not m:
            bad.append(("frontmatter", f, "absent ou mal ferme"))
            continue
        fm = m.group(1)

        name = re.search(r"^name:\s*(\S+)", fm, re.M)
        name = name.group(1) if name else None
        if not name:
            bad.append(("frontmatter", f, "champ `name` manquant"))
            continue
        seen.add(name)
        if name + ".md" != f:
            bad.append(("nommage", f, "le fichier devrait s'appeler %s.md" % name))

        if not re.search(r"^description:\s*\S", fm, re.M):
            bad.append(("frontmatter", f, "champ `description` manquant -- sans lui la delegation "
                                          "automatique ne peut pas se declencher"))

        tools = re.search(r"^tools:\s*(.+)$", fm, re.M)
        tset = set(t.strip() for t in tools.group(1).split(",")) if tools else set()
        if not tset:
            bad.append(("outils", f, "aucune liste `tools:` -- un agent sans perimetre d'outils "
                                     "herite de tout"))
        if "*" in tset:
            bad.append(("outils", f, "`tools: *` -- le perimetre doit etre enumere"))

        # 2. les juges sont en lecture seule
        if name in JUDGES and not tset <= READ_ONLY:
            bad.append(("juge", f, "outils hors lecture seule : %s -- un juge qui peut editer "
                                   "l'artefact qu'il note n'est pas un juge"
                        % ", ".join(sorted(tset - READ_ONLY))))

        if "Bash" in tset and name not in MAY_RUN_COMMANDS:
            bad.append(("outils", f, "`Bash` non declare pour cet agent -- l'ajouter est un choix "
                                     "a inscrire dans MAY_RUN_COMMANDS avec son motif"))

        # 3. aucun agent ne se fait passer pour une personne
        if not NOT_A_PERSON.search(text):
            bad.append(("identite", f, "ne declare pas etre un agent automatique et non une "
                                       "personne"))

    for j in sorted(JUDGES):
        if j not in seen:
            bad.append(("juge", j, "agent attendu absent du tier"))

    if bad:
        print("TIER D'AGENTS NON CONFORME.\n")
        for kind, where, why in bad:
            print("  %-12s %-26s %s" % (kind, where, why))
        print("\nCes trois promesses sont ecrites dans agents-tier/README.md. Une promesse qui")
        print("n'est gardee que par l'intention ne survit pas a la premiere reecriture.")
        return 1

    print("OK: %d agent(s) -- hors plugins, outils enumerees, juges en lecture seule, "
          "identite non humaine declaree." % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
