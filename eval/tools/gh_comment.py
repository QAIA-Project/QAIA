#!/usr/bin/env python3
"""Poste ou modifie un commentaire GitHub depuis un FICHIER, puis verifie ce qui a ete publie.

## Pourquoi ce fichier existe

Le 2026-08-08, **six fois dans la meme session**, un commentaire a ete publie ampute de toutes ses
references : les backticks avaient ete interpretes par le shell qui passait le texte en ligne. A
chaque fois la meme cause, a chaque fois le meme remede note dans le commentaire correctif — et a
chaque fois la recidive dans l'heure.

Deux automatisations du meme jour ont montre ce qui marche : `check_skill_counts.py` et
`check_decision_register.py`. Aucune n'a demande a quiconque de se souvenir de quoi que ce soit.

Celui-ci fait pareil, sur deux plans :

1. **Il supprime l'occasion.** Le corps vient d'un fichier. Aucune chaine ne traverse le shell,
   donc aucun backtick ne peut etre mange.
2. **Il verifie apres coup.** Le commentaire publie est **relu depuis l'API** et compare au fichier.
   S'ils different, la commande echoue en montrant l'ecart — au moment ou ca arrive, pas trois
   heures plus tard quand quelqu'un relit.

Le second point est le plus important : c'est la regle que ce depot applique partout ailleurs
(verifier au lieu de supposer) appliquee enfin a son propre outillage de publication.

## Usage

    python eval/tools/gh_comment.py --file corps.md --issue 88
    python eval/tools/gh_comment.py --file corps.md --comment-id 5228083941
    python eval/tools/gh_comment.py --file corps.md --new-issue --title "..." --repo owner/nom

`--repo` vise un depot tiers. La verification apres coup compte double la-bas : une issue ouverte
chez quelqu'un d'autre ne se corrige pas discretement, elle arrive deja dans sa boite mail.

Exit 0 publie et verifie, 1 le contenu publie differe du fichier, 2 erreur d'appel ou d'API.
"""
import argparse
import io
import json
import os
import sys
import urllib.error
import urllib.request

REPO = os.environ.get("QAIA_REPO", "QAIA-Project/QAIA")
API = "https://api.github.com/repos/" + REPO

CR, LF = chr(13), chr(10)


def norm(t):
    """GitHub renvoie du CRLF ; le fichier peut etre en LF. Comparer le texte, pas les octets."""
    return t.replace(CR + LF, LF).replace(CR, LF).strip()


def call(url, payload=None, method=None):
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        print("BROKEN: GITHUB_PERSONAL_ACCESS_TOKEN absent de l'environnement.")
        sys.exit(2)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
    })
    if method:
        req.get_method = lambda: method
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        print("BROKEN: %s sur %s\n%s" % (e.code, url, e.read().decode("utf-8", "replace")[:400]))
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--file", required=True, help="fichier Markdown contenant le corps")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--issue", type=int, help="numero d'issue : cree un commentaire")
    g.add_argument("--comment-id", type=int, help="identifiant de commentaire : le remplace")
    g.add_argument("--new-issue", action="store_true", help="cree une issue (exige --title)")
    ap.add_argument("--title", help="titre, obligatoire avec --new-issue")
    ap.add_argument("--repo", help="depot cible owner/nom (defaut : QAIA-Project/QAIA)")
    args = ap.parse_args()

    api = "https://api.github.com/repos/" + (args.repo or REPO)
    if args.new_issue and not args.title:
        print("BROKEN: --new-issue exige --title.")
        return 2

    if not os.path.isfile(args.file):
        print("BROKEN: fichier introuvable : %s" % args.file)
        return 2
    body = io.open(args.file, encoding="utf-8").read()
    if not body.strip():
        print("BROKEN: le fichier est vide.")
        return 2

    if args.new_issue:
        r = call("%s/issues" % api, {"title": args.title, "body": body})
        check = call("%s/issues/%d" % (api, r["number"]))
        if check.get("title") != args.title:
            print("TITRE PUBLIE DIFFERENT : %r != %r" % (check.get("title"), args.title))
            return 1
    elif args.issue:
        r = call("%s/issues/%d/comments" % (api, args.issue), {"body": body})
        check = call("%s/issues/comments/%d" % (api, r["id"]))
    else:
        r = call("%s/issues/comments/%d" % (api, args.comment_id), {"body": body}, "PATCH")
        check = call("%s/issues/comments/%d" % (api, r["id"]))
    if norm(check["body"]) != norm(body):
        print("PUBLIE DIFFERENT DU FICHIER : %s" % check["html_url"])
        print("  fichier : %d caracteres | publie : %d" % (len(norm(body)), len(norm(check["body"]))))
        a, b = norm(body).split("\n"), norm(check["body"]).split("\n")
        for i in range(max(len(a), len(b))):
            la, lb = (a[i] if i < len(a) else "<absente>"), (b[i] if i < len(b) else "<absente>")
            if la != lb:
                print("  ligne %d\n    attendu : %s\n    publie  : %s" % (i + 1, la[:100], lb[:100]))
                break
        return 1

    print("OK: publie et verifie (%d caracteres) -> %s" % (len(body), check["html_url"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
