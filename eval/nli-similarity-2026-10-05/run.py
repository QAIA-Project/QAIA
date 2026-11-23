"""Test de contenus générés par IA : similarité de surface, embeddings et NLI.

Tout chiffre affiché ou écrit dans results.csv / rapport.md est calculé ici.
Les seules constantes numériques saisies à la main sont les valeurs PUBLIÉES de
l'article (PUBLISHED), utilisées uniquement pour la comparaison, et les seuils
de protocole (0.02 d'écart, 0.90 d'entailment).

Définition exacte des métriques (aucun prétraitement : texte brut, casse et
ponctuation conservées, sauf mention contraire) :
- Levenshtein : rapidfuzz.distance.Levenshtein.normalized_similarity(a, b)
  = 1 - distance_levenshtein(a, b) / max(len(a), len(b)), en caractères,
  insertion/suppression/substitution de coût 1, sensible à la casse et aux
  accents. (Diagnostic secondaire : rapidfuzz.fuzz.ratio / 100, qui est une
  distance Indel — sans substitution — et donne d'autres valeurs.)
- TF-IDF : sklearn TfidfVectorizer() avec ses paramètres par défaut,
  AJUSTÉ (fit) SUR LES DEUX SEULS TEXTES de la paire : minuscules, tokens
  = regex \\b\\w\\w+\\b (donc mots d'1 lettre comme « à », « l' », « d' » ignorés,
  ponctuation ignorée), idf lissé, pas de stop-words, pas de lemmatisation,
  norme L2. Score = cosinus entre les deux vecteurs.
- Embeddings : sentence-transformers paraphrase-multilingual-MiniLM-L12-v2,
  encode() par défaut (mean pooling du modèle), cosinus via util.cos_sim.
- NLI : MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7,
  tokenizer(premisse, hypothese), softmax sur les logits, étiquettes lues dans
  model.config.id2label. A→B = A prémisse, B hypothèse.
"""
import csv
import platform
import sys
import time
from importlib.metadata import version

T0 = time.perf_counter()

import torch
from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModelForSequenceClassification, AutoTokenizer

torch.manual_seed(0)
torch.use_deterministic_algorithms(True)

EMB_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
NLI_MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
GAP_THRESHOLD = 0.02
ENTAIL_THRESHOLD = 0.90

# ---------------------------------------------------------------- données
REF1 = "Trajet confortable pour les enfants, avec un changement à Paris."
REF2 = "Hôtel calme en centre-ville, petit-déjeuner inclus, vue sur la mer."
REF3 = "Le patient ne présente aucune contre-indication au traitement."
C1V2 = "Un trajet idéal pour les familles, avec une correspondance à Paris-Montparnasse."
C2V1 = "Établissement tranquille au cœur de Coutances, avec vue mer et formule petit-déjeuner."

# (id, référence, variante, Lev publié, TF-IDF publié, Emb publié, attendu NLI, justification)
CASES = [
    ("C1-V1", REF1, "Voyage adapté aux familles avec correspondance parisienne.",
     0.250, 0.068, 0.761, "équivalent", "paraphrase voulue (familles ≈ enfants, discutable)"),
    ("C1-V2", REF1, C1V2,
     0.425, 0.436, 0.647, "revue humaine", "ajoute un fait non sourcé (Montparnasse), « idéal » ≠ « confortable »"),
    ("C1-V3", REF1, "Réservez votre billet de train pour la Normandie dès maintenant.",
     0.172, 0.056, 0.428, "revue humaine", "hors sujet"),
    ("C2-V1", REF2, C2V1,
     0.264, 0.193, 0.479, "revue humaine", "ajoute un fait non sourcé (Coutances)"),
    ("C2-V2", REF2, "Hôtel situé en plein centre, paisible, avec panorama sur l'océan et buffet matinal.",
     0.361, 0.193, 0.859, "équivalent", "paraphrase voulue (océan ≈ mer, buffet ≈ petit-déjeuner)"),
    ("C2-V3", REF2, "Parking gratuit, accès autoroute, idéal pour les voyageurs d'affaires.",
     0.186, 0.000, 0.425, "revue humaine", "hors sujet"),
    ("C3", REF3, "Le patient présente plusieurs contre-indications au traitement.",
     0.825, 0.551, 0.456, "revue humaine", "contradiction"),
]

