# Prompt de revue externe — à coller dans un LLM sans accès au dépôt

> **Document consomme — entree de campagne, pas guide vivant (marque le 2026-08-10).**
> Prompt de la revue externe ; son resultat est la note 2,4/5 consignee dans `docs/STATUS.md`.
> **Les chiffres qu'il contient sont ceux de sa redaction** (« 35 skills » etait juste le
> 2026-07-29 ; le depot en porte 37 au 2026-08-10). Ils ne sont pas corriges : reecrire l'enonce
> d'une campagne apres coup falsifierait ce qui a reellement ete demande au relecteur. Meme
> raison que l'exclusion de `docs/STATUS.md` du perimetre de `check_skill_counts.py`.

Complément de [`ARCHITECTURE-REVIEW-PROMPT.md`](ARCHITECTURE-REVIEW-PROMPT.md), qui s'adresse à un
agent **ayant** le dépôt sous la main. Celui-ci s'adresse à un LLM de conversation — ChatGPT,
Gemini, Mistral — qui n'a rien d'autre que le message qu'on lui envoie.

## Pourquoi il est construit ainsi

Trois analyses externes ont été commandées le 2026-08-08. Deux ont échoué de la même façon, faute
de contexte fiable :

- l'une a **décrit un produit qui n'existe pas** — elle a lu le dossier `eval/` (outillage de
  mainteneur) et en a conclu que QAIA était un banc d'essai de LLM multi-juges. Toute sa feuille de
  route portait sur un autre produit ;
- l'autre a **inventé des chiffres** : un nombre de skills faux, un numéro d'issue inexistant avec
  sa priorité, un nombre de contributeurs erroné.

Aucune des deux n'était de mauvaise foi. Les deux comblaient un vide qu'on ne leur avait pas dit de
laisser vide. D'où les deux règles qui ouvrent le prompt : **marquer `[NON VÉRIFIABLE]`** ce qui ne
peut pas être tiré du message, et **ne pas reformuler ce qu'est le produit**.

Le corps du prompt porte les faits vérifiés — y compris ceux qui ne flattent pas — pour que le
lecteur n'ait rien à deviner.

## Ce qu'il faut mettre à jour avant de l'envoyer

Les chiffres de la section « état réel » et les deux tableaux de couverture. Ils sont datés du
2026-08-08 ; les envoyer périmés reproduirait exactement le défaut qu'ils servent à éviter.

## Deux isolements différents, souvent confondus

Ce prompt affirme *« tu n'as PAS accès au dépôt »*. Encore faut-il que ce soit vrai — sinon c'est
une affirmation invérifiable dans un document dont toute la raison d'être est d'empêcher les
affirmations invérifiables.

Il y a **deux** isolements, ils n'attrapent pas les mêmes défauts, et il faut savoir lequel on veut :

| | Ce que le relecteur ignore | Ce que ça attrape |
|---|---|---|
| **Contexte de conversation vide** | ce qui a été affirmé plus tôt dans la session | une affirmation qui ne correspond pas aux fichiers |
| **Aucun accès au dépôt** | tout, sauf le message reçu | une erreur de positionnement, de récit, de priorité |

Le panel du 2026-08-08 (`eval/cold-review-2026-08-08/`) utilisait le **premier** : les lentilles
pouvaient lire les fichiers, mais ne savaient pas ce que leur auteur avait prétendu. C'est ce qui
leur a permis de trouver 19 écarts entre les affirmations et le dépôt.

Ce prompt-ci veut le **second**. Il ne cherche pas un écart entre le dire et le faire — il cherche
si **ce qu'on a choisi de raconter tient debout**, ce qui est exactement la position d'un prospect.

## Comment l'exécuter

**Par défaut — une conversation neuve dans ChatGPT, Gemini ou Mistral.** Les deux isolements sont
satisfaits gratuitement : le modèle n'a ni l'historique, ni les fichiers. C'est le mode pour lequel
ce prompt est écrit.

**Dans Claude Code — attention.** Un sous-agent lancé depuis le dépôt **a** les outils de lecture.
Lui dire « tu n'as pas accès » ne le lui retire pas : c'est une consigne qu'il peut enfreindre, et
surtout une **prémisse fausse** qui rend sa sortie difficile à interpréter. Deux options honnêtes :

1. le lancer depuis un répertoire qui n'est pas le dépôt — il n'a alors rien à lire, et la prémisse
   devient vraie ;
2. ne pas l'utiliser là, et prendre [`ARCHITECTURE-REVIEW-PROMPT.md`](ARCHITECTURE-REVIEW-PROMPT.md),
   qui est écrit pour un agent qui **a** le dépôt et doit s'appuyer dessus.

**Ce qu'il ne faut pas faire** : le lancer en sous-agent dans le dépôt en affirmant qu'il n'y a pas
accès. La sortie serait un mélange indiscernable de ce qu'on lui a dit et de ce qu'il a lu.

## Le contrôle qui rend l'isolement vérifiable

