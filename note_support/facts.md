# Facts sheet — computed numbers with sources

Generated 2026-07-17 22:18 UTC by `python run_pipeline.py --notepack`. Every number
regenerates from the pipeline CSVs; nothing here is editorial.

## Headline numbers

- **12.9%** — NBA avg franchise value CAGR, 2016→2022 editions (S&P 500 total return over the same window: 18.8%)
- **13.2%** — Listed European football clubs CAGR (EUR, fixed 12 members) (2012-09 → 2026-07)
- **6.3× → 9.5×** — NBA median value/revenue multiple (2016 edition vs 2022 edition)
- **0.56–0.83** — EuroLeague budget rank ↔ standings (Spearman) (across seasons and figure definitions)
- **€1.41B** — EuroLeague league-entity valuation 2025-26 (JB Capital, via official press release)

## Listed index statistics (analysis/output/listed_index_stats.csv)

| series | metric | value | window | months | note |
|---|---|---|---|---|---|
| eu_football | cumulative_return | 1.8425 | 2004-02 → 2026-07 | 270 |  |
| eu_football | cagr | 0.0475 | 2004-02 → 2026-07 | 270 |  |
| eu_football | max_drawdown | -0.6352 | 2004-02 → 2026-07 | 270 |  |
| eu_football_fixed12 | cumulative_return | 4.586 | 2012-09 → 2026-07 | 167 |  |
| eu_football_fixed12 | cagr | 0.1316 | 2012-09 → 2026-07 | 167 |  |
| eu_football_fixed12 | max_drawdown | -0.2986 | 2012-09 → 2026-07 | 167 |  |
| us_holdco | cumulative_return | 3.9808 | 2015-10 → 2026-07 | 130 |  |
| us_holdco | cagr | 0.1598 | 2015-10 → 2026-07 | 130 |  |
| us_holdco | max_drawdown | -0.3606 | 2015-10 → 2026-07 | 130 |  |
| sp500tr_eur | cumulative_return | 9.999 | 2004-02 → 2026-07 | 270 |  |
| sp500tr_eur | cagr | 0.1125 | 2004-02 → 2026-07 | 270 |  |
| sp500tr_eur | max_drawdown | -0.4694 | 2004-02 → 2026-07 | 270 |  |
| ieur_eur | cumulative_return | 1.5797 | 2014-07 → 2026-07 | 145 | investable ETF TR proxy, exists 2014+ |
| ieur_eur | cagr | 0.0816 | 2014-07 → 2026-07 | 145 | investable ETF TR proxy, exists 2014+ |
| ieur_eur | max_drawdown | -0.2449 | 2014-07 → 2026-07 | 145 | investable ETF TR proxy, exists 2014+ |
| stoxx_eur | cumulative_return | 1.6929 | 2004-05 → 2026-07 | 267 | price-only index, not total return |
| stoxx_eur | cagr | 0.0455 | 2004-05 → 2026-07 | 267 | price-only index, not total return |
| stoxx_eur | max_drawdown | -0.5641 | 2004-05 → 2026-07 | 267 | price-only index, not total return |
| eu_football_common_window | cumulative_return | 4.586 | 2012-09 → 2026-07 | 167 | staggered composition over the fixed-12 window (window vs composition split) |
| eu_football_common_window | cagr | 0.1316 | 2012-09 → 2026-07 | 167 | staggered composition over the fixed-12 window (window vs composition split) |
| eu_football_common_window | max_drawdown | -0.2986 | 2012-09 → 2026-07 | 167 | staggered composition over the fixed-12 window (window vs composition split) |
| eu_football | correlation_vs_sp500tr_eur | 0.4408 | 2004-02 → 2026-07 | 270 |  |
| eu_football | correlation_vs_ieur_eur | 0.5871 | 2014-07 → 2026-07 | 145 | investable ETF TR proxy, exists 2014+ |
| eu_football | correlation_vs_stoxx_eur | 0.5615 | 2004-05 → 2026-07 | 267 | price-only index, not total return |
| eu_football_fixed12 | correlation_vs_sp500tr_eur | 0.4651 | 2012-09 → 2026-07 | 167 |  |
| eu_football_fixed12 | correlation_vs_ieur_eur | 0.5871 | 2014-07 → 2026-07 | 145 | investable ETF TR proxy, exists 2014+ |
| eu_football_fixed12 | correlation_vs_stoxx_eur | 0.5444 | 2012-09 → 2026-07 | 167 | price-only index, not total return |
| us_holdco | correlation_vs_sp500tr_eur | 0.582 | 2015-10 → 2026-07 | 130 |  |
| us_holdco | correlation_vs_ieur_eur | 0.5481 | 2015-10 → 2026-07 | 130 | investable ETF TR proxy, exists 2014+ |
| us_holdco | correlation_vs_stoxx_eur | 0.5509 | 2015-10 → 2026-07 | 130 | price-only index, not total return |

