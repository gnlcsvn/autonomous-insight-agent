#!/usr/bin/env python3
"""Rebuild the review-queue grid (public/index.html) from public/drafts/*/meta.json.

Deterministic: the daily generator only writes a draft folder + meta.json; this
script renders the grid so the index never depends on the model's HTML output.
Run after each generation:  python3 scripts/build-index.py
"""
import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFTS = ROOT / "public" / "drafts"
OUT = ROOT / "public" / "index.html"

def load_drafts():
    items = []
    if not DRAFTS.exists():
        return items
    for d in sorted(DRAFTS.iterdir()):
        meta = d / "meta.json"
        if not (d.is_dir() and meta.exists()):
            continue
        try:
            m = json.loads(meta.read_text())
        except Exception:
            continue
        m["slug"] = m.get("slug", d.name)
        items.append(m)
    # newest first by date string, then slug
    items.sort(key=lambda m: (m.get("date", ""), m.get("slug", "")), reverse=True)
    return items

def esc(s):
    return html.escape(str(s), quote=True)

def card(m):
    conf = (m.get("confidence") or "medium").lower()
    if conf not in ("high", "medium", "low"):
        conf = "medium"
    area = esc(m.get("topic_area", "insight"))
    date = esc(m.get("date", ""))
    title = esc(m.get("title", "(untitled)"))
    summary = esc(m.get("summary", ""))
    slug = esc(m.get("slug"))
    nsrc = m.get("sources_count", 0)
    scope = esc(m.get("scope_note", ""))
    return f"""      <a class="card" href="drafts/{slug}/">
        <div class="card__meta"><span>{area}</span><span>&middot; {date}</span><span class="badge {conf}">{conf}</span></div>
        <h2 class="card__title">{title}</h2>
        <p class="card__summary">{summary}</p>
        <div class="card__foot"><span>{nsrc} source(s)</span><span>{scope}</span></div>
      </a>"""

def main():
    items = load_drafts()
    cards = "\n".join(card(m) for m in items)
    if not items:
        cards = '      <p class="empty">No drafts yet. The daily generator will drop the first one here.</p>'
    grid_open = '<div class="grid">' if items else "<div>"
    grid_close = "</div>"
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Insight drafts: review queue</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <header class="rq-header">
    <div class="rq-kicker">Private review queue &middot; rumpelkammer</div>
    <h1 class="rq-title">Insight drafts</h1>
    <p class="rq-sub">Auto-generated drafts to skim each morning. Keep the good, kill the rest. {len(items)} in queue.</p>
  </header>
  <main class="grid-wrap">
    {grid_open}
{cards}
    {grid_close}
  </main>
</body>
</html>
"""
    OUT.write_text(doc)
    print(f"Wrote {OUT} with {len(items)} draft(s).")

if __name__ == "__main__":
    main()
