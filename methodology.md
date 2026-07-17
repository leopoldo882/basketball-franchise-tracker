# Methodology log

Every methodological choice, its one-line rationale, and the main alternative.
Choices marked DEFERRED are flagged for an explicit decision in Phase 2, not
decided silently.

## Decided (user rulings, 2026-07-15)

**Budget-vs-performance uses regular-season standings for every season.**
Rationale: playoffs are a small-sample knockout; regular season is the consistent
34-ish-game basis available for all seasons from the EuroLeague API.
Alternative: final post-playoff placement (rejected — inconsistent format across
seasons and a much noisier measure of season-long strength).

**BasketNews payroll and total-budget figures are separate `figure_type` rows,
never one series.** Rationale: the 2025-26 research reports net player payroll
while earlier seasons report gross total budgets — merging them would fabricate
a trend. Alternative: single "budget" series with footnotes (rejected — the
definitional break would be invisible in charts).
Related caveat to carry into Phase 2: within `payroll_net` itself, 2021-22 and
2024-25 cover players+coaches while 2025-26 covers players only.

**Turkish club stocks (FENER.IS, GSRAY.IS, BJKAS.IS, TSPOR.IS) excluded from the
headline listed index.** Rationale: TRY depreciation and retail-speculative
trading dominate their price series, which would swamp the football-business
signal. Alternative: include them with FX conversion (rejected — conversion
handles the currency but not the speculative-trading noise; also their basketball
exposure is indirect, via multi-sport club structures).

**US holdcos (MSGS, BATRA, TKO, MSGE) are a separate labeled comparator line,
never blended into the headline index.** Rationale: different market, currency,
and business models (arena/media holdcos vs football clubs). Alternative: one
global sports index (rejected — mixing regimes hides more than it shows).

**TKO price history before 2023-09-12 is dropped at collection.** Rationale: the
ticker's earlier history is the legacy WWE listing, a different entity.
Alternative: keep the full series with a note (rejected — too easy to misread in
a chart).

**Swiss SB League dropped.** Rationale: no published club financials exist.
Gets one line in the dashboard caveats section.

**Equal weighting for the headline listed-clubs index.** Rationale: with 12
members and market caps spanning two orders of magnitude, value weighting makes
the index a proxy for its largest one or two names. Alternative: value
weighting (noted; can be added as a robustness line in Phase 2 if wanted).

## Deferred to Phase 2 (must be decided explicitly)

- Benchmark form: S&P 500 total return (^SP500TR) vs price (^GSPC); European
  benchmark: ^STOXX (price) vs IEUR (an investable total-return proxy).
- Currency handling for the European index (local-currency returns vs converting
  everything to EUR or USD).
- Inflation adjustment for the NBA valuation CAGR (nominal vs real).
- Index rebalancing convention (when members list/delist mid-sample).

## Data-collection notes

- All scrapers use a custom descriptive User-Agent and a 3-second delay, and
  cache raw responses in data/raw/ so a site is never re-hit for re-parsing.
  data/raw/ is gitignored (copyrighted page content stays local).
- BasketNews figures are BasketNews's own research estimates, often ranges;
  both range endpoints are kept (`amount_low_eur_m`, `amount_high_eur_m`).
- EuroLeague standings come from the official open XML API
  (api-live.euroleague.net); regular-season group only.
- Forbes NBA values: Wayback snapshots for 2016/2019/2022 + manual entry for the
  2024 and 2025 editions (see data_inventory.md for the access rationale).
- Team names are joined across sources only via data/mappings/team_names.csv
  (`canonical_name`); the pipeline flags any unmapped team.
- Forbes `list_year` is the Forbes edition label: editions from 2021 onward were
  published in October of the preceding calendar year (2022 edition = Oct 2021).

## Known data gaps (carry into dashboard caveats)

- 2021-22 EuroLeague standings contain 15 teams: the official API excludes the
  three Russian clubs (CSKA, UNICS, Zenit) expelled mid-season. Their 2021-22
  budget rows exist but have no standings counterpart for that season.
- Baskonia disclosed no 2021-22 figures ('-' in the source table); six clubs
  lack the 2021-22 gross-salary column. The clean CSV mirrors the source gaps.
- BasketNews 2025-26 ASVEL payroll: the table carries BasketNews' range estimate
  (€4.5-5.0M) while the article prose cites the officially declared €4.5M; the
  pipeline keeps the table figure.
