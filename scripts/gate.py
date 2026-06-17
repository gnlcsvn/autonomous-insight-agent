#!/usr/bin/env python3
"""Deterministic quality gate for a draft. Fail-closed.

Usage: python3 scripts/gate.py <RUN_ID> <SLUG>

Checks (code, not an LLM):
  - every number in meta.numbers_used maps to a VERIFIED claim with a matching value
  - every source URL resolves
  - no em dashes in the draft (outside <title>)
  - required sections present (chart, methodology, sources)
Writes runs/<RUN_ID>/gate.json and stamps confidence/status into the draft meta.json.
Exit 0 if passed, 1 otherwise.
"""
import json, re, sys, html, urllib.request, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUN_ID, SLUG = sys.argv[1], sys.argv[2]
run_dir = ROOT / "runs" / RUN_ID
draft_dir = ROOT / "public" / "drafts" / SLUG
index_p, meta_p = draft_dir / "index.html", draft_dir / "meta.json"
gate_out = run_dir / "gate.json"

def load(p, default=None):
    try:
        return json.loads(pathlib.Path(p).read_text())
    except Exception:
        return default

claims = load(run_dir / "claims.json", {}) or {}
verified = load(run_dir / "verified.json", {}) or {}
meta = load(meta_p, None)

failures, warnings = [], []

# value per claim id (from research) and the set of verified ids (from verify)
claim_value = {c.get("id"): c.get("value") for c in claims.get("claims", []) if "id" in c}
vinfo = verified.get("summary", {})
verified_ids = set(vinfo.get("verified_ids", []))
vetoed_ids = set(vinfo.get("vetoed_ids", []))
abstain = bool(vinfo.get("abstain"))
cross_ok = vinfo.get("cross_comparison_ok", True)

def close(a, b):
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    return abs(a - b) <= max(0.05, abs(b) * 0.001)

held = abstain or not index_p.exists() or meta is None

if not held:
    text = index_p.read_text()
    body = re.sub(r"(?is)<title>.*?</title>", "", text)
    # Stray-number scan runs on PROSE ONLY (lede + body) so the chart axis, the
    # meta date line, and the sources list don't create false positives.
    prose_html = " ".join(re.findall(r'(?is)class="di-lede">(.*?)</p>', text) +
                          re.findall(r'(?is)<div class="di-body">(.*?)</div>', text))
    visible = html.unescape(re.sub(r"(?s)<[^>]+>", " ", prose_html))

    # 1) every used number must be a verified claim with matching value
    for nu in (meta.get("numbers_used") or []):
        cid, val = nu.get("claim_id"), nu.get("value")
        if cid not in verified_ids:
            failures.append({"type": "unverified_number", "detail": f"{val}{nu.get('unit','')} (claim {cid}) is not verified"})
        elif not close(val, claim_value.get(cid)):
            failures.append({"type": "number_mismatch", "detail": f"{val} != source {claim_value.get(cid)} (claim {cid})"})

    # stray numbers in the body that aren't declared/verified (warning only)
    allowed = set()
    for nu in (meta.get("numbers_used") or []):
        allowed.add(round(float(nu.get("value", 0)), 3))
    allowed |= {0.0, 25.0, 50.0, 75.0, 100.0}
    for tok in re.findall(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b", visible):
        n = float(tok.replace(",", ""))
        if 1900 <= n <= 2100 and n == int(n):
            continue  # year
        if round(n, 3) not in allowed:
            warnings.append({"type": "stray_number", "detail": tok})

    # 2) URLs resolve
    urls = list(dict.fromkeys((meta.get("source_urls") or []) + re.findall(r'href="(https?://[^"]+)"', text)))
    for u in urls:
        try:
            req = urllib.request.Request(u, method="GET", headers={"User-Agent": "Mozilla/5.0 insight-gate"})
            with urllib.request.urlopen(req, timeout=12) as r:
                if r.status >= 400:
                    failures.append({"type": "dead_url", "detail": f"{u} -> {r.status}"})
        except urllib.error.HTTPError as e:
            if e.code in (403, 405, 429):
                warnings.append({"type": "url_blocked", "detail": f"{u} -> {e.code} (likely live, bot-blocked)"})
            else:
                failures.append({"type": "dead_url", "detail": f"{u} -> {e.code}"})
        except Exception as e:
            failures.append({"type": "dead_url", "detail": f"{u} -> {type(e).__name__}"})

    # 3) no em dashes outside <title>
    if "—" in body or "&mdash;" in body:
        failures.append({"type": "em_dash", "detail": "draft body contains an em dash"})

    # 4) required sections
    for marker, name in (("di-figure", "missing_chart"), ("di-method", "missing_method"), ("di-sources", "missing_sources")):
        if marker not in text:
            failures.append({"type": name, "detail": f"required section '{marker}' not found"})

passed = (not held) and not failures

if held:
    confidence = "low"
elif failures:
    confidence = "low"
elif vetoed_ids or not cross_ok:
    confidence = "medium"
else:
    confidence = "high"

if meta is not None:
    meta["confidence"] = confidence
    meta["status"] = "draft"
    meta["sources_count"] = len(meta.get("source_urls") or [])
    meta_p.write_text(json.dumps(meta, indent=2))

gate_out.write_text(json.dumps({
    "passed": passed, "held": held, "failures": failures,
    "warnings": warnings, "confidence": confidence,
}, indent=2))

print(f"gate: passed={passed} held={held} failures={len(failures)} warnings={len(warnings)} confidence={confidence}")
for f in failures:
    print("  FAIL", f["type"], "-", f["detail"])
sys.exit(0 if passed else 1)
