# Article — dev.to / Hashnode, prêt à publier

> **Canal** : dev.to en premier (indexé vite, evergreen, et il donne quelque chose à lier depuis
> partout ailleurs), Hashnode en cross-post canonique quelques jours après.
>
> **Pourquoi celui-ci et pas un article sur QAIA** : c'est un retour d'expérience avec des
> chiffres, où QAIA est le décor et pas le sujet. Un article promotionnel se lit une fois ;
> un article qui raconte un résultat inconfortable se relit et se cite.
>
> **Tags dev.to** : `testing`, `ai`, `qa`, `playwright`
>
> **Image de couverture** : aucune. Une couverture générée à l'IA sur un article qui parle de
> rigueur de mesure serait le pire signal possible.

---

## Titre

**I had five AI judges grade my generated test suites. None passed — and they found more defects
in my rubric than in my code.**

*(Variante plus courte si dev.to tronque : « Five judges, five test suites, zero passes »)*

---

## Corps

I write a tool that generates Playwright tests from user stories. Last week I finally did the
thing I had been avoiding: I let five independent judges grade what it produces, using a rubric I
had written months earlier and never actually applied.

Nothing passed. That was expected — the tool is pre-alpha.

What I did not expect: **the judges found nineteen defects in my rubric and twelve in my code.**
The instrument absorbed more correction than the thing it was supposed to measure. Here is what
that looked like, because I think the pattern generalises well beyond my project.

### The setup

Five suites, generated earlier, sitting in the repository as evaluation evidence. Five judges,
each dispatched with **no generation context** — they had the specification, the code, and the
output of a deterministic static checker, and were explicitly told not to read the project's
decision log, its status file, or its git history.

That last constraint matters more than it sounds. My previous attempt at this had the judge and
the generator sharing a session. The scores were meaningless, and I knew it at the time — I wrote
the conflict down and left the box unchecked rather than pretend.

### The worst defect was an assertion that agreed with the application instead of the spec

One suite tested a password-reset flow. The specification said, for an email address that is
**not** a registered account:

> the security question field is **enabled, the same as for a registered email**

The scenario exists for exactly one reason: to check that a public, unauthenticated endpoint does
not leak whether an account exists.

The generated test asserted:

```js
expect(enabled).toBe(false);
```

The inverse.

Sit with the consequence for a second, because it is not a false negative — it is worse. **The day
that test runs green, it is green because the application leaks.** The defect the scenario exists
to detect has become its pass condition, and CI will hold that line indefinitely. And if someone
later fixes the leak, the test turns red and reads as a regression to revert.

I think I understand how generation produces this. When a specification states a *safe default*
rather than the observed behaviour, generating against what the application actually does is the
path of least resistance. That is precisely the moment the specification is telling you the
application might be wrong.

### The one that looks like a real assertion and is not

Another suite, three tests of this shape:

```js
expect(alertText.length).toBeGreaterThan(0);
```

The scenario demanded a specific error alert **and** the absence of a success message. The string
`"Product added"` has a length greater than zero. The test passes against the forbidden behaviour.

Every static checker I have accepts that line. It is a real assertion, on real state, with a real
matcher. It is also vacuous *relative to what its scenario claimed* — and that gap is exactly
where a reading judge earns its keep.

A related finding I had not thought about at all: **a negative test whose positive control is red
proves nothing.** One suite asserted `not.toBe(200)` on an endpoint that was refusing every
request for an unrelated reason. Green by accident, on every single negative.

### Then the judges started grading the rubric

This is the part I would tell someone else to expect.

- **No `n/a`, but a fixed denominator.** One suite honestly declared zero negative scenarios and
  argued the exclusion. Scoring that dimension 2 rewards absence; scoring it 0 punishes honesty;
  and "not judgeable" made the pass threshold arithmetically unreachable.
- **No aggregation rule.** My level wordings mixed "one test…" and "each scenario…". Worst
  instance? Majority? Both judges picked worst-instance independently — before I had written it
  down.
- **One defect satisfying three dimensions at once.** A dropped clause was simultaneously an
  infidelity, a hollow negative and an under-strength assertion. Up to four points of swing, on
  the judge's discretion alone.
- **A rule I wrote in the morning, broken in the afternoon.** After the first fixes, the third
  judge found that "count a defect once" never said what happens to the *other* dimension, whose
  levels are written as universals. It documented both readings and the one-point gap between
  them — which is precisely the variance the fix had been written to remove.

Nineteen of these, over five runs.

### What I actually did with it

Three findings turned out to be mechanically checkable, so I moved them out of the judges' hands
and into the static checker:

- a scenario the specification flagged as resting on an open question, whose test carries no trace
  of the flag;
- a test whose **entire** evidence is one-sided;
- a comment citing a file that does not exist.

Each with a fixture containing cases that must fire **and cases that must not** — a check that
triggers on everything discriminates nothing.

Adding the third one uncovered a bug in my own tool. It found nothing at first, even though the
judge was demonstrably right, because the citation lived in a page object one directory above
where the tool was looking. Two suite layouts existed in my corpus and the tool understood one.
**Two judges had flagged that as a probable tool bug before anyone checked.** They were right, and
I had read past it twice.

### The three things I would keep

**Testing an instrument costs more than writing it, and that expense is what makes it worth
anything.** A rubric nobody has applied mostly measures the confidence you place in it. Mine
needed nineteen corrections before it measured anything else.

**Verify the recovery path, not only the failure path.** My anti-drift check detected drift
correctly and then refused to clear — it hashed raw bytes, and git rewrites line endings on
checkout under Windows. I would never have found that by testing only that it fails.

**A guardrail is worth something the day it stops the person who wrote it.** Four times in one
week, mine caught me: a version claim I forgot to update, a link I wrote in the wrong format, an
accessibility contrast failure in CSS I had just written, and a lint rule that rejected my own new
text. That is the only evidence that counts — not that a check passes on a clean tree, but that it
fails when it should.

### The uncomfortable part

Three of my five suites are vacuous against their own specification in at least two dimensions,
and the deterministic checker reported "no blocking finding" on all five. **A suite can be shapely
and vacuous.** If you generate tests with an LLM — with my tool or any other — that sentence is
the one worth taking away.

---

*Everything above is in the open, including the parts that go against the tool: the five judge
reports, the rubric with its nineteen corrections, the benchmark where a plain direct prompt costs
2.9× fewer tokens and matches it on ambiguity recall (measured in July 2026, before the journey
became a single skill; not re-measured since). It is called
[QAIA](https://github.com/QAIA-Project/QAIA), it is MIT, it is pre-alpha, and no human pilot has
run it end to end — which is currently the largest unknown in the project and the reason I would
rather have an issue telling me where it disappointed you than a star.*

---

## Notes de publication

- **Ne pas ajouter de section « comment installer »**. L'article vaut par le retour d'expérience ;
  un appel à l'installation en fin d'article le fait basculer dans la catégorie promotionnelle et
  perd le lecteur qui l'aurait partagé.
- **Le seul lien vers le dépôt est en italique tout en bas.** C'est volontaire.
- **Répondre aux commentaires le jour même.** Sur dev.to comme ailleurs, un article sans auteur
  présent meurt en 24 h.
- **Cross-post Hashnode avec `canonical_url` pointant sur dev.to**, jamais l'inverse, pour ne pas
  se faire dédupliquer par les moteurs.