# Partie B : (id, variante modifiée, id du cas d'origine)
HYPOTHESES = [
    ("B1 C2-V1 sans « de Coutances »",
     "Établissement tranquille au cœur de la ville, avec vue mer et formule petit-déjeuner.", "C2-V1"),
    ("B2a C2-V1 Coutances→Cherbourg", C2V1.replace("Coutances", "Cherbourg"), "C2-V1"),
    ("B2b C2-V1 Coutances→Lyon", C2V1.replace("Coutances", "Lyon"), "C2-V1"),
    ("B3 C1-V2 sans « -Montparnasse »",
     "Un trajet idéal pour les familles, avec une correspondance à Paris.", "C1-V2"),
]

# Partie C : paires supplémentaires (id, A, B, attendu, justification)
EXTRA_PAIRS = [
    ("P1 dose", "La dose maximale est de 500 mg par jour.",
     "La dose maximale est de 1000 mg par jour.", "revue humaine", "chiffre changé, structure identique"),
    ("P2 consentement", "Le consentement du patient est obligatoire.",
     "Le consentement du patient est facultatif.", "revue humaine", "antonyme sur un seul mot"),
    ("P3 à jeun", "Le médicament doit être pris à jeun.",
     "Le médicament peut être pris pendant les repas.", "revue humaine", "contradiction implicite (à jeun ⇔ hors repas)"),
    ("M1 grossesse", "Ce médicament est contre-indiqué chez la femme enceinte.",
     "Les femmes enceintes ne doivent pas prendre ce médicament.", "équivalent",
     "[choix Claude] reformulation santé : terme technique → langage courant, ajout d'une négation qui ne change pas le sens"),
    ("M2 rétractation", "Le délai de rétractation est de quatorze jours.",
     "Le consommateur dispose de quatorze jours pour se rétracter.", "équivalent",
     "[choix Claude] reformulation juridique : nominalisation → verbe, sujet explicité"),
    ("M3 résiliation", "Le contrat peut être résilié à tout moment.",
     "Le contrat ne peut pas être résilié avant son terme.", "revue humaine",
     "[choix Claude] opposition juridique franche, vocabulaire très proche"),
    ("M4 remboursement", "Ce dispositif est remboursé par l'Assurance maladie.",
     "Ce dispositif n'est plus remboursé par l'Assurance maladie.", "revue humaine",
     "[choix Claude] négation discrète : « n'…plus » (2 mots courts) inverse le sens"),
]


# ---------------------------------------------------------------- métriques
def lev(a, b):
    return Levenshtein.normalized_similarity(a, b)


def lev_indel(a, b):
    return fuzz.ratio(a, b) / 100


def tfidf(a, b):
    m = TfidfVectorizer().fit_transform([a, b])
    return float(cosine_similarity(m[0], m[1])[0, 0])


t = time.perf_counter()
emb_model = SentenceTransformer(EMB_MODEL, device="cpu")
nli_tok = AutoTokenizer.from_pretrained(NLI_MODEL)
nli_model = AutoModelForSequenceClassification.from_pretrained(NLI_MODEL).eval()
LABELS = {i: l.lower() for i, l in nli_model.config.id2label.items()}
t_load = time.perf_counter() - t


def emb(a, b):
    e = emb_model.encode([a, b], convert_to_tensor=True)
    return float(util.cos_sim(e[0], e[1]))


@torch.no_grad()
def nli(premise, hypothesis):
    x = nli_tok(premise, hypothesis, truncation=True, return_tensors="pt")
    p = torch.softmax(nli_model(**x).logits[0], dim=-1)
    return {LABELS[i]: float(p[i]) for i in range(len(p))}


# ---------------------------------------------------------------- calculs
t = time.perf_counter()
rows = []  # une ligne CSV par mesure : partie, id, texte_a, texte_b, metrique, valeur, publie, ecart
part_a = []
for cid, a, b, p_lev, p_tf, p_emb, *_ in CASES:
    r = {"id": cid, "a": a, "b": b, "lev": lev(a, b), "lev_indel": lev_indel(a, b),
         "tfidf": tfidf(a, b), "emb": emb(a, b),
         "pub": {"lev": p_lev, "tfidf": p_tf, "emb": p_emb}}
    part_a.append(r)
    for m in ("lev", "tfidf", "emb"):
        rows.append(["A", cid, a, b, m, r[m], r["pub"][m], r[m] - r["pub"][m]])
    rows.append(["A", cid, a, b, "lev_indel_diagnostic", r["lev_indel"], "", ""])
