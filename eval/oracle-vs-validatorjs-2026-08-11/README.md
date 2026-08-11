# Notre oracle contre validator.js — zéro défaut chez eux, un défaut sérieux chez nous

**2026-08-11.** Cible : [`validatorjs/validator.js`](https://github.com/validatorjs/validator.js)
— 23 740 étoiles, poussé trois jours avant l'exercice. Choisi pour une raison précise : il
implémente **exactement** les standards que notre bibliothèque d'oracles encode (Luhn, IBAN
mod-97, ISO 3166, ISO 4217, RFC 5322). On ne le teste donc pas contre lui-même : contre une
vérité **calculée ou gelée**.

C'était le protocole qui a produit le seul effet externe de ce projet — la campagne json-server.

## Résultat

**Zéro défaut neuf.** Les treize écarts de la première passe sont tous expliqués :

| Écart apparent | Ce que la vérification a montré |
|---|---|
| 12 caractères de contrôle acceptés | **Défaut de NOTRE corpus**, pas du leur — voir ci-dessous |
| `test@io` refusé | `require_tld: true` par défaut, **documenté** |
| `XCG` et `ZWG` refusés (ISO 4217) | Vrais codes ISO — mais **PR #2842 déjà ouverte** en amont |

Luhn : 10 cas, **0 écart**. IBAN mod-97 : 6 cas, **0 écart**. ISO 3166 : 498 codes, **0 écart**.

## Le vrai défaut, et il est à nous

`eval/oracles-2026-08-09/rfc5322-isemail.json` — le corpus canonique que `oracle-generate`
recommande *« quand plus d'une poignée de cas est nécessaire »* — stocke les caractères de
contrôle sous forme d'**images** : le bloc Unicode `U+2400–243F` (`␀` SYMBOL FOR NULL, `␊` FOR
LINE FEED, `␍` FOR CARRIAGE RETURN, `␇` FOR BELL).

La substitution vient du XML source, où un caractère de contrôle ne peut pas s'écrire
littéralement. Nous l'avons gelé tel quel.

**Conséquence mesurée** : un validateur voit un caractère **imprimable**, l'accepte — et il a
raison. Le corpus attend un refus. Douze faux constats, dont l'un aurait été spectaculaire à
publier : *« validator.js accepte les injections d'en-tête CRLF »*. Sonde avec de **vrais**
caractères de contrôle :

```
isEmail("test@iana.org\r\n")                        -> false
isEmail("victim@iana.org\r\nBcc: attacker@evil.com") -> false
isEmail("@iana.org")                          -> false
```

**Tous refusés.** L'accusation était fausse dans les onze autres cas de la même façon.

**37 cas sur 163 — 23 % du corpus — sont concernés.** Ils portent désormais `_unusable` et ne
peuvent plus servir de verdict. Le reste du corpus tient.

### Pourquoi aucun contrôle ne l'avait vu

`check_oracle_library.py` déclare explicitement ne pas couvrir RFC 5322 : *« une lecture de
grammaire »*, hors de son périmètre de « ce qui est calculable ». L'angle mort était **assumé et
écrit** — ce qui est honnête, et ne rendait pas le corpus moins faux.

Mais la substitution, elle, **est calculable** : c'est une plage de points de code. Le contrôle la
vérifie désormais, et il est éprouvé dans les deux sens — retirer un seul drapeau `_unusable` le
fait passer au rouge.

## Ce que cet exercice a réellement coûté et rapporté

| | |
|---|---|
| Défauts trouvés chez la cible | **0** |
| Signalements évités | **13** — dont 12 qui auraient été publiés sous une bannière « faille de sécurité » |
| Défauts trouvés chez nous | **1**, touchant 23 % d'un corpus livré aux utilisateurs |
| Contrôles ajoutés | 1, prouvé rouge |

**Un utilisateur d'`oracle-generate` qui aurait éprouvé son validateur d'e-mails avec ce corpus
aurait obtenu les mêmes douze faux constats — et rien dans nos outils ne l'aurait averti.** C'est
le pire défaut qu'une bibliothèque d'oracles puisse porter : une erreur qui **emprunte l'autorité
d'une norme**, exactement ce que l'en-tête de `check_oracle_library.py` désigne comme le pire cas.

