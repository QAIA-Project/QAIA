# Rétrospective honnête : QAIA face aux erreurs d'IATS

> **Document historique — retrospective close (marque le 2026-08-10).**
> Retour d'experience sur IATS, le projet qui a precede QAIA. Rien ici ne decrit le produit
> actuel ; c'est la matiere d'ou viennent plusieurs decisions de `docs/DECISIONS.md`. A lire
> comme une archive, pas comme une consigne.

*Auto-audit — mis à jour le 2026-07-24 (ter). Écrit pour être inconfortable, pas pour rassurer.*

> **Mise à jour du #24 (2026-07-24 ter).** Le harnais de gap annoncé plus bas comme correction
> de cadrage a été **exécuté** — sur du matériel réel sourcé sur le web (pas le corpus IATS
> confidentiel, indisponible), pas seulement en gold-set démo. Résultat honnête : 2 des 4
> modes (config-driven, variance) confirmés sans régression/comme prévu ; 2 défauts concrets
> trouvés et corrigés dans `istqb-design` (silence sur les entités-sœurs non nommées,
> fabrication convergente non flaggée). Détail complet : `eval/baselines/gap-harness-24.md`.
> Non refait : re-mesure des 50 US de `groundtruth-corpus.md` avec les amendements — la
> correction de cadrage ci-dessous ("le pilote n'est pas la seule preuve possible") est donc
> validée dans les faits, pas seulement en principe.

> **Grounding (2026-07-24).** Cette version est recalée sur la **documentation réelle d'IATS**
> (pas seulement le résumé de `PROMPT.md`). Les specifics confidentiels (client, modules internes,
> volumétrie) ne sont **pas** reproduits ici — seule la leçon portable est gardée. Deux faits
> confirmés par les docs réels : (a) un cas documenté où un test book obtient **100/100 en score
> machine mais ~58/100 en revue humaine** — un AC compté « couvert » reposait en fait sur un
> **tableau en image non lisible** (test creux), un cas n'avait **pas de résultat attendu** (une
> question, pas un test), et des trous d'idempotence qu'un 100 masque : la machine excelle en
> **structure**, l'humain en **sémantique** ; (b) IATS **avait** une observabilité (traçage des
> prompts) **et un budget LLM cappé par run** — ce que QAIA n'a pas.

IATS était le projet interne dont QAIA tire ses leçons (`PROMPT.md`, section 2). Ce document
confronte QAIA **à ces leçons précises** et note, sans complaisance, où le projet les répète.

## Verdict en une ligne

QAIA a **évité** les erreurs de forme d'IATS (sur-scripting bloquant, dépendance à une stack
propriétaire) mais **répète partiellement deux erreurs de fond** : le couplage pipeline entre
skills, et les connecteurs construits **avant** que le cœur soit éprouvé sur pilote. Aucune
mesure FinOps par commande n'existe encore — c'est en soi une régression par rapport à IATS,
qui avait son monitoring de coût.

---

## Leçon IATS #1 — « Outils d'abord, pipelines ensuite »

**L'erreur d'IATS :** avoir sur-scripté des pipelines rigides avant que les briques unitaires
soient fiables ; quand une étape changeait, tout le pipeline cassait.

**Où QAIA est propre :** chaque skill suit la règle « prérequis manquant → propose, n'échoue
pas ». Aucune skill ne `throw` parce qu'une étape amont n'a pas tourné : elle détecte, explique,
propose. 6 skills sont réellement autonomes et invocables seules (`hello`, `qaia-help`,
`testbook-validate`, `oracle-generate`, `us-ingest`, `rag-build`).

**Où QAIA répète l'erreur (partiellement) :** 11 skills du parcours lisent/écrivent un
**checkpoint partagé** dans `.qaia/state/`. Il y a donc bien une **forme de pipeline** : l'ordre
canonique us-ingest → us-review → need-understanding → istqb-design → prioritize →
testbook-generate est une chaîne. Elle est *souple* (chaque maillon peut tourner seul et se
plaint gentiment), mais la **forme séquentielle couplée existe** — c'est une répétition atténuée,
pas évitée, de l'erreur #1. Tant qu'aucun pilote n'a stressé chaque skill **isolément** sur son
propre problème, on ne sait pas si les briques sont fiables indépendamment du pipeline.

**Ce qui manque pour clore :** un audit d'indépendance skill par skill (issue ouverte), et des
pilotes qui invoquent des skills **hors de l'ordre canonique**.

## Leçon IATS #2 — « Public inconnu = standards de l'industrie ; connecteurs jamais avant que le cœur soit éprouvé »

