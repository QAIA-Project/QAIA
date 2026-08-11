---
stepsCompleted: [need-understanding, istqb-design, prioritize]
lastStep: prioritize
lastSaved: 2026-08-11
---

# 03-design — conditions, techniques, niveaux

Source : `01-extraction.md` (US-SITE-001, 7 critères). Niveaux assignés selon
[ADR 0008](../../../../docs/adr/0008-test-level-is-a-design-property.md) — **l'interface par
laquelle la promesse est observable**.

## Les questions ouvertes, avant les conditions

- **Q1 — « sans faire défiler » n'a pas de définition.** AC1 promet une lecture immédiate ; la
  hauteur de fenêtre varie du téléphone au 27 pouces. *Défaut sûr appliqué : la promesse est
  vérifiée sur une fenêtre de 1280×720, taille de référence déjà employée par les suites du dépôt.*
  Un scénario `@low-confidence` le porte.
- **Q2 — « exactement les points d'entrée publiés » (AC6) : lesquels ?** Le sitemap liste quatre
  URL ; `_site` contient aussi `llms.txt`, `robots.txt`, `sitemap.xml`. *Défaut sûr appliqué : les
  points d'entrée sont les pages HTML de premier niveau plus `/demo/` — les fichiers destinés aux
  machines ne s'indexent pas.*
- **Q3 — les liens externes.** Hors périmètre par décision (`01-extraction.md`), pas par oubli.
  Rouvrir la question demanderait de décider ce qu'on fait d'un lien qui répond 403 à un robot et
  200 à un humain, ce qui est un vrai sujet et pas une case à cocher.

## Conditions

| # | Condition | AC | Niveau | Technique | `[req-neg]` |
|---|---|---|---|---|---|
| C1 | Chaque URL déclarée du site répond 200 | AC5 | `api` | ep | — |
| C2 | Une URL inconnue ne répond pas 200 | AC5 | `api` | error-guessing | **oui** |
| C3 | `robots.txt` désigne un sitemap qui répond | AC6 | `api` | ep | — |
| C4 | L'ensemble des URL du sitemap **est** l'ensemble des points d'entrée publiés | AC6 | `api` | ep | — |
| C5 | Chaque page HTML est servie en `text/html` | AC5 | `api` | ep | — |
| C6 | `llms.txt` est servi et non vide | AC6 | `api` | boundary | — |
| C7 | `/demo/` est servi — la seconde source d'assemblage est bien là | AC5 | `api` | ep | — |
| C8 | L'accueil énonce ce qui entre et ce qui sort dans la première fenêtre | AC1 | `e2e` | ep | — |
| C9 | Le statut pré-alpha est visible sur chaque page publique | AC2 | `e2e` | ep | — |
| C10 | Le bloc d'installation nomme les deux plugins et leur commande | AC3 | `e2e` | ep | — |
| C11 | L'affirmation de preuve pointe un artefact atteignable | AC4 | `e2e` | ep | — |
| C12 | Chaque ancre de navigation a une cible existante dans la page | AC5 | `e2e` | ep | — |
| C13 | Chaque page déclare une langue | AC7 | `e2e` | ep | — |
| C14 | Les titres des trois pages sont distincts | AC7 | `e2e` | pairwise | — |

**7 conditions `api`, 7 conditions `e2e`. Une seule `[req-neg]` : C2.**

*Corrigé le 2026-08-11, après relecture.* Six conditions étaient marquées `[req-neg]` et cinq
scénarios étiquetés `@negative` alors que **leur issue attendue est un succès ou une cohérence**,
pas un refus. La définition est fermée et elle est dans ce dépôt : *« a scenario whose outcome is
a refusal, an error, or an explicitly denied access »* — `negative-ratio.md` ajoute même que
compter les issues normales d'une fonctionnalité qui marche est *« the most common way a ratio
inflates without anyone intending to cheat »*. C'est exactement ce qui s'était passé : le ratio
annoncé était **0,31**, il est **0,04**, et l'erreur allait dans le sens qui flatte.

C4, C9, C12 et C14 restent les conditions les plus intéressantes du cahier — ce sont des
**incohérences entre artefacts**, la classe qu'aucune relecture humaine ne trouve parce qu'il faut
lire trois fichiers en même temps. Elles n'ont simplement rien à voir avec la porte des refus.

## Ce que cette conception ne couvre pas, et pourquoi c'est écrit ici

**Le contenu.** Aucune condition ne vérifie que ce que le site affirme est vrai — qu'il y a bien
37 skills, que le défaut json-server existe. Ce sont des affirmations sur le dépôt, gardées par
`check_skill_counts.py` et par la campagne qu'elles citent, pas par une suite web. Les tester ici
en ferait une seconde copie d'une règle déjà gardée ailleurs.
