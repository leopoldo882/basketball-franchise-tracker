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

## Decided (user rulings, 2026-07-17 — Phase 2)

**Benchmarks in total-return form: ^SP500TR for the US; IEUR adjusted close as
the Europe TR proxy.** Rationale: club prices are adjusted closes (dividends
reinvested), so total-return benchmarks are the apples-to-apples comparison;
^STOXX is price-only and would flatter the clubs against Europe. Alternative:
price indices (^GSPC / ^STOXX) — rejected as an inconsistent comparison basis.
Caveat: IEUR is an investable ETF (fee drag, inception 2014), not the pure index.

**Currency: everything converted to EUR using daily FX rates from yfinance.**
Rationale: one reporting currency makes index levels and cross-market
comparisons directly interpretable for a European-focused project. Alternative:
local-currency returns per listing (avoids FX noise per name but makes the
aggregate index meaningless as an investable series). Implementation note:
CCP.L quotes in pence (GBp) — divide by 100 to GBP before converting to EUR.

**Inflation: nominal throughout the dashboard; real-terms appears only as one
computed CAGR in the note-support facts sheet.** Rationale: every chart stays on
one consistent nominal basis; the single real CAGR gives the note an
inflation-aware anchor without doubling every series. Alternative: deflate all
series (rejected — adds a CPI dependency to every number for little insight).

**Index construction: equal-weight, rebalanced monthly.** Rationale: monthly
rebalancing keeps the index genuinely equal-weight as prices drift, so the
stated methodology holds at every point in the sample. Alternative:
equal-weight buy-and-hold (drifts toward past winners and quietly becomes
value-weighted).

## Implementation choices (Phase 2, logged during build)

**Index inception 2004-01, members enter on listing (staggered).** Rationale:
2004-01 is the earliest month every needed FX pair exists on yfinance
(EURUSD/EURDKK start 2003-12); starting the index only when all 12 members
trade would discard eight years. Alternative: fixed composition — provided as
the `eu_football_fixed12` robustness series (only months where all 12 members
trade, i.e. after MANU's 2012-08 listing), so the headline result can be
checked against a constant-membership window. `n_members` is a column in the
monthly output, keeping the staggered entry visible rather than implicit.

**No silent mixed-window statistics.** Every row of listed_index_stats.csv
carries explicit window_start / window_end / n_months. IEUR comparisons are
computed on 2014+ only (its inception) and labeled. ^STOXX is included as a
secondary comparator for pre-2014 context but is a PRICE-ONLY index compared
against dividend-reinvested club prices — it understates the benchmark; this
mismatch is noted on every ^STOXX row. Alternative: a single spliced Europe
benchmark (rejected — splicing price and TR series manufactures a fake series).

**NBA-vs-S&P comparison stays in USD.** NBA franchise values are USD figures;
converting both sides to EUR would only add FX noise to a US-domestic
comparison. The EUR conversion ruling applies to the listed index, where the
portfolio itself is multi-currency. CAGR windows use edition publication
months (Feb of the edition year through 2020; Oct of the preceding year from
2021 on), logged in analysis/nba_growth.py.

**US CPI source: FRED CPIAUCSL** (open CSV endpoint, no key) — feeds only the
single real-terms CAGR in the facts sheet. Alternative: manual BLS entry
(rejected — the FRED fetch is one request and stays within the stack).

## Known biases

**Survivorship bias in the listed index:** the index contains only clubs listed
today — clubs that delisted along the way (AS Roma in 2022, and any earlier
exits) are absent from the entire history. The index therefore likely
overstates the historical experience of investing in "listed football clubs".
Flagged honestly in the dashboard caveats; no adjustment attempted.

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
