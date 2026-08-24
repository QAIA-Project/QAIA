#!/usr/bin/env python3
"""Campagne mutation sur les GARDE-FOUS construits en S38-S40.

Run: python eval/tools/mutate_guards.py   (ecrit eval/mutation-guards-<date>.txt)

Elle N'est PAS dans `make check` : elle modifie des fichiers du depot le temps de chaque
mutation, ce qu'une cible lancee en boucle par un nouveau venu ne doit pas faire. Elle se
relance a la main quand un garde-fou change.

Un controle protege une regle. Qui protege le controle ? Son auto-verification -- si elle est
reelle. Cette campagne mute la LOGIQUE DE DETECTION de chaque controle et exige que son selfcheck
passe au rouge. Une mutation qui survit designe une regle que le controle croit appliquer et
n'applique pas.
"""
import datetime, io, os, subprocess, sys, json

ROOT = os.getcwd()

MUTATIONS = [
    # (cible, selfcheck attendu rouge, libelle, avant, apres)
    ("eval/tools/check_test_levels.py", "eval/tools/selfcheck_test_levels.py",
     "niveau absent : la detection de l'absence est neutralisee",
     "if len(found) == 0:", "if False:"),
    ("eval/tools/check_test_levels.py", "eval/tools/selfcheck_test_levels.py",
     "niveau en double : la detection du doublon est neutralisee",
     "elif len(found) > 1:", "elif False:"),
    ("eval/tools/check_test_levels.py", "eval/tools/selfcheck_test_levels.py",
     "etiquette retiree : la table des retirees est videe",
     'RETIRED_TAGS = {\n    "@use-case"', 'RETIRED_TAGS = {} or {\n    "@NEVER-EMITTED"'),
    ("eval/tools/check_test_levels.py", "eval/tools/selfcheck_test_levels.py",
     "la pile de tags ne remonte plus au-dessus d'un commentaire",
     'elif above.strip() == "" or above.lstrip().startswith("#"):', "elif False:"),

    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "etapes : la comparaison verbatim est neutralisee",
     "if block[2] != steps:", "if False:"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "titre : la comparaison de titre est neutralisee",
     "if block[1] != title:", "if False:"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "scenario omis : la boucle des identifiants attendus est neutralisee",
     "if seen_ids.count(scenario_id) == 0:", "if False:"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "bloc en trop : la detection d'un identifiant inconnu est neutralisee",
     "if scenario_id not in expected_ids:", "if False:"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "langue : l'en-tete `language:` n'est plus exige",
     "if language not in LABELS:", "if False:"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "Outline : les `Examples` ne sont plus eclates",
     'if current["outline"] and current["rows"]:', "if False:"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "substitution : les parametres <x> ne sont plus remplaces",
     'text = text.replace("<%s>" % key, value)', "pass"),

    # PERIMETRE -- ajoutees le 2026-08-11 apres qu'une relecture hostile ait releve que les
    # quatorze mutations precedentes portaient TOUTES sur la logique de detection et AUCUNE sur
    # le perimetre. Or la panne reelle du jour etait une panne de perimetre : `site-qa/` cree le
    # soir, hors du controle ecrit le matin. La campagne ne pouvait pas la voir.
    ("eval/tools/check_test_levels.py", "eval/tools/selfcheck_test_levels.py",
     "perimetre : les cahiers vivants de site-qa sont exclus du controle",
     'FROZEN_EVIDENCE = (', 'FROZEN_EVIDENCE = ("site-qa",) + ('),
    ("eval/tools/check_test_levels.py", "eval/tools/selfcheck_test_levels.py",
     "perimetre : le controle ne voit plus aucun cahier",
     "            yield path", "            continue"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "perimetre : le balayage des paires ne rend plus rien",
     "        if len(projections) != 1:", "        if True:"),

    ("eval/tools/validate_manifest.py", "eval/tools/selfcheck_manifest_bylevel.py",
     "byLevel : la verification de la somme est neutralisee",
     "and summed != total:", "and False:"),
    ("eval/tools/validate_manifest.py", "eval/tools/selfcheck_manifest_bylevel.py",
     "byLevel : la liste fermee de cles n'est plus imposee",
     'unknown = sorted(set(by_lvl) - {"e2e", "api"})', "unknown = []"),
    ("eval/tools/validate_manifest.py", "eval/tools/selfcheck_manifest_bylevel.py",
     "byLevel : le bloc partiel n'est plus refuse",
     'for lvl in ("e2e", "api"):', "for lvl in ():"),

    # BAREME UNIVERSEL -- ajoutees le 2026-08-24 avec la phase 1 de la refonte. Elles visent le
    # defaut qui a coute le plus cher au projet (0 PASS sur 244 cahiers etrangers) et que les
    # 25 controles existants n'ont jamais pu voir. `check_universal_default.py` est son propre
    # selfcheck : il MESURE la propriete sur des cahiers reels au lieu de relire une regle.
    ("eval/tools/structural_score.py", "eval/tools/check_universal_default.py",
     "tracabilite : la dimension est de nouveau NOTEE ZERO au lieu d'etre retiree",
     "        raw = rescaled\n        traceability = None",
     "        raw = readability + completeness + coherence\n        traceability = 0.0"),
    ("eval/tools/structural_score.py", "eval/tools/check_universal_default.py",
     "tracabilite : la detection revient a n'accepter que la convention maison",
     'REQ_REF_PREFIXES = "AC|US|REQ|TC|FR|NFR|PBI|STORY|EPIC|BUG|ISSUE"',
     'REQ_REF_PREFIXES = "QAIA"'),
    ("eval/tools/structural_score.py", "eval/tools/check_universal_default.py",
     "profil : les conventions maison sont de nouveau imposees par defaut",
     '    if profile == "qaia":\n        if no_priority:',
     "    if True:\n        if no_priority:"),
    ("eval/tools/structural_score.py", "eval/tools/check_universal_default.py",
     "profil : le defaut bascule sur `qaia` a l'insu de l'appelant",
     'def score_feature(path, declared_acs=None, source_text=None, profile="universal",',
     'def score_feature(path, declared_acs=None, source_text=None, profile="qaia",'),

    # Le meme defaut, un etage plus haut. `automation_score.py` le portait EN PREMIER : il a
    # ete corrige le 2026-08-08 apres 408 constats faux, et `structural_score.py` l'a reproduit
    # a l'identique le lendemain. Deux outils, deux jours, une lecon ecrite entre les deux.
    ("eval/tools/automation_score.py", "eval/tools/selfcheck_automation_score.py",
     "budget : les quatre dimensions redeviennent inconditionnelles",
     'applicable = {"substantive_assertions": True}',
     'applicable = {"substantive_assertions": True, "robust_selectors": True,\n'
     '                  "pom_as_fixtures": True, "traceability": True}'),
    ("eval/tools/automation_score.py", "eval/tools/selfcheck_automation_score.py",
     "tracabilite : la detection revient a n'accepter que la convention maison",
     "            ref = tag or REQ_REF.search(title)", "            ref = tag"),
    ("eval/tools/automation_score.py", "eval/tools/selfcheck_automation_score.py",
     "profil : le defaut bascule sur `qaia` a l'insu de l'appelant",
     '                 profile="universal", third_party=None):',
     '                 profile="qaia", third_party=None):'),
    ("eval/tools/automation_score.py", "eval/tools/selfcheck_automation_score.py",
     "constats : ceux de convention remontent meme pour une dimension non evaluee",
     "        if dim in applicable:\n            findings.extend(convention_findings[key])",
     "        if True:\n            findings.extend(convention_findings[key])"),
    ("eval/tools/automation_score.py", "eval/tools/selfcheck_automation_score.py",
     "portee : le score ne dit plus qu'il est etroit",
     '"narrow": len(applicable) < 3,', '"narrow": False,'),

    # REFUS SUR PARSE VIDE -- ajoutees le 2026-08-24 avec la campagne de derive. Un repertoire
    # sans le moindre fichier de test rendait trois `unexercised-status` affirmatifs : la regle
    # est vraie et vide, l'outil ne mesure plus la suite mais sa propre cecite. Sur quatre
    # projets tiers, 11 constats sur 11 etaient de cette espece.
    ("eval/tools/spec_suite_drift.py", "eval/tools/selfcheck_spec_suite_drift.py",
     "parse vide : le refus de rendre un verdict est neutralise",
     "    findings = [] if unreadable else compare(declared, pairs, seen_paths, all_status)",
     "    unreadable = None\n"
     "    findings = compare(declared, pairs, seen_paths, all_status)"),
    ("eval/tools/spec_suite_drift.py", "eval/tools/selfcheck_spec_suite_drift.py",
     "parse vide : zero fichier lu n'est plus une raison de se taire",
     "    if files_read == 0:", "    if False:"),
    ("eval/tools/spec_suite_drift.py", "eval/tools/selfcheck_spec_suite_drift.py",
     "parse vide : aucun code HTTP reconnu n'est plus une raison de se taire",
     "    elif not all_status:", "    elif False:"),
    ("eval/tools/spec_suite_drift.py", "eval/tools/selfcheck_spec_suite_drift.py",
     "comptage : les fichiers illisibles ne sont plus comptes",
     "                    files_skipped += 1", "                    pass"),

    # REFUTATION -- ajoutees le 2026-08-24 apres que trois relecteurs en contexte vierge aient
    # trouve onze defauts que les 30 mutations precedentes et les cinq invariants de la garde
    # laissaient tous passer. Six etaient des regressions introduites le jour meme.
    ("eval/tools/structural_score.py", "eval/tools/check_universal_default.py",
     "tracabilite : le facteur reserve a nos identifiants revient sur le chemin universel",
     "    if profile == \"qaia\":\n        traceability = 25 * (len(traced) / n) * "
     "(0.6 + 0.4 * (len(ac_linked) / n))\n    else:\n        traceability = 25 * (len(traced) / n)",
     "    traceability = 25 * (len(traced) / n) * (0.6 + 0.4 * (len(ac_linked) / n))"),
    ("eval/tools/structural_score.py", "eval/tools/check_universal_default.py",
     "falaise : detecter une convention peut de nouveau faire baisser le score",
     "            raw = max(scored, rescaled)", "            raw = scored"),
    ("eval/tools/structural_score.py", "eval/tools/check_universal_default.py",
     "profil qaia : la tracabilite n'y est plus exigee",
     "    traceability_assessed = bool(traced) or profile == \"qaia\"",
     "    traceability_assessed = bool(traced)"),
    ("eval/tools/structural_score.py", "eval/tools/check_universal_default.py",
     "motif : le separateur redevient facultatif et reprend @HTML5, @IE11",
     '    r"@(?:[A-Z]{2,}(?:[-_][A-Za-z0-9]+)*[-_]\\d+"',
     '    r"@(?:[A-Z]{2,}[-_]?[A-Za-z0-9_-]*\\d+"'),
    ("eval/tools/automation_score.py", "eval/tools/check_universal_default.py",
     "motif : les deux outils du noyau divergent de nouveau",
     '                     r"|(?:AC|US|REQ|TC|FR|NFR|PBI|STORY|EPIC|BUG|ISSUE)\\d+)\\b")',
     '                     r")\\b")'),
    ("eval/tools/automation_score.py", "eval/tools/selfcheck_automation_score.py",
     "selecteurs : la precondition dure saute de nouveau sous le profil qaia",
     '    if selectors_applicable and (profile == "qaia" or selector_role > 0):',
     '    if profile == "qaia" or (selectors_applicable and selector_role > 0):'),
    ("eval/tools/automation_score.py", "eval/tools/selfcheck_automation_score.py",
     "parse vide : la suite sans test rend de nouveau un verdict",
     "    if tests_total == 0:", "    if False:"),
    ("eval/tools/structural_score.py", "eval/tools/check_universal_default.py",
     "ratio negatif : un zero faux revient a la place du non-evalue",
     "    negative_convention_present = bool(negative)",
     "    negative_convention_present = True"),
]


