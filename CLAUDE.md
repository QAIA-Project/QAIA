# Instructions pour Claude — QAIA

## Toujours vérifier la CI après un `git push` vers `main`

Trouvé le 2026-07-30 : le job "Lint Gherkin features" était cassé en silence depuis plusieurs
commits (dossiers de fixtures ajoutés sans mettre à jour le scope du linter), jamais détecté
parce qu'aucune session n'avait revérifié l'état de la CI après avoir poussé.

**Règle** : après tout `git push` sur `main` (ou toute branche avec CI), attendre que le
workflow associé se termine et vérifier son statut avant de considérer la tâche terminée —
ne jamais supposer que la CI passe simplement parce que le push a réussi localement.

**Automatisé depuis le 2026-07-30** : un hook `PostToolUse` (`.claude/settings.json` +
`.claude/hooks/check-ci-after-push.sh`) se déclenche automatiquement après tout `git push`,
poll la CI en arrière-plan (jusqu'à 180s) et réveille l'agent uniquement si le run échoue,
reste bloqué, ou est introuvable — silencieux sur un succès. Nécessite
`GITHUB_PERSONAL_ACCESS_TOKEN` dans l'environnement (déjà présent dans les settings globaux
du fondateur) ; s'auto-désactive proprement si absent. Ne dispense pas de vérifier
manuellement (méthode ci-dessous) si le hook est indisponible ou désactivé.

Méthode manuelle de repli (pas de `gh` CLI disponible dans cet environnement) :
```bash
# Récupérer le run déclenché par le SHA qu'on vient de pousher
curl -sL -H "Authorization: Bearer $GITHUB_PERSONAL_ACCESS_TOKEN" \
  "https://api.github.com/repos/QAIA-Project/QAIA/actions/runs?head_sha=<SHA>"

# Une fois le run identifié, poller son statut (conclusion "success"/"failure")
curl -sL -H "Authorization: Bearer $GITHUB_PERSONAL_ACCESS_TOKEN" \
  "https://api.github.com/repos/QAIA-Project/QAIA/actions/runs/<RUN_ID>"

# Si échec, récupérer les logs du job pour diagnostiquer avant de clore la tâche :
curl -sL -H "Authorization: Bearer $GITHUB_PERSONAL_ACCESS_TOKEN" \
  "https://api.github.com/repos/QAIA-Project/QAIA/actions/jobs/<JOB_ID>/logs"
```

Si le run met du temps à démarrer/finir, utiliser `Monitor` (poll en arrière-plan, une
notification par événement) plutôt que d'attendre en bloquant le tour — ou signaler
explicitement à l'utilisateur qu'on n'a pas encore confirmé le vert avant de clore.

## Ne jamais faire passer du Markdown par le shell

Trouvé le 2026-08-08, **six fois dans la même session** : un commentaire GitHub publié amputé de
toutes ses références, parce que les backticks avaient été interprétés par le shell qui passait le
texte en ligne (`python -c "..."`, heredoc non quoté). À chaque fois la même cause, à chaque fois
le remède noté dans le commentaire correctif — et à chaque fois la récidive dans l'heure.

**Règle** : tout corps de commentaire, d'issue ou de PR s'écrit **dans un fichier**, jamais dans une
chaîne passée à Bash. Un rappel écrit n'a jamais tenu plus de quelques heures ; l'outil, lui,
supprime l'occasion.

```bash
python eval/tools/gh_comment.py --file corps.md --issue 88
python eval/tools/gh_comment.py --file corps.md --comment-id 5228083941
python eval/tools/gh_comment.py --file corps.md --new-issue --title-file titre.txt
```

**Le titre aussi passe par un fichier** (trouvé le 2026-11-23) : trois titres accentués passés en
`--title` depuis Git Bash sont arrivés sur GitHub encodés deux fois (« reÃ§oit »), sans que la
vérification le voie — elle comparait au même argument déjà abîmé. L'outil refuse désormais un
titre qui porte cette signature ; `--title-file` l'évite à la source.

L'outil relit le commentaire **depuis l'API** après publication et le compare au fichier : si quoi
que ce soit a été mangé en route, il échoue en montrant la première ligne divergente, au moment où
ça arrive. Éprouvé dans les deux sens (une faute injectée reproduisant l'effet du shell est bien
détectée, 231 caractères manquants signalés à la ligne 1).

Même logique que `check_skill_counts.py` et `check_decision_register.py`, nés le même jour du même
constat : **une règle qui se répète malgré son rappel n'est pas tenable par l'intention.**
