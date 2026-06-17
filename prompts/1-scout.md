# Stage 1: Scout

You pick ONE topic for today. The bar is high: it must have a **Switzerland or EU angle** AND **add
something beyond simply restating one source**. A faithful rephrase of a single global finding is a
REJECT.

Read first: `brief/SCOPE_AND_STYLE.md` (scope, value bar, facts vs derived), `brief/topics.md`,
`state/used-topics.json` (never repeat these), and glance at `public/drafts/` for recent topic_areas.

Procedure:
1. Build a candidate pool from `brief/topics.md` AND a fresh web search for recent, credible, in-scope
   developments. Weight list and radar EQUALLY. Drop anything already used or too similar.
2. For each candidate, probe TWO things with WebSearch/WebFetch:
   a. a credible source for the core finding (numbers), and
   b. a **Swiss or EU hook**: a Swiss/EU data point, comparison, or implication you could localize or
      synthesize toward (FSO/BFS, KOF, SECO, SNB, Eurostat, EU AI Act, Swiss AI Initiative, etc.).
   A candidate with no real Swiss/EU hook is rejected, no matter how interesting globally.
3. Decide the **value_add**: `localize` (surface the Swiss/EU number on a global trend) or `synthesize`
   (combine 2+ sources into an implication none stated). The data check decides the winner; tiebreak
   toward a `topic_area` different from recent drafts.

Write `runs/{{RUN_ID}}/topic.json`:
```json
{
  "slug": "kebab-case-slug",
  "title": "working finding with the Swiss/EU angle",
  "topic_area": "jobs | adoption | compute | policy | energy | talent | research | funding | health | ...",
  "scope_note": "Switzerland | EU | Switzerland-vs-global",
  "value_add": "localize | synthesize",
  "swiss_angle": "one sentence: the specific Swiss/EU angle and what data supports it",
  "angle": "one sentence: the question this insight answers",
  "source_leads": [ { "label": "core source", "url": "https://..." } ],
  "swiss_source_leads": [ { "label": "Swiss/EU data hook", "url": "https://..." } ],
  "rationale": "one sentence naming the MOAT: why this is differentiated, not a rephrase"
}
```

If you genuinely cannot find a candidate with BOTH a real finding AND a Swiss/EU data hook, write
`"slug": "none"` with a `rationale`, and stop. Do not invent sources or a fake Swiss angle.
