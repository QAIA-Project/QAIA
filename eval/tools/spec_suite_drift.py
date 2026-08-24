#!/usr/bin/env python3
"""Compare a specification against the test suite that claims to cover it. Pure text.

## Pourquoi ce fichier existe

Le 2026-08-09, en marchant les phases du SDLC sur `realworld-apps/realworld`, un constat est
apparu qu'aucune des deux sources ne montre seule :

- `specs/api/openapi.yml` promet un **409 Conflict** sur `POST /users` et `POST /articles` ;
- `specs/e2e/error-handling.spec.ts:50` mocke ce cas exact -- `email: ['is already taken']` --
  en **400** ;
- et **aucun** des 150 comportements de la suite n'exerce le 409.

Pour un projet dont le but est que N implementations respectent un contrat, les deux ne peuvent
pas avoir raison. Chaque moitie est pourtant coherente vue de l'interieur : c'est exactement la
classe de defaut qu'un scan de la couche automatisation ne peut pas produire.

`contract-probe` compare une **application** a sa documentation. Il manquait l'autre moitie :
comparer la **suite** a la documentation. C'est du texte contre du texte -- ni application qui
tourne, ni credential, ni reseau -- donc c'est executable a chaque commit.

C'est la **boucle B** de `eval/sdlc-realworld-2026-08-09/REPORT.md`, et la raison de la batir
avant les trois autres : elle est la seule dont le retour soit mecanique. Les boucles qui passent
par un jugement humain sont toutes a l'arret depuis qu'elles existent.

## Ce qui est verifie

- **R1 `undeclared-status`** -- la suite simule ou attend un code que la specification **ne
  declare pas** pour ce chemin. La suite teste une promesse qui n'existe pas, ou la
  specification a oublie un cas reel.
- **R2 `unexercised-status`** -- la specification declare un code d'erreur qu'**aucun** test ne
  mentionne nulle part. Une promesse non eprouvee.
- **R3 `path-not-in-spec`** -- la suite appelle un chemin d'API absent de la specification.

## Ce qui n'est PAS verifie, et pourquoi

La correspondance chemin -> code est une **heuristique de proximite** : dans un bloc de test, les
codes sont apparies au chemin cite dans ce meme bloc, et **uniquement quand le bloc n'en cite
qu'un seul**. Un bloc citant deux chemins est laisse de cote plutot que devine -- 490 constats
faux ont ete produits en deux jours par des regles qui preferaient repondre a se taire.

Les codes 2xx ne declenchent jamais R2 : un test nominal exerce le chemin heureux sans jamais
ecrire `200`. Les codes 5xx ne declenchent jamais R1 : une suite qui simule un 500 injecte une
panne pour verifier la degradation du client, elle n'affirme rien sur le contrat.

**Limite connue, non corrigee, et dite plutot que tue : la specification est agregee PAR CHEMIN,
toutes methodes confondues.** `/articles` se voit donc crediter l'union des codes de `GET` et de
`POST`. Aucun constat emis n'est donc conscient de la methode, et un code legitime pour l'une
peut masquer son absence pour l'autre. La corriger demanderait de connaitre la methode du cote
**suite**, ce que l'heuristique de proximite ne sait pas faire de facon fiable ; une correction a
moitie serait pire qu'une limite ecrite. Trouve par une revue adversariale le 2026-08-09.

Run:
  python eval/tools/spec_suite_drift.py --spec openapi.yml --tests-dir specs/e2e [--json out.json]

Exit 0 aucun ecart, 1 ecart trouve, 2 entree illisible.
"""
import argparse
import io
import json
import os
import re
import sys

NL = chr(10)
METHODS = ("get", "post", "put", "delete", "patch", "head", "options")