**L'erreur d'IATS :** avoir bâti des intégrations (connecteurs) avant d'avoir prouvé que le cœur
apportait de la valeur — effort dépensé sur de la plomberie pour un cœur non validé.

**Où QAIA répète l'erreur :** deux connecteurs existent déjà alors que **le cœur n'a passé aucun
pilote** (gate G2 non atteint) :
- le **connecteur Jira à l'ingestion** (issue #9, D9) ;
- l'**oracle projet OpenAPI/JSON Schema** (issue #16) — un connecteur de spec.

La discovery avait *explicitement* mis en garde contre ça. Les deux sont « portable-first » et
n'ajoutent pas de dépendance propriétaire dure, ce qui limite la casse — mais **l'ordre est
inversé** : on a construit de la connectique avant la preuve pilote du cœur. C'est la leçon #2,
répétée en connaissance de cause.

**Circonstance atténuante honnête :** ces connecteurs sont du texte de skill (pas du code
auto-exécuté), donc réversibles à coût nul. L'erreur est d'allocation d'effort, pas de dette
technique irréversible.

## Leçon IATS — monitoring de coût (FinOps)

**Ce qu'IATS avait :** Langfuse / suivi FinOps — la visibilité du coût par run.

**Ce que QAIA n'a pas :** **aucune instrumentation du coût token par commande utilisateur.**
Seule existe une télémétrie côté mainteneur sur les workflows d'évaluation (~115k à 1.76M tokens
par campagne). Le tableau « ordre de grandeur » du README (issue #7) est aujourd'hui **estimé**
depuis la taille des prompts de skill et le nombre typique de tours — **pas mesuré** sur des runs
instrumentés. C'est une régression par rapport à IATS et l'issue #7 reste **partiellement
adressée** (estimation datée publiée ; instrumentation réelle à faire).

---

## Ce que QAIA a fait mieux qu'IATS (pour être juste)

- **Pas de stack propriétaire** : plugins Claude Code, aucune clé API, tourne dans la session de
  l'utilisateur avec ses permissions. IATS dépendait d'une infra ; QAIA se distribue en Markdown.
- **Mesuré, pas asserté** : held-out ≥ train (53 % ≥ 33 % de rappel pondéré) prouve l'absence de
  sur-apprentissage ; qaia-score discrimine proprement (18/PASS vs 2/FAIL). IATS affirmait sans
  gold set held-out.
- **Sécurité en dur avant la fonctionnalité** : gates PII/abus/injection/not-a-spec à l'ingestion,
  deux blockers sécurité trouvés et corrigés.
- **Bruit assumé** : le juge LLM est déclaré ±15-20 pts ; seules les comparaisons intra-run sont
  crues.
- **Garde-fou anti-« test creux » déjà en place** : le cas documenté à 100/100-machine échouait
  notamment parce qu'un AC « couvert » reposait sur une **image non lisible**. `us-ingest` liste
  explicitement les images/pièces jointes comme **« non analysées »** et interdit de les ignorer
  en silence — QAIA a donc intégré *par conception* la contre-mesure de ce mode d'échec précis.
  (À prouver en usage : que `testbook-generate` ne compte jamais « couvert » un AC dont la seule
  source est une pièce non analysée — c'est un test de gap à ajouter au #24.)

## RAF pour vraiment clore les leçons

1. **Pilotes (G2)** — la seule vraie preuve. Web ≠ pilote (voir ci-dessous). Bloque #1, #5, la
   majorité du RAF M3.
2. **Audit d'indépendance des skills** — chaque skill stressée hors pipeline.
3. **Instrumentation FinOps réelle** (#7) — remplacer l'estimation par du mesuré par commande.
4. **Ne plus construire de connecteur** tant que G2 n'est pas franchi.

## Ce que la doc IATS réelle révèle — écarts de conception concrets (2026-07-24)

En lisant la doc réelle d'IATS (et non le résumé), un fait s'impose : **IATS est un système
mûr**, et sur plusieurs points QAIA est *en dessous* de ce que le projet fondateur avait déjà
résolu. Leçons **portables** (l'IP Softway n'est pas reproduite) :

1. **Le score n'est pas un LLM qui s'auto-note — IATS le sait, QAIA pas encore.** IATS score la
   structure de façon **déterministe** : un barème explicite /100 (lisibilité / complétude = % d'AC
   couverts / cohérence = aucun step tronqué / traçabilité), **reproductible**, séparé d'un audit
   sémantique distinct. QAIA repose sur un **juge LLM** (bruit ±15-20 pts, que j'ai flaggé). C'est
   une faiblesse : QAIA devrait avoir un **score structurel déterministe** séparé de tout jugement
   LLM. → issue.

2. **Détecteur anti-fabrication (« sniffer ») — la vraie réponse au mode d'échec #3.** IATS
   **pénalise** les inventions : −5 pt par marqueur « à définir », et un *sniffer* qui repère un nom
   propre **inventé** dans un champ technique (port, host, code) → pénalité, et **≥3 hits = STOP
   forcé**. QAIA se contente d'une *consigne* « ne jamais inventer » dans `oracle-generate` — aucune
   **détection**. Or « jeu de données fantaisie » est précisément le mode d'échec que tu as cité.
   Une consigne n'est pas un garde-fou ; il faut un détecteur. → issue.

3. **Cas sans résultat attendu = une question, pas un test (C2 du cas 676266).** IATS l'a
   rencontré et documenté. QAIA n'a **pas de détecteur** d'un scénario dont le `Then` n'affirme
   rien de vérifiable. C'est un test de gap concret pour le #24. → issue.

4. **Auditabilité inviolable.** IATS garde un trail **JSONL haché SHA-256 en chaîne** (exigence
   IEC). Le manifeste QAIA n'est **pas** infalsifiable. Hors-scope tant que QAIA n'est pas régulé,
   mais à noter.

5. **Observabilité / budget.** IATS : budget LLM cappé par run + traçage des prompts. QAIA : rien
   (déjà tracé, issue #7).

**Le cas US 676266 comme banc d'essai du #24.** Ses trois défauts se traduisent en tests de gap
concrets pour QAIA : **C1** (AC « couvert » par une image illisible) → vérifier que
`testbook-generate` ne compte **jamais** couvert un AC dont la seule source est une pièce « non
analysée » ; **C2** (cas sans résultat attendu) → détecteur de `Then` non-vérifiable ; **M**
(idempotence/ré-imports) → couverture sémantique transverse. Ces trois cas entrent tels quels dans
le gold set durci du #24.

**Nuance importante :** IATS a été **construit sur mesure** pour un domaine régulé, avec l'équipe
et l'infra pour le porter. QAIA est une **distillation open-source portable, sans clé API**, pour
un public inconnu. Tout ce qu'IATS a n'est pas à copier — mais le *scoring déterministe* et le
*détecteur anti-fabrication* sont des patterns génériques que QAIA gagnerait à reprendre.

## Correction (challenge fondateur, 2026-07-24) — j'avais sur-pondéré « pilote »

Le fondateur a cassé mon cadrage, à raison. Les 4 modes d'échec *techniques* d'IATS —
(1) extraction d'AC rien/partiel/confus, (2) contexte lu sur une seule US sans remonter à la
feature/epic, (3) jeu de données fantaisie/redondant (pesticide), (4) orchestrateur à variance
non maîtrisée — sont **tous mesurables par analyse de gap unitaire par skill sur le gold set,
sans aucun pilote**. J'avais confondu deux choses : dé-risquer les échecs techniques d'IATS
(gold-set-mesurable — et **non livré** à cette granularité) vs prouver la valeur produit à un vrai
testeur (pilote). J'ai brandi le pilote comme bouclier là où la vraie dette est une **mesure de
gap par skill × mode d'échec** que je n'ai pas faite (j'ai un rappel *agrégé*, pas le détail par
mode). → issue **#24**.

**Faille dans l'argument « le gold set démo suffit » :** les cas de démo ont des **AC propres**.
IATS échouait sur AC *implicites/en désordre*. Mesurer le gap d'extraction sur des démos donne un
vert **faussement rassurant**. Le gold set doit donc inclure **délibérément des cas durs** (AC
implicites, besoin réparti epic, pièges de redondance) — sinon l'analyse de gap ment. Et la
variance ne se voit qu'en **N runs**, pas en tir unique (held-out ≥ train est mono-shot).

**Ordre des leviers corrigé :** le prochain levier technique est le **harnais de gap #24** (agent-
faisable, sans G2), *avant* les pilotes. Le pilote reste nécessaire — mais pour la valeur produit,
pas pour dé-risquer les échecs techniques d'IATS.

## Pourquoi « testé sur des exemples web » n'est pas un pilote

Les 50+ US réelles de GitHub et l'app medibook prouvent le **rappel contre un artefact humain
figé** — pas qu'un vrai testeur, sur son vrai problème, est aidé par le workflow conversationnel.
Les validations humaines du parcours ont été **simulées** par l'agent (non interactives). Le gate
G2 (5 pilotes réels) reste **non atteint**, par construction. C'est la limite la plus importante
du projet à ce jour, et elle est structurelle : aucune quantité de test web ne la lève.
