#!/usr/bin/env python3
"""Deterministic structural scorer for Gherkin test books (maintainer eval tooling).

Grounds issues #26 (deterministic score, not an LLM self-note), #27 (anti-fabrication
sniffer) and #28 (a case with no verifiable expected result is a question, not a test),
themselves derived from the founding project's documented failure modes (case US 676266:
100/100 machine vs 58/100 human — an AC "covered" by an unreadable image, a case with no
expected result, idempotence gaps).

Also reports the "pesticide paradox" (#24 gap harness, mode 3b): the same test repeated under a
new name catches nothing new.

**It penalises only byte-for-byte identical steps, and reports everything else.** Measured on
257 foreign books on 2026-08-24: of the 852 pairs the previous rule charged as duplicates,
**693 (81 %) differed only by literals** — and once literals are collapsed, a boundary pair and a
copy-paste are the same text. `Opening new model` / `Opening new controller` / `Opening a new
job` is an equivalence partition, not a repetition. No text tool can separate "same test, new
value, no new behaviour" from "distinct values, deliberate coverage": that is a judgement about
the domain. A detector that charges points for a judgement it cannot make is worse than a silent
one — it carries the authority of a number.

Redundancy never forces a STOP (unlike C1/C2/sniffer).

NO LLM, NO network — reproducible and auditable, by design.

This file is the SOURCE. Since the 2026-08-09 decision (ADR 0002) it is also SHIPPED, byte for
byte, to `plugins/qaia-score/scripts/structural_score.py`, and `check_repo_structure.py` keeps
the two identical. The docstring said the opposite -- "NOT in plugins/ (it is not shipped to
installers)" -- for fifteen days after the decision that made it false, and so did
`docs/OUTPUT-CONTRACT.md`. Found on 2026-08-24 by a first-time reader who followed the prose,
looked for the file where it said the file was not, and found it there. A comment that contradicts
the repository is worse than no comment: it is trusted.

Usage: python3 structural_score.py <file.feature> [--acs AC1,AC2,...] [--source src.md]
                                                  [--profile universal|qaia]
       python3 structural_score.py --batch <dir> [--profile universal|qaia] [--format json|md]

  --format md          rapport lisible par un humain, trie par gravite (mode --batch). Sans lui,
                       la sortie est du JSON, une ligne par fichier -- utilisable pour trois
                       fichiers, illisible pour trois cents.

  --profile universal  (defaut) ne juge que ce qui est vrai de tout cahier, quel qu'en soit
                       l'auteur. La tracabilite et le ratio negatif y sont DETECTES : mesures
                       quand le cahier montre la convention, declares non evalues sinon.
  --profile qaia       ajoute par-dessus les conventions de ce projet (tag de priorite, tag de
                       technique). Elles n'existent pas en Gherkin : ne le demandez que pour un
                       cahier qui les a adoptees.
"""
import re
import sys, sys, os, json, glob

# Kept in sync with istqb-design/SKILL.md's technique palette (D109 reorganization) -- stale
# vs. that palette caused false "wrong tag count" findings on legitimate @crud/@metamorphic/
# @domain-analysis/@ai-feature scenarios, independently caught by two pilot runs (2026-07-29).
# @use-case is D109's pre-rename name for "Scenario-Based Testing", kept for older generated
# content that predates the rename.
TECHNIQUE_TAGS = {"@ep", "@boundary", "@decision-table", "@state-transition", "@use-case",
                   "@pairwise", "@error-guessing", "@crud", "@metamorphic", "@domain-analysis",
                   "@ai-feature"}
PRIORITY_TAGS = {"@p1", "@p2", "@p3"}

# --- traçabilité : une propriété DETECTEE, jamais exigée -------------------------------------
# `traced` valait « le scenario porte un tag @QAIA-<ID> », ce qui faisait perdre 25 points sur
# 100 par construction a tout cahier ecrit ailleurs -- 0 PASS sur 244 fichiers etrangers, et un
# barème incapable de distinguer « ce test est mauvais » de « ce test n'est pas de moi ».
#
# Le remede evident (« accepter toute reference d'exigence, pas seulement la notre ») a ete
# ESSAYE SUR LE CORPUS AVANT D'ETRE ECRIT, et il ne marche pas : sur 410 occurrences de tags
# dans 257 fichiers etrangers, il n'y a **aucune** reference d'exigence. Les tags du monde reel
# sont des directives de lanceur -- @javascript (47), @wip, @fixture, @seed_*. La tracabilite
# par tag n'est pas une propriete universelle du Gherkin : c'est une convention de projet.
#
# Donc elle n'est plus une dimension qu'on exige, mais une dimension qu'on DETECTE : notee si
# le cahier montre une convention de reference, declaree NON EVALUEE sinon -- et le barème se
# remet a l'echelle sur les trois dimensions qui transferent, au lieu de noter zero la
# quatrieme. Aucun drapeau a passer : l'outil s'adapte au materiau, ce n'est plus au materiau
# de s'adapter a l'outil.
#
# DEUX FORMES, et le separateur n'est facultatif que pour une liste FERMEE de prefixes.
#
# La premiere version demandait « deux majuscules puis un chiffre quelque part », et se
# justifiait ainsi : « calibre contre les 126 tags distincts du corpus etranger pour ne
# declencher sur aucun ». C'etait vrai de CE corpus et faux en general -- elle prenait `@HTML5`,
# `@CSS3`, `@IE11`, `@WCAG21`, `@OAuth2`, des tags de capacite qu'aucun cahier reel n'entend
# comme des references. **Un echantillon ou une regle ne se declenche jamais ne prouve rien de
# sa precision** ; il prouve seulement qu'on a regarde du cote ou elle ne risquait rien.
#
# Le cout etait mesurable : combine au tout-ou-rien de `traceability_assessed`, un unique
# `@HTML5` faisait perdre 21 points et une porte a un cahier. Trouve par une passe de
# refutation le 2026-08-24, pas par le calibrage.
#
# `check_universal_default.py` (I9) fait passer a ce motif et a son jumeau d'`automation_score`
# la MEME table de 18 cas, et echoue s'ils divergent : ils divergeaient, sur `@AC1` et `@TC2`.
REQ_REF_PREFIXES = "AC|US|REQ|TC|FR|NFR|PBI|STORY|EPIC|BUG|ISSUE"
REQ_REF_RE = re.compile(
    r"@(?:[A-Z]{2,}(?:[-_][A-Za-z0-9]+)*[-_]\d+"       # JIRA-1234, QAIA-US-004-009, US-4
    r"|(?:" + REQ_REF_PREFIXES + r")\d+)")             # @AC1, @REQ5 -- liste FERMEE