emb_by_id = {r["id"]: r["emb"] for r in part_a}
ref_by_id = {c[0]: c[1] for c in CASES}
var_by_id = {c[0]: c[2] for c in CASES}

part_b = []
for hid, variant, orig in HYPOTHESES:
    s = emb(ref_by_id[orig], variant)
    part_b.append({"id": hid, "orig": orig, "variant": variant, "emb": s,
                   "emb_orig": emb_by_id[orig], "delta": s - emb_by_id[orig]})
    rows.append(["B", hid, ref_by_id[orig], variant, "emb", s, "", s - emb_by_id[orig]])

part_c = []
for cid, a, b, expected, why in [(c[0], c[1], c[2], c[6], c[7]) for c in CASES] + EXTRA_PAIRS:
    ab, ba = nli(a, b), nli(b, a)
    verdict = ("équivalent" if min(ab["entailment"], ba["entailment"]) >= ENTAIL_THRESHOLD
               else "revue humaine")
    part_c.append({"id": cid, "a": a, "b": b, "ab": ab, "ba": ba, "verdict": verdict,
                   "expected": expected, "why": why})
    for sens, probs in (("A→B", ab), ("B→A", ba)):
        for lab in ("entailment", "neutral", "contradiction"):
            rows.append(["C", cid, a, b, f"nli_{sens}_{lab}", probs[lab], "", ""])
    rows.append(["C", cid, a, b, "verdict_regle", verdict, expected, "OK" if verdict == expected else "ÉCART"])
t_compute = time.perf_counter() - t

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["partie", "id", "texte_a", "texte_b", "metrique", "valeur",
                "publie_ou_attendu", "ecart_ou_delta"])
    w.writerows(rows)

# ---------------------------------------------------------------- rapport
f3 = "{:.3f}".format
fs = "{:+.3f}".format
L = ["# Test de contenus IA : similarité et NLI — résultats recalculés", ""]
L += ["Tous les chiffres ci-dessous sont produits par `run.py` (affichage arrondi à 3 décimales "
      "par le code ; valeurs pleine précision dans `results.csv`).", ""]

L += ["## Méthode de calcul", "",
      "- **Levenshtein** : `rapidfuzz.distance.Levenshtein.normalized_similarity(a, b)` = "
      "1 − distance / max(len(a), len(b)), en caractères, sur le texte brut (casse, accents et "
      "ponctuation conservés). Colonne « Indel » = `fuzz.ratio/100` (distance sans substitution), "
      "donnée à titre de diagnostic seulement.",
      "- **TF-IDF** : `TfidfVectorizer()` par défaut, ajusté sur les **deux seuls textes** de la "
      "paire ; minuscules, tokens `\\b\\w\\w+\\b` (mots d'une lettre et ponctuation ignorés), idf "
      "lissé, sans stop-words ni lemmatisation, norme L2 ; cosinus.",
      f"- **Embeddings** : `{EMB_MODEL}`, `encode()` par défaut, cosinus.",
      f"- **NLI** : `{NLI_MODEL}`, softmax sur les logits, étiquettes lues dans "
      f"`model.config.id2label` = `{nli_model.config.id2label}`. A→B : A prémisse, B hypothèse.",
      ""]

L += ["## Partie A — valeurs publiées vs recalculées", "",
      f"Écart = recalculé − publié. ⚠️ = |écart| > {GAP_THRESHOLD}.", "",
      "| Cas | Métrique | Publié | Recalculé | Écart | |",
      "|---|---|---|---|---|---|"]
gaps = []
for r in part_a:
    for m, name in (("lev", "Levenshtein"), ("tfidf", "TF-IDF"), ("emb", "Embeddings")):
        d = r[m] - r["pub"][m]
        flag = abs(d) > GAP_THRESHOLD
        if flag:
            gaps.append((r["id"], name, r["pub"][m], r[m], d))
        L.append(f"| {r['id']} | {name} | {f3(r['pub'][m])} | {f3(r[m])} | {fs(d)} | {'⚠️' if flag else ''} |")
