# Écrire l'anomalie dans le format du tracker

Le contenu ne change pas d'un tracker à l'autre. Seul le contenant change. Ce qui suit dit
où va chaque champ du rapport, et ce qu'il ne faut pas perdre au passage.

## Le rapport, sous sa forme neutre

```
Titre      une ligne : quelle promesse n'est pas tenue, où
Sévérité   + une phrase d'argument
Version    l'identifiant exact du SUT (commit, tag, build)
Scénario   @QAIA-xxx, et le .feature où il vit
Promesse   citation verbatim de l'exigence + sa position
Étapes     reproduction minimale, numérotée, en termes d'utilisateur ou de client
Attendu    déduit de la promesse
Obtenu     relevé de l'exécution, cité de la preuve
Preuves    fichiers nommés, chacun référencé plus haut
Cause      « non établie » sauf observation. Si observée : dire ce qui a été observé.
Portée     ce qui a été vérifié par ailleurs et trouvé intact
```

## GitHub Issues

Titre → titre. Le corps prend tout le reste en Markdown, dans l'ordre ci-dessus. Les preuves
s'attachent par glisser-déposer ; **référencer chaque pièce par son nom dans le texte**, sinon
personne ne fait le lien entre la capture en bas et l'affirmation en haut.

Sévérité et portée n'ont pas de champ dédié : les mettre en tête du corps, pas en labels — un
label se change sans laisser de trace, une phrase argumentée non.

Le scénario `@QAIA-xxx` va dans le corps **et** dans le titre si le projet accepte les préfixes :
c'est ce qui permet de retrouver l'anomalie depuis le cahier de tests des mois plus tard.

## Jira

| Champ du rapport | Champ Jira |
|---|---|
| Titre | Summary |
| Sévérité + argument | champ `Severity` s'il existe, sinon en tête de Description |
| Version | `Affects Version/s` — le champ existe, s'en servir |
| Étapes | `Steps to Reproduce` si le type Bug l'a, sinon Description |
| Attendu / Obtenu | champs dédiés s'ils existent, sinon Description |
| Scénario `@QAIA-xxx` | un label, **et** en clair dans la Description |
| Preuves | pièces jointes |

Piège classique : Jira confond volontiers `Priority` et `Severity`. Ne pas remplir l'un à la place
de l'autre. La sévérité est une conséquence, la priorité est une décision d'ordonnancement — et
c'est le chef de projet qui décide de la seconde, pas le testeur.

## Azure DevOps

Type `Bug`. `Repro Steps` prend étapes, attendu et obtenu. `System Info` prend la version du SUT.
La sévérité a son champ. Le scénario va dans les Tags.

## Ce qui ne doit jamais être perdu à la traduction

Trois éléments disparaissent systématiquement quand on adapte un rapport à un formulaire :

1. **La citation verbatim de la promesse.** Sans elle, la discussion devient « c'est un bug » /
   « c'est le comportement attendu », et elle se perd.
2. **La ligne `Cause : non établie`.** Beaucoup de formulaires n'ont pas de champ pour ça, et
   l'absence de cause se lit alors comme un oubli plutôt que comme une position tenue.
3. **La ligne `Portée`.** C'est elle qui dit au correcteur ce qui n'a *pas* été vérifié.

Quand le formulaire n'a pas de champ, ces trois éléments vont en tête de la description. Jamais à
la fin : personne ne lit la fin d'une anomalie.
