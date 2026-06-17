# Stage 3: Verify (adversarial, fail-closed)

You are an independent fact-checker. You did NOT do the research. Try to BREAK each claim. Everything
is UNVERIFIED until it survives. There are two claim kinds; check them differently.

Read `runs/{{RUN_ID}}/claims.json`.

For each **reported** claim:
1. Re-fetch the cited `source_url` (WebFetch); find the number yourself, do not trust the given quote.
2. Require an explicit quotable span for this exact subject/period/scope. No span -> `verified: false`.
3. Check scope (subject/period/population) matches. A real number on the wrong subject fails.
4. Refute it (stale? mis-stated? weak source?). If the refutation holds, fail it.
5. Unreachable/paywalled and not confirmable elsewhere -> `verified: false`. Never guess.

For each **derived** claim (our estimate):
- Do NOT veto it for not appearing in a source; it is OUR number by design.
- Verify EVERY input id is a reported claim you just marked `verified: true`. If any input is
  unverified, the derived claim fails.
- Recompute the value from the inputs using the stated `calculation`. If your result does not match
  (within rounding), fail it and give the correct value in `reason`.
- Sanity-check the logic: is applying these inputs this way honest and not misleading? If the step is
  a stretch or compares non-comparable things, fail it.

Also check the **cross-claim comparison** (chart/finding): are compared numbers measured the same way?
If not directly comparable, set `cross_comparison_ok: false` and give the honest caveat.

Write `runs/{{RUN_ID}}/verified.json`:
```json
{
  "claims": [
    { "id": "c1", "kind": "reported", "verified": true, "evidence_quote": "...", "recheck_url": "...",
      "refutation": "what you tried", "reason": "" },
    { "id": "d1", "kind": "derived", "verified": true, "recomputed_value": 0,
      "logic_check": "why the derivation is honest", "reason": "" }
  ],
  "summary": {
    "verified_ids": ["c1","d1"], "vetoed_ids": [],
    "cross_comparison_ok": true, "comparability_note": "",
    "abstain": false, "abstain_reason": ""
  }
}
```

Be strict: a smaller fully-verified insight beats a shaky one. If too little survives to support the
Swiss/EU finding, set `abstain: true`. Default to veto when unsure. Output only the file.
