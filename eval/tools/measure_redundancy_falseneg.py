#!/usr/bin/env python3
"""Measurement for issue #113 false-negative: does a Jaccard near-duplicate signal catch
copy-paste drift (When differs by a word or two) WITHOUT flagging boundary/metamorphic pairs?

Discipline: measured on a foreign corpus BEFORE any rule is written. Reports, per threshold s,
the pairs a Jaccard signal would ADD beyond the current strict shape_key grouping, split by
whether their literals are identical (copy-paste signature) or differ (metamorphic → false pos).
"""
import re, glob, sys, itertools
from collections import Counter

def parse_scenarios(text):
    scen, cur, tags = [], None, []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("@"): tags += line.split(); continue
        m = re.match(r"(Scenario Outline|Scenario|Sc[ée]nario|Plan du sc[ée]nario)\s*:\s*(.*)", line, re.I)
        if m:
            if cur: scen.append(cur)
            cur = {"name": m.group(2).strip(), "steps": []}; tags = []
            continue
        if cur is not None:
            sm = re.match(r"(Given|When|Then|And|But|Soit|Quand|Alors|Et|Mais|Etant donn[ée])\b(.*)", line, re.I)
            if sm: cur["steps"].append((sm.group(1), sm.group(2).strip()))
    if cur: scen.append(cur)
    return scen

def normalize_step(t):
    t = re.sub(r'"[^"]*"|\'[^\']*\'', "<val>", t)
    t = re.sub(r"\d+", "<num>", t)
    return re.sub(r"\s+", " ", t).strip().lower()

GW = ("given","when","soit","quand","etant donné","etant donnée")
THEN = ("then","alors")
AND = ("and","but","et","mais")

def gw_norm_steps(s):
    out, in_then = [], False
    for kw, t in s["steps"]:
        k = kw.lower()
        if k in THEN: in_then = True; continue
        if k in GW: in_then = False
        if in_then: continue
        out.append(normalize_step(t))
    return out

def shape_key(s):  # current detector's grouping key
    gw, in_then = [], False
    for kw, t in s["steps"]:
        k = kw.lower()
        if k in THEN: in_then = True; continue
        if k in GW: in_then = False
        if in_then: continue
        gw.append(("and" if k in AND else k, normalize_step(t)))
    return tuple(gw)

def gw_tokens(s):
    toks = set()
    for st in gw_norm_steps(s):
        toks |= set(re.findall(r"\S+", st))
    return toks

def literals(s):  # raw quoted strings + numbers across Given/When (before collapse)
    lits, in_then = [], False
    for kw, t in s["steps"]:
        k = kw.lower()
        if k in THEN: in_then = True; continue
        if k in GW: in_then = False
        if in_then: continue
        lits += re.findall(r'"[^"]*"|\'[^\']*\'', t) + re.findall(r"\d+", t)
    return tuple(sorted(lits))

def jaccard(a, b):
    if not a and not b: return 1.0
    return len(a & b) / len(a | b) if (a | b) else 0.0

files = glob.glob(sys.argv[1] + "/**/*.feature", recursive=True)
THRESH = [0.6, 0.7, 0.8, 0.9, 0.95]
# counters: new pairs (jaccard>=s, shape differs) split by same/diff literals
new_same = Counter(); new_diff = Counter()
# also: how many pairs the CURRENT detector already groups (shape_eq), for context
shape_pairs = 0; total_pairs = 0; n_scen = 0; examples_same = []; examples_diff = []

for f in files:
    try: text = open(f, encoding="utf-8", errors="replace").read()
    except Exception: continue
    scen = [s for s in parse_scenarios(text) if gw_norm_steps(s)]
    n_scen += len(scen)
    feats = [(s, shape_key(s), gw_tokens(s), literals(s)) for s in scen]
    for (s1,k1,t1,l1),(s2,k2,t2,l2) in itertools.combinations(feats, 2):
        total_pairs += 1
        if k1 == k2:
            shape_pairs += 1
            continue                      # already grouped by current detector
        j = jaccard(t1, t2)
        same_lit = (l1 == l2 and l1 != ())
        for s in THRESH:
            if j >= s:
                (new_same if same_lit else new_diff)[s] += 1
        if 0.8 <= j < 1.0:
            ex = (round(j,2), same_lit, s1["name"][:30], "  ||  ".join(gw_norm_steps(s1))[:70], "  ||  ".join(gw_norm_steps(s2))[:70])
            (examples_same if same_lit else examples_diff).append(ex)

print(f"corpus: {len(files)} files, {n_scen} scenarios, {total_pairs} within-file pairs")
print(f"already grouped by current shape_key (exact): {shape_pairs} pairs\n")
print(f"{'thresh':>7} | {'NEW same-literals':>18} | {'NEW diff-literals':>18}")
print(f"{'':>7} | {'(copy-paste sig)':>18} | {'(metamorphic=FP)':>18}")
for s in THRESH:
    print(f"{s:>7} | {new_same[s]:>18} | {new_diff[s]:>18}")
print("\n--- sample NEW same-literals pairs (copy-paste signature), 0.8<=J<1.0 ---")
for e in examples_same[:6]: print(f"  J={e[0]} sameLit={e[1]} | {e[3]}  <=>  {e[4]}")
print("\n--- sample NEW diff-literals pairs (metamorphic / likely false positive) ---")
for e in examples_diff[:6]: print(f"  J={e[0]} sameLit={e[1]} | {e[3]}  <=>  {e[4]}")
