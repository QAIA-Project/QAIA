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

DIX invariants, chacun tombant sur un defaut REELLEMENT SURVENU -- aucun n'est hypothetique, et
sept ont ete ajoutes le jour meme ou trois relecteurs en contexte vierge ont trouve ce que les
trois premiers laissaient passer.

  I1. Retirer les tags de priorite et de technique ne change PAS le score par defaut.
      (Ils produisaient 493 constats sur 666 sur un corpus etranger.)

  I2. Retirer les tags d'identifiant ne fait pas CHUTER le score : la tracabilite sort du
      denominateur au lieu d'etre notee zero.
      (Elle valait 25 points sur 100 perdus par construction -- 0 PASS sur 244 fichiers.)

  I3. Aucun CONSTAT du chemin par defaut ne nomme une convention de ce projet.

  I4. Une convention de tracabilite ETRANGERE est reconnue et notee.
      (I1-I3 se mesurent tous sur nos cahiers : ils prouvaient que l'outil ne nous penalise pas,
      jamais qu'il crediterait quelqu'un d'autre.)

  I5. Aucun chiffre ne vaut zero faute de convention ; l'absence de mesure est DECLAREE.
      (`negative_ratio` annoncait 0,0 % sur un cahier plein de tests negatifs. Il ne pese sur
      aucun score -- il pese sur la confiance dans tous les autres chiffres.)

  I6. Quatre conventions de tracabilite differentes donnent le meme score ET la meme dimension.
      (Reconnaitre n'est pas crediter : `@JIRA-1234` rendait 78/CONCERNS la ou `@QAIA-...`
      rendait 88/PASS, sur un cahier par ailleurs identique.)

  I7. DETECTER NE DOIT JAMAIS PUNIR : une tracabilite partielle ne coute aucun point.
      (Un seul `@HTML5` faisait perdre 21 points et une porte.)

  I8. Le profil `qaia` AJOUTE des exigences, il n'en retire pas.
      (Il avait cesse d'exiger la tracabilite : un cahier ayant perdu ses identifiants passait
      de 75/CONCERNS a 100/PASS -- la porte le PROMOUVAIT.)

  I9. Les deux outils du noyau s'accordent sur ce qu'est une reference d'exigence.
      (Table de 18 cas, testant le COMPORTEMENT et non le texte des motifs.)

  I10. Une paire de valeurs limites n'est pas un doublon, dans les DEUX sens : elle est
      signalee sans penalite, et un doublon strict reste penalise.
      (Le detecteur facturait jusqu'a 15 points ce que la profession enseigne d'ecrire.)

Exit 0 si les dix tiennent, 1 sinon.
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

    # I6 -- EGALITE des conventions, pas seulement reconnaissance.
    #
    # I4 n'exigeait qu'un credit NON NUL. Il passait au vert a 15/25, c'est-a-dire pendant que
    # `@JIRA-1234` rendait 78/CONCERNS la ou `@QAIA-US-004-009` rendait 88/PASS sur un cahier
    # PAR AILLEURS IDENTIQUE -- dix points et une porte, pour n'avoir pas adopte notre
    # convention. Le defaut que toute la refonte pretend supprimer, conserve a l'echelle 0,4
    # par le facteur `ac_linked`. Trouve par une passe de refutation, invisible pour I1-I5.
    #
    # Reconnaitre n'est pas crediter. L'invariant compare des SCORES, pas des booleens.
    def book(tag_template):
        out = ["Feature: panier", ""]
        for i in range(4):
            out += ["  " + tag_template.replace("#", str(i)),
                    "  Scenario: le montant %d est accepte" % i,
                    "    Given un panier de %d EUR" % i,
                    "    When l'utilisateur valide",
                    '    Then le total affiche est "%d,00 EUR"' % i, ""]
        return "\n".join(out)

    conventions = {"QAIA": "@QAIA-US-004-00#", "JIRA": "@JIRA-123#",
                   "REQ": "@REQ-#", "AC": "@AC#"}
    results = dict((k, score(book(v))) for k, v in conventions.items())
    scores = dict((k, r["score"]) for k, r in results.items())
    # La DIMENSION, pas seulement le score final. Comparer les scores seuls ne suffit pas : la
    # protection anti-falaise (I7) plafonne le resultat par le rebasement, si bien qu'un credit
    # de tracabilite reduit peut etre masque sur un cahier dont les autres dimensions sont
    # bonnes. Une mutation retablissant le facteur reserve a nos identifiants a survecu
    # exactement comme cela, le 2026-08-24 : elle ne se voyait pas sur ce cahier-la, et se
    # serait vue sur un cahier moins bien note ailleurs.
    dims = dict((k, r["traceability"]) for k, r in results.items())
    if len(set(dims.values())) != 1:
        failures.append(
            "I6 : la dimension `traceability` differe selon la convention -- %s. Le chemin par "
            "defaut credite notre convention plus que celle des autres, meme quand le score "
            "final n'en laisse rien paraitre."
            % ", ".join("%s=%s" % kv for kv in sorted(dims.items())))
    elif len(set(scores.values())) != 1:
        failures.append(
            "I6 : le meme cahier note differemment selon la convention de tracabilite -- %s."
            % ", ".join("%s=%s" % kv for kv in sorted(scores.items())))
    else:
        print("  ok : quatre conventions de tracabilite, un seul score (%s) et une seule "
              "dimension (%s)" % (list(scores.values())[0], list(dims.values())[0]))

    # I7 -- DETECTER NE DOIT JAMAIS PUNIR.
    #
    # `traceability_assessed = bool(traced)` etait un tout-ou-rien : un UNIQUE tag sur quatre
    # scenarios basculait la dimension en « evaluee » et faisait perdre 21 points et une porte.
    # L'adoption PARTIELLE etait punie plus durement que l'absence totale -- et un simple
    # `@HTML5`, tag de capacite navigateur, suffisait a la declencher.
    none_ref = book("@smoke")
    partial = none_ref.replace("  @smoke", "  @JIRA-1234", 1)
    s_none, s_part = score(none_ref), score(partial)
    if s_part["score"] < s_none["score"]:
        failures.append(
            "I7 : une reference d'exigence sur quatre scenarios FAIT BAISSER le score (%s -> "
            "%s). Detecter une convention ne doit jamais couter de points -- sanctionner une "
            "tracabilite incomplete est le travail du profil `qaia`, pas du chemin par defaut."
            % (s_none["score"], s_part["score"]))
    else:
        print("  ok : une tracabilite partielle ne coute aucun point (%s -> %s)"
              % (s_none["score"], s_part["score"]))

    # I8 -- le profil `qaia` AJOUTE des exigences, il n'en retire pas.
    #
    # `traceability_assessed` etait calcule hors de toute condition de profil : un cahier QAIA
    # ayant perdu ses identifiants passait de 75/CONCERNS a 100/PASS. La porte ecrite pour
    # attraper une perte de tracabilite dans notre propre production la PROMOUVAIT.
    q = score(none_ref, profile="qaia")
    if q["traceability"] is None or q["score"] >= s_none["score"]:
        failures.append(
            "I8 : sous le profil `qaia`, un cahier sans aucun identifiant note %s (universel : "
            "%s) avec traceability=%r. Le profil qui revendique la convention doit l'EXIGER."
            % (q["score"], s_none["score"], q["traceability"]))
    else:
        print("  ok : le profil `qaia` exige la tracabilite (%s contre %s en universel)"
              % (q["score"], s_none["score"]))

    # I10 -- une paire de valeurs limites n'est pas un doublon.
    #
    # Le detecteur de redondance penalisait tout groupe de meme forme Given/When, jusqu'a
    # -15 points, alors que l'en-tete du fichier promet « reported for human judgment, not
    # auto-failed ». Il facturait donc les paires nominal/refus et les paires de valeurs
    # limites -- ce que la profession enseigne d'ecrire. Mesure sur le corpus etranger :
    # 82 des 225 groupes (36 %) avaient des `Then` differents.
    #
    # Trouve par une relectrice en contexte vierge, sur son propre cahier : « il me facture
    # 6 points pour avoir ecrit une paire de valeurs limites ».
    def pair(then_a, then_b, given_a="499", given_b="501"):
        return "\n".join([
            "Feature: seuil", "",
            "  Scenario: juste en dessous du seuil",
            "    Given un panier de %s EUR" % given_a,
            "    When l'utilisateur valide",
            "    Then " + then_a, "",
            "  Scenario: juste au-dessus du seuil",
            "    Given un panier de %s EUR" % given_b,
            "    When l'utilisateur valide",
            "    Then " + then_b, "",
        ])

    boundary = score(pair('la commande est acceptee et le total affiche est "499,00 EUR"',
                          'la commande est refusee avec le message "plafond depasse"'))
    # La paire dont SEULS les litteraux different. C'est le cas le plus dur, et celui que la
    # regle du matin facturait encore : apres reduction des litteraux, elle est indiscernable
    # d'un copier-coller. 693 des 852 paires du corpus etranger sont de cette forme. Elle doit
    # etre signalee, pas facturee -- « 499 accepte / 501 refuse » et « model / controller » ont
    # exactement la meme signature textuelle, et seule la premiere est evidemment legitime.
    literals_only = score(pair('le total affiche est "499,00 EUR"',
                               'le total affiche est "501,00 EUR"'))
    # Octet pour octet : memes Given, memes When, memes Then. Ma premiere fixture faisait
    # varier le Given (499/501) et se croyait « vrai doublon » -- elle ne testait donc pas
    # le cas qu'elle nommait, et la contre-epreuve passait a cote de son objet.
    twin = score(pair('le total affiche est "499,00 EUR"',
                      'le total affiche est "499,00 EUR"',
                      given_a="499", given_b="499"))
    if boundary["penalties"]["redundancy"]:
        failures.append(
            "I10 : une paire de valeurs limites (meme forme, resultats attendus DIFFERENTS) est "
            "penalisee de %d point(s). C'est ce que la profession enseigne d'ecrire ; le "
            "detecteur doit la SIGNALER, pas la facturer."
            % boundary["penalties"]["redundancy"])
    elif not any("NOT penalised" in n for n in boundary.get("notes", [])):
        failures.append("I10 : la paire de valeurs limites n'est meme pas signalee -- la "
                        "correction a supprime la detection au lieu de la requalifier.")
    else:
        print("  ok : paire de valeurs limites signalee sans penalite (%d point(s))"
              % boundary["penalties"]["redundancy"])
    if literals_only["penalties"]["redundancy"]:
        failures.append(
            "I10 : une paire ne differant QUE par ses litteraux est penalisee de %d point(s). "
            "Apres reduction des litteraux elle est indiscernable d'un copier-colle : la "
            "facturer, c'est rendre un jugement de domaine qu'aucun outil de texte ne peut "
            "rendre." % literals_only["penalties"]["redundancy"])
    else:
        print("  ok : une paire ne differant que par ses litteraux n'est pas penalisee")

    # Contre-epreuve : un VRAI doublon -- des etapes STRICTEMENT identiques, octet pour octet --
    # doit rester penalise. Sans elle, la correction aurait pu simplement eteindre le detecteur,
    # ce qui est le risque de tout affinage successif : a force de retirer les cas douteux, il
    # ne reste rien. Trois affinages le meme jour rendent cette contre-epreuve indispensable.
    if not twin["penalties"]["redundancy"]:
        failures.append("I10 : un doublon strict (etapes identiques octet pour octet) n'est plus "
                        "penalise du tout -- le detecteur a ete eteint, pas affine.")
    else:
        print("  ok : un doublon strict reste penalise (%d point(s))"
              % twin["penalties"]["redundancy"])

    # I9 -- les deux outils du noyau s'accordent sur ce qu'est une reference d'exigence.
    #
    # Ils ne s'accordaient pas : `@AC1` et `@TC2` etaient reconnus par l'un, refuses par
    # l'autre, pour la meme notion. Deux definitions manuscrites de la meme regle dans deux
    # fichiers, sans rien pour les tenir d'accord -- la faute que ce depot ferme partout
    # ailleurs. La table ci-dessous est le contrat : elle teste le COMPORTEMENT, pas le texte
    # des motifs, donc les deux implementations restent libres et verifiables.
    TABLE = [("@QAIA-US-004-009", True), ("@JIRA-1234", True), ("@REQ-77", True),
             ("@US-4", True), ("@AC1", True), ("@TC2", True), ("@PROJ-12", True),
             ("@HTML5", False), ("@CSS3", False), ("@IE11", False), ("@WCAG21", False),
             ("@OAuth2", False), ("@P1", False), ("@wip", False), ("@smoke", False),
             ("@javascript", False), ("@seed_users", False), ("@tag1", False)]
    try:
        import automation_score as _A
        for tag, expected in TABLE:
            a = bool(structural_score.REQ_REF_RE.match(tag))
            b = bool(_A.REQ_REF.search(tag))
            if a != expected or b != expected:
                failures.append(
                    "I9 %s : attendu %s, structural_score=%s automation_score=%s"
                    % (tag, expected, a, b))
        if not any(f.startswith("I9 ") for f in failures):
            print("  ok : les deux outils s'accordent sur les %d cas de la table de reference"
                  % len(TABLE))
    except ImportError as exc:
        failures.append("I9 : automation_score introuvable, l'accord des deux motifs n'est pas "
                        "verifie -- %s" % exc)

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
