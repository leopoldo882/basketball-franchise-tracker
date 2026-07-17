# Data Inventory — Phase 0 recon

Recon date: 2026-07-15. Everything below was checked live on this date (robots.txt
fetches, test requests, yfinance calls). "Scrapable" means: allowed by robots.txt for
a generic user-agent, technically reachable with our stack, and no explicit ToS bar
found. Where ToS were not fully verified this is flagged.

---

## 1. NBA franchise valuations

### 1a. Forbes annual NBA team valuations
- **URL:** annual list article, e.g. 2025 edition:
  https://www.forbes.com/sites/justinteitelbaum/2025/10/23/the-most-valuable-nba-teams-2025/
  (interactive list at https://www.forbes.com/nba-valuations/list/ — JS-rendered)
- **What it contains:** all 30 teams: value, 1-yr % change, revenue, operating income.
  Revenue column matters — it lets us compute value/revenue multiples ourselves.
- **History:** published annually since the 1991-92 season. Older editions reachable
  via each year's article and via Wayback Machine snapshots of
  `forbes.com/nba-valuations/list/` (verified snapshots: 2016, 2019, 2022; the URL
  appears stale after ~2023, later years live in the annual articles instead).
- **Scrapable:** robots.txt (checked 2026-07-15) allows article pages for `User-agent: *`
  (only /search/, /ajax/, /forbesapi-ish infra paths disallowed). Forbes ToS not
  verified in detail — large publishers typically prohibit automated collection.
  The tried-and-tested `forbesapi` JSON endpoint pattern returned empty for NBA lists
  (tested live), so no clean API route exists anyway.
- **Update frequency:** annual (typically October).
- **Verdict: MANUAL-ENTRY CSV**, keyed from the annual articles (30 rows/year, they
  are free to read).
- **DECIDED (2026-07-15):** full 30-team panel at snapshot years only — 2016, 2019,
  2022 (Wayback) plus the two most recent live editions (2024, 2025 articles —
  manual). Value + revenue per team. Supports both the league CAGR and top-5 vs
  bottom-5 dispersion over time.
- **Phase 1 upgrade:** the archived HTML pages turned out to be empty JS shells,
  but the Wayback Machine also archived the JSON endpoint the page loaded from
  (`forbes.com/ajax/list/data?year=YYYY&uri=nba-valuations&type=organization`,
  found via the Wayback CDX index). Full 30-team value+revenue JSON for the three
  snapshot years is now scraped automatically with pinned capture timestamps.
  Captures also exist for 2017, 2018, 2020, 2021, 2023 if the panel is ever
  widened. `list_year` = Forbes edition label (2022 = the list published Oct 2021).

### 1b. Sportico NBA valuations
- **URL:** https://www.sportico.com/feature/nba-team-values-ranking-list-1234697991/
  and annual pieces, e.g. 2025: avg $5.51B, Warriors $11.33B, total $165B.
- **History:** annual since 2020 (6 editions). Includes revenue and premium data.
- **Scrapable: NO.** Parent company PMC's Terms of Use (fetched 2026-07-15) explicitly
  prohibit "spidering, 'screen scraping,' 'database scraping'… or any other automatic
  means of obtaining… information". robots.txt also blocks AI crawlers site-wide.
- **Verdict: MANUAL-ENTRY CSV.**
- **DECIDED (2026-07-15):** latest year only, as an estimate-divergence check vs
  Forbes — produces a "publisher disagreement" caveat stat, not a second panel.

### 1c. CNBC Official NBA Team Valuations (cross-check only)
- **URL:** https://www.cnbc.com/2025/02/14/cnbcs-official-nba-team-valuations-2025.html
- **History:** new list, started 2025. One edition, maybe two by now.
- **Verdict:** manual. **DECIDED (2026-07-15):** included in the same latest-year
  publisher-divergence check as Sportico (three-way Forbes/Sportico/CNBC spread).

---

## 2. European basketball

### 2a. BasketNews EuroLeague budget/payroll research ★ core source
- **URLs (confirmed live):**
  - 2021-22: https://basketnews.com/news-159564-euroleague-team-budgets-2021-22-three-dominant-clubs.html
  - 2024-25: https://basketnews.com/news-204932-euroleague-teams-clubs-budgets.html
  - 2025-26: https://basketnews.com/news-233398-euroleague-budgets-payrolls-2026-biggest-spenders.html
  - trend piece (budgets 2021-22 → 2024-25, +29%): https://basketnews.com/news-220204-euroleague-clubs-budget-rise-panathinaikos-zvezda-olympiacos-lead.html
    (context only — carries no per-team table; confirmed during Phase 1)
  - 2022-23 and 2023-24 full roundups: not yet located as single articles; per-club
    announcements exist (e.g. Partizan news-198907, Maccabi news-195257). To confirm
    in Phase 1 via their site archive.
- **Format:** article HTML with a real `<table>` (verified by fetching 2025-26: full
  20-team table `No. | Team | Team payroll (players net)` is served in the page
  source; the BN+ paywall only gates an audio player, not the table).
- **Scrapable: YES.** robots.txt is permissive (only a feedback endpoint disallowed).
  Site returns 403 to the default `python-requests` UA but 200 to a descriptive
  custom UA (tested all three) — so our planned polite custom user-agent is required,
  not just nice-to-have. ~5 pages total, cached to /data/raw, so effectively one hit
  per page ever.
- **Major caveat (methodology-relevant):** 2025-26 figures are *net player payroll*;
  earlier seasons' articles report *club budgets*. Not directly comparable across
  seasons without care — must be logged in methodology.md and probably kept as
  separate columns.
- **Update frequency:** annual (autumn/winter).

### 2b. JB Capital EuroLeague valuation report ★ the European valuation anchor
- **Primary source (official EuroLeague press release, March 2026):**
  https://www.euroleaguebasketball.net/news/euroleague-and-clubs-valued-at-over-3-2-billion-according-to-jb-capital/
  (BasketNews coverage kept only as secondary corroboration).
- **What it contains (official figures):** combined enterprise value of league +
  licensed teams >€3.2B; the league itself €1.41B for 2025-26 (€1.64B applying the
  same multiple to estimated 2026-27 EBITDA); aggregate club valuations ~€1.8B;
  individual clubs from >€60M to >€320M on revenue-based multiples; management
  forecast of >10% revenue/EBITDA CAGR 2022-23 → 2034-35; potential combined €4.3B
  by 2026-27 if the franchise-model transition executes. This is the only club-level
  *valuation* (not budget) dataset found for European basketball.
- **History:** single snapshot (2026). No time series.
- **Verdict: MANUAL-ENTRY CSV** keyed from the official press release with full
  citation; locate the underlying JB Capital report PDF in Phase 1 for club-level
  numbers and method notes.

### 2c. EuroLeague standings — official API ★ fully automated
- **Endpoint (verified live):**
  `https://api-live.euroleague.net/v1/standings?seasonCode=E2024` — open XML, no key.
  Tested seasons E2005, E2010, E2016, E2024 — all return data; history reaches at
  least 2005, likely 2001.
- **Note:** returns regular-season/Top-16 group standings; final placements after
  playoffs/Final Four need the results endpoints or a small manual mapping per season
  (only 8 teams/season affected). The euroleaguebasketball.net website itself is
  behind Vercel bot protection — irrelevant, the API is the right door.
- **Use:** budget rank vs standing analysis, seasons 2021-22 → 2025-26 (matching the
  budget data window).
- **Update frequency:** live; we need it once per season.

### 2d. LNB / Betclic Élite (France) — DNCCG financial reports ★ best-in-class transparency
- **What exists:** the league's financial control body (DNCCG) publishes annual
  reports with actual club accounts — revenues, payroll, operating result — for all
  36 pro clubs. Official sources:
  - Reports index: https://www.lnb.fr/elite/documents-lnb/rapports-financiers-lnb/
    (hosts editions back to at least 2017-18)
  - 2022-23 accounts: https://cdn.lnb.fr/uploads/content-library/7c207068ed0fd02db181aa59d6a3e1a4f23b47143b6bf9eae1707596fd33208c.pdf
  - 2024-25 accounts press release (2026-01-23): https://cdn.lnb.fr/uploads/content-library/ae533f4f33a596f9863a45176bf64cc3e9ca72b58781c3e51a0a3933621622cc.pdf
  - 2023-24 accounts: via the reports index above (official copy; third-party
    mirrors exist but are not cited)
  - Provisional budgets each autumn via LNB newsroom (2025-26: record avg budget
    €10.3M; Monaco €38.7M, Paris €28.8M).
- **Format: PDF** — clashes with the minimal stack.
- **DECIDED (2026-07-15): MANUAL-ENTRY CSV, no PDF dependency.** Scope: top
  division (Betclic Élite) only, last two published seasons (2023-24 and 2024-25
  accounts), headline fields only: revenue, payroll, net result per club.
- **Update frequency:** annual (report ~Dec/Jan; budgets in autumn).

### 2e. ACB / Liga Endesa (Spain)
- **What exists:** no official per-club dataset. Media report budgets each season
  (e.g. https://www.solobasket.com/liga-endesa/presupuestos-acb-top — 2025-26:
  Real Madrid €45M … Manresa €3.8M; ACB aggregate revenues €168.95M in 2023-24).
- **Verdict: MANUAL-ENTRY CSV**, headline budgets for the EuroLeague-relevant clubs
  (Real Madrid, Barcelona, Baskonia, Valencia) + league aggregate. Spotty history.

### 2f. Lega Basket Serie A (Italy)
- **What exists:** no official dataset; Italian sports-finance media publish annual
  per-club revenue/bilanci pieces (e.g. sportefinanza.it: 16 clubs ~€130M combined
  2023-24; economiaesport.it club-by-club 2024-25).
- **Verdict: MANUAL-ENTRY CSV**, Milan/Bologna/Virtus + league aggregate. Comparator
  depth only.

### 2g. Swiss SB League
- **What exists: effectively nothing.** No published budgets or accounts found; the
  financial story is club mergers for survival and league contraction to 9 teams.
- **Verdict: DROP** from the dataset (worth one line in the dashboard caveats as an
  illustration of how thin small-league data is).

---

## 3. Publicly listed sports companies (verified on yfinance, 2026-07-14 close)

All tickers below were tested live with yfinance (1-month fetch + max-history probe).

| Ticker | Company | Exposure | Listed? | Daily data since |
|---|---|---|---|---|
| MSGS | Madison Square Garden Sports | NBA Knicks (+ NHL Rangers) | ✅ | 2015-09 |
| MSGE | MSG Entertainment | Arena (venue side) | ✅ | 2023-04 |
| BATRA | Atlanta Braves Holdings | MLB | ✅ | 2016-04 |
| MANU | Manchester United | Football | ✅ | 2012-08 |
| TKO | TKO Group | UFC/WWE | ✅ | 1999-10* |
| JUVE.MI | Juventus | Football | ✅ | 2001-12 |
| SSL.MI | SS Lazio | Football | ✅ | 1998-07 |
| BVB.DE | Borussia Dortmund | Football | ✅ | 2000-10 |
| AJAX.AS | Ajax | Football | ✅ | 1998-07 |
| CCP.L | Celtic | Football | ✅ | 1995-09 |
| SLBEN.LS | Benfica | Football (+ basketball section) | ✅ | 2007-05 |
| FCP.LS | FC Porto | Football (+ basketball section) | ✅ | 2000-01 |
| SCP.LS | Sporting CP | Football | ✅ | 2000-01 |
| FENER.IS | Fenerbahçe | Football club co; group runs EuroLeague side | ✅ | 2004-02 |
| GSRAY.IS | Galatasaray | Football club co; group runs BSL side | ✅ | 2002-02 |
| BJKAS.IS | Beşiktaş | Football club co | ✅ | 2002-02 |
| TSPOR.IS | Trabzonspor | Football | ✅ | 2005-05 |
| PARKEN.CO | Parken Sport (FC København) | Football | ✅ | 2000-01 |
| BIF.CO | Brøndby IF | Football | ✅ | 2000-01 |
| EFG.PA | Eagle Football Group (ex-OL Groupe, Lyon) | Football | ✅ | 2007-02 |
| ASR.MI | AS Roma | — | ❌ delisted Sep 2022 (Friedkin tender offer) | — |
| AGF.CO | AGF Aarhus | — | ❌ no data (ticker may differ) | — |

*TKO history pre-2023 is legacy WWE listing — excluded from any TKO series (or
clearly noted) per 2026-07-15 decision.

Correction from user review, verified 2026-07-15: OL Groupe was renamed Eagle
Football Group (2024) and trades on Euronext Paris as `EFG.PA` (continuous price
history back to 2007 through the OL Groupe era) — the earlier `OLG.PA` "delisted"
reading was a stale-ticker artifact. Lyon is IN the football index.

- **Benchmarks verified:** `^GSPC` (S&P 500 price, since 1927), `^SP500TR`
  (S&P 500 total return, since 1988), `^STOXX` (STOXX Europe 600, since 2004),
  `IEUR` (iShares Core MSCI Europe ETF, since 2014).
- **Honest limitation for the write-up:** there is no listed European basketball
  pure-play. MSGS is the closest basketball equity anywhere. Turkish club companies
  are the football-side entities of multi-sport clubs whose basketball teams play
  EuroLeague/BSL — exposure is indirect at best. A "listed sports index" is
  necessarily football-heavy and must be labeled as such.
- **DECIDED (2026-07-15):** headline index = European football clubs only,
  equal-weight: MANU, JUVE.MI, SSL.MI, BVB.DE, AJAX.AS, CCP.L, SLBEN.LS, FCP.LS,
  SCP.LS, EFG.PA, PARKEN.CO, BIF.CO. Turkish club stocks EXCLUDED
  (currency/speculative noise — to be logged in methodology.md with the
  alternative). MSGS + US holdcos (BATRA/TKO/MSGE) form a separate labeled
  comparator line, never blended into the headline index. Delisted names dropped.
- **Scrapable: YES** — yfinance, monthly refresh in GitHub Actions. Currency
  handling: everything converted to EUR (Phase 2 ruling; see methodology.md).
- **Phase 2 additions to the same collector family:**
  - FX rates via yfinance (`EURUSD=X` since 2003-12, `EURGBP=X` since 1999,
    `EURDKK=X` since 2003-12; verified live 2026-07-17) → data/fx_rates.csv.
  - US CPI (CPIAUCSL) via FRED's open CSV endpoint
    `https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL` (no key,
    1947→present; verified live 2026-07-17) → data/us_cpi.csv. Feeds the single
    real-terms CAGR in the facts sheet.

---

## 4. Precedent transactions (basketball + comparable sports)

No single scrapable database exists (PitchBook/Sportico deal trackers are paywalled).
**Verdict: MANUAL-ENTRY CSV** with a documented template. Seed list confirmed during
recon (all with public source links):

| Deal | Date | Stake | Implied valuation |
|---|---|---|---|
| Lakers → Mark Walter | 2025 (approved) | control | $10B |
| Celtics → Chisholm group | 2025 | ≥51%, full by 2028 | $6.1B (→$7.3B) |
| Sixth Street in Celtics | 2025 | ~12.5% | part of above |
| Trail Blazers → Dundon group | 2025 (agreed) | control | $4.25B |
| Mavericks → Adelson/Dumont | 2023 | majority | ~$3.5B |
| Suns/Mercury → Ishbia | 2023 | majority | $4B |
| Hornets → Plotkin/Schnall | 2023 | majority | ~$3B |
| Arctos in Warriors | 2021 | ~5% | n/a |
| Arctos in Kings | 2021 | ~17% | n/a |
| Arctos in Jazz | 2022 | undisclosed | n/a |
| NBA Europe franchise bids | 2026 | licenses | >$1B in top markets; 20+ groups; 16-team league targeted for Oct 2027 |
| Dubai Basketball → EuroLeague | 2025-26 entry | 5-yr wildcard | n/a (budget top-6 immediately) |
| JB Capital EuroLeague valuation | 2026-03 | study, not deal | league+clubs >€3.2B |

Context worth capturing as columns: buyer type (PE / individual / sovereign-linked),
league, % stake, control vs minority — the PE-minority vs control-sale price gap is
itself analyzable. Front Office Sports reports ~2/3 of NBA teams now have some PE
connection; NBA rules cap a fund at 20% of one team, 5 teams max.

- **Update frequency:** event-driven; manual row per deal.

---

## 5. Football comparators (clearly labeled, not core)

### Deloitte Football Money League
- **URL:** https://www.deloitte.com/uk/en/services/consulting-financial/analysis/deloitte-football-money-league.html
- **What:** top-20 clubs by revenue; 2026 edition (29th): €12.4B combined, Real
  Madrid €1.161B. Revenue splits (matchday/broadcast/commercial).
- **History:** ~29 years. Wikipedia's "Deloitte Football Money League" article
  tabulates historical editions and is cleanly scrapable (CC BY-SA, stable API) —
  better pipeline target than Deloitte's own page/PDF.
- **Verdict:** scrape Wikipedia table (cite Deloitte as underlying source), or
  manual CSV. Annual (January).

### Football club valuations (Sportico/Forbes soccer lists)
- Same access story as the NBA lists (manual). Optional — only if the note needs a
  football value/revenue multiple to set against basketball's.

---

## Recommendation — what this dataset can realistically support

**Strong (build on these):**
1. **NBA value CAGR vs S&P 500 total return** — Forbes series (manual CSV) vs
   `^SP500TR`. Clean, defensible, fully sourced.
2. **Value/revenue multiples** — NBA from Forbes (value + revenue in same table);
   EuroLeague single-point from JB Capital (€60–320M clubs vs known budgets);
   football from Deloitte revenue + published valuations. Cross-league multiple
   comparison is the most interview-friendly artifact this project will produce.
3. **Listed sports index vs benchmarks** — fully automated via yfinance; longest
   clean series in the project (Celtic since 1995). Football-heavy, labeled as such.
4. **EuroLeague budget rank vs final standing** — BasketNews budgets (scrapable)
   × EuroLeague API standings, seasons 2021-22 → 2025-26.

**Thin (include with explicit caveats):** EuroLeague club valuations are one
JB Capital snapshot, not a series; BasketNews mixes payroll vs total-budget
definitions across seasons; ACB/LBA are headline media figures; no listed
European basketball pure-play exists.

**Dead ends (documented, dropped):** Swiss SB League financials; Sportico as a
scrape target (ToS); Forbes interactive-list API; club-level audited accounts
outside France.

**Decisions (all resolved by user, 2026-07-15):**
1. Forbes: full 30-team panel at snapshot years 2016 / 2019 / 2022 (Wayback) + two
   most recent live editions; value + revenue per team.
2. LNB: manual entry, no PDF dependency; top division, last two published seasons,
   headline fields only (revenue, payroll, net result).
3. Listed index: European football clubs only, equal-weight, Turkish stocks
   excluded (logged with alternative); MSGS + US holdcos as separate comparator
   line; TKO pre-2023 legacy-WWE history excluded/noted.
4. Sportico + CNBC: latest-year manual cross-check only → publisher-divergence
   caveat stat.

**Standing methodology rulings for methodology.md (user, 2026-07-15):**
- Budget-vs-performance uses regular-season standings consistently across all
  seasons, never post-playoff placements.
- BasketNews payroll vs total-budget figures stay separate columns, never merged
  into one series.
- Switzerland dropped; one line in dashboard caveats.
