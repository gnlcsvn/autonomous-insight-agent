# Insight draft factory — scope, style, and output contract

This is the spec the daily generator follows. Goal: produce **one draft Data Insight per day** for a
private review queue. The bar is a **~90%-good draft**, not a publish-ready piece. A human curates the
queue each morning and develops keepers further (deep verification + polish) in a separate session.

## The beat (scope) — Switzerland / Europe REQUIRED
How **AI is reshaping work, the economy, and society**, told through data, **centered on Switzerland
(first) and the EU (second)**. Every insight must have a Swiss or European angle. A global or US
finding is allowed ONLY as a benchmark *inside* a Swiss/EU story (e.g. "globally X; in Switzerland Y").
A pure global/US insight with no Swiss/EU angle is out of scope.

Already published (do not repeat; use for tone + dedup):
- "Swiss SME AI adoption jumped from 22% to 34% in a year" (AXA/Sotomo).
- "Two-thirds of Google searches now end without a click" (SparkToro; AI Overviews; US vs EU).

## The value bar — add something the sources did not say
A faithful rephrase of one source is NOT good enough and should be rejected at scout time. Every
insight must do at least one of:
1. **Localize** — surface the Swiss/EU number on a trend others discuss only globally; or
2. **Synthesize** — combine 2+ sources into a comparison, ratio, or implication none of them stated; or
3. **Imply** — draw a clearly-labeled implication for Switzerland/EU that the sources leave implicit.

Default format: **a broader finding, then what it means for Switzerland** (with Swiss data where it
exists, or a transparent derived implication where it does not).

## Facts vs. derived claims (how we add value without losing rigor)
- A **reported** claim is a number stated in a source. It must trace to that source (quote + URL).
- A **derived** claim is OUR number: a ratio, combination, or application computed from reported
  claims. It is allowed ONLY if every input is a verified reported claim AND the calculation is
  explicit. In the prose and methodology it must be **labeled as our estimate/analysis** (e.g.
  "applying the global premium to Swiss ICT wages suggests..."), never presented as a source's finding.
- Keep derived claims to simple, transparent steps (one ratio or one application). Multi-step
  speculative projections are TIER 2 (below), not for the daily draft.

## Two tiers
- **Tier 1 (this daily factory):** localize + light synthesis. Defensible, mostly sourced, one
  labeled derived step at most.
- **Tier 2 (human "develop further"):** deeper original projections/estimates. NOT produced here; the
  human does these when promoting a draft.

## Swiss / EU sources to reach for
FSO/BFS (PX-Web), SECO, KOF (ETH), SNB, CSCS, cantonal stats offices, Swiss AI Initiative / EPFL-ETH,
digitalswitzerland; EU: Eurostat, EU AI Watch / AI Act, OECD.AI; benchmark anchors: Stanford AI Index,
Epoch AI, Our World in Data. Prefer primary/official; mark consultancy/press as secondary.

## House style (match gianlucasavino.com)
- **Title = the finding**, as a sentence, with the Swiss/EU angle where natural.
- **Lede** states the finding with the key numbers inline.
- **One chart**, site idiom: system sans, accent blue ~45% for the main series, gray for secondary,
  **no gridlines, no shadows**. Bar or 100%-stacked-bar from `assets/style.css`.
- **"How we measured this"**: source, a small figures table, limitations, and the **derivation of any
  derived number**.
- **Sources** list with working links.
- Be honest about scope and uncertainty (Swiss vs EU vs global, secondary source, estimate).
- **No em dashes** anywhere. **No "what we removed during fact-checking" notes.**

## Rigor (even for a draft)
- Every reported number traces to a findable source; if you cannot source it, do not use it.
- Every derived number has verified inputs + an explicit calculation + an "our analysis" label.
- A smaller, fully-grounded insight beats a bigger shaky one. If no real Swiss/EU angle with data
  exists today, set `confidence: low` / abstain rather than inventing.

## Output contract (strict)
Write the draft into `public/drafts/<slug>/`:
- `index.html` — built from `../../brief/DRAFT_TEMPLATE.html`, linking `../../assets/style.css`,
  `../../lib/html-to-image.min.js`, `../../js/insight.js`.
- `meta.json` — fields: `slug, title, summary, date, topic_area, scope_note (Switzerland|EU|...),
  status:"draft", sources_count, numbers_used:[{value,unit,claim_id}], source_urls:[...]`.
Do not edit `public/index.html` (the grid is rebuilt by `scripts/build-index.py`).
