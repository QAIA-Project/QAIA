---
stepsCompleted: [00-ingest, 01-review, 02-understanding, 03-design]
lastStep: 03-design
lastSaved: 2026-08-10
status: waived
---

# 03-design — US-002 : techniques ISTQB choisies et justifiées

**Périmètre : boîte noire uniquement.** Aucune technique structurelle (instruction, branche,
décision, MC-DC) n'est proposée — QAIA part des critères d'acceptation et ne lit jamais
l'implémentation de l'application cible. Le test exploratoire est l'exclusion symétrique. Ce sont
deux exclusions délibérées, pas des lacunes.

## AC → technique(s), avec la raison tenant à la forme de l'AC

| AC | Technique(s) | Justification |
|---|---|---|
| AC1 | Partitionnement d'équivalence + devinette d'erreur | Fiche présente / incomplète / absente : trois classes traitées différemment. La classe « absente » vient du log d'ambiguïté (Q7), pas d'une intuition |
| AC2 | Valeurs limites | Seuil bas avec inclusivité **énoncée** (« strictly below ») : min−1, min, min+1 sont décidables sans arbitrage |
| AC3 | Valeurs limites | Seuil haut dont l'inclusivité est **indécise** (Q1) : max−1 décidable, max **indécidable**, max+1 décidable |
| AC4 | Valeurs limites + test de domaine (§3.1.1) | Le cumul lie deux variables liées — la dose de chaque prise et l'instant de la prise dans la fenêtre. Une AVL par variable manquerait la combinaison ; le domaine la couvre |
| AC5 | Table de décision (§3.3.1) | Deux conditions (âge < plancher, rôle pédiatre) → trois actions distinctes (passe, bloque, avertit-surchargeable). C'est la forme canonique d'une table |
| AC6 | Test métamorphique (§3.3.2) | **La valeur attendue exacte ne peut pas être énoncée** : la règle d'arrondi est absente (Q6). Mais la *relation* est connue et vérifiable — à médicament et dose égaux, le patient avec drapeau rénal doit obtenir un verdict au moins aussi restrictif que celui sans drapeau. On vérifie la relation au lieu d'affirmer un chiffre fabriqué |
| AC7 | Valeurs limites + partitionnement | Seuil de longueur à 20 : 19 / 20 / 21, plus les classes de contenu (vide, espaces seuls) issues de Q10 |
| AC8 | Test basé sur scénario (§3.2.3) | **Un seul par US**, marqué `@smoke` : il traverse saisie → validation → restitution sans rechargement |
| AC5 × AC6 | Table de décision | L'interaction est une combinaison de conditions, pas un seuil — la table est la seule technique qui rend l'indécision visible en colonne |

**Techniques considérées et écartées :** transition d'états (§3.2.2) — la prescription a bien un
cycle de vie, mais cette US ne décrit aucune transition de statut, seulement un verdict de
validation ; CRUD (§3.2.1) — aucune gestion d'entité complète ici ; combinatoire/pairwise
(§3.1.2) — les paramètres ne sont pas indépendants, ils sont liés par des règles, ce qui appelle
la table de décision et non le pairwise ; CT-AI — l'application cible ne porte aucun modèle.

## Conditions de test dérivées — entrée contractuelle de `testbook-generate`

Ce sont des **conditions**, pas encore des scénarios.

