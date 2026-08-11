# Les mêmes cibles, avec et sans la méthode

**Expérience témoin, 2026-08-11.** Trois sites réels. Deux moitiés. La première écrit des user
stories et des critères d'acceptation par rétro-ingénierie, **sans ouvrir une seule skill**. La
seconde reprend les mêmes cibles et les mêmes critères, **avec la méthode**.

C'est la première mesure comparative de ce projet. Jusqu'ici il avait des preuves de *capacité* —
deux défauts corrigés en amont chez `typicode/json-server` — et aucune preuve de **différence**.

---

## Le résultat en une ligne

> **La moitié sans méthode s'est trompée sur deux critères d'acceptation, et les deux étaient
> exactement ceux qu'elle avait signalés comme non vérifiés. La méthode est allée voir.**

| | Sans méthode | Avec méthode |
|---|---|---|
| Conditions de test | 35 critères | **87 conditions** |
| Opérations API couvertes | 3 sur 8 | **8 sur 8** |
| Questions ouvertes posées | 0 | **27** |
| Défauts du *contrat* API | 0 | **7** |
| Critères faux détectés | — | **2** |
| Défauts du dépôt QAIA lui-même | — | **6**, tous corrigés le jour même |

---

## Les deux critères faux, et pourquoi ça compte

La moitié sans méthode avait écrit, en toute bonne foi :

> **AC7** — *« Un panier vide ne permet pas d'atteindre la confirmation. »*
> **AC6** — *« Après un refus, le mot de passe est vidé. »*

Elle les avait marqués « non vérifiés ». **Les deux sont faux**, vérifiés par exécution :

```
panier : 0 article
→ tunnel complet → Item total: $0 · Total: $0.00
→ « Thank you for your order! »

mot de passe après un refus → "WRONGPASS" toujours dans le champ
```

Ce n'est pas une question d'intelligence : c'est une question de **méthode qui oblige à aller
voir**. Un critère non vérifié ressemble, dans un document, exactement à un critère vérifié.

## Les quatre profils que personne n'avait regardés

La page d'accueil de SauceDemo **publie six identifiants**. La moitié sans méthode en a utilisé
deux. Les 20 critères qu'elle a écrits ne mentionnent jamais les quatre autres.

C'est là qu'étaient les vrais défauts :

| Profil | Ce que la méthode a trouvé |
|---|---|
| `problem_user` | **Ne peut pas commander du tout** : le lien d'un article ouvre un *autre* article, le champ Nom du tunnel refuse la saisie |
| `visual_user` | **$54.97 sur la vignette, $29.99 sur la fiche et au panier** — trois prix pour un article |
| `error_user` | Le bouton `Finish` est sans effet |
| `performance_glitch_user` | 5 063 ms contre ~50 ms |

Ils ne sont pas sortis d'une intuition. Ils sont sortis d'un **motif nommé** de la checklist de
couverture : *« comportement conditionnel — table de décision sur les axes de variation »*. L'axe
de variation de cette application est publié sur sa page d'accueil sous forme de six rôles.

Trois autres défauts de la même famille : le tri ne survit à aucune navigation ; le retour arrière
après confirmation permet une **seconde commande** ; et « obligatoire » accepte trois espaces.

## Sur l'API : sept défauts qu'aucune requête ne révèle

La moitié sans méthode a trouvé quatre anomalies **en envoyant des requêtes**. Bien.

La moitié avec méthode en a trouvé sept de plus **en lisant le contrat contre lui-même** — la
passe des quatre contradictions, appliquée systématiquement plutôt que quand on y pense :

- **`Ping` et `DeleteBooking` déclarent `Success 200` avec un exemple qui montre `201 Created`.**
  Le document se contredit en trois lignes.
- **Les huit opérations documentées ne déclarent aucun code d'erreur.** Que des `Success 200`.
  Tout le comportement défensif de cette API est hors contrat.
- `id` est typé `String` par une opération et `Number` par trois autres.

Et la correction la plus utile de l'expérience porte sur la moitié témoin : **sa colonne
« Documenté » était fausse dans trois cellules, dans les deux sens.** Elle avait mélangé ce que la
spécification *promet* et ce que le service *fait* — la règle que la méthode énonce en première
page et qu'elle n'avait pas lue.

