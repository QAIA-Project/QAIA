# "Nothing else" — why the empty fetch must stay empty

## The situation

The user designates a source. It comes back thin or empty: a JS-rendered application that serves
only `<div id="app"></div>`, a ticket whose body is a link, a page behind a login. You now have a
capture that will not support a test book, and an obvious way to fix it — look somewhere else.

**Do not.** Report the gap and ask the user for a fuller source: exported HTML, the underlying
documents, or explicit permission to search elsewhere.

## Why this rule is stricter than it looks

An empty fetch is **a fact to report, not a hole to fill.** Everything downstream — the
ambiguity hunt, the test conditions, the Gherkin, the traceability — treats `00-source.md` as
*the requirement*. Content that entered the capture without being designated is therefore not
context: it becomes a requirement the product owner never wrote, tested as if they had.

Three moves feel reasonable in the moment and are all forbidden:

1. **Falling back to a web search.** Substitutes content the user never designated.
2. **Supplementing with a different page** of the same site, or a sibling ticket. Same problem,
   with a stronger appearance of legitimacy because the domain matches.
3. **Citing a third-party write-up** — a blog post, a tutorial, a vendor page — to make concrete
   a detail the designated source left abstract. This is the most tempting of the three, because
   the addition genuinely does describe the system. It is still content nobody designated.

**A detail the source states abstractly must stay abstract in the capture.** Its vagueness is
information: it is precisely what `need-understanding` exists to turn into a question for the
product owner. Resolving it from an outside source does not answer the question — it hides that
there was one.

## Transparency does not grant authorization

Two rationalisations to name, because both are forms of asking forgiveness from a reader who
never gets to refuse:

- **"I'll tell the user I did it."** Being transparent about a substitution does not make the
  substitution authorized. The rule is not "do not do it secretly", it is "do not do it".
- **"I'll label it `[secondary-source]`."** The label changes the label. Non-designated content
  was still fetched, still written into the capture, and will still be tested. A tag on a
  requirement that should not be there does not remove it — it documents its presence.

## What to do instead

Report, in one message:

- what was designated;
- what came back (verbatim size and shape — "200 OK, 412 bytes, an empty application shell");
- what that makes impossible downstream;
- the concrete alternatives the user can supply — an export, a PDF, the ticket text pasted, or
  an explicit go-ahead to search named sources.

Then stop. A journey that halts at step 1 with an accurate reason costs the user a message. A
journey that continues on substituted content costs them a test book they will believe.
