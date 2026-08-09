# Portabilité du contrat d'émission — mesure du 2026-08-09 (issue #88)

**Question posée :** écrire dans `testbook-generate` le contrat d'émission qu'elle supposait
fait-il disparaître les échecs de forme mesurés le 2026-08-08 ?

**Réponse courte : les trois causes d'origine ont disparu. Une quatrième est apparue, et surtout
la mesure elle-même s'est révélée instable — ce qui est le résultat le plus important du jour.**

## Protocole

Bras A de #84 rejoué à l'identique : même entrée réelle (`03-design.md` + `04-priorities.md` de
US-004), mêmes séparateurs, même consigne finale. **Seule la skill change.** Quatre fournisseurs
(Gemini, Groq, HuggingFace, Mistral) via `eval/tools/multi_model_generate.py`. Cerebras répond
`402 Payment Required` sur toute la campagne et est exclu, pas compté comme échec.

Arbitre : `gherkin-lint` avec la configuration du dépôt, la même que la CI.

## Ce qui a été mesuré

| Passage | Contrat | gemini | groq | huggingface | mistral |
|---|---|---|---|---|---|
| **2026-08-08** (référence) | absent | OK | ÉCHEC | ÉCHEC | OK |
| **2026-08-08 after-fix** | partiel | OK | OK | OK | ÉCHEC |
| **Tour 1** | prose | OK | ÉCHEC | OK | ÉCHEC |
| **Tour 2** | prose + squelette | *expiré* | ÉCHEC | OK | **OK** |
| **Tour 2 bis** | prose + squelette | **OK** | **OK** | ÉCHEC | **OK** |

Les tours 2 et 2 bis ont reçu **exactement le même prompt**.

## Les trois causes d'origine sont fermées

1. **Bloc de code autour de la sortie** — 2 modèles sur 4 en émettaient le 2026-08-08.
   **0 sur 4 sur les trois passages d'aujourd'hui**, soit 12 sorties consécutives. La règle
   « émets le fichier, rien d'autre » tient.
2. **Ligne `Feature:` manquante ou commentée** — c'était l'échec le plus répété (Groq, puis
   Mistral après une première correction). **Aucune occurrence aujourd'hui.**
3. **Langue d'émission** — aucune occurrence de mots-clés Gherkin non anglais.

## Ce que la prose n'a pas suffi à obtenir

L'indentation. Après le contrat **en prose**, Mistral indentait un cran trop court partout —
`Scenario:` à 0 au lieu de 2, les pas à 2 au lieu de 4. Il avait lu « `Feature:` at column 0 »
puis appliqué sa propre échelle.

Remplacer la description par un **squelette littéral** (colonnes annotées) a corrigé Mistral :
ÉCHEC au tour 1, OK aux tours 2 et 2 bis. **Une règle de forme décrite se prête à
l'interprétation ; une forme montrée se copie.** C'est la leçon transférable de cette campagne.

## La cause nouvelle, documentée et non contournée

**Étiquettes au-dessus d'un `Background:`** — interdit par le linter, et le contrat se taisait
dessus : il parlait des étiquettes précédant un `Scenario:`. Ajouté comme règle 4. Groq, qui
échouait là-dessus au tour 1, passe au tour 2 bis.

**Troncature volontaire (Groq, tour 2).** Groq a écrit `# ... (les autres scenarios)` puis un
épilogue en français, produisant 79 lignes contre 255 au passage suivant sur le même prompt. Ce
n'est pas un défaut de forme : c'est du **contenu élidé**, que le linter attrape par accident.
À surveiller, pas à corriger par le prompt.

## Le vrai résultat : la mesure n'est pas déterministe

**Deux passages du même prompt donnent trois modèles sur quatre au vert — mais pas les mêmes
trois.** HuggingFace passe au tour 2 et échoue au tour 2 bis, sur l'indentation, avec le
squelette sous les yeux.

Conséquences, à assumer plutôt qu'à lisser :

- **La définition de fini de #88 — « les trois échecs de forme disparaissent » — est atteinte
  pour les trois causes nommées, et ne peut pas être atteinte « pour toujours » par une
  campagne d'un seul passage.** Un modèle qui passe une fois n'est pas un modèle qui passe.
- **Un taux annoncé sur une seule exécution n'a pas de sens ici.** Toute mesure de portabilité
  future doit répéter et rapporter la dispersion, pas un chiffre.
- La correction reste nette et mesurable : **0/12 blocs de code, 0 ligne `Feature:` manquante**,
  contre 2/4 et 1/4 avant. Ce sont les gains solides ; l'indentation, elle, reste probabiliste.

## Ce que cette campagne n'établit pas

Elle mesure la **forme**, parce que c'est ce que le linter arbitre. Elle ne dit rien du fond :
aucun des cahiers produits ici n'a été noté par `structural_score.py`, ni relu par un humain.
Le 2026-08-08 notait déjà qu'aucun des deux modèles en échec n'échouait sur le fond — cela n'a
pas été revérifié aujourd'hui et ne doit pas être supposé.
