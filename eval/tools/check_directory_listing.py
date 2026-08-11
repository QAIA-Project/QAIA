#!/usr/bin/env python3
"""Compare ce que SOURCES.json declare publie avec ce que l'annuaire sert reellement.

## Pourquoi ce fichier existe

`docs/outreach/qaskills/SOURCES.json` a porte pendant trois jours `directory: qaskills.sh` sur
**sept** copies, sous un en-tete disant « skills PUBLISHED to external directories ». **Quatre
n'avaient jamais ete soumises** : preparees le 2026-08-08 apres que `GO-LIVE.md` ait deliberement
recommande de commencer par trois, et le geste manuel n'a jamais eu lieu pour les autres.

Personne ne l'a vu, alors que l'annuaire expose une **API publique** (`/api/skills`) qui rendait
l'affirmation verifiable depuis le premier jour. C'est la meme classe que les trois perimetres
faux du 2026-08-11 : un controle absent la ou personne n'avait pense a en mettre un.

`check_published_copies.py` compare la copie a sa SOURCE DANS CE DEPOT. Il ne peut pas savoir ce
qui est en ligne. Ce fichier-ci couvre l'autre moitie.

## Ce qui est verifie

- toute entree `state: live` est reellement servie par l'annuaire, sous le `live_slug` declare ;
- toute entree `state: prepared` n'y est PAS (sinon le fichier est en retard sur la realite) ;
- le compte d'installations est rapporte, jamais juge -- c'est une mesure, pas une note.

## Ce qui n'est PAS verifie, et pourquoi c'est dit

Le CONTENU en ligne. L'API rend un nom, un slug et des compteurs, pas le corps de la skill. Une
copie modifiee ici et non retéléversée reste donc invisible -- et c'est arrive le 2026-08-11 avec
la classe D10 ajoutee a `generated-test-self-review`. Le controle date les deux cotes quand il le
peut ; il ne compare pas les octets.

## Pourquoi il n'est pas dans `make check`

Il depend du reseau. Une cible de verification qui echoue parce qu'un site tiers est lent
apprendrait a tout le monde a ignorer son rouge -- et un controle qu'on ignore est pire qu'absent.
Il se lance a la main, ou par une tache planifiee. **Sans reseau il sort 2 et le dit** : il ne
passe jamais vert sur une absence de mesure.

Run: python eval/tools/check_directory_listing.py
Exit 0 concordance, 1 divergence, 2 annuaire injoignable ou fichier illisible.
"""
import io
import json
import os
import sys
import urllib.error
import urllib.request

SOURCES = os.path.join("docs", "outreach", "qaskills", "SOURCES.json")
API = "https://qaskills.sh/api/skills"
TIMEOUT = 30


def fetch_all():
    """Toutes les entrees de l'annuaire, paginees. Leve sur echec reseau."""
    first = json.loads(urllib.request.urlopen(API + "?page=1", timeout=TIMEOUT).read().decode("utf-8"))
    items = list(first.get("skills", []))
    pages = int(first.get("totalPages") or 1)
    for page in range(2, pages + 1):
        chunk = json.loads(
            urllib.request.urlopen("%s?page=%d" % (API, page), timeout=TIMEOUT).read().decode("utf-8"))
        items.extend(chunk.get("skills", []))
    return items, int(first.get("total") or len(items))


def main():
    if not os.path.isfile(SOURCES):
        print("::error::%s introuvable" % SOURCES, file=sys.stderr)
        return 2
    declared = json.load(io.open(SOURCES, encoding="utf-8")).get("published", [])
    if not declared:
        print("::error::aucune copie declaree dans %s -- le controle porterait sur du vide"
              % SOURCES, file=sys.stderr)
        return 2

    try:
        items, total = fetch_all()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print("ANNUAIRE INJOIGNABLE : %s" % exc, file=sys.stderr)
        print("Le controle ne rend AUCUN verdict -- il ne passe pas vert sur une absence de "
              "mesure.", file=sys.stderr)
        return 2

    by_slug = {s.get("slug"): s for s in items}
    # Les auteurs sous lesquels NOS copies sont publiees, deduits des entrees deja en ligne
    # plutot que codes en dur -- un compte renomme ne doit pas rendre le controle aveugle.
    ours = {(by_slug[e["live_slug"]].get("author") or "").lower()
            for e in declared
            if e.get("state") == "live" and e.get("live_slug") in by_slug}
    if not ours:
        print("ATTENTION : aucun auteur deduit (aucune entree `live` retrouvee). Le volet "
              "« preparee ne doit pas etre en ligne » ne peut rien conclure et ne conclut rien.",
              file=sys.stderr)
    problems, live, prepared = [], [], []

    for entry in declared:
        folder = entry["copy"].split("/")[-2]
        state = entry.get("state")
        if state == "live":
            slug = entry.get("live_slug")
            if not slug:
                problems.append("%s: state=live sans `live_slug`" % folder)
                continue
            found = by_slug.get(slug)
            if found is None:
                problems.append("%s: declaree EN LIGNE sous le slug %r, absente de l'annuaire "
                                "(retiree, renommee, ou jamais soumise)" % (folder, slug))
            else:
                live.append((folder, slug, found.get("installCount"), found.get("author"),
                             found.get("verified")))
        elif state == "prepared":
            # Restreint A NOTRE AUTEUR. Le premier jet comparait les slugs sans regarder qui les
            # publie : il prenait le `visual-regression` de `thetestingacademy` (38 installations)
            # pour le notre et signalait une divergence inexistante. Une regle qui matche trop
            # large est la faute la plus repetee de la journee du 2026-08-11 -- ici dans l'outil
            # ecrit pour la corriger, et attrapee des sa premiere execution.
            hits = [s for s in items
                    if (s.get("author") or "").lower() in ours
                    and (folder in (s.get("slug") or "")
                         or (s.get("slug") or "").startswith(folder))]
            if hits:
                problems.append("%s: declaree PREPAREE seulement, mais l'annuaire sert %r -- ce "
                                "fichier est en retard sur la realite"
                                % (folder, [h.get("slug") for h in hits]))
            else:
                prepared.append(folder)
        else:
            problems.append("%s: `state` absent ou inconnu (%r) -- attendu 'live' ou 'prepared'"
                            % (folder, state))

    print("Annuaire qaskills.sh : %d entrees au total." % total)
    print("Declare ici : %d en ligne, %d preparees." % (len(live), len(prepared)))
    for folder, slug, installs, author, verified in sorted(live):
        print("  EN LIGNE  %-28s %-52s installs=%-5s auteur=%-10s verifiee=%s"
              % (folder, slug, installs, author, verified))
    for folder in sorted(prepared):
        print("  PREPAREE  %-28s (non soumise)" % folder)

    if problems:
        print("::error::%d divergence(s) entre ce que le depot declare et ce que l'annuaire sert."
              % len(problems))
        for p in problems:
            print("  " + p)
        return 1

    print("OK: chaque copie declaree en ligne y est, chaque copie declaree preparee n'y est pas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
