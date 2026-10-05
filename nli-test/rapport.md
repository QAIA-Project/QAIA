# Test de contenus IA : similarité et NLI — résultats recalculés

Tous les chiffres ci-dessous sont produits par `run.py` (affichage arrondi à 3 décimales par le code ; valeurs pleine précision dans `results.csv`).

## Méthode de calcul

- **Levenshtein** : `rapidfuzz.distance.Levenshtein.normalized_similarity(a, b)` = 1 − distance / max(len(a), len(b)), en caractères, sur le texte brut (casse, accents et ponctuation conservés). Colonne « Indel » = `fuzz.ratio/100` (distance sans substitution), donnée à titre de diagnostic seulement.
- **TF-IDF** : `TfidfVectorizer()` par défaut, ajusté sur les **deux seuls textes** de la paire ; minuscules, tokens `\b\w\w+\b` (mots d'une lettre et ponctuation ignorés), idf lissé, sans stop-words ni lemmatisation, norme L2 ; cosinus.
- **Embeddings** : `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, `encode()` par défaut, cosinus.
- **NLI** : `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`, softmax sur les logits, étiquettes lues dans `model.config.id2label` = `{0: 'entailment', 1: 'neutral', 2: 'contradiction'}`. A→B : A prémisse, B hypothèse.

## Partie A — valeurs publiées vs recalculées

Écart = recalculé − publié. ⚠️ = |écart| > 0.02.

| Cas | Métrique | Publié | Recalculé | Écart | |
|---|---|---|---|---|---|
| C1-V1 | Levenshtein | 0.250 | 0.234 | -0.016 |  |
| C1-V1 | TF-IDF | 0.068 | 0.068 | +0.000 |  |
| C1-V1 | Embeddings | 0.761 | 0.779 | +0.018 |  |
| C1-V2 | Levenshtein | 0.425 | 0.425 | +0.000 |  |
| C1-V2 | TF-IDF | 0.436 | 0.436 | +0.000 |  |
| C1-V2 | Embeddings | 0.647 | 0.673 | +0.026 | ⚠️ |
| C1-V3 | Levenshtein | 0.172 | 0.156 | -0.016 |  |
| C1-V3 | TF-IDF | 0.056 | 0.056 | +0.000 |  |
| C1-V3 | Embeddings | 0.428 | 0.388 | -0.040 | ⚠️ |
| C2-V1 | Levenshtein | 0.264 | 0.256 | -0.008 |  |
| C2-V1 | TF-IDF | 0.193 | 0.193 | -0.000 |  |
| C2-V1 | Embeddings | 0.479 | 0.676 | +0.197 | ⚠️ |
| C2-V2 | Levenshtein | 0.361 | 0.361 | +0.000 |  |
| C2-V2 | TF-IDF | 0.193 | 0.193 | -0.000 |  |
| C2-V2 | Embeddings | 0.859 | 0.884 | +0.025 | ⚠️ |
| C2-V3 | Levenshtein | 0.186 | 0.171 | -0.015 |  |
| C2-V3 | TF-IDF | 0.000 | 0.000 | +0.000 |  |
| C2-V3 | Embeddings | 0.425 | 0.403 | -0.022 | ⚠️ |
| C3 | Levenshtein | 0.825 | 0.825 | +0.000 |  |
| C3 | TF-IDF | 0.551 | 0.551 | -0.000 |  |
| C3 | Embeddings | 0.456 | 0.455 | -0.001 |  |

Diagnostic Levenshtein (deux définitions de « ratio » chez rapidfuzz) :

| Cas | Publié | Levenshtein normalisé | Indel (`fuzz.ratio/100`) |
|---|---|---|---|
| C1-V1 | 0.250 | 0.234 | 0.426 |
| C1-V2 | 0.425 | 0.425 | 0.611 |
| C1-V3 | 0.172 | 0.156 | 0.422 |
| C2-V1 | 0.264 | 0.256 | 0.431 |
| C2-V2 | 0.361 | 0.361 | 0.493 |
| C2-V3 | 0.186 | 0.171 | 0.380 |
| C3 | 0.825 | 0.825 | 0.880 |

Ordre des variantes par score d'embeddings (publié vs recalculé) :

- C1 : publié `C1-V1 > C1-V2 > C1-V3` — recalculé `C1-V1 > C1-V2 > C1-V3`
- C2 : publié `C2-V2 > C2-V1 > C2-V3` — recalculé `C2-V2 > C2-V1 > C2-V3`

### Écarts > 0.02 avec les valeurs publiées

5 écart(s) sur 21 valeurs :

- C1-V2 Embeddings : publié 0.647, recalculé 0.673 (écart +0.026)
- C1-V3 Embeddings : publié 0.428, recalculé 0.388 (écart -0.040)
- C2-V1 Embeddings : publié 0.479, recalculé 0.676 (écart +0.197)
- C2-V2 Embeddings : publié 0.859, recalculé 0.884 (écart +0.025)
- C2-V3 Embeddings : publié 0.425, recalculé 0.403 (écart -0.022)

Métriques concernées : Embeddings. Plus grand écart : C2-V1 Embeddings (+0.197).

## Partie B — hypothèses (embeddings seulement)

| Variante testée | Score | Score de la variante d'origine | Δ |
|---|---|---|---|
| B1 C2-V1 sans « de Coutances » : « Établissement tranquille au cœur de la ville, avec vue mer et formule petit-déjeuner. » | 0.805 | 0.676 (C2-V1) | +0.129 |
| B2a C2-V1 Coutances→Cherbourg : « Établissement tranquille au cœur de Cherbourg, avec vue mer et formule petit-déjeuner. » | 0.730 | 0.676 (C2-V1) | +0.055 |
| B2b C2-V1 Coutances→Lyon : « Établissement tranquille au cœur de Lyon, avec vue mer et formule petit-déjeuner. » | 0.685 | 0.676 (C2-V1) | +0.010 |
| B3 C1-V2 sans « -Montparnasse » : « Un trajet idéal pour les familles, avec une correspondance à Paris. » | 0.762 | 0.673 (C1-V2) | +0.089 |

## Partie C — NLI dans les deux sens

Règle : « équivalent » si entailment ≥ 0.90 dans les deux sens, sinon « revue humaine ».

| Paire | A→B E / N / C | B→A E / N / C | Verdict règle | Attendu | |
|---|---|---|---|---|---|
| C1-V1 | 0.985 / 0.010 / 0.005 | 0.972 / 0.024 / 0.004 | équivalent | équivalent | ✅ |
| C1-V2 | 0.026 / 0.965 / 0.009 | 0.955 / 0.043 / 0.002 | revue humaine | revue humaine | ✅ |
| C1-V3 | 0.031 / 0.817 / 0.151 | 0.001 / 0.988 / 0.010 | revue humaine | revue humaine | ✅ |
| C2-V1 | 0.096 / 0.903 / 0.001 | 0.999 / 0.001 / 0.000 | revue humaine | revue humaine | ✅ |
| C2-V2 | 0.998 / 0.002 / 0.000 | 0.999 / 0.001 / 0.000 | équivalent | équivalent | ✅ |
| C2-V3 | 0.001 / 0.997 / 0.002 | 0.001 / 0.996 / 0.002 | revue humaine | revue humaine | ✅ |
| C3 | 0.000 / 0.001 / 0.999 | 0.001 / 0.002 / 0.998 | revue humaine | revue humaine | ✅ |
| P1 dose | 0.002 / 0.004 / 0.995 | 0.003 / 0.006 / 0.991 | revue humaine | revue humaine | ✅ |
| P2 consentement | 0.000 / 0.008 / 0.992 | 0.000 / 0.010 / 0.990 | revue humaine | revue humaine | ✅ |
| P3 à jeun | 0.224 / 0.023 / 0.754 | 0.102 / 0.069 / 0.828 | revue humaine | revue humaine | ✅ |
| M1 grossesse | 0.998 / 0.001 / 0.001 | 0.917 / 0.081 / 0.002 | équivalent | équivalent | ✅ |
| M2 rétractation | 0.956 / 0.044 / 0.000 | 0.998 / 0.002 / 0.000 | équivalent | équivalent | ✅ |
| M3 résiliation | 0.007 / 0.028 / 0.964 | 0.013 / 0.008 / 0.979 | revue humaine | revue humaine | ✅ |
| M4 remboursement | 0.005 / 0.002 / 0.993 | 0.008 / 0.005 / 0.987 | revue humaine | revue humaine | ✅ |

Accord règle / attendu : 14 sur 14.

Textes et justification de l'attendu :

- **C1-V1** — A : « Trajet confortable pour les enfants, avec un changement à Paris. » / B : « Voyage adapté aux familles avec correspondance parisienne. » — paraphrase voulue (familles ≈ enfants, discutable)
- **C1-V2** — A : « Trajet confortable pour les enfants, avec un changement à Paris. » / B : « Un trajet idéal pour les familles, avec une correspondance à Paris-Montparnasse. » — ajoute un fait non sourcé (Montparnasse), « idéal » ≠ « confortable »
- **C1-V3** — A : « Trajet confortable pour les enfants, avec un changement à Paris. » / B : « Réservez votre billet de train pour la Normandie dès maintenant. » — hors sujet
- **C2-V1** — A : « Hôtel calme en centre-ville, petit-déjeuner inclus, vue sur la mer. » / B : « Établissement tranquille au cœur de Coutances, avec vue mer et formule petit-déjeuner. » — ajoute un fait non sourcé (Coutances)
- **C2-V2** — A : « Hôtel calme en centre-ville, petit-déjeuner inclus, vue sur la mer. » / B : « Hôtel situé en plein centre, paisible, avec panorama sur l'océan et buffet matinal. » — paraphrase voulue (océan ≈ mer, buffet ≈ petit-déjeuner)
- **C2-V3** — A : « Hôtel calme en centre-ville, petit-déjeuner inclus, vue sur la mer. » / B : « Parking gratuit, accès autoroute, idéal pour les voyageurs d'affaires. » — hors sujet
- **C3** — A : « Le patient ne présente aucune contre-indication au traitement. » / B : « Le patient présente plusieurs contre-indications au traitement. » — contradiction
- **P1 dose** — A : « La dose maximale est de 500 mg par jour. » / B : « La dose maximale est de 1000 mg par jour. » — chiffre changé, structure identique
- **P2 consentement** — A : « Le consentement du patient est obligatoire. » / B : « Le consentement du patient est facultatif. » — antonyme sur un seul mot
- **P3 à jeun** — A : « Le médicament doit être pris à jeun. » / B : « Le médicament peut être pris pendant les repas. » — contradiction implicite (à jeun ⇔ hors repas)
- **M1 grossesse** — A : « Ce médicament est contre-indiqué chez la femme enceinte. » / B : « Les femmes enceintes ne doivent pas prendre ce médicament. » — [choix Claude] reformulation santé : terme technique → langage courant, ajout d'une négation qui ne change pas le sens
- **M2 rétractation** — A : « Le délai de rétractation est de quatorze jours. » / B : « Le consommateur dispose de quatorze jours pour se rétracter. » — [choix Claude] reformulation juridique : nominalisation → verbe, sujet explicité
- **M3 résiliation** — A : « Le contrat peut être résilié à tout moment. » / B : « Le contrat ne peut pas être résilié avant son terme. » — [choix Claude] opposition juridique franche, vocabulaire très proche
- **M4 remboursement** — A : « Ce dispositif est remboursé par l'Assurance maladie. » / B : « Ce dispositif n'est plus remboursé par l'Assurance maladie. » — [choix Claude] négation discrète : « n'…plus » (2 mots courts) inverse le sens

Paires M1–M4 (choisies par Claude) : deux reformulations équivalentes (santé, juridique) qui changent la structure de phrase sans changer le sens, pour vérifier que la règle n'envoie pas tout en revue ; une opposition juridique franche à vocabulaire partagé ; une négation discrète (« n'…plus ») qui ne modifie que deux mots courts — le cas où les métriques de surface sont les plus trompeuses.

## Limites constatées

- **« Ratio Levenshtein » est ambigu** : rapidfuzz expose au moins deux normalisations (`Levenshtein.normalized_similarity` et `fuzz.ratio`, qui est en fait une distance Indel). Elles donnent des valeurs différentes (tableau diagnostic ci-dessus) ; il faut nommer la fonction exacte dans l'article.
- **TF-IDF sur deux phrases** : l'idf est appris sur 2 documents, donc tout mot présent dans les deux reçoit le poids minimal et le score dépend fortement de la tokenisation (mots d'une lettre supprimés, « l'océan » → « océan », « Paris-Montparnasse » → 2 tokens) et du choix du corpus d'ajustement. Un autre corpus ou des stop-words donneraient d'autres valeurs.
- **Embeddings** : le score dépend du modèle exact, de sa version et du pooling ; le cosinus n'a pas d'échelle absolue (un « bon » score dans un cas peut être inférieur à un « mauvais » dans un autre).
- **Les métriques de surface et d'embeddings ne voient pas la négation** : sur C3 (contradiction), Lev 0.825, TF-IDF 0.551, Emb 0.455 ; sur M4 (« n'est plus remboursé »), Lev 0.881, TF-IDF 0.883, Emb 0.724.
- **La NLI est asymétrique** : plus grand écart d'entailment entre les deux sens sur C1-V2 (A→B 0.026, B→A 0.955). Avec un seul sens, la règle aurait changé de verdict sur : A→B seul aucune ; B→A seul C1-V2, C2-V1.
- **Seuil de 0.90** : choisi a priori, non calibré ; les verdicts proches du seuil sont instables d'une version de modèle à l'autre.
- **« Résultat attendu »** : c'est mon jugement de relecteur (colonne justification), pas une vérité terrain ; pour C1-V1 en particulier (« familles » vs « enfants »), l'équivalence se discute.
- **Échantillon minuscule** (18 paires au total) : illustre des comportements, ne mesure aucun taux d'erreur.
- **Choix pris par simplicité** : textes non normalisés pour Levenshtein et embeddings ; NLI sans troncature effective (phrases courtes) ; aucune graine n'influe sur l'inférence (modèles en mode eval, CPU, algorithmes déterministes forcés).

## Environnement et temps d'exécution

- Python 3.11.15 (Linux-6.18.44-fc-v70-x86_64-with-glibc2.39, x86_64)
- torch 2.14.1+cpu
- transformers 5.18.0
- sentence-transformers 6.1.0
- sentencepiece 0.2.2
- scikit-learn 1.9.1
- rapidfuzz 3.14.6
- tokenizers 0.23.2
- huggingface_hub 1.33.0
- numpy 2.4.6
- protobuf 7.36.2
- Threads torch : 4
- Chargement des modèles : 8.2 s ; calculs : 3.1 s ; total (imports compris) : 15.8 s
- Premier lancement : téléchargement des modèles depuis Hugging Face (non compté s'ils sont en cache).
