# Go-live — ce qui t'attend, dans l'ordre, avec le texte déjà écrit

Tout ce qui suit demande **ton nom** : soit un clic dans une interface où je ne peux pas
m'authentifier, soit une prise de parole publique qu'un agent n'a pas à faire à ta place. Rien
ici ne demande de rédaction : les textes existent, les liens sont vérifiés, l'ordre est réfléchi.

**Budget total : environ 40 minutes**, dont 25 pour l'étape 4.

L'ordre n'est pas cosmétique. Les annuaires d'abord (personne ne les lit en temps réel, donc
aucun risque si quelque chose cloche) ; la prise de parole ensuite, une fois que les liens qu'elle
contient sont déjà indexés ; le recrutement de pilotes en dernier, quand il y a enfin des gens
pour le voir.

---

## Étape 1 — awesome-claude-code (2 minutes)

**51 858 ★, poussé quotidiennement. C'est l'annuaire qui compte le plus.**

⚠️ **À cliquer, pas à scripter.** Leur `CONTRIBUTING.md` menace de restreindre les comptes qui
contournent le formulaire web. Je ne risque pas ton compte sur le dépôt le plus visible de
l'écosystème pour économiser deux minutes.

**Éligibilité vérifiée** : leur règle est « ≥ 14 jours ET développement actif » OU « ≥ 100 ★ ».
QAIA a 16 jours et des commits quasi quotidiens. La première branche passe. Une seule ressource à
la fois — ne soumets pas les quatre plugins.

👉 **[Ouvrir le formulaire](https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml)**