# Sensible a la casse, volontairement : `@html5` n'est pas une convention d'exigence, et une
# regle insensible a la casse reprendrait tout ce que la liste fermee vient d'ecarter.

MARKER_RE = re.compile(r"\[\s*(?:À|A)\s*D[EÉ]FINIR[^\]]*\]|\bTODO\b|\bFIXME\b|<\s*placeholder\s*>|\bXXX\b|\bTBD\b", re.I)
# XXX/TBD are also legitimate literal test data (e.g. ISO 4217's reserved "no currency" code is
# literally "XXX") -- found by running the scorer on a real generated .feature (2026-07-29 pilot
# campaign), not a hand-built fixture. A quoted occurrence is business data, not an unresolved
# placeholder, so it's stripped before marker detection; TODO/FIXME/placeholder/DEFINIR have no
# such legitimate quoted use and are always flagged.
QUOTED_XXX_TBD_RE = re.compile(r'"\s*(?:XXX|TBD)\s*"', re.I)
# a Then that defers to an external artifact as its sole evidence is hollow (C1 of case 676266).
# Requires a referential/deference cue immediately before the artifact noun (#24 gap-harness
# fix: the naive "contains the word image/table" version false-positived on legitimate business
# assertions that merely mention a picture/image field, e.g. "the picture should be the default
# image" — found by running the scorer on a real generated .feature, not a hand-built fixture).
HOLLOW_RE = re.compile(
    r"\b(voir|see|cf\.?|selon|according to|refers? to|referred to|se r[ée]f[ée]rer (à|au)|consulter|"
    r"conforme (au|à l['’]|aux)|correspond(ent|s)? (au|à|aux)|as (shown|depicted) (in|on))\s+"
    r"(le\s+|la\s+|les\s+|the\s+|l['’])?(tableau|table|image|screenshot|capture d.?[ée]cran|copie d.?[ée]cran|annexe|maquette)\b"
    r"|\b(exactement\s+)?(exactly\s+)?(tel(le)?\s+que|as)\s+(dessin[ée]|dessin[ée]e|drawn|configur[ée]|configured|"
    r"sp[ée]cifi[ée]|specified|document[ée]|documented|d[ée]crit(e)?|described|illustr[ée]|illustrated|"
    r"[ée]crit(e)?|written)\b",
    re.I,
)
# vague, non-verifiable outcomes (C2): restates success without an asserted value/state/status.
# Also catches non-committal deferrals to "a rule/mechanism" and circular restatements of a
# formula ("is the sum of...") that name no concrete resulting number/state — found via the
# corpus-24-depth C5/C10/C18 gap: these evade the original narrow success-word list entirely,
# scoring completeness down but never surfacing as a named C2 finding (eval/baselines/corpus-24-depth.md).
VAGUE_RE = re.compile(
    r"\b(correct(e|ement|ly)?|comme attendu|as expected|works?|fonctionne|"
    r"r[ée]pond correctement|responds? correctly|behaves? correctly|works? correctly|"
    r"le syst[eè]me r[ée]pond|properly|ok|sans erreur|no error|success(fully)?|"
    r"appropri[ée]e?(ment)?|appropriately|as appropriate|"
    r"(une\s+)?r[èe]gle\s+d[ée]terministe|deterministic rule|"
    r"\bconsistent(e|ly)?\b|\bcoh[ée]rent(e|s)?\b|"
    r"(is|est|sont|are)\s+(the\s+|le\s+|la\s+|les\s+)?(sum|somme|total|full amount|montant (complet|int[ée]gral)|correct amount|montant correct))\b",
    re.I,
)
# a real assertion carries a concrete token: number, quoted value, status code, comparator, state verb
# Noyau commun aux deux expressions ci-dessous : un jeton concret (chiffre, code, statut,
# comparateur, verbe d'etat). Ecrit UNE fois -- il l'etait deux, a la main, et vingt lignes
# de commentaire expliquaient pourquoi les deux copies doivent differer sans que rien ne
# garantisse qu'elles ne different QUE la-dessus (B27, revue « developpeur » 2026-08-09).
_ASSERT_CORE = (r"\d|\b(status|code|HTTP|=|==|>=|<=|>|<|equals?|[ée]gal|contains?|contient|"
                r"affiche|displays?|redirect|returns?|retourne|is (not )?(visible|present|"
                r"enabled|disabled)|est (visible|pr[ée]sent|absent))\b")
# La seule difference voulue entre les deux : accepter n'importe quel litteral entre
# guillemets comme preuve d'assertion concrete.
_QUOTED_LITERAL = r"\"[^\"]+\"|'[^']+'"

# a real assertion carries a concrete token: number, quoted value, status code, comparator,
# state verb
ASSERT_RE = re.compile(r"\d|" + _QUOTED_LITERAL + r"|" + _ASSERT_CORE.lstrip(r"\d|"), re.I)
# #31 (P3, follow-up to D65/D71's documented residual limit): ASSERT_RE's bare quote clause
# above treats ANY quoted literal as proof of a concrete assertion, but a Then can cite an
# already-known entity identifier (e.g. `the order between "P1" and "P2" is consistent`) without
# ever asserting a real result value - the quotes then mask an otherwise-correct VAGUE_RE hit on
# "consistent" (real case: eval/baselines/corpus-24-depth.md, lot 3, C5/Mistral). has_strict_assertion()
# below requires a quoted literal to sit immediately next to a state/assertion verb (is/are/shows/
# displays/equals/contains/returns/redirects...) to count - a citation embedded in an unrelated
# phrase ("between X and Y") no longer does, and a bare digit embedded INSIDE a quoted literal
# (e.g. the "1" in "P1") is blanked out first so it can't satisfy the plain `\d` alternative on
# its own either - same false-positive, different route. Used ONLY to gate `vague` below,
# deliberately NOT swapped into ASSERT_RE itself/`covers()`: real fixtures legitimately phrase
# assertions with the verb *not* immediately adjacent to the quote (`the slot with "Dr. Ben Osei"
# is not listed`, `an audit entry is recorded with ... the action "book"`, `only slots ...
# "Dermatology" ... are shown`) - tightening the general-purpose ASSERT_RE the same way flips ~15
# legitimate assertions across eval/concerns-zone-fixtures/, eval/baselines/
# multi-judge-median-testbook/ and eval/baselines/rag-recall-gain/ to "no concrete signal", a real
# regression for no gain, since none of them also trip VAGUE_RE (the only place a bare quote's
# leniency is actually a problem). Honest partial fix: it closes the documented C5 gap without
# touching completeness scoring elsewhere; a quoted entity ID sitting next to VAGUE_RE wording in
# some other phrasing this regex doesn't anticipate could still slip through - not exhaustive.
_ASSERT_OUTSIDE_QUOTES_RE = re.compile(_ASSERT_CORE, re.I)

