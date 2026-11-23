# Show HN / Reddit / Ministry of Testing — textes prêts

> Chaque plateforme sanctionne un registre différent. Ce ne sont pas trois copies du même texte.
> **Ne pas poster les trois le même jour** : si un fil part mal quelque part, on veut pouvoir
> corriger avant le suivant.

---

## Hacker News — « Show HN »

**Titre** (HN déteste les majuscules marketing et les points d'exclamation) :

```
Show HN: QAIA – Claude Code plugins that turn a user story into traceable Gherkin tests
```

**Premier commentaire, posté par l'auteur immédiatement après la soumission.** Sur HN c'est ce
commentaire, pas le lien, qui décide du sort du fil.

```
Author here.

QAIA is three Claude Code plugins (4 Markdown skills plus readable, pinned Python
scorers, MIT) that take a user story
to a Gherkin test book with stable scenario IDs and a requirement coverage matrix,
then to native Playwright tests. No API key, no backend, nothing installed into
your repo that executes on its own — it runs inside your own Claude session on
your own quota.

Three things I think are worth your time, all checkable without installing anything:

1. A generated suite runs on a GitHub Actions runner with no Claude session and no
   skill loaded — 8 tests, 8 green. The claim "the tests survive the tool that
   wrote them" is a run, not a sentence.

2. No producer scores its own output. The structural score is deterministic and
   lives in a separate read-only plugin, kept apart from the semantic judge. It has
   caught defects the producing skill could not see in itself — including a case
   where the spec was too weak and the generated tests faithfully inherited the
   weakness.

3. When the story is ambiguous, it does not pick. On the example story, 11 of 38
   scenarios carry a named open question with the trade-off of both answers written
   out. I think silent disambiguation is the real failure mode of AI test
   generation and almost nobody treats it as one.

What it is not: pre-alpha, zero human pilots, and the quality of its output for a
real user is unmeasured. An external 13-persona audit scored it 2.4/5 and an
architecture review 5.0/10 — both published in the repo with what I fixed and what
I didn't. I'd rather you read that than my landing page.

Nearest neighbours, honestly: QASkills.sh (~380 MIT skills, one command, backed by
The Testing Academy) is a better answer if you want your agent to write better
tests today. QA Orchestra is a better answer if you want a QA pass on a diff. I
wrote a comparison page that recommends them for three of four use cases.

Happy to be told this is overengineered — that's a live hypothesis and it would be
useful to hear it argued.

https://github.com/QAIA-Project/QAIA
```

**Le commentaire qui tuerait le fil, et la réponse honnête préparée :**

> *« C'est juste un prompt dans un fichier Markdown. »*

```
Largely yes, and I'd rather not pretend otherwise — the skills are Markdown, that's
the whole distribution model and it's deliberate (no API key, no supply-chain
surface, portable).

The part that isn't a prompt is the machinery around it: stable IDs that survive
regeneration, a coverage matrix that diffs, a negative/boundary ratio checked
against a gate, a manifest validated in CI, and a scorer that is a different
component from the producer. Whether that machinery earns its complexity for a
working tester is exactly what no pilot has tested yet, so I can't claim it does.
```

---

## r/QualityAssurance

Reddit sanctionne l'autopromotion déguisée. **Poster en son nom, dire que c'est le sien dès la
première phrase**, et lire les règles du sub avant (certains exigent un flair ou un jour dédié).

**Titre :**

```
I built an open-source tool that refuses to resolve ambiguous acceptance criteria — 11 of its 38 generated scenarios say "I don't know, here's the question"
```

**Corps :**

```
Mine, MIT, and pre-alpha — flagging that up front.

The thing I keep running into with AI test generation is not that the tests are
bad. It's that when the acceptance criterion is ambiguous, the generator picks an
interpretation and says nothing. "Above €500 needs finance approval" — does exactly
€500 need it? Something decided. You now have a suite that looks complete and
encodes a guess, precisely at the boundary where the bugs live.

So I made the tool surface those instead. On a sample expense-approval story it
produced 38 scenarios; 11 carry a "low confidence" flag naming the open question,
with the risk of both answers spelled out, waiting on a human. The coverage matrix
shows it per row.

It's slower. It's also the only version I'd hand to an auditor.

Honest state: no QA engineer has ever run it on real work. That's the biggest
unknown and I'd rather say it than get caught. An external review panel gave it
2.4/5 and I published that too.

What I actually want from this post: tell me whether the ambiguity flags would help
you or just add noise to your day. That's the design bet and I have no field data
on it.

https://github.com/QAIA-Project/QAIA
```

---

## Ministry of Testing (club / forum)

Registre différent : praticiens, allergiques au marketing, réceptifs à la méthode.
D12 désignait cette communauté comme canal pilote dès M0 — c'est ici que se trouvent les 5
pilotes de #1.

**Titre :** `Asking for 5 testers to break my open-source test-generation tool`

```
I've built an open-source tool that goes from a user story to a Gherkin test book
to Playwright tests, and I've reached the point where more internal evaluation is
worthless. Everything about it has been measured by harnesses and review panels.
Nothing has been measured by a tester doing their actual job.

So I'm asking for five people to try it on one real user story and tell me where it
disappoints. Not "does it work" — I know it runs. Where the output is wrong, thin,
or so verbose you'd never use it.

Two things you might find worth poking at:
- it flags ambiguous acceptance criteria as open questions rather than resolving
  them (11 of 38 scenarios on the sample story)
- nothing scores its own output — the scorer is a separate read-only component

It's MIT, it's Markdown skills for Claude Code, no API key. It's also pre-alpha and
an external panel scored it 2.4/5, which is published in the repo.

I'll take every finding into the tracker with attribution, and I'll say publicly
which ones I couldn't fix.

https://github.com/QAIA-Project/QAIA
```