Champs à remplir — le texte est dans
[`directory-submissions.md`](directory-submissions.md#2-hesreallyhimawesome-claude-code--à-faire-à-la-main-2-minutes),
section 2. Nom `QAIA`, URL du dépôt, licence MIT, et la description de six lignes déjà rédigée.

*Leur note, que je trouve juste : « si "être sur la liste" fait partie de ta stratégie
promotionnelle, prévois un plan B ». Deux minutes, aucune attente.*

## Étape 2 — QASkills.sh (10 minutes, création de compte)

Le canal le plus direct vers l'audience QA : adossé à **The Testing Academy, 189 000+ abonnés
YouTube** — exactement la communauté que D12 désignait dès M0 et qui n'a jamais été approchée.

👉 **[qaskills.sh](https://qaskills.sh/)** → « Publish a Skill »

**Une décision à prendre, et je te donne ma recommandation plutôt qu'un menu** : commence par
**trois skills qui tiennent debout seules** — `istqb-design`, `us-review`, `security-surface` — et
lie le marketplace QAIA depuis chacune. Leur unité est la skill ; soumettre le marketplace entier
serait plus fidèle à ce qu'est QAIA mais bien moins découvrable, et la découvrabilité est
justement ce qui manque.

À vérifier en créant le compte : conditions de publication (attribution, licence, exigence
d'auto-suffisance du fichier). Si l'une d'elles est incompatible avec MIT + attribution, ne
soumets pas et dis-le-moi.

## Étape 2 bis — l'état réel, mesuré le 2026-08-11 (et ce qu'il reste à soumettre)

**Trois skills sur sept sont en ligne. Les quatre autres n'ont jamais été soumises** — préparées le
2026-08-08 après que l'étape 2 ci-dessus ait recommandé de commencer par trois, et le geste manuel
n'a pas suivi. `SOURCES.json` les déclarait pourtant toutes « publiées » ; corrigé, et
`eval/tools/check_directory_listing.py` interroge désormais l'API publique de l'annuaire pour que
l'écart ne puisse plus passer.

**En ligne, 0 installation chacune, `verified: false` :**

| Slug servi par l'annuaire | Problème |
|---|---|
| `requirement-ambiguity-hunt` | aucun — slug propre |
| `accessibility-audit-axe-core-plus-the-pass-axe-cannot-do` | **56 caractères** |
| `security-surface-checks-passive-risk-ranked-with-the-mis-runs-named` | **67 caractères** |

La médiane des slugs du site est de **20 caractères**, et les entrées les mieux installées sont
nommées en deux mots d'après leur outil : `playwright-e2e` (422 installations), `playwright-cli`
(106), `jest-unit` (83), `cypress-e2e` (71). Nos deux longs slugs viennent de titres qui étaient des
phrases descriptives — l'annuaire les a transformés en slug tels quels.

**Les noms ont été raccourcis dans le dépôt** (le qualificatif est passé dans la description) :

| Copie | Nouveau nom | Slug attendu |
|---|---|---|
| `istqb-technique-selection` | ISTQB Technique Selection | `istqb-technique-selection` |
| `generated-test-self-review` | Generated Test Self-Review | `generated-test-self-review` |
| `performance-check` | Performance Budget Check | `performance-budget-check` |
| `visual-regression` | Visual Regression Baselines | `visual-regression-baselines` |

Les quatre slugs attendus ont été **vérifiés libres** sur l'annuaire le 2026-08-11.
`visual-regression` tout court est **pris** par `thetestingacademy` — d'où le suffixe.

### Ce qui reste manuel, et qui n'appartient qu'au fondateur

1. **Soumettre les quatre** via `qaskills.sh` → *Publish a Skill*. Le corps est prêt dans
   `docs/outreach/qaskills/<dossier>/SKILL.md`, autonome, MIT.
2. **Renommer les deux longues** déjà en ligne, si l'interface le permet — `Accessibility Audit` et
   `Security Surface Checks`. Le nom est déjà corrigé côté dépôt.
3. **Retéléverser `generated-test-self-review` après soumission** : sa version ici a gagné la
   classe D10 le 2026-08-11 (la fixture qui invalide l'assertion), et l'API ne permet pas de
   vérifier le contenu en ligne — seulement la présence.
4. **Regarder ce que demande `verified`.** Les trois entrées sont `verified: false` pendant que les
   gros contributeurs sont vérifiés ; il y a probablement une étape qu'on n'a pas franchie.

**À ne pas espérer** : les trois en ligne totalisent **zéro installation** depuis le 2026-08-08.
C'est cohérent avec le reste des signaux — 0 étoile, 0 fork, 16 visiteurs uniques sur 14 jours — et
c'est la première métrique d'*usage* que le projet obtienne. Soumettre quatre skills de plus ne la
changera probablement pas ; ça ferme surtout un écart entre ce que le dépôt affirme et ce qui est.

---

## Étape 3 — le reste des annuaires (je m'en occupe, sauf blocage)

`claudemarketplaces.com`, `claudepluginhub.com`, `aitmpl.com`, SkillsMP, ClawHub, skills.sh,
Smithery. Suivi dans [`directory-submissions.md`](directory-submissions.md). La PR sur
`jeremylongshore/claude-code-plugins-plus-skills` (2 608 ★) est **déjà ouverte** —
[#1163](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1163) — et leur
relecteur automatique l'a notée 5/5, « safe to merge ». Rien à faire dessus.

## Étape 4 — LinkedIn (25 minutes, dont 20 de réponses)

Texte prêt : [`linkedin-post-fr.md`](linkedin-post-fr.md), **version A**, l'angle « j'ai publié
mes mauvaises notes ».

Trois consignes qui changent la portée :

1. **Le lien ne va pas dans le post** — LinkedIn dégrade les posts sortants. Premier commentaire,
   immédiatement après publication, et édite le post pour ajouter « lien en commentaire ».
2. **Créneau** : mardi, mercredi ou jeudi, 8h-9h ou 12h-13h.
3. **Reste 20 minutes après** pour répondre. Un post sans réponses de l'auteur dans l'heure meurt.

**Un point de vérité à corriger dans le texte avant de publier**, et je préfère le dire que le
laisser passer : la version A dit « un panel de 13 personas ». Depuis, on a établi que **ce panel
est auto-administré** — des agents jouant un cabinet fictif, pas des relecteurs extérieurs. Le
site le dit maintenant. Le post doit le dire aussi, sinon quelqu'un ouvre `docs/KANBAN.md` et
l'argument d'honnêteté s'effondre en un commentaire. Formulation proposée :

> J'ai fait auditer mon projet open source par un panel de 13 personas — que j'ai fait tourner
> moi-même, ce sont des agents jouant un cabinet fictif, pas des relecteurs extérieurs, et c'est
> écrit tel quel dans le dépôt.
>
> Note moyenne : 2,4 sur 5.

C'est moins vendeur et beaucoup plus solide. Un lecteur qui vérifie trouve exactement ce que le
post annonce.

## Étape 5 — recruter les 5 pilotes (#1)

À faire **après** le post, pas avant : c'est le premier moment où il y a des gens pour répondre.

Le matériel existe : [`docs/PILOT-KIT.md`](../PILOT-KIT.md), un parcours guidé de 15 minutes sur
une histoire toute prête, lié depuis le site, la page de comparaison et le README.

Canaux, dans l'ordre de proximité :

1. **Réponses au post LinkedIn** — les gens qui commentent sont déjà intéressés. Demande-leur
   directement, en message privé.
2. **Ministry of Testing** — texte prêt dans
   [`show-hn-and-reddit.md`](show-hn-and-reddit.md), section Ministry of Testing. C'est le canal
   que D12 désignait dès M0.
3. **r/QualityAssurance** — texte prêt, même fichier. Lis les règles du sub avant : certains
   exigent un flair ou un jour dédié à l'autopromotion.

**Ce que je peux faire dès qu'un pilote dit oui** : préparer son ticket, dépouiller son retour,
ouvrir les issues avec attribution, et écrire publiquement ce qu'on n'a pas su corriger. C'est ce
que le kit promet ; il faut le tenir.

## Étape 6 — #61, la relecture PM/PO à froid

**Ce que je ne peux pas faire** : l'auteur des encarts ne peut pas juger si les encarts sont
clairs (règle 3). Il faut un vrai PM ou PO qui n'a pas travaillé sur QAIA.

**Ce qui est prêt** : l'encart existe dans **six skills**, identique, à citer verbatim —
`need-understanding`, `prioritize`, `feedback`, `oracle-generate`, `aptitude-gate`,
`dataset-generate`.

Le protocole de relecture tient en un message à envoyer à la personne :

> Tu es PM ou PO. Voici un encart qu'un outil de QA affiche quand il a besoin d'un arbitrage de
> ta part. Trois questions, et **ne lis rien d'autre du projet** :
>
> 1. Est-ce que tu comprends ce qu'on te demande de décider, sans jargon de test ?
> 2. Est-ce que tu comprends ce qui se passe si tu ne réponds pas ?
> 3. Est-ce que « je ne sais pas » te semble une réponse acceptable après avoir lu ça ?
>
> Si la réponse à l'une des trois est non, dis-moi **quelle phrase** t'a perdu.

Le contrôle mécanique est déjà passé (trois volets partout, zéro jargon non glosé). Ce qui manque
est exactement ce qu'une machine ne peut pas produire : est-ce que ça marche sur quelqu'un dont ce
n'est pas le métier.

---

## Ce que je continue pendant ce temps

Le backlog technique. Il reste `#18` (bloquée par un vrai pilote, donc par l'étape 5), `#63`
(reliquat de suites à juger), `#29`/`#30` (tier opt-in, post-pilote par décision), `#32` (crédit
Hugging Face épuisé). Et tout ce que les pilotes remonteront, qui aura priorité sur le reste.