| ID | AC | Condition | Technique | Question liée |
|---|---|---|---|---|
| C01 | AC1 | Médicament avec fiche complète → validation nominale possible | EP | — |
| C02 | AC1 | Médicament **sans fiche de référence** | EP / erreur | Q7 `[open]` |
| C03 | AC1 | Fiche présente mais âge plancher absent | EP / erreur | Q7 `[open]` |
| C04 | AC2 | Dose = min − 1 unité → avertissement | AVL | — |
| C05 | AC2 | Dose = min exactement → **pas** d'avertissement (« strictly below ») | AVL | — |
| C06 | AC2 | Surcharge d'avertissement avec motif documenté → signature possible | EP | Q9 `[open]` |
| C07 | AC3 | Dose = max − 1 → autorisée | AVL | — |
| C08 | AC3 | Dose = max **exactement** → verdict **indécidable** | AVL | Q1 `[open]` |
| C09 | AC3 | Dose = max + 1 → blocage, signature impossible | AVL `[req-neg]` | — |
| C10 | AC4 | Somme des prises = cumul max exactement | AVL / domaine | Q1, Q3 `[open]` |
| C11 | AC4 | Somme = cumul max + 1 → blocage | AVL `[req-neg]` | Q3 `[open]` |
| C12 | AC4 | Deux prises à cheval sur minuit, conformes en calendaire, dépassant en glissant | Domaine | Q3 `[open]` |
| C13 | AC4 | Deux prescriptions concurrentes, chacune conforme, somme dépassant | Domaine / erreur | Q8 `[open]` |
| C14 | AC5 | Âge = plancher − 1, prescripteur non pédiatre → blocage | Table `[req-neg]` | — |
| C15 | AC5 | Âge = plancher exactement → autorisé | AVL | — |
| C16 | AC5 | Âge = plancher − 1, prescripteur **pédiatre** → avertissement surchargeable | Table | — |
| C17 | AC5 | Surcharge pédiatrique **sans** justification → refusée | Table `[req-neg]` | — |
| C18 | AC6 | Drapeau rénal : verdict au moins aussi restrictif qu'à dose égale sans drapeau | Métamorphique | — |
| C19 | AC6 | Drapeau rénal sur seuil impair → arrondi **indécidable** | Métamorphique | Q6 `[open]` |
| C20 | AC6 | Drapeau rénal rendant max réduit < min efficace → verdict **indécidable** | Table | Q4 `[open]` |
| C21 | AC5×AC6 | Patient pédiatrique **et** insuffisant rénal, prescripteur pédiatre | Table | Q5 `[open]` |
| C22 | AC7 | Justification de 19 caractères → surcharge refusée | AVL `[req-neg]` | — |
| C23 | AC7 | Justification de 20 caractères → surcharge acceptée | AVL | Q10 `[assumption]` |
| C24 | AC7 | Justification de 20 espaces → **indécidable** | EP | Q10 `[assumption]` |
| C25 | AC7 | Trace : identité, horodatage et texte présents après surcharge | EP | — |
| C26 | AC8 | Verdict rendu dans l'écran de signature sans rechargement, identifiants de règle inclus | Scénario `@smoke` | — |
| C27 | AC8 | Verdict de blocage multiple → **plusieurs** identifiants de règle rendus | EP | — |
| C28 | AC2 | Unité de dose hétérogène entre saisie et fiche | EP / erreur | Q2 `[open]` |

## Porte de couverture des chemins de refus (ADR 0001)

Toute règle capable de refuser, bloquer ou nier **doit** porter au moins une condition qui
l'exerce. Recensement exhaustif :

| Règle capable de refuser | Condition qui l'exerce | Statut |
|---|---|---|
| AC3 — blocage dose max par prise | C09 `[req-neg]` | ✅ |
| AC4 — blocage cumul 24 h | C11 `[req-neg]` | ✅ |
| AC5 — blocage âge plancher | C14 `[req-neg]` | ✅ |
| AC5 — refus de surcharge sans justification | C17 `[req-neg]` | ✅ |
| AC7 — refus de surcharge sous 20 caractères | C22 `[req-neg]` | ✅ |

**Porte franchie : 5 règles de refus, 5 exercées.**

Ratio négatif/limite brut, **mesuré sur le cahier émis** et non estimé ici : **18 scénarios sur
28 portent `@negative` ou `@boundary`, soit 64 %** (relevé depuis
`.qaia/testbooks/US-002/*.feature`). Cette ligne annonçait 50 % avant génération ; le chiffre
d'origine était une estimation de conception, remplacée par la mesure plutôt que l'inverse.
**Rapporté comme signal de biais happy-path, jamais comme seuil à atteindre** (ADR 0001) — le
ratio ne gate rien, la couverture des chemins de refus ci-dessus, si.

## Ce que ce dessin ne couvre pas, et le dit

Onze conditions (C02, C03, C08, C10, C12, C13, C19, C20, C21, C24, C28) reposent sur une question
`[open]` non arbitrée. Elles seront **générées et marquées**, jamais présentées comme vérifiant
une règle confirmée : un test qui affirme une supposition passe au vert et ne prouve rien.
