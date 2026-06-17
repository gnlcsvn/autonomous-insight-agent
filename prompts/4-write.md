# Stage 4: Write

You write the draft, using ONLY verified claims (reported or derived), centered on Switzerland/EU.

Read: `runs/{{RUN_ID}}/topic.json`, `runs/{{RUN_ID}}/claims.json`, `runs/{{RUN_ID}}/verified.json`,
`brief/SCOPE_AND_STYLE.md`, `brief/DRAFT_TEMPLATE.html`.

Rules:
- Use only `verified: true` claims. If `verified.json` set `abstain: true`, do NOT write a draft;
  write `public/drafts/{{RUN_ID}}-{slug}/meta.json` with `"confidence":"low"`, `"status":"draft"`,
  and a `"hold_reason"`, then stop.
- **Lead with the Swiss/EU "so what,"** not a restatement of the global headline. The title and lede
  should make the Swiss/EU angle the point.
- **Label every derived claim** in the prose as our analysis (e.g. "our estimate", "applying X to Y
  suggests"), never as a source's finding. In "How we measured this", show the derivation
  (the inputs and the calculation) for each derived number.
- If `cross_comparison_ok` is false, include the `comparability_note` honestly.
- House style (brief): one chart in the site idiom built from the verified chart spec (bar fill width =
  value / axis_max * 100%); methodology with a small figures table + limitations; sources with working
  links. **No em dashes.** No "what we removed" notes.

Write (slug = `{{RUN_ID}}-` + the topic slug):
1. `public/drafts/{slug}/index.html` — filled template (replace every `{{...}}`; keep asset paths and
   the export button).
2. `public/drafts/{slug}/meta.json`:
```json
{ "slug": "{slug}", "title": "...", "summary": "one line", "date": "{{RUN_DATE}}",
  "topic_area": "...", "scope_note": "Switzerland | EU | Switzerland-vs-global", "status": "draft",
  "sources_count": 0,
  "numbers_used": [ { "value": 62, "unit": "%", "claim_id": "c1" } ],
  "source_urls": [ "https://..." ] }
```
   `numbers_used` must list EVERY numeric value in the draft body and chart, each tied to a verified
   claim id (reported or derived). The gate rejects any number not backed by a verified claim.
Output only the files.
