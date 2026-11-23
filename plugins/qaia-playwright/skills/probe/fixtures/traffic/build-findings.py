#!/usr/bin/env python3
"""
build-findings.py -- reference implementation of the traffic-replay Method (../SKILL.md),
used to produce this skill's own validation evidence (VALIDATION.md).

This mirrors the D42 tier-1 pattern: a short-lived, in-session script that an agent running
the skill would generate and execute against the user's HAR, then discard. It is kept here, in
the fixture, as a transparent, reproducible record of exactly how the evidence in output/ was
produced -- it is NOT runtime code the qaia-playwright plugin ships or auto-executes on
install (ADR 0002 / D42: no hooks, no auto-exec; a plugin skill only ever generates and runs a
throwaway script in the user's own session, under their own permissions).

Usage: python build-findings.py demo-traffic.har output/
"""
import json
import os
import re
import sys
from collections import OrderedDict, defaultdict

# ---------------------------------------------------------------------------
# Masking rules (SKILL.md "Masking" table) -- applied before anything else is
# derived. pii_counts is the only record kept: type -> count (no ledger of
# original value -> placeholder, per D37).
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(\+?\d[\d .-]{7,16}\d)(?!\d)")
DIGITS_RUN_RE = re.compile(r"\d{13,19}")
AUTH_HEADER_NAME_RE = re.compile(r"auth|api.?key|x-.*-token|x-.*-secret", re.I)
QUERY_TOKEN_KEY_RE = re.compile(r"token|key|secret|session|auth|password", re.I)
NAME_KEY_RE = re.compile(r"name|assignee|author|owner|contact", re.I)
SECRET_KEY_RE = re.compile(r"password|passwd|pwd|secret|token|api.?key", re.I)

pii_counts = defaultdict(int)


def luhn_ok(digits: str) -> bool:
    total = 0
    parity = len(digits) % 2
    for i, ch in enumerate(digits):
        d = int(ch)
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def mask_card_numbers(text: str) -> str:
    def repl(m):
        digits = m.group(0)
        if luhn_ok(digits):
            pii_counts["card"] += 1
            return "[REDACTED:card]"
        return digits  # fails Luhn -- not a plausible card number, left alone

    return DIGITS_RUN_RE.sub(repl, text)


def mask_email(text: str) -> str:
    def repl(_m):
        pii_counts["email"] += 1
        return "[REDACTED:email]"

    return EMAIL_RE.sub(repl, text)


def mask_phone(text: str) -> str:
    def repl(_m):
        pii_counts["phone"] += 1
        return "[REDACTED:phone]"

    return PHONE_RE.sub(repl, text)


def mask_value_text(text):
    """Value-based regex passes only -- no key context available (header/query values)."""
    if not isinstance(text, str):
        return text
    # Order matters: card (contiguous digit runs) before phone (digits + separators),
    # so a bare card number is never re-flagged as a phone number afterwards.
    text = mask_email(text)
    text = mask_card_numbers(text)
    text = mask_phone(text)
    return text


def mask_json_value(key, value):
    """Key-based heuristics (name, secret/token) first, then value-based regexes."""
    if isinstance(value, str):
        if key and NAME_KEY_RE.search(key):
            pii_counts["name"] += 1
            return "[REDACTED:name]"
        if key and SECRET_KEY_RE.search(key):
            pii_counts["secret"] += 1
            return "[REDACTED:secret]"
        return mask_value_text(value)
    if isinstance(value, dict):
        return {k: mask_json_value(k, v) for k, v in value.items()}
    if isinstance(value, list):
        return [mask_json_value(key, v) for v in value]
    return value


def mask_body_for_counting(mime_type, text):
    """Runs the masking pass over a request/response body purely to update
    pii_counts -- the return value is intentionally never written anywhere;
    only shape_fingerprint()'s key/type-only view of the body is ever output."""
    if not text:
        return
    if mime_type and "json" in mime_type:
        try:
            obj = json.loads(text)
        except ValueError:
            mask_value_text(text)
            return
        mask_json_value(None, obj)
        return
    mask_value_text(text)


