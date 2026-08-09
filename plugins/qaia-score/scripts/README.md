# Les scoreurs, livres

Trois programmes, figes, que la skill correspondante **lance** au lieu de les redecrire.

| Fichier | Ce qu'il note | Dependances |
|---|---|---|
| `structural_score.py` | la qualite d'un cahier de test Gherkin | bibliotheque standard seule |
| `automation_score.py` | la substance d'une suite Playwright (piste statique + mutation) | bibliotheque standard seule |
| `spec_suite_drift.py` | l'ecart entre une specification OpenAPI et la suite qui la teste | **PyYAML** |

## Pourquoi ils sont ici

Jusqu'au 2026-08-09, ces trois skills demandaient au modele de **materialiser l'algorithme en
session** depuis leur propre prose, puis de le lancer. La promesse mise en avant par le projet --
« une note deterministe, pas une auto-notation par un LLM » -- tenait donc a l'interieur du depot
QAIA, ou ces fichiers sont figes et executes par une CI, et s'amollissait a la frontiere de
livraison : ce que l'utilisateur recevait etait un modele re-derivant ~300 lignes d'expressions
regulieres a chaque invocation. Deux passages sur le meme fichier pouvaient legitimement diverger.

Une revue independante l'a releve ; le prix a d'abord ete simplement ecrit, puis la decision a
ete prise de le supprimer plutot que de le documenter.

## Ce que ca ne change pas

**Rien ne s'execute tout seul.** Aucun hook, aucun agent, aucun serveur MCP, aucun script
d'installation. Ces fichiers sont lus et lances par Claude quand vous invoquez la skill, avec vos
droits, dans votre session -- exactement comme avant. La difference est que le code est
maintenant fige et lisible plutot que reecrit de memoire : vous pouvez le diffier, l'epingler,
refuser de le lancer.

## Ce que ca change

La formule « 100 % skills Markdown » n'est plus vraie et a ete retiree partout ou elle figurait.

## Ces fichiers sont des copies

Les originaux vivent dans [`eval/tools/`](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/) du depot QAIA, ou une CI les eprouve a chaque commit par
injection de faute. Les copies ci-dessus sont **identiques a l'octet pres**, et
[`eval/tools/check_repo_structure.py`](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/check_repo_structure.py) le verifie a chaque passage de la CI : si l'original bouge
sans que la copie suive, la CI echoue. Une copie sans rien qui la surveille est une copie qui
cesse silencieusement de correspondre -- c'est la faute que ce depot a corrigee quatre fois le
2026-08-09, et elle ne sera pas reintroduite par la porte de service.

## Lancer a la main

```bash
python structural_score.py --batch <dossier-de-cahiers>
python automation_score.py --tests-dir <suite> --testbook <cahier> --skip-mutation
python spec_suite_drift.py --spec <openapi.yml> --tests-dir <suite>
```

Chacun sort du JSON sur la sortie standard et rend 1 quand un constat est bloquant.