L += ["", "Diagnostic Levenshtein (deux définitions de « ratio » chez rapidfuzz) :", "",
      "| Cas | Publié | Levenshtein normalisé | Indel (`fuzz.ratio/100`) |", "|---|---|---|---|"]
for r in part_a:
    L.append(f"| {r['id']} | {f3(r['pub']['lev'])} | {f3(r['lev'])} | {f3(r['lev_indel'])} |")

# Classement par embeddings : l'ordre relatif est ce qui porte le message de l'article
L += ["", "Ordre des variantes par score d'embeddings (publié vs recalculé) :", ""]
for case in ("C1", "C2"):
    ids = [r for r in part_a if r["id"].startswith(case)]
    pub = " > ".join(r["id"] for r in sorted(ids, key=lambda r: -r["pub"]["emb"]))
    new = " > ".join(r["id"] for r in sorted(ids, key=lambda r: -r["emb"]))
    L.append(f"- {case} : publié `{pub}` — recalculé `{new}`{'' if pub == new else ' — **ordre différent**'}")

L += ["", "### Écarts > 0.02 avec les valeurs publiées", ""]
if gaps:
    L += [f"{len(gaps)} écart(s) sur {3 * len(part_a)} valeurs :", ""]
    L += [f"- {cid} {name} : publié {f3(p)}, recalculé {f3(v)} (écart {fs(d)})" for cid, name, p, v, d in gaps]
    worst = max(gaps, key=lambda g: abs(g[4]))
    L += ["", f"Métriques concernées : {', '.join(sorted({g[1] for g in gaps}))}. Plus grand écart : "
          f"{worst[0]} {worst[1]} ({fs(worst[4])})."]
else:
    L.append("Aucun.")

L += ["", "## Partie B — hypothèses (embeddings seulement)", "",
      "| Variante testée | Score | Score de la variante d'origine | Δ |", "|---|---|---|---|"]
for r in part_b:
    L.append(f"| {r['id']} : « {r['variant']} » | {f3(r['emb'])} | {f3(r['emb_orig'])} ({r['orig']}) | {fs(r['delta'])} |")

L += ["", "## Partie C — NLI dans les deux sens", "",
      f"Règle : « équivalent » si entailment ≥ {ENTAIL_THRESHOLD:.2f} dans les deux sens, sinon « revue humaine ».", "",
      "| Paire | A→B E / N / C | B→A E / N / C | Verdict règle | Attendu | |",
      "|---|---|---|---|---|---|"]
def enc(p):
    return f"{f3(p['entailment'])} / {f3(p['neutral'])} / {f3(p['contradiction'])}"
for r in part_c:
    ok = r["verdict"] == r["expected"]
    L.append(f"| {r['id']} | {enc(r['ab'])} | {enc(r['ba'])} | {r['verdict']} | {r['expected']} | {'✅' if ok else '❌'} |")
n_ok = sum(r["verdict"] == r["expected"] for r in part_c)
L += ["", f"Accord règle / attendu : {n_ok} sur {len(part_c)}.", "",
      "Textes et justification de l'attendu :", ""]
for r in part_c:
    L.append(f"- **{r['id']}** — A : « {r['a']} » / B : « {r['b']} » — {r['why']}")
L += ["", "Paires M1–M4 (choisies par Claude) : deux reformulations équivalentes (santé, juridique) "
      "qui changent la structure de phrase sans changer le sens, pour vérifier que la règle "
      "n'envoie pas tout en revue ; une opposition juridique franche à vocabulaire partagé ; une "
      "négation discrète (« n'…plus ») qui ne modifie que deux mots courts — le cas où les métriques "
      "de surface sont les plus trompeuses.", ""]

# Indicateurs calculés pour la section Limites
asym = max(part_c, key=lambda r: abs(r["ab"]["entailment"] - r["ba"]["entailment"]))
c3 = next(r for r in part_a if r["id"] == "C3")
m4 = next(r for r in part_c if r["id"].startswith("M4"))
def one_way(k):
    return ", ".join(r["id"] for r in part_c
                     if (r[k]["entailment"] >= ENTAIL_THRESHOLD) != (r["verdict"] == "équivalent"))