def write_atomic(path, text):
    """Ecrit par fichier temporaire + os.replace.

    `io.open(path, "w")` TRONQUE avant d'ecrire : une interruption dans cette fenetre laissait un
    garde-fou de ZERO OCTET, et la seule copie de l'original vivait en memoire du processus tue.
    Releve le 2026-08-11 par une relecture « developpeur ».
    """
    tmp = path + ".mutating"
    io.open(tmp, "w", encoding="utf-8", newline="").write(text)
    os.replace(tmp, path)


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, shell=False)
    return p.returncode, (p.stdout + p.stderr)


def main():
    # La date etait ECRITE EN DUR (« 2026-08-11 »), si bien que toute passe ulterieure
    # s'archivait sous une date a laquelle elle n'avait pas eu lieu. Un registre dont
    # les entrees mentent sur leur date ne prouve plus dans quel ordre les choses se
    # sont passees -- ce qui est la seule chose qu'un registre serve a prouver.
    today = datetime.date.today().isoformat()
    log = ["Campagne mutation sur les garde-fous -- passe du %s" % today, ""]
    log.append("Chaque mutation neutralise UNE regle de detection dans un controle.")
    log.append("TUEE = l'auto-verification du controle passe au rouge. SURVIT = personne ne l'aurait vu.")
    log.append("")
    killed = survived = unrunnable = 0
    for target, selfcheck, label, before, after in MUTATIONS:
        original = io.open(target, encoding="utf-8", newline="").read()
        if before not in original:
            print("!! motif introuvable :", label)
            log.append("[ERREUR] motif introuvable : %s" % label)
            unrunnable += 1
            continue
        write_atomic(target, original.replace(before, after, 1))
        try:
            code, out = run([sys.executable, selfcheck])
            ok = code != 0
        finally:
            write_atomic(target, original)
        killed += ok
        survived += (not ok)
        first = next((l for l in out.splitlines() if l.strip()), "")
        log.append("[%s] %s\n    %s -> exit=%d  %s"
                   % ("TUEE  " if ok else "SURVIT", label,
                      os.path.basename(selfcheck),
                      code, first[:150]))
        print(("TUEE   " if ok else "SURVIT "), label)
    log.append("")
    executed = killed + survived
    log.append("TOTAL : %d candidates, %d executees, %d tuees, %d survivantes, %d motif(s) "
               "introuvable(s)" % (len(MUTATIONS), executed, killed, survived, unrunnable))
    if unrunnable:
        log.append("ATTENTION : %d mutation(s) n'ont pas pu tourner -- un motif devenu obsolete "
                   "apres refactor sortait silencieusement du compte, et le TOTAL annoncait quand "
                   "meme len(MUTATIONS) executees. C'est le « vert a vide » exact, dans l'outil "
                   "ecrit pour le chasser (corrige le 2026-08-11)." % unrunnable)
    # REGISTRE, jamais ecrasement. Ce fichier a ete ECRASE une fois, le 2026-08-11 : la passe
    # precedente y decrivait la seule survivante interessante de la journee, une relance l'a
    # remplacee par le total final, et le commit qui a emporte la suppression affirmait dans
    # son message « trace brute conservee des DEUX passages ». Un outil de mesure qui detruit
    # la mesure precedente est la faute la plus couteuse qu'il puisse commettre, et aucun
    # controle ne l'aurait vue -- c'est la passe de refutation qui l'a trouvee.
    journal = "eval/mutation-guards-2026-08-11.txt"
    previous = ""
    if os.path.exists(journal):
        previous = io.open(journal, encoding="utf-8").read().rstrip("\n") + "\n\n"
        log.insert(0, "## Passe du %s -- les passes precedentes sont conservees ci-dessus" % today)
        log.insert(1, "")
    io.open(journal, "w", encoding="utf-8", newline="\n").write(previous + "\n".join(log) + "\n")
    print("killed", killed, "survived", survived, "unrunnable", unrunnable)
    # Une campagne qui laisse une survivante ou une mutation non jouee ne peut pas sortir 0 :
    # aucune automatisation ne pourrait s'appuyer dessus. La survivante legitime s'annote dans
    # le journal et se retire de la liste, elle ne se tolere pas par le code de sortie.
    return 1 if (survived or unrunnable) else 0


if __name__ == "__main__":
    sys.exit(main())
