#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Echoue si le chemin par defaut du barème penalise un cahier pour n'etre pas QAIA.

C'est la porte d'ENTREE qui remplace les portes de sortie. Les 25 controles de `make check`
verifient a posteriori que le depot a bien ecrit ce qu'il devait ; aucun n'a attrape le defaut
qui a coute le plus cher au projet -- un barème qui confond « ce test est mauvais » avec « ce
test n'est pas de moi », commis deux fois en deux outils a un jour d'ecart alors que la lecon
avait ete ecrite entre les deux.

Ce controle ne relit pas une regle : il MESURE la propriete, en prenant un cahier reel et en lui
retirant les conventions de ce projet.

Trois invariants, chacun tombant sur un defaut deja survenu :

  I1. Retirer les tags de priorite et de technique ne change PAS le score par defaut.
      (Ils produisaient 493 constats sur 666 sur un corpus etranger.)

  I2. Retirer les tags d'identifiant ne fait pas CHUTER le score par defaut : la tracabilite
      sort du denominateur au lieu d'etre notee zero.
      (Elle valait 25 points sur 100 perdus par construction -- 0 PASS sur 244 fichiers.)

  I3. Aucun CONSTAT du chemin par defaut ne nomme une convention de ce projet.
      (Un constat nomme un defaut ; l'absence d'une convention maison n'en est pas un.)

Exit 0 si les trois tiennent, 1 sinon.
"""
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import structural_score  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cahiers reels de ce depot -- pas des fixtures fabriquees pour l'occasion. Une fixture ecrite
# pour passer le controle prouve seulement que la fixture a ete bien ecrite.
BOOKS = [
    "examples/expense-demo/qaia-journey/testbooks/US-004/approval-chain.feature",
    "examples/expense-demo/qaia-journey/testbooks/US-004/line-items.feature",
    "examples/expense-demo/qaia-journey/testbooks/US-004/audit-and-auth.feature",
    "examples/expense-demo/qaia-journey/testbooks/US-004/workflow-state-machine.feature",
]

CONVENTION_TAGS = re.compile(
    r"@(?:P[123]|ep|boundary|decision-table|state-transition|use-case|pairwise|error-guessing|"
    r"crud|metamorphic|domain-analysis|ai-feature)\b", re.I)
# On retire TOUTE reference d'exigence, pas seulement la notre : la premiere version ne retirait
# que `@QAIA-...` et laissait `@AC1`, qui est une reference legitime que la detection reconnait
# a juste titre -- le controle accusait l'outil d'un defaut qui etait dans le controle.
#
# Le motif est ecrit ICI, en toutes lettres, PAS emprunte a `structural_score.REQ_REF_RE`. Il
# l'a ete, « pour que les deux ne puissent plus diverger », et le resultat fut l'inverse : une
# mutation ramenant la detection a `@QAIA-` mutait aussi le controle, qui la laissait passer.
# Elle a survecu a la campagne du 2026-08-24. Un controle qui importe la logique qu'il verifie
# ne verifie rien -- il devient aveugle exactement la ou l'outil l'est.
ID_TAGS = re.compile(r"@[A-Z]{2,}[-_:]?[A-Za-z0-9_-]*\d\S*")
# Vocabulaire qui trahit une convention maison dans un constat rendu a un utilisateur tiers.
CONVENTION_WORDS = re.compile(r"priority tag|technique tag|@P[123]|@QAIA|closed list", re.I)

failures = []


def score(text, profile=None):
    """`profile=None` appelle l'outil SANS argument de profil -- c'est le defaut qu'on teste.

    La premiere version passait `profile="universal"` partout : elle verifiait donc que le
    profil universel se comporte bien, jamais que c'est LUI le defaut. Une mutation basculant
    le defaut sur `qaia` a survecu a la campagne du 2026-08-24. Un controle qui nomme
    explicitement ce qu'il veut tester ne teste pas ce que l'appelant obtiendra.
    """
    fd, path = tempfile.mkstemp(suffix=".feature")
    os.close(fd)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    try:
        if profile is None:
            return structural_score.score_feature(path)
        return structural_score.score_feature(path, profile=profile)
    finally:
        os.unlink(path)


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

    print("check_universal_default :")
    checked = 0
    for rel in BOOKS:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            failures.append("cahier de reference absent : %s" % rel)
            continue
        original = open(path, encoding="utf-8").read()
        base = score(original)
        if base.get("score") is None:
            failures.append("%s n'est pas notable -- controle impossible" % rel)
            continue
        checked += 1
        name = os.path.basename(rel)

        # I1 -- retirer priorite et technique ne bouge pas le score
        stripped = CONVENTION_TAGS.sub("", original)
        s1 = score(stripped)
        if s1["score"] != base["score"]:
            failures.append(
                "I1 %s : retirer les tags de priorite/technique change le score par defaut "
                "(%s -> %s). Une convention de ce projet pese sur le barème universel."
                % (name, base["score"], s1["score"]))

        # I2 -- retirer les identifiants ne fait pas chuter le score
        untraced = ID_TAGS.sub("", original)
        s2 = score(untraced)
        if s2.get("traceabilityAssessed"):
            failures.append(
                "I2 %s : la tracabilite est encore declaree evaluee apres retrait de tous les "
                "identifiants -- la detection reconnait quelque chose qu'elle ne devrait pas."
                % name)
        else:
            # « Ne chute pas » etait mal pose : retirer une dimension ou le cahier avait le
            # maximum fait baisser sa moyenne, arithmetiquement, meme quand le traitement est
            # correct. La propriete qui compte est exacte et se calcule.
            #
            # Notee zero :        S3 - penalites            (S3 = lisibilite+completude+coherence)
            # Retiree du denom. : S3 * 100/75 - penalites   >= la precedente, toujours.
            #
            # Le controle exige donc que le score obtenu soit AU MOINS celui du reechelonnement,
            # et STRICTEMENT superieur au zero-notation des que le cahier n'est pas parfait sur
            # les trois autres dimensions. C'est la difference entre « on ne t'evalue pas
            # la-dessus » et « tu as zero » -- toute la refonte tient dans cet ecart.
            s3 = base["readability"] + base["completeness"] + base["coherence"]
            pen = sum(base["penalties"].values())
            zeroed = max(0, round(s3 - pen))
            rescaled = max(0, round(s3 * 100.0 / 75.0 - pen))
            if s2["traceability"] is not None:
                failures.append(
                    "I2 %s : `traceability` vaut %s au lieu de null sur un cahier sans reference "
                    "-- une dimension non evaluee doit se dire non evaluee, pas valoir un nombre."
                    % (name, s2["traceability"]))
            if s2["score"] != rescaled:
                failures.append(
                    "I2 %s : score %s, or le reechelonnement des trois dimensions qui "
                    "transferent donne %s. Le calcul applique n'est pas celui annonce."
                    % (name, s2["score"], rescaled))
            if s3 < 75 and s2["score"] <= zeroed:
                failures.append(
                    "I2 %s : score %s <= %s, ce que donnerait une tracabilite NOTEE ZERO. La "
                    "dimension n'est pas sortie du denominateur." % (name, s2["score"], zeroed))

        # I3 -- aucun constat par defaut ne nomme une convention maison
        for r, label in ((base, "cahier d'origine"), (s2, "cahier sans identifiants")):
            for f in r.get("findings", []):
                if CONVENTION_WORDS.search(f):
                    failures.append(
                        "I3 %s (%s) : un constat du chemin par defaut nomme une convention de "
                        "ce projet -- %r" % (name, label, f[:90]))

        print("  ok : %-34s base=%s  sans conventions=%s  sans identifiants=%s (trace %s)"
              % (name[:34], base["score"], s1["score"], s2["score"],
                 "evaluee" if s2.get("traceabilityAssessed") else "non evaluee"))

    # I5 -- aucun chiffre du chemin par defaut ne doit valoir zero faute de convention.
    #
    # `negative_ratio_recomputed_pct` comptait les scenarios portant le tag `@negative` et
    # rendait le resultat sous un nom qui promet une mesure. Sur un cahier ecrit ailleurs il
    # annoncait « 0,0 % » -- pas une convention manquante, UN CHIFFRE FAUX. Mesure : sur
    # 1 564 scenarios etrangers, zero porte ce tag.
    #
    # I1-I3 ne pouvaient pas le voir : ils comparent des SCORES, et ce chiffre-la ne pese sur
    # aucun score. Il pese sur la confiance, ce qu'aucun invariant numerique n'attrape. Trouve
    # par une relectrice en contexte vierge, pas par un controle -- d'ou cet invariant.
    numeric_fields = ("negative_ratio_recomputed_pct", "negative_scenarios")
    for rel in BOOKS[:1]:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            continue
        stripped_neg = re.sub(r"@negative\b", "", open(path, encoding="utf-8").read(), flags=re.I)
        n = score(stripped_neg)
        for field in numeric_fields:
            if n["tag_audit"].get(field) is not None:
                failures.append(
                    "I5 %s : `%s` vaut %r sur un cahier sans convention `@negative`. Un chiffre "
                    "qu'on ne peut pas mesurer se dit null, jamais zero -- un zero se lit comme "
                    "une mesure et detruit la confiance dans les chiffres voisins."
                    % (os.path.basename(rel), field, n["tag_audit"][field]))
        if n["tag_audit"].get("negativeRatioAssessed") is not False:
            failures.append("I5 %s : l'absence de mesure du ratio negatif n'est pas declaree."
                            % os.path.basename(rel))
        if not any("negative ratio NOT ASSESSED" in x for x in n.get("notes", [])):
            failures.append("I5 %s : rien ne dit au lecteur POURQUOI le ratio est null."
                            % os.path.basename(rel))
        # Contre-epreuve : avec la convention presente, le chiffre doit revenir. Sans elle, la
        # correction aurait supprime la mesure au lieu de la conditionner.
        b = score(open(path, encoding="utf-8").read())
        if b["tag_audit"].get("negative_ratio_recomputed_pct") is None:
            failures.append("I5 %s : le ratio negatif reste null alors que le cahier PORTE des "
                            "tags @negative -- la mesure a ete supprimee, pas conditionnee."
                            % os.path.basename(rel))
        else:
            print("  ok : ratio negatif mesure=%s%% avec la convention, null sans elle"
                  % b["tag_audit"]["negative_ratio_recomputed_pct"])

    # I4 -- une convention de tracabilite ETRANGERE doit etre reconnue.
    #
    # Les invariants I1-I3 se mesurent tous sur des cahiers de CE depot. Ils prouvent donc
    # seulement que l'outil ne nous penalise pas -- pas qu'il crediterait quelqu'un d'autre.
    # La campagne de mutation l'a montre : ramener la detection a `@QAIA-` survivait a I1-I3,
    # parce qu'un cahier prive de ses tags QAIA n'est pas trace dans les deux cas.
    #
    # Il faut donc un cahier trace SANS aucune convention QAIA. Ecrit ici en toutes lettres :
    # c'est la seule fixture fabriquee du controle, et elle l'est parce que le corpus etranger
    # reel n'en contient aucune -- 0 reference d'exigence sur 410 occurrences de tags, mesure
    # du 2026-08-24. Ce que la fixture represente n'est pas une hypothese sur le Gherkin du
    # monde : c'est le cas, rare mais legitime, d'une equipe qui trace avec SA convention.
    foreign_traced = (
        "Feature: Panier\n"
        "\n"
        "  @JIRA-1234 @smoke\n"
        "  Scenario: Un panier vide affiche un total de 0\n"
        "    Given un panier vide\n"
        "    When l'utilisateur ouvre le panier\n"
        '    Then le total affiche est "0,00 EUR"\n'
        "\n"
        "  @REQ-77\n"
        "  Scenario: Ajouter un article met le total a jour\n"
        '    Given un panier vide\n'
        '    When l\'utilisateur ajoute l\'article "A-1" a 12,50 EUR\n'
        '    Then le total affiche est "12,50 EUR"\n'
    )
    f = score(foreign_traced)
    if not f.get("traceabilityAssessed"):
        failures.append(
            "I4 : un cahier trace par `@JIRA-1234` / `@REQ-77` est declare NON trace. La "
            "detection ne reconnait que la convention de ce projet -- c'est exactement le "
            "defaut qui rendait 0 PASS sur 244 cahiers etrangers.")
    elif f.get("traceability") in (None, 0.0):
        failures.append(
            "I4 : la tracabilite est declaree evaluee mais vaut %r sur un cahier trace par une "
            "convention etrangere." % (f.get("traceability"),))
    else:
        print("  ok : une tracabilite etrangere (@JIRA-1234, @REQ-77) est reconnue et notee %s"
              % f["traceability"])

    # Le profil `qaia`, lui, DOIT continuer a dire ces constats : sinon la surcouche opt-in ne
    # sert plus a rien et la correction aurait supprime la regle au lieu de la deplacer.
    if BOOKS:
        p = os.path.join(ROOT, BOOKS[0])
        if os.path.isfile(p):
            txt = CONVENTION_TAGS.sub("", open(p, encoding="utf-8").read())
            q = score(txt, profile="qaia")
            if not any(CONVENTION_WORDS.search(f) for f in q.get("findings", [])):
                failures.append(
                    "le profil `qaia` ne signale plus l'absence des conventions maison : la "
                    "surcouche opt-in a ete videe, pas deplacee.")
            else:
                print("  ok : le profil `qaia` signale toujours les conventions absentes")

    if not checked:
        failures.append("aucun cahier de reference n'a pu etre note -- controle sans objet")

    if failures:
        print("")
        for f in failures:
            print("::error::%s" % f)
        print("\n%d invariant(s) rompu(s)" % len(failures))
        return 1
    print("  -> le chemin par defaut ne penalise aucun cahier pour n'etre pas QAIA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
