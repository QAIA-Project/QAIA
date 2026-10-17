# QAIA — playbook de lancement

Un guide court pour transformer le produit en visibilité, sans trahir ce qui le rend crédible.
Écrit pour un fondateur qui n'écrit pas de code et dont l'avantage est d'être un ancien directeur
QA avec une audience LinkedIn.

## La règle qui gouverne tout

**L'honnêteté est l'angle, pas un handicap.** Un mainteneur de marketplace externe a fermé une
soumission QAIA *en saluant* sa candeur. Le statut « pre-alpha, aucun pilote humain » n'est pas une
faiblesse à cacher : c'est ce qui rend le reste crédible. Ne jamais fabriquer de métrique, de
témoignage, d'étoile. La concurrence promet ; QAIA mesure. C'est la marque.

## Le funnel

Un seul chemin, dans cet ordre :

1. **La démo** (`/try.html`) — le hameçon visuel. « Un test peut scorer 100 et être nul. » On clique,
   on voit un verdict réel, on comprend en 30 s. C'est la page à partager, pas le README.
2. **GitHub** — la conversion. Qui a aimé la démo va voir le code et met une étoile.
3. **Le pilote** — la preuve qui manque (gate G2). Un vrai testeur essaie `judge` sur ses propres
   tests. C'est ce qui débloque la marketplace *et* la crédibilité.

La démo sert les trois d'un coup. Tout post ramène à elle.

## Où, et à quelle cadence

- **LinkedIn d'abord** — c'est là qu'est ton réseau QA, et le build-in-public y marche. 1 post /
  semaine, pas plus. La régularité bat le volume.
- Puis les communautés de testeurs (Ministry of Testing, r/QualityAssurance, forums ISTQB).
- **Pas** TikTok/Twitter-viralité : mauvais public pour un outil de dev QA.
- Le « like » suit la valeur. On ne court pas après lui ; on rend la valeur visible et il vient.

## Trois posts prêts à coller (LinkedIn, FR)

### Post 1 — le hameçon honnête
> J'ai passé des mois à construire un outil de QA open-source **sans écrire une ligne de code** —
> en « vibecodant » avec Claude.
>
> Le truc que j'ai appris en tant qu'ancien directeur QA et que l'outil incarne : **un cahier de
> test peut scorer 100/100 et être complètement nul.** Un critère « couvert » par une image
> illisible. Un cas sans résultat attendu — une question déguisée en test.
>
> J'en ai fait une démo. Colle un cahier Gherkin, vois ce qu'il vaut vraiment :
> 👉 [lien /try.html]
>
> C'est pré-alpha, et ça le dit. Je cherche des testeurs curieux pour l'essayer sur leurs *vrais*
> tests et me dire où ça casse. #QA #testing #opensource

### Post 2 — build-in-public, le journal
> Semaine N de QAIA en public. Cette semaine, un mainteneur de marketplace a **refusé** ma
> soumission — et c'est la meilleure chose qui me soit arrivée.
>
> Sa raison : trop large, pas encore de pilote humain. Exactement ce que mon propre audit disait.
> Il a salué la franchise et m'a donné le chemin : une skill, étroite, prouvée.
>
> Je ne cache pas les refus. C'est ça, construire honnêtement. [lien /try.html] #buildinpublic #QA

### Post 3 — la démonstration technique
> « Score élevé = bon test » est le piège n°1 de l'IA en QA.
>
> Preuve par un cas réel : une facturation hospitalière notée **100/100 par la machine, 58/100 par
> un testeur**. La machine voit la structure ; l'humain voit le sens.
>
> QAIA transforme ces écarts en détecteurs déterministes : le score peut être haut, la porte reste
> **FAIL**, avec la raison nommée. Un nombre qu'on peut rejouer, jamais un modèle qui se note.
>
> Essaie : [lien /try.html]. #QualityAssurance #AI #testing

## Ce qu'il faut pour que la démo soit *live*

La page existe et est vérifiée, mais elle se déploie depuis `main` (GitHub Pages). Tant qu'elle
n'est pas fusionnée dans `main`, l'URL `qaia-project.github.io/QAIA/try.html` ne répond pas.
Merger la branche (ou ouvrir une PR) est le seul geste restant avant de poster.

## Checklist avant le premier post

- [ ] La démo est live (`/try.html` répond).
- [ ] Le lien du post pointe vers la démo, pas le README.
- [ ] Aucune métrique inventée ; « pre-alpha » assumé.
- [ ] Un appel clair à des **testeurs pilotes** (c'est le vrai besoin, gate G2).
- [ ] Prêt à répondre vite aux premiers retours — le premier pilote vaut cent likes.