Source: Yahoo Finance adjusted closes via yfinance; EUR conversion via yfinance FX pairs; construction rules in methodology.md.

## NBA valuation metrics (analysis/output/nba_growth.csv)

| metric | editions | value | note |
|---|---|---|---|
| league_avg_value_usd_m | 2016 | 1245.3333 |  |
| league_median_value_usd_m | 2016 | 967.5 |  |
| top5_avg_value_usd_m | 2016 | 2420.0 |  |
| bottom5_avg_value_usd_m | 2016 | 699.0 |  |
| top5_over_bottom5_ratio | 2016 | 3.4621 |  |
| median_value_rev_multiple | 2016 | 6.2519 |  |
| league_avg_value_usd_m | 2019 | 1868.3333 |  |
| league_median_value_usd_m | 2019 | 1562.5 |  |
| top5_avg_value_usd_m | 2019 | 3380.0 |  |
| bottom5_avg_value_usd_m | 2019 | 1240.0 |  |
| top5_over_bottom5_ratio | 2019 | 2.7258 |  |
| median_value_rev_multiple | 2019 | 6.198 |  |
| league_avg_value_usd_m | 2022 | 2480.1667 |  |
| league_median_value_usd_m | 2022 | 1952.5 |  |
| top5_avg_value_usd_m | 2022 | 4820.0 |  |
| bottom5_avg_value_usd_m | 2022 | 1546.0 |  |
| top5_over_bottom5_ratio | 2022 | 3.1177 |  |
| median_value_rev_multiple | 2022 | 9.4941 |  |
| nba_avg_value_cagr | 2016→2019 | 0.1448 | 2016-02 to 2019-02 |
| sp500tr_cagr_same_window | 2016→2019 | 0.1528 | 2016-02 to 2019-02, USD total return |
| nba_avg_value_cagr | 2019→2022 | 0.1121 | 2019-02 to 2021-10 |
| sp500tr_cagr_same_window | 2019→2022 | 0.2288 | 2019-02 to 2021-10, USD total return |
| nba_avg_value_cagr | 2016→2022 | 0.1293 | 2016-02 to 2021-10 |
| sp500tr_cagr_same_window | 2016→2022 | 0.1879 | 2016-02 to 2021-10, USD total return |
| nba_avg_value_cagr_real | 2016→2022 | 0.0992 | 2016-02 to 2021-10, CPI-deflated (CPIAUCSL) — facts-sheet number, dashboard stays nominal |

Source: Forbes NBA list data via Wayback-archived Forbes AJAX JSON (capture URLs in data/nba_valuations.csv, source_url column); S&P 500 total return = ^SP500TR (USD); real-terms deflator = FRED CPIAUCSL.

## EuroLeague budget rank vs regular-season standing

| season | figure type | clubs joined | Spearman rho |
|---|---|---|---|
| 2021-22 | payroll_gross | 9 | 0.828 |
| 2021-22 | payroll_net | 14 | 0.7046 |
| 2021-22 | total_budget_gross | 14 | 0.6451 |
| 2024-25 | payroll_net | 18 | 0.7677 |
| 2024-25 | total_budget_gross | 18 | 0.6908 |
| 2025-26 | payroll_net | 20 | 0.5587 |

Join drops (all source gaps, no mapping failures):
- 2021-22 payroll_gross: CSKA Moscow: not in 2021-22 standings (source gap); Zenit St Petersburg: not in 2021-22 standings (source gap)
- 2021-22 payroll_net: CSKA Moscow: not in 2021-22 standings (source gap); UNICS Kazan: not in 2021-22 standings (source gap); Zenit St Petersburg: not in 2021-22 standings (source gap)
- 2021-22 total_budget_gross: CSKA Moscow: not in 2021-22 standings (source gap); UNICS Kazan: not in 2021-22 standings (source gap); Zenit St Petersburg: not in 2021-22 standings (source gap)

Source: BasketNews budget research (estimate ranges; midpoints used for ranks) × official EuroLeague API standings, joined on canonical names.

## EuroLeague valuations (JB Capital, March 2026)

- EuroLeague (league entity) (2025-26): **€1410M** — JB Capital report; EBITDA multiple
- EuroLeague (league entity) (2026-27): **€1640M** — same multiple applied to estimated 2026-27 EBITDA
- All licensed clubs (aggregate) (2025-26): **€1800M** — revenue-based multiples; reported as approximately EUR 1.8B
- League + clubs combined (2025-26): **€3200M** — combined enterprise value; reported as over EUR 3.2B
- League + clubs combined (scenario) (2026-27): **€4300M** — scenario: franchise-model transition executes; same multiples
- Individual clubs (range) (2025-26): **€60–320M** — revenue-based multiples; reported as over EUR 60M to more than EUR 320M

Source: official EuroLeague press release: https://www.euroleaguebasketball.net/news/euroleague-and-clubs-valued-at-over-3-2-billion-according-to-jb-capital/

## Chart files

One PNG per dashboard chart, same identifiers as the dashboard div ids.

