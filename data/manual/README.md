# Manual-entry CSVs — column documentation

These files hold figures keyed in by hand from sources that can't or shouldn't be
scraped (paywalls, ToS restrictions, PDFs, prose articles — see data_inventory.md).
`run_pipeline.py` validates each file's columns, numeric fields, and duplicate keys.

Conventions: monetary amounts in millions (`_usd_m` / `_eur_m`), plain numbers
(45 = 45 million, 10000 = 10 billion). Every row needs a `source_url`. Blank cells
are fine where a figure is unknown.

## nba_valuations_manual.csv
Forbes NBA list rows that aren't auto-scraped: the 2024 and 2025 editions, plus any
Wayback snapshot year (2016/2019/2022) the parser reports as failed.
- `list_year` — Forbes edition year (2025 = list published Oct 2025)
- `team`, `rank` — as printed in the list
- `value_usd_m`, `revenue_usd_m` — franchise value and revenue, $M
- `source` — use `forbes_manual`
- `source_url` — the Forbes article the row was keyed from

## publisher_divergence.csv
Latest-year cross-check of Forbes vs Sportico vs CNBC valuations (per-team, $M).
Feeds one caveat stat ("publishers disagree by X% on average"), not a panel.
- `publisher` — `sportico` or `cnbc` (Forbes side comes from nba_valuations.csv)

## lnb_dnccg.csv
Headline figures from the LNB's DNCCG annual reports (official PDFs — keyed by
hand, no PDF dependency). Scope: Betclic Élite only, 2023-24 and 2024-25 accounts.
- `season` — e.g. `2023-24`
- `revenue_eur_m`, `payroll_eur_m`, `net_result_eur_m` — €M, negative = loss

## euroleague_valuations.csv
JB Capital valuation figures, keyed from the official EuroLeague press release
(March 2026). Pre-seeded. Add club-level rows if the underlying report PDF is found.
- `entity_type` — `league`, `clubs_aggregate`, `combined`, `club_range`, or `club`
- `value_eur_m_low/high` — equal when a single figure was reported
- `basis` — one line on what the number represents

## transactions.csv
Precedent deals in basketball and comparable sports. Pre-seeded with the deals
confirmed during Phase 0 recon; rows with empty `source_url` or figures marked
"verify" in `notes` need checking before use in analysis.
- `buyer_type` — `individual`, `private equity`, `sovereign-linked`, `mixed`
- `stake_pct` — blank if undisclosed; `control` — `y`/`n`
- `price_usd_m` — price paid for the stake; `implied_valuation_usd_m` — 100% valuation

## acb_budgets.csv / lba_budgets.csv
Headline club budgets from Spanish/Italian media reports (no official dataset).
- `figure_type` — `total_budget` or `revenue`, as described by the source
