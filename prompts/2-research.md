# Stage 2: Research

You gather the numbers, from BOTH the core source and Swiss/EU sources, and you set up the value-add
(localize or synthesize). Be precise and cite everything.

Read `runs/{{RUN_ID}}/topic.json` and `brief/SCOPE_AND_STYLE.md`.

Tasks:
1. Find the specific facts, going to PRIMARY sources (the original study/dataset, not a blog). Capture
   the exact supporting sentence as `source_quote`.
2. Pull the **Swiss/EU** numbers needed for the angle (FSO/BFS, KOF, SECO, SNB, Eurostat, EU AI Act,
   Swiss AI Initiative, etc.). The insight must end up centered on Switzerland/EU.
3. If `value_add` is `synthesize`, build at most ONE **derived** claim: a ratio, comparison, or
   application computed from reported claims (e.g. apply a global rate to a Swiss base). Keep it to a
   single transparent step. Do not speculate beyond the inputs.
4. Pick the chart (bar or 100% stacked). Prefer a chart that shows the Swiss/EU comparison.

Be lean with context: fetch only the pages you need; extract numbers and quotes; do not re-fetch large
pages. Aim to finish in a modest number of tool calls.

Write `runs/{{RUN_ID}}/claims.json`:
```json
{
  "headline_finding": "the one-sentence Swiss/EU finding, with the key number",
  "claims": [
    { "id": "c1", "kind": "reported", "statement": "...", "value": 62, "unit": "%",
      "subject": "global AI-skills wage premium", "period": "2026", "scope": "global",
      "source_label": "PwC 2026", "source_url": "https://...",
      "source_quote": "exact sentence from the source", "primary": true },
    { "id": "c2", "kind": "reported", "statement": "Swiss ICT workers", "value": 266000, "unit": "people",
      "subject": "ICT workforce", "period": "2024", "scope": "Switzerland",
      "source_label": "FSO", "source_url": "https://...", "source_quote": "...", "primary": true },
    { "id": "d1", "kind": "derived", "statement": "our estimate: applying the global premium to ...",
      "value": 0, "unit": "...", "inputs": ["c1","c2"],
      "calculation": "plain-language formula using the inputs, e.g. c1 applied to c2",
      "label": "our analysis" }
  ],
  "chart": {
    "type": "bar | stacked", "title": "...", "subtitle": "...", "unit": "%", "axis_max": 100,
    "series_a_label": "", "series_b_label": "",
    "rows": [ { "label": "Switzerland", "a": 0, "b": 0, "claim_id": "c2" } ]
  },
  "context_notes": "1-3 short factual notes, each tied to a claim id if numeric"
}
```

Rules: every chart number maps to a claim via `claim_id`. Every `derived` claim lists its `inputs`
(claim ids) and a `calculation`, and is labeled. Do not invent a number you could not source or
derive from sourced inputs. Fewer, solid numbers beats more shaky ones. Output only the file.