## Sur la performance et la sécurité : le résultat est un refus

Aucune charge, aucun scan, aucun fuzzing. Pas par prudence vague : **le catalogue du dépôt marque
SauceDemo `Security ❌ / Perf ❌`**, restful-booker est un bac à sable Heroku partagé, et le
troisième site est celui d'une collectivité territoriale.

Ce qu'une **requête ordinaire** suffit à établir a quand même été rendu : `restful-booker` répond
`200 OK` en **HTTP clair, sans redirection**, alors que `POST /auth` transporte des identifiants
dans le corps. Un seul en-tête de sécurité sur 18 cases examinées. Trois certificats TLS valides —
et c'est un résultat.

**Aucune vulnérabilité établie sur aucune cible.** Écrit comme un résultat, pas comme un silence.

---

## Ce que l'expérience a coûté au dépôt QAIA — six défauts chez nous

Une méthode qu'on applique pour de bon renvoie ses propres factures. Tous corrigés le jour même :

1. **`testbook-generate` contenait deux fois son contrat d'émission**, divergents sur la règle que
   le fichier lui-même appelle *« the most repeated failure of the four »*. Le second exemplaire se
   terminait par *« not to become a second source of truth »*.
2. **`perf-check` énonçait son interdit en avant-dernière ligne** d'un fichier de 76.
   « Un agent qui lit en flux a déjà conçu le run quand il rencontre l'interdit. »
3. **`openapi-ingest` demandait d'écrire un fichier sans en donner la forme.** Le schéma ne vivait
   que dans le code d'un contrôle qu'un installeur ne voit jamais.
4. **Notre lint anti-complaisance avait un angle mort** : ses neuf classes regardent l'assertion,
   aucune ne regarde si la **fixture invalide l'assertion**. Deux tests verts qui ne prouvaient
   rien, trouvés en exécutant. C'est devenu la classe D10.
5. **`automate` ne couvrait pas le cas « pas de cahier du tout »**, le plus courant sur une cible
   que personne n'a encore conçue.
6. **Le contrat de sortie est par user story** ; un run réel en couvrait six sur deux cibles.

---

## Ce que cette expérience ne prouve pas

**Les deux moitiés sortent de la même partie.** Elle mesure ce que la méthode ajoute à *cette*
rédaction-là, pas à celle d'un testeur humain qui aurait, lui, peut-être pensé aux quatre profils
tout seul. Un vrai témoin demanderait deux personnes.

**Les cibles sont des bancs d'essai.** SauceDemo et restful-booker sont conçus pour être testés ;
leurs défauts sont partiellement du matériel pédagogique. Le troisième site n'a été que lu.

**Rien ici ne dit que le cahier produit sert à quelqu'un.** C'est la question que ce projet n'a
toujours pas posée à un humain extérieur, et aucune ligne de ce document n'y répond.

---

## Les fichiers

| | |
|---|---|
| [`00-BASELINE-sans-skills.md`](00-BASELINE-sans-skills.md) | La moitié témoin : 8 US, 35 critères, ses trois faiblesses écrites par elle-même |
| [`10-saucedemo-03-design.md`](10-saucedemo-03-design.md) · [`11-saucedemo.feature`](11-saucedemo.feature) | 45 conditions, 39 scénarios |
| [`20-restfulbooker-03-design.md`](20-restfulbooker-03-design.md) · [`21-restfulbooker.feature`](21-restfulbooker.feature) | 42 conditions, 38 scénarios, 8 opérations sur 8 |
| [`30-perf-secu-conception.md`](30-perf-secu-conception.md) · [`31-perf-secu-observations.md`](31-perf-secu-observations.md) | Conçu, non exécuté — et pourquoi |
| [`automation/`](automation/) | La suite générée, exécutée : 76 tests, `junit.xml` conservé |
| [`upstream/`](upstream/) | Les signalements préparés pour le mainteneur de restful-booker |
| [`sources/`](sources/) | La documentation d'API gelée, avec son sha256 |
