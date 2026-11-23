# La discipline de preuve d'un rapport d'anomalie

La règle : **chaque affirmation du rapport doit être lisible dans la preuve jointe.**

Elle paraît évidente. Elle ne l'est pas, parce qu'un rapport d'anomalie est exactement le format
où il est le plus tentant de compléter une observation par une déduction — et où la déduction se
lit comme une observation.

## Les quatre glissements, du plus fréquent au plus coûteux

**1. La cause déduite présentée comme constatée.**

> ❌ « Le serveur ne valide pas le paramètre. »
> ✅ « La requête `DELETE /posts/1?_dependent=comments` renvoie `200` et les deux commentaires
> sont toujours présents dans `GET /comments`. Cause : non établie. »

La première phrase peut être vraie. Rien dans la trace ne le dit. Et si elle est fausse, le
correcteur cherche au mauvais endroit — avec la confiance que lui donne un rapport affirmatif.

**2. La généralisation à partir d'un cas.**

> ❌ « La suppression en cascade est cassée. »
> ✅ « `_dependent=comments` sur `/posts/1` ne supprime pas les commentaires. Non vérifié sur
> d'autres ressources. »

Un cas observé est un cas. La ligne `Scope` du rapport existe pour dire jusqu'où on a regardé,
donc aussi où on n'a pas regardé.

**3. La sévérité sans conséquence lisible.**

Une sévérité est une affirmation sur les conséquences. « Critique » demande qu'on puisse lire,
dans la preuve, la donnée perdue ou la frontière d'autorisation franchie. Sinon c'est une opinion
avec un mot fort.

**4. Le correctif suggéré.**

Suggérer un correctif, c'est affirmer une cause. Si la cause n'est pas observée, il n'y a pas de
correctif à suggérer — et un correctif proposé par une machine qui n'a pas lu le code est une
invitation à casser autre chose.

## Ce que la règle n'interdit pas

Elle interdit de **deviner**, pas de **regarder**. Ouvrir le code, lire la ligne fautive et la
citer, c'est observer : le rapport peut alors nommer la cause, et il doit citer la ligne.

C'est exactement ce qui sépare le ticket humain #1551 du rapport QAIA sur le même défaut
(`verified-against-1551.md`) : l'humain a ouvert `src/app.ts`, donc il avait le droit de nommer
la cause, et il l'a nommée juste. La campagne QAIA s'interdisait de lire le code pour des raisons
de protocole, donc elle a écrit « non établie ». Les deux respectent la règle.

## Le test à s'appliquer avant d'envoyer

Pour chaque phrase du rapport : **quel fichier joint la contient ?** Si aucun, deux issues, et
seulement deux — supprimer la phrase, ou aller chercher la preuve.