## Relancer

```bash
cd eval/oracle-vs-validatorjs-2026-08-11 && npm install && node probe.js
```

Sortie brute conservée : [`resultats.txt`](resultats.txt).

## La leçon, et c'est la deuxième fois dans la même journée

Première passe : treize défauts. Après vérification : zéro. Deux heures plus tôt, sur
restful-booker : trois candidats, un publiable — et celui que j'avais annoncé « vérifié » était
le premier à tomber.

**Le rapport entre constats bruts et constats publiables sur cette journée est de 16 contre 1.**
Ce n'est pas un accident de méthode, c'est le régime normal — et c'est précisément le chiffre que
la passe de réfutation de ce dépôt existe pour produire : *91 constats faux contre 2 confirmés*.

Ce qui a tenu ici n'est aucun contrôle automatique. C'est d'avoir refait l'expérience avec les
vrais octets au lieu de croire le corpus.

---

# Seconde attaque : le code récent, et la même conclusion

Après zéro défaut sur le cœur (Luhn, mod-97, ISO), j'ai visé ce qui est statistiquement plus
fragile : **le code ajouté récemment et les combinaisons d'options**. Cibles tirées du journal
des commits — `isTaxID en-IN` (ajouté **une semaine** avant), `isISO31661` Kosovo (février),
`isUUID` option `loose`, `isJSON` « allow any valid JSON value », six locales de codes postaux.

**Zéro défaut, encore.** Et chaque écart apparent s'explique :

| Écart apparent | Explication |
|---|---|
| `isJSON("null")` = false | `allow_primitives: false` **par défaut**, documenté |
| `isJSON("1", {allow_primitives:true})` = false | la doc énumère *'true', 'false' et 'null'* — pas les nombres. `allow_any_value` existe pour ça, **documenté et livré** |
| `isTaxID(..., 'en-IN')` lève | fonctionnalité **non encore publiée** : absente de 13.15.35 |
| Kosovo `XK` refusé | conforme à notre registre gelé |
| 34 « écarts » isJson | **mon erreur** : l'API est `isJSON`, pas `isJson` |

`isUUID` (9 cas, dont version et variante invalides), codes postaux AR/JO/MC/BD/PK (14 cas) :
**aucun écart**.

## Pourquoi on ne trouve rien, et ce n'est pas la méthode

**J'ai choisi la mauvaise classe de cible, et je l'ai choisie parce qu'elle était facile à
lancer.** Trois raisons, dans l'ordre d'importance :

1. **Une fonction pure implémentant une norme publiée, dans une bibliothèque à 23 000 étoiles,
   est le code le plus vérifié de son écosystème.** Mes cas sont exactement ceux que sa suite de
   tests couvre depuis dix ans.
2. **Notre avantage ne s'y applique pas.** Ce que QAIA fait mieux qu'un test ordinaire, c'est
   remonter l'ambiguïté d'une **exigence**, dériver depuis un **contrat en prose**, et attraper
   la **dérive doc/implémentation**. La spécification d'une fonction pure est une norme publiée :
   pas d'ambiguïté à remonter, pas de prose qui dérive.
3. **Les défauts se concentrent où il y a de l'état, de la concurrence, de l'intégration et de la
   configuration.** Un validateur n'a aucun des quatre.

**Ce qui a marché, les deux fois, avait la forme inverse.** Le défaut json-server : un serveur
**avec état**, et un écart d'un caractère entre la prose du README et l'implémentation. Le défaut
du site QAIA : une **incohérence entre trois artefacts** que personne ne lit ensemble.

**Conclusion opérationnelle** : cesser de sonder des bibliothèques. La cible qui vaut le
déplacement est une **application avec état, auto-hébergée, dont la documentation promet un
comportement** — la forme exacte de la campagne json-server, la seule qui ait jamais produit un
effet externe ici.
