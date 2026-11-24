# Hand-entered data

Figures typed in from sources that can't or shouldn't be scraped (paywalls, terms of use, PDFs,
numbers buried in article text). See data_inventory.md for why each source is manual.
`run_pipeline.py` checks each file's columns, number fields and duplicate rows on every run.

Money is in millions (`_usd_m`, `_eur_m`): 45 means 45 million, 10000 means 10 billion. Every row
has a `source_url`. Leave a cell blank if the figure isn't known.

## nba_valuations_manual.csv
Forbes NBA rows for any edition without an archived copy (see collectors/forbes_wayback.py).
Empty at the moment: every edition used is in the archive.
- `list_year`: Forbes edition (2025 = list published October 2025)
- `team`, `rank`: as printed
- `value_usd_m`, `revenue_usd_m`: team value and revenue
- `source`: `forbes_manual`
- `source_url`: the Forbes article

## publisher_divergence.csv
Sportico and CNBC values for the teams whose figures were republished elsewhere, for the check
against Forbes. Not a full list for either publisher.
- `publisher`: `sportico` or `cnbc`
- `list_year`: that publisher's edition (Sportico 2026 = Oct 2026, CNBC 2026 = Feb 2026)
- `source_url`: the page the value was copied from (Bleacher Report, NBC Chicago)

## lnb_dnccg.csv
French top division (Betclic Élite) figures from the league's financial watchdog.
- `season`: e.g. `2025-26`
- `club`: club name, or a group such as `Betclic ELITE (all clubs)` for league totals
- `figure_type`:
  - `budget_total`: budget filed in September, defined by the league as total revenue
  - `payroll_dnccg`: gross payroll for players and coaches approved by the DNCCG
  - `operating_result`, `net_result`: from the audited accounts (negative = loss)
- `amount_eur_m`

## euroleague_valuations.csv
JB Capital's valuation, from the EuroLeague press release of March 2026.
- `entity_type`: `league`, `clubs_aggregate`, `combined`, `club_range` or `club`
- `value_eur_m_low`, `value_eur_m_high`: the same number when a single figure was given
- `basis`: one line on what the number is

## transactions.csv
NBA deals and a few European basketball events.
- `date`: month the price was agreed (YYYY-MM), or just the year if that's all that's known
- `buyer_type`: `individual`, `private equity`, `sovereign-linked` or `mixed`
- `stake_pct`: blank if not disclosed; `control`: `y` or `n`
- `price_usd_m`: price paid for the stake, if reported
- `implied_valuation_usd_m`: value of 100% of the team implied by the deal
- `notes`: approval status, payment stages and anything else needed to read the row

## acb_budgets.csv / lba_budgets.csv
Spanish and Italian club budgets from media reports. Different seasons and definitions from the
other files, so reference only.
- `figure_type`: `total_budget` or `revenue`, whichever the source says