_ASSERT_VALUE_NEAR_QUOTE_RE = re.compile(
    r"\b(?:is|are|est|sont|shows?|displays?|affiche(?:nt)?|equals?|[ée]gal(?:e|es)?|contains?|contient|returns?|retourne(?:nt)?|redirects?)\s+(?:not\s+)?(?:to\s+)?[\"'][^\"']+[\"']",
    re.I,
)

def has_strict_assertion(t):
    outside_quotes = re.sub(r'"[^"]*"|\'[^\']*\'', " ", t)
    return bool(_ASSERT_OUTSIDE_QUOTES_RE.search(outside_quotes) or _ASSERT_VALUE_NEAR_QUOTE_RE.search(t))

# fabrication sniffer: technical literals that should trace to a source/oracle
TECH_LITERAL_RE = re.compile(r"https?://\S+|\b\d{1,3}(?:\.\d{1,3}){3}\b|\b[a-z0-9.-]+\.(?:com|net|org|io|local|internal)\b|:\d{2,5}\b|\b[A-Z]{2,}-\d+\b|\b\d+[.,]\d{2}\s?(?:€|EUR|\$|USD)\b", re.I)

def parse_scenarios(text):
    scen, cur = [], None
    tags_pending = []
    in_examples = False
    background = []      # les pas d'un `Background:` valent pour chaque scenario du fichier
    in_background = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("@"):
            tags_pending += line.split()
            continue
        # `Background:` et `Rule:` etaient ignores : les pas communs disparaissaient, et un
        # scenario qui s'appuyait dessus se lisait comme incomplet (B24).
        if re.match(r"(Background|Contexte)\s*:", line, re.I):
            in_background = True
            if cur:
                scen.append(cur)
                cur = None
            continue
        if re.match(r"(Rule|R[ée]gle)\s*:", line, re.I):
            in_background = False
            continue
        # Une table de donnees sous un `Then` PORTE les valeurs attendues. Les ignorer faisait
        # noter « aucune assertion concrete » des cahiers dont c'est justement la forme (B24).
        # Un bloc `Examples:` n'est PAS une table de donnees attachee a un pas : ses lignes sont
        # des cas de test. Les absorber dans le dernier pas faisait qu'un Outline a 6 exemples
        # comptait pour 1, quand `testbook-export` en fait 6 lignes -- deux tailles pour le meme
        # cahier, et des ratios calcules sur le mauvais denominateur (2026-08-10).
        # `Scenarios:` est l'alias officiel d'`Examples:`. Verifie AVANT le motif de scenario :
        # sinon `Scenarios:` serait lu comme un `Scenario` sans titre (#105).
        if re.match(r"(Examples|Exemples|Scenarios)\s*:", line, re.I):
            in_examples = True
            # -1 : la premiere ligne de pipes qui suit est l'EN-TETE de la table, pas un cas.
            # Le defaut a -1 dans le compteur ne servait a rien puisque la cle est initialisee a
            # 0 a la creation du scenario -- l'Outline a 6 exemples rendait 7 (2026-08-10).
            if cur is not None: cur["examples"] = -1
            continue
        if line.startswith("|") and in_examples and cur is not None:
            cur["examples"] = cur.get("examples", 0) + 1
            continue
        if line.startswith("|") and cur is not None and cur["steps"]:
            kw, txt = cur["steps"][-1]
            cur["steps"][-1] = (kw, (txt + " " + line.strip("| ").replace("|", " ")).strip())
            continue
        # Alias officiels de Gherkin 6, absents jusqu'au 2026-08-10 : `Example:` pour
        # `Scenario:`, `Scenario Template:` pour `Scenario Outline:`. Un cahier ecrit avec
        # eux -- la documentation Cucumber s'en sert dans ses propres exemples de `Rule:` --
        # rendait ZERO scenario, aucun constat, et un 20/100 FAIL muet (#105).
        # Les formes longues passent avant les courtes : `Scenario Outline` avant `Scenario`.
        m = re.match(r"(Scenario Outline|Scenario Template|Scenario|Sc[ée]nario|Plan du sc[ée]nario|Example|Exemple)\s*:\s*(.*)", line, re.I)
        if m:
            in_background = False
            if cur: scen.append(cur)
            in_examples = False
            cur = {"name": m.group(2).strip(), "tags": tags_pending, "steps": [], "then": [],
                   "examples": 0}
            tags_pending = []
            continue
        # tags only bind to the next scenario, but a comment line between the tags and the
        # `Scenario:` line (e.g. "# Condition: ...", common when a scenario cites its source
        # condition) must not wipe them — found via cross-model comparison (#25bis-multimodel):
        # this exact pattern silently dropped every tag past the first scenario in a real
        # generated .feature, tanking traceability to ~0 for a file that was actually tagged.
        if not line.startswith("#"):
            tags_pending = tags_pending if not cur else []
        # `*` remplace n'importe quel mot-cle de pas -- Gherkin standard, documente par
        # Cucumber. Absent de ce motif, les pas de Karate (qui n'utilise que `*`) n'etaient
        # jamais captures : `then` restait vide et C2 prononcait un FAIL force sur des suites
        # correctes qui tournent en production (#103, 2026-08-10).
        sm = re.match(r"(Given|When|Then|And|But|Soit|Quand|Alors|Etant donn[ée]e?s?|Et|Mais|\*)(?:\b|\s)(.*)", line, re.I)
        if sm and (cur is not None or in_background):
            kw, txt = sm.group(1), sm.group(2).strip()
            (background if in_background else cur["steps"]).append((kw, txt))
    if cur: scen.append(cur)
    # Les pas du `Background:` prefixent chaque scenario : c'est ce qu'ils sont.
    if background:
        for sc in scen:
            sc["steps"] = list(background) + sc["steps"]
    # attach 'then' steps: a Then and the And/But that follow it
    for s in scen:
        in_then = False
        for kw, txt in s["steps"]:
            k = kw.lower()
            if k in ("then", "alors"): in_then = True; s["then"].append(txt)
            elif k in ("and", "but", "et", "mais") and in_then: s["then"].append(txt)
            elif k in ("given", "when", "soit", "quand", "etant donné", "etant donnée"): in_then = False
    return scen