def mask_header(name, value):
    lname = name.lower()
    if lname in ("cookie", "set-cookie"):
        pii_counts["cookie"] += 1
        return "[REDACTED:cookie]"
    if AUTH_HEADER_NAME_RE.search(name):
        pii_counts["auth-header"] += 1
        return "[REDACTED:auth-header]"
    return mask_value_text(value)


def mask_query_value(name, value):
    if QUERY_TOKEN_KEY_RE.search(name):
        pii_counts["query-token"] += 1
        return "[REDACTED:query-token]"
    return mask_value_text(value)


# ---------------------------------------------------------------------------
# Response/request shape fingerprint -- keys and types ONLY, values never
# included even after masking (independent second safety layer, SKILL.md).
# ---------------------------------------------------------------------------


def type_name(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    if isinstance(v, dict):
        return "object"
    return "unknown"


def shape_fingerprint(mime_type, text):
    if not text:
        return None
    if not mime_type or "json" not in mime_type:
        return {"kind": "non-json", "contentType": mime_type, "byteSize": len(text)}
    try:
        obj = json.loads(text)
    except ValueError:
        return {"kind": "non-json", "contentType": mime_type, "byteSize": len(text)}
    if isinstance(obj, dict):
        return {"kind": "json-object", "keys": {k: type_name(v) for k, v in obj.items()}}
    if isinstance(obj, list):
        elem_type = type_name(obj[0]) if obj else "empty"
        return {"kind": "json-array", "length": len(obj), "elementType": elem_type}
    return {"kind": "json-scalar", "type": type_name(obj)}


# ---------------------------------------------------------------------------
# Signature grouping + condition derivation (SKILL.md "Method")
# ---------------------------------------------------------------------------

SIGNIFICANT_HEADERS = {
    "content-type",
    "cache-control",
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
    "strict-transport-security",
}


def path_of(url: str) -> str:
    m = re.match(r"^[a-zA-Z]+://[^/]+([^?]*)", url)
    return m.group(1) if m else url


def significant_headers(headers):
    out = OrderedDict()
    for h in headers:
        if h["name"].lower() in SIGNIFICANT_HEADERS:
            out[h["name"]] = mask_header(h["name"], h["value"])
    return out


def main(har_path, out_dir):
    with open(har_path, encoding="utf-8") as f:
        har = json.load(f)

    entries = har["log"]["entries"]
    signatures = OrderedDict()

    for entry in entries:
        req = entry["request"]
        res = entry["response"]
        method = req["method"]
        path = path_of(req["url"])
        qnames = tuple(sorted(q["name"] for q in req.get("queryString", [])))
        sig_key = (method, path, qnames)

        # Apply masking to every header and query value (blocking, before anything
        # else is derived) -- pii_counts is updated as a side effect; nothing raw
        # is stored beyond this point.
        for q in req.get("queryString", []):
            mask_query_value(q["name"], q["value"])
        for h in req.get("headers", []):
            mask_header(h["name"], h["value"])
        for h in res.get("headers", []):
            mask_header(h["name"], h["value"])

        post_data = req.get("postData") or {}
        req_body, req_mime = post_data.get("text"), post_data.get("mimeType")
        mask_body_for_counting(req_mime, req_body)

        content = res.get("content") or {}
        res_body, res_mime = content.get("text"), content.get("mimeType")
        mask_body_for_counting(res_mime, res_body)

        if sig_key not in signatures:
            signatures[sig_key] = {
                "method": method,
                "path": path,
                "queryParamNames": list(qnames),
                "statuses": [],
                "timingsMs": [],
                "reqShapes": [],
                "resShapes": [],
                "significantHeaders": significant_headers(res.get("headers", [])),
            }
        cond = signatures[sig_key]
        cond["statuses"].append(res["status"])
        if "time" in entry:
            cond["timingsMs"].append(entry["time"])
        if req_body:
            cond["reqShapes"].append(shape_fingerprint(req_mime, req_body))
        cond["resShapes"].append(shape_fingerprint(res_mime, res_body))

    conditions = []
    for i, (_key, cond) in enumerate(signatures.items(), start=1):
        sample_count = len(cond["statuses"])
        status_counts = defaultdict(int)
        for s in cond["statuses"]:
            status_counts[s] += 1
        res_shapes = cond["resShapes"]
        shapes_consistent = all(s == res_shapes[0] for s in res_shapes)

        if sample_count == 1:
            note = "1 sample observed -- documents what happened this one time, not a guaranteed contract."
        else:
            note = f"{sample_count} samples observed for this exact signature."

        conditions.append(
            {
                "id": f"@QAIA-TRAFFIC-{i:03d}",
                "method": cond["method"],
                "path": cond["path"],
                "queryParamNames": cond["queryParamNames"],
                "sampleCount": sample_count,
                "singleSample": sample_count == 1,
                "observedStatuses": [
                    {"status": s, "samples": c, "of": sample_count}
                    for s, c in sorted(status_counts.items())
                ],
                "requestShape": cond["reqShapes"][0] if cond["reqShapes"] else None,
                "responseShape": res_shapes[0],
                "responseShapeConsistentAcrossSamples": shapes_consistent,
                "significantHeaders": cond["significantHeaders"],
                "timingMs": cond["timingsMs"],
                "note": note,
            }
        )

    findings = {
        "harSource": os.path.basename(har_path),
        "entriesTotal": len(entries),
        "conditionsTotal": len(conditions),
        "piiMasked": dict(sorted(pii_counts.items())),
        "conditions": conditions,
    }

    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "traffic-findings.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)
        f.write("\n")

    lines = []
    lines.append("# traffic-replay findings -- fixture/demo-traffic.har\n")
    lines.append(f"Entries parsed: {len(entries)} | Conditions derived: {len(conditions)}\n")
    lines.append("## PII/secret masking summary (type -> placeholder -> count, no ledger, D37)\n")
    lines.append("| Type | Placeholder | Count |")
    lines.append("|---|---|---|")
    for t, c in sorted(pii_counts.items()):
        lines.append(f"| {t} | `[REDACTED:{t}]` | {c} |")
    lines.append("")
    lines.append("## Conditions\n")
    lines.append(
        "| ID | Method | Path | Query params | Samples | Status(es) | Response shape (keys:type) | Timing (ms) |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    for c in conditions:
        statuses = ", ".join(f"{o['status']} ({o['samples']}/{o['of']})" for o in c["observedStatuses"])
        shape = c["responseShape"]
        if shape and shape.get("kind") == "json-object":
            shape_str = ", ".join(f"{k}:{v}" for k, v in shape["keys"].items())
        elif shape:
            shape_str = shape.get("kind", "?")
        else:
            shape_str = "(no body)"
        qp = ",".join(c["queryParamNames"]) or "-"
        timing = ", ".join(str(t) for t in c["timingMs"])
        single = " *(single sample)*" if c["singleSample"] else ""
        lines.append(
            f"| {c['id']} | {c['method']} | {c['path']} | {qp} | {c['sampleCount']}{single} "
            f"| {statuses} | {shape_str} | {timing} |"
        )
    lines.append("")
    lines.append("## Known limitations of this run (stated, not hidden)")
    lines.append("- Name detection is heuristic and key-based only; a name outside a matched JSON key is not caught.")
    lines.append("- Card detection is Luhn-checksum + digit-length based; edge cases are possible (see SKILL.md Guardrails).")
    lines.append("- National ID / SSN patterns are not covered in v1.")
    lines.append("- Path-template inference (`/api/tasks/{id}`) is deliberately not performed (see SKILL.md Method step 3) -- each literal path is its own signature.")
    lines.append("")

    md_path = os.path.join(out_dir, "traffic-findings.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote {json_path} and {md_path}")
    print(f"PII masked (type -> count): {dict(sorted(pii_counts.items()))}")


if __name__ == "__main__":
    har_arg = sys.argv[1] if len(sys.argv) > 1 else "demo-traffic.har"
    out_arg = sys.argv[2] if len(sys.argv) > 2 else "output"
    main(har_arg, out_arg)