# Un chemin d'API cite dans le code de test : '/users', "/api/articles/{slug}", `/articles/${x}`
SUITE_PATH = re.compile(r"""['"`](/(?:api/)?[a-zA-Z][a-zA-Z0-9_\-/]*(?:\$\{[^}]*\}|\{[^}]*\}|\*)?[a-zA-Z0-9_\-/*]*)['"`]""")
# `page.goto('/settings')` designe une page, pas un point d'entree d'API. Sans cette distinction
# l'outil reprochait a la suite d'appeler `/editor` et `/settings` -- six constats faux -- et,
# plus grave, **etouffait son constat le plus fort** : le bloc qui mocke `/users` en 400 fait
# aussi `page.goto('/register')`, donc il citait deux chemins et l'appariement prudent le
# laissait de cote. Retirer les routes de navigation rend le bloc univoque et la contradiction
# 400-contre-422 apparait.
NAVIGATION = re.compile(r"""\.\s*(?:goto|waitForURL|toHaveURL)\s*\(\s*(?:new\s+RegExp\s*\(\s*)?['"`/]""")
# Un code HTTP ecrit comme une valeur, jamais comme un fragment de nombre plus long.
# Un code HTTP ecrit comme une valeur, jamais comme un fragment de nombre plus long.
# La derniere alternative -- une virgule suivie d'un nombre de 100 a 599 -- est volontairement
# large : elle attrape `mockApiError(page, '/users', 409, ...)`, le cas qui a fait naitre cet
# outil, et on ne peut pas deviner le nom du helper qu'un depot inconnu s'est ecrit. Le prix
# est un faux positif sur les APIs numeriques, ferme par NUMERIC_API juste en dessous.
SUITE_STATUS = re.compile(r"(?:(?<![\w.])status\s*[:=]\s*|(?<![\w])(?:toBe|toEqual|toHaveProperty)\s*\(\s*|,\s*)([1-5]\d{2})(?![\w.])")
# Appels dont un argument numerique de 100 a 599 n'est pas un code HTTP : delais, decoupages,
# arrondis, coordonnees. Cherche dans ce qui precede immediatement le nombre, sur la meme ligne.
# Sans ca, `waitForTimeout(page, 500)` faisait lire a l'outil une 500 exercee par la suite --
# et donc taire un vrai « la specification promet une 500 que personne ne teste ».
NUMERIC_API = re.compile(
    r"\b(?:waitForTimeout|setTimeout|setInterval|slice|substring|substr|splice|padStart|padEnd|"
    r"toFixed|repeat|scrollTo|scrollBy|resize|setViewportSize|mouse\s*\.\s*\w+|move|click|"
    r"fill\s*Rect|drawImage|timeout|delay|width|height|top|left)\b[^;]{0,60}$")


def is_http_status(line, match_start):
    """Le nombre qui commence a `match_start` est-il un code HTTP, ou un nombre ordinaire ?"""
    return not NUMERIC_API.search(line[:match_start])


TEST_DECL = re.compile(r"^\s*(?:test|it)\s*(?:\.\s*\w+\s*)?\(\s*(['\"`])((?:\\.|(?!\1).)*)\1")
SPEC_GLOB = re.compile(r"\.(spec|test|e2e)\.(js|ts|mjs|cjs)$")


def norm(p):
    """`/api/articles/{slug}` et `/articles/${slug}` designent le meme chemin specifie."""
    p = p.split("?")[0]
    p = re.sub(r"^/api", "", p)
    p = re.sub(r"\$\{[^}]*\}|\{[^}]*\}|:[a-zA-Z_]\w*", "{}", p)
    # Un joker est un SEGMENT, pas son absence : `/profiles/*` instancie `/profiles/{username}`.
    # Le raboter donnait `/profiles`, qui ne correspond a aucun gabarit -- un constat faux.
    p = re.sub(r"(?<=/)\*+(?=/|$)", "{}", p)
    p = re.sub(r"\*+", "", p)
    p = re.sub(r"/+", "/", p).rstrip("/")
    return p or "/"