La section D du format demande au relecteur de **déclarer lui-même** s'il a consulté autre chose
que le message. Une réponse qui cite un chemin de fichier, un numéro d'issue ou un chiffre absent
du prompt s'est disqualifiée toute seule — et c'est vérifiable sans lui faire confiance.

---

```
Tu es Directeur Technique de QAIA. Tu ne connais ce projet QUE par ce message :
tu n'as PAS accès au dépôt.

═══ RÈGLE ABSOLUE, AVANT TOUT LE RESTE ═══
1. Tu ne peux vérifier aucun fait. Toute affirmation factuelle que tu ne peux pas
   tirer de CE message doit être marquée [NON VÉRIFIABLE]. N'invente jamais un
   chiffre, un nom de fichier, un numéro d'issue ou une priorité.
2. Ne reformule pas ce qu'est le produit. Si ma description te semble incomplète,
   dis-le ; ne comble pas.
3. Si deux demandes se contredisent, ou contredisent une décision listée plus bas,
   NOMME la contradiction et demande-moi d'arbitrer. Ne tranche pas à ma place.
4. Préfère la critique à l'éloge. Une liste vide honnête vaut mieux qu'une
   recommandation inventée.
5. Ne produis aucune feuille de route à échéances : tu n'as ni mes coûts, ni mon
   temps disponible, ni mon équipe.

═══ CE QU'EST LE PRODUIT ═══
QAIA = 4 plugins Claude Code, 35 skills en Markdown, licence MIT.
Chaîne : user story (ou spécification OpenAPI) → cahier de tests Gherkin tracé à
identifiants stables → tests Playwright exécutables → score → rapport.
Les skills s'exécutent dans la session Claude Code de l'utilisateur, sur son
propre quota de modèle.

CE QUE CE N'EST PAS — un lecteur s'est déjà trompé là-dessus :
ce n'est PAS un framework d'évaluation de LLM. Le dossier `eval/` contient
l'outillage du mainteneur, jamais livré aux utilisateurs. Ne bâtis rien dessus.

═══ CONTRAINTE DURE ═══
Aucune dépendance à une ressource tierce au runtime : pas de clé API livrée, pas
de backend, pas de composant qui s'exécute seul. Cette contrainte prime sur toute
fonctionnalité. Une recommandation qui la viole doit être signalée comme telle.

═══ DÉCISIONS PRISES (ne pas les rouvrir sans nommer le coût) ═══
- Pas de niveau unitaire ni d'intégration entre composants internes : QAIA part
  d'une promesse observable de l'extérieur. Un test unitaire s'écrit contre une
  fonction, donc contre l'implémentation — c'est abandonner l'oracle. NOTE : cette
  décision n'interdit PAS la revue statique, qui part de l'exigence.
- Hooks, agents et serveurs MCP INTERDITS dans les plugins, bloqués par la CI.
  Motif : chemin d'attaque le plus fort contre un mainteneur qui ne lit pas le code.
- Aucun producteur ne note sa propre sortie : score déterministe dans un plugin
  séparé, distinct du juge sémantique.
- Le périmètre VISE désormais Discovery et Run, arbitré par le fondateur, alors que le
  produit vit aujourd'hui dans Delivery et Maintenance. C'est un écart assumé, pas un
  oubli.
- « Multi-LLM » signifie ici : les skills tournent dans l'agent que l'utilisateur paie
  déjà (Claude Code, ChatGPT, Gemini). AUCUNE clé n'est livrée. Ce n'est donc pas en
  conflit avec la contrainte d'autonomie — c'est son extension.

═══ COUVERTURE PAR PHASE DU CYCLE ═══
Modèle : SDLC canonique en 7 phases, et Discovery / Delivery / Run.

  Discovery (besoins, faisabilité, EXIGENCES NON-FONCTIONNELLES)  FAIBLE
    on ingère une user story DÉJÀ ÉCRITE ; on ne fait pas la discovery.
    Aucune skill ne dérive une exigence de perf ou de sécurité au moment
    où elle serait encore négociable.
  Delivery — conception (stratégie, techniques ISTQB, risque)      FORTE
  Delivery — implémentation (revue de code, statique, unitaire)    ABSENTE
  Delivery — test système (fonctionnel + non-fonctionnel)          FORTE (le cœur)
  Delivery — déploiement (smoke, prêt-à-livrer, rollback)          PARTIELLE
    une porte PASS/CONCERNS/FAIL/WAIVED existe ; ni smoke ni rollback.
  Run (monitoring synthétique, chaos, incident→test, A/B)          QUASI ABSENTE
    une seule skill rejoue un fichier HAR que l'utilisateur fournit.
    Zéro sur les quatre pratiques du shift-right.
  Maintenance (régression, impact, santé de la suite)              FORTE

═══ COUVERTURE PAR TYPE D'AUTOMATISATION ═══
Architecture : Page Object Model exposé en fixtures Playwright (pas d'héritage),
vérifié par une machine qui refuse une suite sans dossier `pages/`.

  E2E            Playwright (JS) uniquement — ni Cypress ni Selenium
  API            via `request` de Playwright — aucun leader API (ni Karate,
                 ni REST Assured, ni Postman/Newman)
  Performance    script k6 réel généré + version légère — le leader OSS, oui
  Sécurité       passif + baseline OWASP ZAP en option — partiel, bon outil
  Accessibilité  axe-core — le standard, oui
  Visuel         snapshots Playwright — pas de moteur perceptuel type Applitools
  Chaos          RIEN. Aucune mention dans tout le dépôt.
  Contrat        sonde HTTP maison — ni Pact ni aucun standard

  Un concurrent direct sort en Playwright, Cypress, Selenium, pytest, JUnit et
  Gherkin. Nous : un langage, un framework.

═══ AUTRES FAITS VÉRIFIÉS ═══
- Orchestrateur : une méta-skill conversationnelle de type ReAct existe. Jamais
  utilisée par un humain.
- Multi-LLM : les skills ont été passées sur Claude + Gemini + Groq + Hugging Face
  en juillet 2026. Le PRODUIT, lui, ne tourne que dans Claude Code.
- Portabilité MESURÉE une fois : la skill qui génère le cahier a été envoyée telle
  quelle à quatre modèles, chaque sortie passée au linter du projet. **Deux sur quatre**
  produisent un cahier conforme ; le meilleur reproduit la référence à l'identifiant
  près (38 scénarios, 38 identifiants, 11 marqués douteux). Écrire le contrat
  d'émission manquant n'a rien changé au net : un modèle corrigé, un régressé.
- Jamais essayé sur un autre HÔTE : ni Cursor, ni Copilot, ni Codex. Le mécanisme
  d'installation, l'accès fichiers et l'enchaînement entre skills ne sont pas testés.
- FinOps : aucune skill. Le budget token est mesuré par skill, rien ne le pilote,
  ne l'agrège ni ne le plafonne.
- RAG : une skill construit une base de connaissance versionnée dans git.
- Audits multi-persona : plusieurs (3 personas, 13 personas, un panel adverse à
  contexte vide). TOUS auto-administrés — aucun lecteur extérieur.

═══ ÉTAT RÉEL, MESURÉ ═══
0 étoile · 0 fork · 1 seul contributeur humain · AUCUN utilisateur, jamais.
2 défauts réels trouvés dans un projet tiers de 75 694 étoiles, en générant depuis
sa SEULE documentation sans jamais lire son code, confirmés par des correctifs
intégrés en amont.
111 assertions sur 111 prouvées non-décoratives par test de mutation.
Le même jour, un panel de relecture à contexte vide a trouvé 19 défauts réels dans
le travail produit — dont un qui rendait la preuve principale non reproductible.

═══ TES QUESTIONS ═══
1. L'objectif affiché est « couvrir tout le cycle ». Le produit vit dans Delivery
   et Maintenance. Faut-il corriger l'objectif, ou viser les deux bouts
   (Discovery et Run) ? Que coûte chaque option, et laquelle recommandes-tu ?
2. La portabilité plafonne à deux modèles sur quatre, et préciser les règles n'a rien
   amélioré en net. Trois leviers restent : contraindre la sortie par un gabarit,
   valider-et-redemander (émettre, linter, renvoyer l'erreur), ou assumer que le produit
   suppose un agent capable. Lequel, et qu'est-ce que chacun coûte à la contrainte
   « aucun composant qui s'exécute seul » ?
3. Côté automatisation : faut-il élargir aux autres frameworks (Cypress, Selenium,
   Karate), ou combler les catégories vides (chaos, contrat standard) ? Justifie
   par ce que ça change pour un utilisateur, pas par l'exhaustivité.
4. Avec 0 utilisateur et 35 skills, quel est le facteur limitant RÉEL ? Justifie.
5. Quels sont les 3 trous les plus coûteux — et lesquels recommandes-tu de NE PAS
   combler ?
6. Si tu étais ingénieur QA, qu'est-ce qui, dans cet état, t'empêcherait d'essayer
   ce produit ? Sois précis et brutal.

═══ FORMAT ATTENDU ═══
A. Contradictions relevées, avant tout le reste.
B. Réponses aux 6 questions, chacune avec son raisonnement.
C. Ce que tu recommandes de NE PAS faire, et pourquoi.
D. Ce que tu n'as pas pu évaluer faute d'accès — liste explicite.
E. Déclare si tu as consulté quoi que ce soit d'autre que ce message (fichier, web,
   souvenir d'un échange antérieur). Si oui, dis quoi : ta réponse doit rester
   interprétable.
```

## Deux choix assumés

**« 0 utilisateur, jamais » est en tête de l'état réel**, avant les 35 skills. Un lecteur à qui on
annonce d'abord un catalogue recommande d'y ajouter une entrée ; un lecteur à qui on annonce
d'abord une absence d'utilisateurs questionne la stratégie.

**Les 19 défauts trouvés dans notre propre travail y figurent.** C'est contre-intuitif de le donner
à un juge, mais ça l'informe sur la fiabilité du reste du message — et ça évite qu'il découvre ce
biais seul et disqualifie l'ensemble.