def score_feature(path, declared_acs=None, source_text=None, profile="universal",
                  third_party=None):
    """Note un cahier Gherkin. Le barème UNIVERSEL est le chemin par defaut.

    `profile="universal"` (defaut) ne juge que ce qui est vrai de tout test, quel qu'en soit
    l'auteur : le scenario a-t-il un resultat attendu, ce resultat est-il verifiable, les
    etapes sont-elles completes, le cahier repete-t-il la meme forme sans rien tester de neuf.
    La tracabilite y est DETECTEE, jamais exigee (cf. REQ_REF_RE).

    `profile="qaia"` ajoute par-dessus les conventions de ce projet -- tag de priorite
    `@P1/@P2/@P3`, tag de technique issu d'une liste fermee. Elles n'existent pas en Gherkin :
    appliquees a un cahier ecrit ailleurs elles produisent un constat par scenario et noient
    tout le reste (493 constats sur 666 mesures sur le corpus etranger).

    L'inversion est le coeur de la refonte du 2026-08-24. L'ancien defaut appliquait nos
    conventions a tout le monde et l'exception `--third-party` etait a demander : un outil qui
    juge ne peut pas avoir « ce test n'est pas de moi » cable dans son chemin par defaut.

    `third_party` est conserve comme ALIAS DEPRECIE pour les appelants existants : `True` ->
    profil universel (desormais le defaut), `False` -> profil `qaia` (l'ancien defaut).
    """
    if third_party is not None:
        profile = "universal" if third_party else "qaia"
    try:
        text = open(path, encoding="utf-8").read()
    except (IOError, OSError) as exc:
        # Convention du depot : « BROKEN », pas une trace Python. Une trace, dans une CI, se lit
        # comme un plantage de l'outil et non comme un chemin mal ecrit (B26).
        print("BROKEN: %s illisible -- %s" % (path, exc), file=sys.stderr)
        raise SystemExit(2)
    scen = parse_scenarios(text)
    findings = []
    notes = []   # etats et non-defauts : jamais melanges aux constats
    # ZERO scenario extrait : on ne note pas. Le `or 1` ci-dessous rendait une note sur un
    # denominateur invente, donc un 20/100 FAIL muet sur un cahier parfaitement valide dont on
    # n'avait simplement pas su lire les mots-cles -- `Example:` et `Scenario Template:` l'ont
    # produit jusqu'au 2026-08-10 (#105). Un verdict fabrique sur un parse vide est exactement
    # la faute que ce projet reproche aux modeles : une reponse assuree a la place d'un « je ne
    # sais pas ». On le DIT, et on ne met aucun chiffre.
    if not scen:
        return {"file": os.path.basename(path), "scenarios": 0, "executableCases": 0,
                "outlines": 0, "unmappableDialect": 0,
                "scoreable": False, "score": None, "gate": "UNSCORED", "forced_stop": False,
                "readability": None, "completeness": None, "coherence": None,
                "traceability": None, "traceabilityAssessed": False, "profile": profile,
                "gateReason": "not scoreable: no scenario could be extracted",
                "notes": [], "penalties": {}, "tag_audit": {},
                "findings": ["not scoreable: no scenario could be extracted from this file. "
                             "It may use Gherkin keywords this scorer does not know, a "
                             "localisation it does not carry, or contain no scenario at all. "
                             "No score is emitted -- a number here would be fabricated."]}
    n = len(scen)

    # --- detectors ---
    markers = MARKER_RE.findall(QUOTED_XXX_TBD_RE.sub('""', text))
    # Indexes par POSITION, pas par nom : un Scenario Outline donne le meme nom a tous ses
    # exemples, et un copier-coller aussi. Indexer par nom faisait qu'un scenario vague
    # excluait son homonyme parfaitement assertif de la completude (revue dev, 2026-08-09).
    # Un pas d'UN SEUL MOT est suspect, pas fautif : `When submit` est laconique mais complet.
    # Ne restent tronques que les pas qui s'interrompent visiblement (ponctuation suspendue) --
    # les monosyllabes deviennent un constat non penalisant. L'heuristique plafonnait un PASS a
    # CONCERNS sans aucune echappatoire (B25).
    truncated_i = set(i for i, s in enumerate(scen)
                      if any(t.endswith(("…", "...", ",", "-")) for _, t in s["steps"] if t))
    terse_i = set(i for i, s in enumerate(scen)
                  if i not in truncated_i and any(len(t.split()) < 2 for _, t in s["steps"] if t))
    # Un scenario dont TOUS les pas sont `*` n'est pas depourvu de resultat attendu : c'est un
    # dialecte que ce scoreur ne sait pas mapper vers Given/When/Then. Karate assertait
    # `status 200` et `match response == first` et recevait « no expected result » -- un verdict
    # faux rendu avec l'autorite d'un programme. Rendre 0 quand on ne sait pas lire, c'est la
    # faute meme qu'on reproche aux modeles : une reponse assuree a la place d'un « je ne sais
    # pas ». On l'exclut des detecteurs de resultat attendu et on le DIT (#103, 2026-08-10).
    unmappable_i = set(i for i, s in enumerate(scen)
                       if s["steps"] and all(kw == "*" for kw, _ in s["steps"]))
    empty_then_i = set(i for i, s in enumerate(scen) if not s["then"]) - unmappable_i
    hollow_i = set(i for i, s in enumerate(scen) if s["then"] and all(HOLLOW_RE.search(t) for t in s["then"]))
    vague_i = set(i for i, s in enumerate(scen) if s["then"] and not any(has_strict_assertion(t) for t in s["then"]) and any(VAGUE_RE.search(t) for t in s["then"]))
    # les noms restent pour les constats lisibles, mais ne servent plus a decider
    truncated = [scen[i]["name"] for i in sorted(truncated_i)]
    empty_then = [scen[i]["name"] for i in sorted(empty_then_i)]
    hollow = [scen[i]["name"] for i in sorted(hollow_i)]
    vague = [scen[i]["name"] for i in sorted(vague_i)]
    # a scenario "really covers" only if it has a Then with a concrete assertion, not hollow/empty
    def covers_i(i):
        s = scen[i]
        return bool(s["then"]) and i not in empty_then_i and i not in hollow_i and i not in vague_i and any(ASSERT_RE.search(t) for t in s["then"])
    def covers(s): return covers_i(scen.index(s))
    traced = [s for s in scen if any(REQ_REF_RE.match(t) for t in s["tags"])]
    # `ac_linked` ne reconnaissait QUE `@AC...` et `@QAIA-...`. Comme il porte le facteur 0,4 de
    # la formule de tracabilite, un cahier etranger PARFAITEMENT trace plafonnait a 60 % de la
    # dimension : 78/CONCERNS pour `@JIRA-1234` la ou `@QAIA-US-004-009` rendait 88/PASS, sur un
    # cahier par ailleurs identique. Le defaut que la refonte pretend supprimer, conserve a
    # l'echelle 0,4 -- et la garde ne pouvait pas le voir, elle n'exigeait qu'un credit NON NUL,
    # jamais un credit EGAL. Trouve par une passe de refutation, pas par un controle.
    #
    # Le raffinement « la reference pointe un critere d'acceptation » est une convention de ce
    # projet : il reste, mais sous le profil qui le revendique.
    ac_linked = [s for s in scen if any(re.search(r"@AC[:_-]?\w+|@QAIA-\w+-\d+", t) for t in s["tags"])]

    # fabrication sniffer: technical literals present in a step but not in the source (if given)
    sniffer_hits = []
    if source_text is not None:
        for s in scen:
            for _, t in s["steps"]:
                for lit in TECH_LITERAL_RE.findall(t):
                    if lit and lit not in source_text:
                        sniffer_hits.append((s["name"], lit))

    # pesticide-paradox / redundancy detector (#24 mode 3b): group scenarios by the
    # normalized shape of their Given/When steps only (literals collapsed) — same shape,
    # different literal, no new behavior. Then is deliberately excluded from the shape key:
    # a distinct assertion on an identical Given/When is still flagged (reported, not failed)
    # so a human decides whether it is a real per-value rule or a copy-paste scenario.
    def normalize_step(t):
        t = re.sub(r'"[^"]*"|\'[^\']*\'', "<val>", t)
        t = re.sub(r"\d+", "<num>", t)
        return re.sub(r"\s+", " ", t).strip().lower()
    def shape_key(s):
        gw, in_then = [], False
        for kw, t in s["steps"]:
            k = kw.lower()
            if k in ("then", "alors"): in_then = True; continue
            if k in ("given", "when", "soit", "quand", "etant donné", "etant donnée"): in_then = False
            if in_then: continue
            gw.append(("and" if k in ("and", "but", "et", "mais") else k, normalize_step(t)))
        return tuple(gw)
    # Un groupe de forme Given/When identique n'est un DOUBLON que si son `Then` l'est aussi.
    #
    # Le detecteur penalisait tout groupe de forme identique, jusqu'a -15 points, alors que le
    # commentaire d'en-tete de ce fichier promet l'inverse : « reported for human judgment, not
    # auto-failed ». Il facturait donc les paires de valeurs limites et les paires
    # nominal/refus -- ce que la profession enseigne d'ecrire.
    #
    # Mesure avant correction, sur les 257 cahiers etrangers : **225 groupes, dont 82 (36 %) a
    # `Then` differents**. « Creating a new draft consultation » groupe avec « ... in another
    # language », « Going from: format.html » avec « render :new, formats: [:js] ». Un tiers des
    # constats de redondance nommait des comportements distincts.
    #
    # Desormais : penalite sur les groupes dont le `Then` est lui aussi equivalent, et simple
    # SIGNALEMENT pour les autres -- ce que le detecteur disait deja faire.
    # Troisieme affinage du meme detecteur dans la journee, et le seul qui aille jusqu'au bout.
    #
    # La regle du matin -- « meme forme ET meme `Then` collapse » -- ratait un fait mesurable :
    # sur les 852 paires qu'elle comptait comme doublons dans le corpus etranger, **693 (81 %)
    # ne different QUE par des litteraux**. Or apres reduction des litteraux, une paire de
    # valeurs limites et un copier-coller sont LE MEME TEXTE. Le detecteur ne les distinguait
    # donc pas -- il avait seulement l'air de le faire.
    #
    # Les exemples reels tranchent la question : « Opening new model » / « Opening new
    # controller » / « Opening a new job » dans `expanding-snippets`. C'est une partition
    # d'equivalence, pas une repetition. Aucun outil de texte ne peut trancher entre « meme test,
    # nouvelle valeur, aucun comportement neuf » et « valeurs distinctes, couverture
    # deliberee » : c'est un jugement sur le DOMAINE, pas sur le texte.
    #
    # Donc il ne penalise plus que l'inambigu -- le texte STRICTEMENT identique, 159 paires sur
    # 852 -- et signale tout le reste. Un detecteur qui facture un jugement qu'il ne peut pas
    # rendre est pire que muet : il a l'autorite d'un chiffre.
    #
    # LE FAUX NEGATIF (#113) EST UNE LIMITE MESUREE, PAS UN OUBLI. Deux scenarios copies-colles
    # dont le `When` derive d'un mot (`ajoute <val>` / `ajoute l'article <val>`) ont un shape_key
    # different et ne sont donc jamais compares. La piste « similarite Jaccard » a ete MESUREE sur
    # 224 cahiers reels avant d'etre ecrite (eval/universal-default-2026-08-24/REDUNDANCY-FALSENEG.md) :
    # a tout seuil, les faux positifs (paires metamorphiques a litteraux differents) depassent les
    # vrais copies-colles ; et meme filtre par litteraux identiques + `Then` identique + inclusion
    # de jetons, le split reste ~50/50 -- `cucumber -q` vs `cucumber -x -q` (l'option testee) et
    # `reference` vs `comparison screenshot directory` passent tous les filtres. Le signal qui
    # separe copie-colle et couverture deliberee est SEMANTIQUE, pas textuel. Un signalement a
    # ~50 % de precision porterait « l'autorite d'un chiffre » sur un jugement qu'il ne peut pas
    # rendre : on nomme la limite ici plutot que d'ajouter un detecteur bruite.
    def raw_key(s):
        return "\n".join(re.sub(r"\s+", " ", t).strip().lower() for _kw, t in s["steps"])

    shape_groups, then_of, raw_of = {}, {}, {}
    for s in scen:
        shape_groups.setdefault(shape_key(s), []).append(s["name"])
        then_of[s["name"]] = "\n".join(normalize_step(t) for t in s["then"])
        raw_of[s["name"]] = raw_key(s)
    duplicate_groups, variant_groups = [], []
    for names in shape_groups.values():
        if len(names) < 2:
            continue
        if len({raw_of[n] for n in names}) == 1:
            duplicate_groups.append(names)     # texte identique : aucune lecture n'en fait deux tests
        else:
            variant_groups.append(names)       # litteraux ou `Then` differents : un humain tranche
    # Pas d'alias : `redundant_groups = duplicate_groups` en etait un, et il ne pilotait que le
    # TEXTE du constat -- la penalite, elle, se calculait a partir de `duplicate_groups`. Une
    # mutation vidant l'alias survivait donc a la campagne : elle changeait ce que le rapport
    # DIT sans changer ce que le score FAIT. Deux noms pour une chose, c'est deja un endroit ou
    # les deux peuvent diverger.
    redundant_scenarios = [name for group in duplicate_groups for name in group]

    # --- independent tag/ratio audit (reported facts, NOT folded into the /100 score) ---
    # This is the mechanical bookkeeping half of the gate (tag presence, ratio) — deliberately
    # kept separate from the 0-100 budget above so it never silently shifts scores for fixtures
    # that predate this check, and separate from the generator's OWN self-reported ratio (rule 3:
    # no producer scores/validates itself — the ratio a user sees must be independently
    # recomputed from the .feature file, not trusted from synthesis.md).
    def tags_lower(s): return {t.lower() for t in s["tags"]}
    no_priority = [s["name"] for s in scen if not (tags_lower(s) & PRIORITY_TAGS)]
    technique_hits = [s["name"] for s in scen for t in [tags_lower(s) & TECHNIQUE_TAGS]
                       if len(t) != 1 and "@smoke" not in tags_lower(s)]
    smoke = [s for s in scen if "@smoke" in tags_lower(s)]
    negative = [s for s in scen if "@negative" in tags_lower(s)]
    non_smoke_n = len(scen) - len(smoke) or 1

    # `negative_scenarios` comptait les scenarios PORTANT LE TAG `@negative`, et le rendait sous
    # un nom qui promet une mesure. Sur un cahier ecrit ailleurs il annonce donc « ratio negatif
    # 0,0 % » pour un cahier qui teste les refus a moitie : ce n'est pas une convention
    # manquante, c'est UN CHIFFRE FAUX presente comme mesure. Mesure du 2026-08-24 : sur
    # 1 564 scenarios etrangers, **zero** porte ce tag.
    #
    # Trouve par une relectrice en contexte vierge jouant une QA lead, pas par un controle.
    # Elle l'a dit mieux que ce commentaire : « le jour ou je decouvre qu'un des chiffres compte
    # en realite une convention de tags, je cesse de croire les autres. »
    #
    # Meme traitement que la tracabilite : mesure quand la convention est presente, DECLARE NON
    # EVALUE sinon. Et surtout PAS remplace par une detection semantique du refus -- essayee sur
    # le corpus, elle rend 13,6 %, un chiffre plus plausible et tout aussi peu verifiable.
    # Remplacer un chiffre faux par un chiffre fragile n'est pas une correction.
    negative_convention_present = bool(negative)
    negative_ratio_recomputed = (round(100 * len(negative) / non_smoke_n, 1)
                                 if negative_convention_present else None)
    tag_audit = {
        "negative_scenarios": len(negative) if negative_convention_present else None,
        "non_smoke_scenarios": non_smoke_n,
        "negative_ratio_recomputed_pct": negative_ratio_recomputed,
        "negativeRatioAssessed": negative_convention_present,
    }
    # Les deux lignes de convention pure ne sortent que sous le profil qui les demande. Rendues
    # systematiquement, elles se lisent comme des reproches -- « missing priority tag » sur un
    # cahier Cucumber ordinaire nomme un manque qui n'en est pas un.
    if profile == "qaia":
        tag_audit["missing_priority_tag"] = no_priority
        tag_audit["technique_tag_violations"] = technique_hits

    # --- deterministic /100 (explicit budget, like a real tg_scorer) ---
    readability = 25 * (len([s for s in scen if s["name"] and s["steps"]]) / n)
    completeness_base = len([i for i in range(len(scen)) if covers_i(i)]) / n
    if declared_acs:
        covered_acs = set()
        for i, s in enumerate(scen):
            if covers_i(i):
                for tag in s["tags"]:
                    for ac in declared_acs:
                        # jeton entier, pas sous-chaine : sinon @AC10 credite AC1 (revue dev)
                        if re.search(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(ac),
                                     tag, re.I):
                            covered_acs.add(ac)
        completeness = 30 * (len(covered_acs) / len(declared_acs))
    else:
        completeness = 30 * completeness_base
    coherence = 20 * (1 - (len(truncated_i | empty_then_i) / n))
    # Le facteur 0,4 recompense « la reference pointe un critere d'acceptation », ce qui se
    # reconnait a `@AC...` ou `@QAIA-...` : une convention de CE projet. Applique a tout le
    # monde, il plafonnait un cahier etranger PARFAITEMENT trace a 60 % de la dimension --
    # 78/CONCERNS pour `@JIRA-1234` la ou `@QAIA-US-004-009` rendait 88/PASS sur un cahier
    # par ailleurs identique. Le raffinement reste, sous le profil qui le revendique.
    if profile == "qaia":
        traceability = 25 * (len(traced) / n) * (0.6 + 0.4 * (len(ac_linked) / n))
    else:
        traceability = 25 * (len(traced) / n)

    # La tracabilite se DETECTE (cf. REQ_REF_RE) : notee quand le cahier montre une convention
    # de reference, retiree du denominateur quand il n'en montre aucune. Un cahier qui ne trace
    # pas n'est pas note zero sur ce point : il est declare non evalue, ce qui est la verite.
    # Sous le profil `qaia`, la tracabilite est EXIGEE : un cahier de ce projet qui perd ses
    # identifiants doit etre retrograde, c'est meme la raison d'etre de la dimension. Le
    # rendre « non evalue » l'aurait promu de 75/CONCERNS a 100/PASS, dans le sens qui ne
    # pardonne pas -- releve par une relecture developpeur en contexte vierge.
    traceability_assessed = bool(traced) or profile == "qaia"
    rescaled = (readability + completeness + coherence) * 100.0 / 75.0
    if traceability_assessed:
        scored = readability + completeness + coherence + traceability
        if profile == "qaia":
            raw = scored
        else:
            # DETECTER NE DOIT JAMAIS PUNIR. Le tout-ou-rien faisait qu'un unique tag sur
            # quatre scenarios basculait la dimension en « evaluee » et faisait perdre
            # 21 points et une porte -- l'adoption PARTIELLE punie plus durement que l'absence
            # totale. Le maximum des deux lectures supprime la falaise par construction : la
            # tracabilite ne peut qu'ajouter des points sur le chemin universel, jamais en
            # retirer. Sanctionner une tracabilite incomplete reste le travail du profil `qaia`,
            # ou elle est une exigence et non une observation.
            raw = max(scored, rescaled)
            if rescaled > scored:
                notes.append(
                    "partial traceability: %d of %d scenarios carry a requirement reference. "
                    "The dimension was scored but DID NOT lower the result -- detecting a "
                    "convention must never cost points." % (len(traced), n))
    else:
        raw = rescaled
        traceability = None
    marker_pen = min(25, 5 * len(markers))
    sniffer_pen = min(25, 5 * len(sniffer_hits))
    redundancy_pen = min(15, 3 * len(redundant_scenarios))
    score = max(0, round(raw - marker_pen - sniffer_pen - redundancy_pen))

    # forced STOP (IEC-style): >=3 fabrication/marker hits, or any hollow/empty/vague Then.
    # Redundancy alone never forces STOP (mode 3b — real per-value assertions may still
    # differ on an identical Given/When; a human, not the detector, judges that call).
    forced_stop = (len(markers) + len(sniffer_hits) >= 3) or bool(hollow or empty_then or vague)
    unmappable = [scen[i]["name"] for i in sorted(unmappable_i)]
    # Le JSON posait `"score": 87` et `"gate": "FAIL"` cote a cote sans un mot. Defendable sur le
    # fond -- un `Then` vide n'est pas un test, quel que soit le score -- mais le lecteur passe
    # trente secondes a chercher pourquoi, a chaque fichier. Releve par une relectrice en
    # contexte vierge : « un score et un verdict qui se contredisent ».
    if forced_stop:
        gate = "FAIL"
        causes = []
        if hollow: causes.append("hollow AC (covered only by an image/table reference)")
        if empty_then: causes.append("scenario with no expected result")
        if vague: causes.append("Then that asserts nothing verifiable")
        if len(markers) + len(sniffer_hits) >= 3:
            causes.append("3+ unresolved markers or untraceable literals")
        gate_reason = ("forced STOP regardless of the score (%s) -- these are defects no total "
                       "can outweigh" % "; ".join(causes))
    elif score >= 80:
        gate = "PASS"
        gate_reason = "score %d >= 80" % score
    elif score >= 60:
        gate = "CONCERNS"
        gate_reason = "score %d in [60, 80)" % score
    else:
        gate = "FAIL"
        gate_reason = "score %d < 60" % score
    # a truncated step is never publishable as-is: cap a would-be PASS at CONCERNS
    if truncated and gate == "PASS":
        gate = "CONCERNS"
        gate_reason = ("score %d would PASS, capped at CONCERNS: a truncated step is not "
                       "publishable as written" % score)

    if markers: findings.append(f"{len(markers)} unresolved marker(s) → -{marker_pen}")
    if sniffer_hits: findings.append(f"fabrication sniffer: {len(sniffer_hits)} untraceable technical literal(s): {sniffer_hits[:3]}")
    if hollow: findings.append(f"hollow AC (C1 — covered only by an image/table ref): {hollow}")
    if unmappable:
        findings.append("dialect not mapped: %d scenario(s) use only the `*` step keyword "
                        "(valid Gherkin — Karate and similar). Their expected results were NOT "
                        "assessed and NOT scored zero; this file is not comparable to a "
                        "Given/When/Then book: %s" % (len(unmappable), unmappable))
    if empty_then: findings.append(f"no expected result (C2 — a question, not a test): {empty_then}")
    if vague: findings.append(f"vague/non-verifiable Then (C2): {vague}")
    if truncated: findings.append(f"truncated step(s): {truncated}")
    if duplicate_groups:
        findings.append(f"pesticide paradox: {len(duplicate_groups)} duplicate group(s) — "
                        f"BYTE-FOR-BYTE identical steps, not merely a shared shape "
                        f"→ -{redundancy_pen}: {duplicate_groups[:3]}")
    if variant_groups:
        # SIGNALEMENT, pas constat, et aucune penalite : meme forme mais resultat attendu
        # different, c'est-a-dire ce qu'est une paire de valeurs limites ou une paire
        # nominal/refus. 82 des 225 groupes du corpus etranger sont de cette espece.
        notes.append("same Given/When shape but different literals or different expected results "
                     "in %d group(s) — reported and NOT penalised. After literals are collapsed, "
                     "a boundary pair and a copy-paste look identical, so no text tool can tell "
                     "\"same test, new value\" from \"distinct values, deliberate coverage\": that "
                     "is a judgement about the domain. A human decides whether the repetition "
                     "earns its keep: %s" % (len(variant_groups), variant_groups[:3]))
    # @P1/@P2/@P3 et le tag de technique sont des conventions de CE projet -- elles n'existent
    # pas en Gherkin. Elles ne comptaient deja pas dans le score, mais elles produisaient 493
    # constats sur les 666 d'un corpus etranger : un bruit qui noyait les 159 constats reels.
    # Elles ne sont donc plus emises que sous le profil `qaia`, demande explicitement.
    if profile == "qaia":
        if no_priority:
            findings.append(f"missing priority tag (@P1/@P2/@P3): {no_priority}")
        if technique_hits:
            findings.append(f"technique tag count != 1 from the closed list: {technique_hits}")
    if not negative_convention_present:
        notes.append("negative ratio NOT ASSESSED: no scenario carries the @negative tag, so "
                     "there is no negative-path convention to measure here. The ratio is null, "
                     "NOT 0.0 -- a zero would be a false number, not a missing convention.")
    if not traceability_assessed:
        # Un ETAT, pas un defaut : il va dans `notes`, pas dans `findings`. Mis dans `findings`
        # il gonflait le compte de 247 sur un corpus de 257 fichiers -- le meme bruit que celui
        # qu'on venait de retirer, reintroduit par la correction elle-meme. Un constat nomme un
        # defaut ; tout le reste se dit ailleurs, sinon « nombre de constats » ne veut plus rien
        # dire et la mesure qui juge la refonte devient inutilisable.
        notes.append("traceability NOT ASSESSED: this book carries no requirement-reference "
                     "tag convention. The dimension was removed from the denominator, NOT "
                     "scored zero -- the other three were rescaled to 100.")

    return {
        "file": os.path.basename(path), "scenarios": len(scen),
        # `scenarios` compte les BLOCS `Scenario`/`Scenario Outline` -- semantique historique,
        # conservee pour ne pas invalider les baselines publiees. `executableCases` compte ce
        # qu'un lanceur executera reellement : un Outline de 6 exemples vaut 6, ce que
        # `testbook-export` projette deja en 6 lignes. Nommer les deux plutot que d'en changer une
        # en silence (#104, 2026-08-10).
        "executableCases": sum(max(1, s.get("examples", 0)) for s in scen),
        "outlines": sum(1 for s in scen if s.get("examples", 0) > 0),
        "unmappableDialect": len([1 for i, s in enumerate(scen)
                                  if s["steps"] and all(k == "*" for k, _ in s["steps"])]),
        "readability": round(readability, 1), "completeness": round(completeness, 1),
        "coherence": round(coherence, 1),
        "traceability": round(traceability, 1) if traceability is not None else None,
        "traceabilityAssessed": traceability_assessed, "profile": profile,
        "penalties": {"markers": marker_pen, "sniffer": sniffer_pen, "redundancy": redundancy_pen},
        "score": score, "gate": gate, "gateReason": gate_reason,
        "forced_stop": forced_stop, "findings": findings,
        "notes": notes,
        "tag_audit": tag_audit,
    }

