# Stage 5: Critic (runs ONLY when the gate failed)

The deterministic gate rejected the draft. Fix exactly the listed problems. Do not rewrite for taste.

Read: `runs/{{RUN_ID}}/gate.json` (the failures), the draft at `public/drafts/{slug}/index.html`,
`public/drafts/{slug}/meta.json`, and `runs/{{RUN_ID}}/verified.json`.

For each failure in `gate.json.failures`, fix the specific cause:
- `unverified_number`: remove the offending number or replace it with a `verified: true` claim, and
  update `meta.json.numbers_used`. Never add a number that is not verified.
- `dead_url`: replace with a working source URL for the same fact, or remove the claim and any number
  that depended only on it.
- `em_dash`: replace every em dash with a comma, colon, or period.
- `missing_chart` / `missing_method` / `missing_sources`: add the missing required section.

Edit the draft and `meta.json` in place. Change only what the failures require. Do not introduce new
claims or numbers beyond the verified set. Output only the edited files.