m4_surface = (lev(m4["a"], m4["b"]), tfidf(m4["a"], m4["b"]), emb(m4["a"], m4["b"]))

L += ["## Limites constatées", "",
      "- **« Ratio Levenshtein » est ambigu** : rapidfuzz expose au moins deux normalisations "
      "(`Levenshtein.normalized_similarity` et `fuzz.ratio`, qui est en fait une distance Indel). "
      "Elles donnent des valeurs différentes (tableau diagnostic ci-dessus) ; il faut nommer la "
      "fonction exacte dans l'article.",
      "- **TF-IDF sur deux phrases** : l'idf est appris sur 2 documents, donc tout mot présent dans "
      "les deux reçoit le poids minimal et le score dépend fortement de la tokenisation (mots d'une "
      "lettre supprimés, « l'océan » → « océan », « Paris-Montparnasse » → 2 tokens) et du choix "
      "du corpus d'ajustement. Un autre corpus ou des stop-words donneraient d'autres valeurs.",
      "- **Embeddings** : le score dépend du modèle exact, de sa version et du pooling ; le cosinus "
      "n'a pas d'échelle absolue (un « bon » score dans un cas peut être inférieur à un « mauvais » "
      "dans un autre).",
      f"- **Les métriques de surface et d'embeddings ne voient pas la négation** : sur C3 "
      f"(contradiction), Lev {f3(c3['lev'])}, TF-IDF {f3(c3['tfidf'])}, Emb {f3(c3['emb'])} ; sur M4 "
      f"(« n'est plus remboursé »), Lev {f3(m4_surface[0])}, TF-IDF {f3(m4_surface[1])}, "
      f"Emb {f3(m4_surface[2])}.",
      f"- **La NLI est asymétrique** : plus grand écart d'entailment entre les deux sens sur "
      f"{asym['id']} (A→B {f3(asym['ab']['entailment'])}, B→A {f3(asym['ba']['entailment'])}). "
      f"Avec un seul sens, la règle aurait changé de verdict sur : A→B seul {one_way('ab') or 'aucune'} ; "
      f"B→A seul {one_way('ba') or 'aucune'}.",
      f"- **Seuil de {ENTAIL_THRESHOLD:.2f}** : choisi a priori, non calibré ; les verdicts proches "
      "du seuil sont instables d'une version de modèle à l'autre.",
      "- **« Résultat attendu »** : c'est mon jugement de relecteur (colonne justification), pas une "
      "vérité terrain ; pour C1-V1 en particulier (« familles » vs « enfants »), l'équivalence se "
      "discute.",
      f"- **Échantillon minuscule** ({len(part_a) + len(part_b) + len(EXTRA_PAIRS)} paires au total) : illustre des comportements, ne mesure "
      "aucun taux d'erreur.",
      "- **Choix pris par simplicité** : textes non normalisés pour Levenshtein et embeddings ; NLI "
      "sans troncature effective (phrases courtes) ; aucune graine n'influe sur l'inférence (modèles "
      "en mode eval, CPU, algorithmes déterministes forcés).",
      ""]

pkgs = ["torch", "transformers", "sentence-transformers", "sentencepiece", "scikit-learn",
        "rapidfuzz", "tokenizers", "huggingface_hub", "numpy", "protobuf"]
t_total = time.perf_counter() - T0
L += ["## Environnement et temps d'exécution", "",
      f"- Python {sys.version.split()[0]} ({platform.platform()}, {platform.processor() or platform.machine()})",
      *[f"- {p} {version(p)}" for p in pkgs],
      f"- Threads torch : {torch.get_num_threads()}",
      f"- Chargement des modèles : {t_load:.1f} s ; calculs : {t_compute:.1f} s ; "
      f"total (imports compris) : {t_total:.1f} s",
      "- Premier lancement : téléchargement des modèles depuis Hugging Face (non compté s'ils sont en cache).",
      ""]

report = "\n".join(L)
with open("rapport.md", "w", encoding="utf-8") as f:
    f.write(report)
print(report)
