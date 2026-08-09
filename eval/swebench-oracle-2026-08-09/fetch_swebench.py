# -*- coding: utf-8 -*-
"""Gele un corpus borne de SWE-bench Lite : enonce en langage naturel + tests-oracles.

Pourquoi ce corpus et pas un autre : chaque cas porte les trois choses qu'il faut pour juger
QAIA sur ce qu'il promet vraiment.

  problem_statement -> l'ENTREE : un rapport de defaut ecrit par un humain, sans code
  FAIL_TO_PASS      -> l'ORACLE : les tests qui echouent avant le correctif et passent apres
  test_patch        -> l'ORACLE FORT : le code de test reellement ajoute

QAIA affirme generer des tests **depuis l'exigence, jamais depuis le code**. Ici la verite
terrain existe et elle a ete etablie par quelqu'un d'autre : la question « la condition que
QAIA a derivee couvre-t-elle ce que le test-oracle exerce ? » a une reponse, pas une opinion.
"""
import hashlib, json, os, sys, time, urllib.request

DEST = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 30
DS = "princeton-nlp%2FSWE-bench_Lite"
os.makedirs(DEST, exist_ok=True)

# Le jeu est TRIE par depot : prendre les N premieres lignes donne deux projets sur
# les douze. Un echantillon biaise se lit comme un corpus. On balaie donc les 300
# positions a pas regulier.
TOTAL = 300
step = max(1, TOTAL // N)
rows = []
for offset in range(0, TOTAL, step):
    if len(rows) >= N:
        break
    u = ("https://datasets-server.huggingface.co/rows?dataset=%s&config=default&split=test"
         "&offset=%d&length=1" % (DS, offset))
    d = json.load(urllib.request.urlopen(u, timeout=90))
    batch = d.get("rows", [])
    if not batch:
        break
    for r in batch:
        row = r["row"]
        rows.append({
            "instance_id": row["instance_id"],
            "repo": row["repo"],
            "created_at": row.get("created_at", "")[:10],
            "problem_statement": row["problem_statement"],
            "fail_to_pass": json.loads(row["FAIL_TO_PASS"]) if isinstance(row["FAIL_TO_PASS"], str)
                            else row["FAIL_TO_PASS"],
            "test_patch": row["test_patch"],
        })
    time.sleep(0.4)

blob = json.dumps(rows, sort_keys=True, ensure_ascii=False)
out = {
    "_source": "https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite (split test)",
    "_retrieved": "2026-08-09",
    "_license": "SWE-bench: MIT (Princeton NLP)",
    "_total_available": 300,
    "_frozen_here": len(rows),
    "_sha256_of_extract": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
    "_why_bounded": "30 cas suffisent pour mesurer une tendance et tiennent dans une revue "
                    "humaine. Un corpus qu'on ne peut pas relire a la main se lit comme une "
                    "preuve alors qu'il n'est qu'un volume.",
    "instances": rows,
}
p = os.path.join(DEST, "swebench-lite-extract.json")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")

print("geles : %d cas" % len(rows))
print("depots distincts : %d" % len({r["repo"] for r in rows}))
print("tests-oracles au total : %d" % sum(len(r["fail_to_pass"]) for r in rows))
print("sha256 extrait : %s" % out["_sha256_of_extract"][:24])