def resolve(path, declared):
    """Ramene un chemin concret au gabarit qu'il instancie.

    Un test ecrit `/articles/some-article` la ou la specification declare `/articles/{slug}`.
    Sans cette resolution l'outil signalait quatre chemins « absents de la specification » qui y
    sont, et comparait leurs codes a rien. On n'apparie que si le nombre de segments concorde et
    si chaque segment litteral du gabarit est identique -- un `{}` absorbe n'importe quoi.
    """
    if path in declared:
        return path
    parts = path.strip("/").split("/")
    for template in declared:
        tparts = template.strip("/").split("/")
        if len(tparts) != len(parts):
            continue
        if all(t == "{}" or t == p for t, p in zip(tparts, parts)):
            return template
    return None


UNREADABLE = []


def read(path):
    """Rend "" si le fichier est illisible -- mais le CONSIGNE. Sans cette liste, un fichier
    qu'on n'a pas pu ouvrir se lisait exactement comme un fichier sans defaut, et l'outil
    sortait « aucun ecart » avec un code 0. Trouve par la revue « developpeur »."""
    try:
        return io.open(path, encoding="utf-8", errors="replace").read()
    except (IOError, OSError) as exc:
        UNREADABLE.append((path, str(exc)))
        return ""


def load_spec(path):
    try:
        import yaml
    except ImportError:
        print("BROKEN: PyYAML absent -- pip install pyyaml", file=sys.stderr)
        return None
    try:
        if path.endswith(".json"):
            d = json.loads(read(path))
        else:
            d = yaml.safe_load(read(path))
    except Exception as e:
        print("BROKEN: specification illisible (%s)" % e, file=sys.stderr)
        return None
    if not isinstance(d, dict) or "paths" not in d:
        print("BROKEN: pas de bloc `paths` -- est-ce bien une specification OpenAPI ?", file=sys.stderr)
        return None
    declared = {}
    for raw_path, item in (d.get("paths") or {}).items():
        key = norm(raw_path)
        for method, op in (item or {}).items():
            if method not in METHODS or not isinstance(op, dict):
                continue
            for code in (op.get("responses") or {}):
                declared.setdefault(key, set()).add(str(code))
    return declared


def collect_blocks(text):
    """[(titre, debut, fin)] -- 1-indexe, fin exclue. Meme decoupage grossier qu'ailleurs."""
    lines = text.split(NL)
    starts = [(i + 1, m.group(2)) for i, line in enumerate(lines)
              for m in [TEST_DECL.match(line)] if m]
    out = []
    for idx, (ln, title) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines) + 1
        out.append((title, ln, end))
    return out


def scan_suite(tests_dir):
    """Retourne (paires, chemins_vus, codes_vus, fichiers_lus, fichiers_ignores).

    Une paire est (chemin, code, fichier, ligne, titre).

    Les deux derniers comptes ont ete ajoutes le 2026-08-24 : sans eux, l'outil ne savait pas
    dire s'il n'avait rien trouve ou rien lu, et rendait des constats affirmatifs sur un
    repertoire VIDE (cf. la garde dans `compare_or_refuse`).
    """
    pairs, seen_paths, all_status = [], set(), set()
    files_read, files_skipped = 0, 0
    for root, dirs, files in os.walk(tests_dir):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
        for f in sorted(files):
            if not SPEC_GLOB.search(f):
                # Un fichier de test que ce lecteur ne sait pas lire (Go, Python, Ruby, Java,
                # ou un JS qui ne suit pas la convention `.spec.`/`.test.`) n'est pas rien : il
                # est COMPTE, pour que l'absence de resultat puisse se distinguer de l'absence
                # de lecture.
                if f.endswith((".go", ".py", ".rb", ".java", ".kt", ".php", ".cs",
                               ".js", ".ts", ".mjs", ".cjs")):
                    files_skipped += 1
                continue
            path = os.path.join(root, f)
            files_read += 1
            text = read(path)
            lines = text.split(NL)
            rel = os.path.relpath(path, tests_dir)
            for title, start, end in collect_blocks(text):
                body = lines[start - 1:end - 1]
                here_paths, here_status = set(), []
                for offset, line in enumerate(body):
                    code_only = line.split("//")[0]
                    if NAVIGATION.search(code_only):
                        continue          # route de page, pas point d'entree d'API
                    for m in SUITE_PATH.finditer(code_only):
                        p = norm(m.group(1))
                        if p != "/" and not p.startswith("/http"):
                            here_paths.add(p)
                    for m in SUITE_STATUS.finditer(code_only):
                        if not is_http_status(code_only, m.start()):
                            continue  # nombre ordinaire, pas un code HTTP (B31)
                        here_status.append((m.group(1), start + offset))
                seen_paths |= here_paths
                all_status |= {s for s, _ in here_status}
                # Apparier UNIQUEMENT quand le bloc ne cite qu'un chemin : deviner ferait plus
                # de bruit que de constats, et c'est la lecon des 490 faux positifs.
                if len(here_paths) == 1:
                    only = next(iter(here_paths))
                    for status, ln in here_status:
                        pairs.append((only, status, rel, ln, title))
    return pairs, seen_paths, all_status, files_read, files_skipped


