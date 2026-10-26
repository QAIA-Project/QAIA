# The optional git-history signal

An extra input to the **probability** score — never a new score dimension, never a verdict, never
a shortcut around arbitration.

## When it may be used at all

**Only when the user has explicitly named a target repo path for this session.** Never scan or
infer a repo the user did not name, and never reach beyond it — no other repos, no crawling
outside the files tied to the condition at hand (shared-contract rule 6: no side effects beyond
what was requested).

## How to use it

When a repo path is named and a condition maps to identifiable files (from the US or design
context), a lightweight `git log --stat` on those files is **one more input** to the probability
call. Recent or frequent changes there are cited in the rationale as an additional risk factor:

> `path/to/file` changed N times / M lines in the recent history — cited as a probability input.

## Substance over raw count

A file touched often by small, mechanical, append-only edits — a changelog, a version bump — is
**not** a higher-risk zone just because its commit count is high. A file with few but large or
structural recent diffs **can** be.

**Raw commit frequency alone is never sufficient justification.** The citation must point to
something concrete — a diff's content, not just a count — for the nudge to stand up to
arbitration.

## What it can never do

- **Never raise probability on its own** past what the condition's own complexity already
  supports.
- **Never lower impact.** Impact is a business judgement; history says nothing about it.
- **Never substitute for reading the condition's actual logic.**
- **Never survive unnoticed.** Every use is cited (file + stat) so the user can reject it as
  easily as any other proposed score — **including, and especially, when it was the deciding
  nudge across a priority-band boundary.**

## Absence of data is not evidence of safety

Silently skipped — no error, no placeholder score — when no repo path is available, or when a
condition maps to no identifiable file.

But **"no history data" is not "low risk"**. Say which conditions had no signal, rather than
letting a missing input read as a reassuring one.