GATE_ORDER = {"FAIL": 0, "CONCERNS": 1, "UNSCORED": 2, "PASS": 3}


def render_markdown(rows, where, profile):
    """Rend un rapport lisible par un humain, trie par gravite.

    Ajoute le 2026-08-24. Le mode `--batch` ne rendait que du JSON, une ligne par fichier. Une
    relectrice en contexte vierge, QA lead de son etat, l'a dit sans detour : « du JSON brut pour
    trois fichiers, ca va ; pour les 340 .feature de mon depot, non ». Sans cette sortie, la face
    « juger » demande a son utilisateur d'ecrire lui-meme son rapport -- c'est-a-dire de faire le
    travail pour lequel il a installe l'outil.

    Trie par gravite, pas par nom : ce qu'un lecteur veut voir en premier est ce qui bloque.
    """
    scored = sorted([r["score"] for r in rows if r.get("score") is not None])
    gates = {}
    for r in rows:
        gates[r["gate"]] = gates.get(r["gate"], 0) + 1
    out = ["# Audit structurel — %d fichier(s)" % len(rows), ""]
    out.append("Profil **%s**%s. Aucun LLM, aucun reseau : ce rapport est rejouable a "
               "l'identique." % (profile,
                                 " (le barème universel — rien ici n'exige une convention QAIA)"
                                 if profile == "universal" else
                                 " (surcouche QAIA demandee explicitement)"))
    out.append("")
    out.append("| | |")
    out.append("|---|---:|")
    for g in ("PASS", "CONCERNS", "FAIL", "UNSCORED"):
        if gates.get(g):
            out.append("| %s | %d |" % (g, gates[g]))
    if scored:
        out.append("| score median | %d |" % scored[len(scored) // 2])
    total_findings = sum(len(r.get("findings", [])) for r in rows)
    out.append("| constats | %d |" % total_findings)
    out.append("")

    ordered = sorted(rows, key=lambda r: (GATE_ORDER.get(r["gate"], 9),
                                          r["score"] if r.get("score") is not None else -1))
    out.append("| Fichier | Score | Porte | Pourquoi |")
    out.append("|---|---:|---|---|")
    for r in ordered:
        out.append("| `%s` | %s | %s | %s |"
                   % (r["file"], "—" if r.get("score") is None else r["score"], r["gate"],
                      (r.get("gateReason") or "")[:110]))
    out.append("")

    problems = [r for r in ordered if r["gate"] in ("FAIL", "CONCERNS", "UNSCORED")
                and r.get("findings")]
    if problems:
        out.append("## Ce qu'il y a a corriger")
        out.append("")
        for r in problems:
            out.append("### `%s` — %s" % (r["file"], r["gate"]))
            for f in r["findings"]:
                out.append("- %s" % f)
            out.append("")

    # Les etats se disent UNE FOIS, pas une fois par fichier. Repetes 247 fois sur un corpus de
    # 257, ils noient les constats reels -- la faute meme que l'inversion du barème a corrigee.
    seen = []
    for r in rows:
        for n in r.get("notes", []):
            key = n.split(":")[0]
            if key not in seen:
                seen.append(key)
    if seen:
        out.append("## Ce qui n'a pas ete evalue, et pourquoi")
        out.append("")
        for r in rows:
            for n in r.get("notes", []):
                if n.split(":")[0] in seen:
                    out.append("- %s" % n)
                    seen.remove(n.split(":")[0])
        out.append("")
    return "\n".join(out)


def main():
    # Findings text uses non-ASCII characters (e.g. the "->" arrow); on Windows, stdout defaults
    # to the console's legacy codepage (cp1252) rather than UTF-8, crashing on print() -- found by
    # actually running this script on Windows (2026-07-29 skill-eval campaign), not by inspection.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try: stream.reconfigure(encoding="utf-8")
            except Exception: pass
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        # `--help` etait lu comme un CHEMIN et rendait « BROKEN: --help illisible ». Un outil en
        # ligne de commande qui traite sa propre demande d'aide comme un fichier introuvable
        # apprend a son utilisateur qu'il ne l'attendait pas.
        print(__doc__)
        sys.exit(0 if args else 1)
    fmt = "json"
    if "--format" in args:
        i = args.index("--format")
        fmt = args[i + 1] if len(args) > i + 1 else ""
        if fmt not in ("json", "md"):
            print("BROKEN: --format attend `json` ou `md`, pas %r" % fmt, file=sys.stderr)
            raise SystemExit(2)
        args = args[:i] + args[i + 2:]
    profile = "universal"
    if "--profile" in args:
        i = args.index("--profile")
        profile = args[i + 1]
        if profile not in ("universal", "qaia"):
            print("BROKEN: --profile attend `universal` ou `qaia`, pas %r" % profile,
                  file=sys.stderr)
            raise SystemExit(2)
        args = args[:i] + args[i + 2:]
    if "--third-party" in args:
        # Alias deprecie : ce qu'il demandait est devenu le defaut le 2026-08-24. Conserve pour
        # ne pas casser les appelants, et il le DIT -- un drapeau devenu sans effet qui reste
        # silencieux laisse croire a son lecteur qu'il fait encore quelque chose.
        print("NOTE: --third-party est deprecie -- le barème universel est desormais le defaut. "
              "Utilisez `--profile qaia` pour ajouter les conventions de ce projet.",
              file=sys.stderr)
        args = [a for a in args if a != "--third-party"]
    if args[0] == "--batch":
        if len(args) < 2:
            print("BROKEN: --batch attend un repertoire", file=sys.stderr)
            raise SystemExit(2)
        paths = sorted(glob.glob(os.path.join(args[1], "*.feature")))
        if not paths:
            # Zero fichier n'est pas zero probleme. Le mode --batch se taisait et sortait 0 :
            # indiscernable d'un succes, donc un chemin mal ecrit passait pour un depot sain.
            # C'est le « vert a vide » exact -- dans l'outil qui, FICHIER PAR FICHIER, refuse
            # deja de noter un parse vide (UNSCORED, #105). La garde existait un niveau trop bas.
            # Releve par une relectrice en contexte vierge : « si je me trompe de chemin, et sous
            # Windows ca arrivera, je crois que tout va bien. »
            print("BROKEN: aucun fichier .feature sous %s -- le perimetre est vide, ce n'est "
                  "pas un succes" % args[1], file=sys.stderr)
            raise SystemExit(2)
        rows = [score_feature(f, profile=profile) for f in paths]
        if fmt == "md":
            print(render_markdown(rows, args[1], profile))
        else:
            for r in rows: print(json.dumps(r, ensure_ascii=False))
        return
    declared = None; source = None; path = args[0]
    if "--acs" in args: declared = args[args.index("--acs") + 1].split(",")
    if "--source" in args:
        _src_path = args[args.index("--source") + 1]
        try:
            source = open(_src_path, encoding="utf-8").read()
        except (IOError, OSError) as exc:
            print("BROKEN: --source %s illisible -- %s" % (_src_path, exc), file=sys.stderr)
            raise SystemExit(2)
    print(json.dumps(score_feature(path, declared, source, profile=profile),
                     ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