def compare(declared, pairs, seen_paths, all_status):
    findings = []

    for path, status, rel, ln, title in pairs:
        template = resolve(path, declared)
        # Un 5xx simule est une INJECTION DE PANNE, pas une affirmation sur le contrat. La suite
        # ne pretend pas que l'API promet un 500 : elle force une defaillance serveur arbitraire
        # pour verifier que le client se degrade proprement. Aucune specification n'est tenue de
        # declarer un 500, donc les deux branches de la regle R1 (« la suite teste une promesse
        # inexistante, ou la spec a oublie un cas ») sont fausses ici.
        # Quatre des huit constats publies sur RealWorld etaient de cette forme -- meme faute que
        # les 279 selecteurs et les 408 conventions : **la regle est-elle seulement applicable ?**
        # Le pendant existait deja pour les 2xx dans R2 ; il manquait ici.
        if status.startswith("5"):
            continue
        if template and status not in declared[template]:
            shown = path if path == template else "%s (%s)" % (path, template)
            findings.append({
                "rule": "undeclared-status", "path": template, "status": status,
                "file": rel, "line": ln, "test": title[:110],
                "detail": "la suite utilise %s sur %s ; la specification y declare %s"
                          % (status, shown, ", ".join(sorted(declared[template]))),
            })

    # Groupe par CODE et non par chemin : « 422 promis sur 11 chemins, jamais mentionne » est un
    # seul fait. Le rapporter onze fois donnait onze lignes disant la meme chose, ce qui noie le
    # 409 -- le constat pour lequel cet outil existe.
    missing = {}
    for path, codes in sorted(declared.items()):
        for status in sorted(codes):
            if status.startswith("2") or not status.isdigit() or status in all_status:
                continue
            missing.setdefault(status, []).append(path)
    for status, paths in sorted(missing.items()):
        findings.append({
            "rule": "unexercised-status", "path": ", ".join(paths), "status": status,
            "file": "<suite>", "line": 0, "test": "",
            "detail": "la specification promet %s sur %d chemin(s) -- %s -- ; aucun test ne "
                      "mentionne ce code" % (status, len(paths), ", ".join(paths)),
        })

    for path in sorted(seen_paths):
        if resolve(path, declared) is None and any(path == p for p, _, _, _, _ in pairs):
            findings.append({
                "rule": "path-not-in-spec", "path": path, "status": "",
                "file": "<suite>", "line": 0, "test": "",
                "detail": "la suite appelle %s ; la specification ne le declare pas" % path,
            })

    # Dedupliquer : un meme couple (regle, chemin, code) rapporte une fois.
    out, keys = [], set()
    for f in findings:
        k = (f["rule"], f["path"], f["status"])
        if k in keys:
            continue
        keys.add(k)
        out.append(f)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split(NL)[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True, help="OpenAPI/Swagger, .yml ou .json")
    ap.add_argument("--tests-dir", required=True, help="repertoire de la suite de tests")
    ap.add_argument("--json", help="ecrit le resultat ici au lieu de la sortie standard")
    args = ap.parse_args()

    if not os.path.isfile(args.spec):
        print("BROKEN: specification introuvable : %s" % args.spec, file=sys.stderr)
        return 2
    if not os.path.isdir(args.tests_dir):
        print("BROKEN: repertoire de tests introuvable : %s" % args.tests_dir, file=sys.stderr)
        return 2

    declared = load_spec(args.spec)
    if declared is None:
        return 2
    pairs, seen_paths, all_status, files_read, files_skipped = scan_suite(args.tests_dir)

    # --- refus de rendre un verdict sur un parse vide -----------------------------------------
    #
    # Trouve le 2026-08-24 en pointant cet outil sur du logiciel tiers : un repertoire ne
    # contenant AUCUN fichier de test rendait trois `unexercised-status` affirmatifs. La regle
    # R2 dit « la specification promet 400 et aucun test ne mentionne ce code » ; sur une suite
    # que l'outil n'a pas su lire, c'est vrai et vide -- il ne mesure plus la suite, il mesure
    # sa propre cecite. Les regles R1 et R3, elles, ne peuvent alors PAS se declencher : sur
    # quatre projets tiers, 11 constats sur 11 etaient des R2 de cette espece.
    #
    # C'est l'invariant que `structural_score.py` applique deja (UNSCORED plutot qu'un 20/100
    # muet) et que celui-ci n'avait pas, parce qu'il n'avait jamais lu qu'un seul projet -- celui
    # qui a servi a l'ecrire.
    unreadable = None
    if files_read == 0:
        unreadable = ("aucun fichier de test lisible par cet outil (%d ignore(s) : il ne lit "
                      "que le JS/TS nomme .spec./.test./.e2e.)" % files_skipped)
    elif not all_status:
        unreadable = ("%d fichier(s) lu(s), mais AUCUN code HTTP reconnu : la suite emploie "
                      "vraisemblablement une autre facon d'affirmer un statut que celles que "
                      "cet outil sait lire" % files_read)

    findings = [] if unreadable else compare(declared, pairs, seen_paths, all_status)

    result = {
        "tool": "spec_suite_drift", "version": 1,
        "inputs": {"spec": args.spec, "tests_dir": args.tests_dir},
        "counts": {
            "spec_paths": len(declared),
            "suite_files_read": files_read,
            "suite_files_skipped_unreadable": files_skipped,
            "path_status_pairs_in_suite": len(pairs),
            "distinct_status_in_suite": len(all_status),
            "findings": len(findings),
        },
        "verdict": "UNCOMPARABLE" if unreadable else "compared",
        "uncomparableReason": unreadable,
        "findings": findings,
    }

    if args.json:
        io.open(args.json, "w", encoding="utf-8", newline=NL).write(
            json.dumps(result, indent=2, ensure_ascii=False) + NL)
        print("written: %s" % args.json)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    if unreadable:
        print(NL + "UNCOMPARABLE : %s." % unreadable, file=sys.stderr)
        print("Aucun ecart n'est rendu -- un verdict ici mesurerait la cecite de l'outil, pas "
              "la suite.", file=sys.stderr)
        return 3

    if findings:
        print(NL + "%d ecart(s) entre la specification et la suite :" % len(findings), file=sys.stderr)
        for f in findings:
            where = "%s:%s" % (f["file"], f["line"]) if f["line"] else f["file"]
            print("  %-20s %-28s %s" % (f["rule"], where, f["detail"]), file=sys.stderr)
        return 1
    print(NL + "aucun ecart : chaque code declare est exerce, chaque code utilise est declare.",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
