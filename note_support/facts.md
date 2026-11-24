# Facts sheet

Numbers computed by `python run_pipeline.py --notepack`, market data to 23 Nov 2026.
Each section says where its numbers come from. No commentary.

## Headline numbers

- **16.1%**: NBA average team value, growth per year (2016 to 2026 Forbes editions) (S&P 500 with dividends, same months: 15.6%)
- **12.2%**: 12 listed European football clubs, growth per year in EUR (2012-09 to 2026-11)
- **12.2x**: Median NBA team value / revenue, 2026 edition (6.3x in the 2016 edition)
- **1.02x to 1.41x**: NBA control sales vs the last Forbes value before the deal (5 deals, 2025 to 2026)
- **0.56 to 0.83**: EuroLeague budget rank vs league position (Spearman) (range across seasons and budget definitions)
- **€1.41bn**: EuroLeague league company, 2025-26 valuation (JB Capital, March 2026)

## Listed index (analysis/output/listed_index_stats.csv)

| series | metric | value | window | months | note |
|---|---|---|---|---|---|
| eu_football | cumulative_return | 1.6112 | 2004-02 to 2026-11 | 274 |  |
| eu_football | cagr | 0.0429 | 2004-02 to 2026-11 | 274 |  |
| eu_football | max_drawdown | -0.6352 | 2004-02 to 2026-11 | 274 |  |
| eu_football_fixed12 | cumulative_return | 4.1316 | 2012-09 to 2026-11 | 171 |  |
| eu_football_fixed12 | cagr | 0.1216 | 2012-09 to 2026-11 | 171 |  |
| eu_football_fixed12 | max_drawdown | -0.2986 | 2012-09 to 2026-11 | 171 |  |
| us_holdco | cumulative_return | 4.4473 | 2015-10 to 2026-11 | 134 |  |
| us_holdco | cagr | 0.1639 | 2015-10 to 2026-11 | 134 |  |
| us_holdco | max_drawdown | -0.3606 | 2015-10 to 2026-11 | 134 |  |
| sp500tr_eur | cumulative_return | 10.2409 | 2004-02 to 2026-11 | 274 |  |
| sp500tr_eur | cagr | 0.1118 | 2004-02 to 2026-11 | 274 |  |
| sp500tr_eur | max_drawdown | -0.4694 | 2004-02 to 2026-11 | 274 |  |
| ieur_eur | cumulative_return | 1.5853 | 2014-07 to 2026-11 | 149 | ETF used as a total return proxy, exists from 2014 |
| ieur_eur | cagr | 0.0795 | 2014-07 to 2026-11 | 149 | ETF used as a total return proxy, exists from 2014 |
| ieur_eur | max_drawdown | -0.2449 | 2014-07 to 2026-11 | 149 | ETF used as a total return proxy, exists from 2014 |
| stoxx_eur | cumulative_return | 1.6172 | 2004-05 to 2026-11 | 271 | price-only index, not total return |
| stoxx_eur | cagr | 0.0435 | 2004-05 to 2026-11 | 271 | price-only index, not total return |
| stoxx_eur | max_drawdown | -0.5641 | 2004-05 to 2026-11 | 271 | price-only index, not total return |
| eu_football_common_window | cumulative_return | 4.1316 | 2012-09 to 2026-11 | 171 | staggered index measured over the fixed-12 months |
| eu_football_common_window | cagr | 0.1216 | 2012-09 to 2026-11 | 171 | staggered index measured over the fixed-12 months |
| eu_football_common_window | max_drawdown | -0.2986 | 2012-09 to 2026-11 | 171 | staggered index measured over the fixed-12 months |
| eu_football | correlation_vs_sp500tr_eur | 0.4397 | 2004-02 to 2026-11 | 274 |  |
| eu_football | correlation_vs_ieur_eur | 0.5905 | 2014-07 to 2026-11 | 149 | ETF used as a total return proxy, exists from 2014 |
| eu_football | correlation_vs_stoxx_eur | 0.5646 | 2004-05 to 2026-11 | 271 | price-only index, not total return |
| eu_football_fixed12 | correlation_vs_sp500tr_eur | 0.4637 | 2012-09 to 2026-11 | 171 |  |
| eu_football_fixed12 | correlation_vs_ieur_eur | 0.5905 | 2014-07 to 2026-11 | 149 | ETF used as a total return proxy, exists from 2014 |
| eu_football_fixed12 | correlation_vs_stoxx_eur | 0.5504 | 2012-09 to 2026-11 | 171 | price-only index, not total return |
| us_holdco | correlation_vs_sp500tr_eur | 0.5751 | 2015-10 to 2026-11 | 134 |  |
| us_holdco | correlation_vs_ieur_eur | 0.5334 | 2015-10 to 2026-11 | 134 | ETF used as a total return proxy, exists from 2014 |
| us_holdco | correlation_vs_stoxx_eur | 0.5339 | 2015-10 to 2026-11 | 134 | price-only index, not total return |

Source: Yahoo Finance adjusted closes via yfinance, converted to EUR with yfinance FX rates. Index rules in methodology.md.

## NBA team values (analysis/output/nba_growth.csv)

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
| league_avg_value_usd_m | 2024 | 4416.6667 |  |
| league_median_value_usd_m | 2024 | 3975.0 |  |
| top5_avg_value_usd_m | 2024 | 6980.0 |  |
| bottom5_avg_value_usd_m | 2024 | 3130.0 |  |
| top5_over_bottom5_ratio | 2024 | 2.23 |  |
| median_value_rev_multiple | 2024 | 11.288 |  |
| league_avg_value_usd_m | 2025 | 5355.8333 |  |
| league_median_value_usd_m | 2025 | 4750.0 |  |
| top5_avg_value_usd_m | 2025 | 8990.0 |  |
| bottom5_avg_value_usd_m | 2025 | 3620.0 |  |
| top5_over_bottom5_ratio | 2025 | 2.4834 |  |
| median_value_rev_multiple | 2025 | 12.2245 |  |
| league_avg_value_usd_m | 2026 | 6126.0 |  |
| league_median_value_usd_m | 2026 | 5550.0 |  |
| top5_avg_value_usd_m | 2026 | 10680.0 |  |
| bottom5_avg_value_usd_m | 2026 | 4156.0 |  |
| top5_over_bottom5_ratio | 2026 | 2.5698 |  |
| median_value_rev_multiple | 2026 | 12.2135 |  |
| nba_avg_value_cagr | 2016 to 2019 | 0.1448 | 2016-02 to 2019-02 |
| sp500tr_cagr_same_window | 2016 to 2019 | 0.1528 | 2016-02 to 2019-02, USD total return |
| nba_avg_value_cagr | 2019 to 2022 | 0.1121 | 2019-02 to 2021-10 |
| sp500tr_cagr_same_window | 2019 to 2022 | 0.2288 | 2019-02 to 2021-10, USD total return |
| nba_avg_value_cagr | 2022 to 2024 | 0.2121 | 2021-10 to 2024-10 |
| sp500tr_cagr_same_window | 2022 to 2024 | 0.0908 | 2021-10 to 2024-10, USD total return |
| nba_avg_value_cagr | 2024 to 2025 | 0.2126 | 2024-10 to 2025-10 |
| sp500tr_cagr_same_window | 2024 to 2025 | 0.2145 | 2024-10 to 2025-10, USD total return |
| nba_avg_value_cagr | 2025 to 2026 | 0.1438 | 2025-10 to 2026-10 |
| sp500tr_cagr_same_window | 2025 to 2026 | 0.1211 | 2025-10 to 2026-10, USD total return |
| nba_avg_value_cagr | 2016 to 2026 | 0.1611 | 2016-02 to 2026-10 |
| sp500tr_cagr_same_window | 2016 to 2026 | 0.1559 | 2016-02 to 2026-10, USD total return |
| nba_avg_value_cagr_real | 2016 to 2026 | 0.1234 | 2016-02 to 2026-10, deflated with US CPI (CPIAUCSL) |

Source: Forbes list data archived on the Wayback Machine (capture links in data/nba_valuations.csv); S&P 500 total return = ^SP500TR in USD; inflation = FRED CPIAUCSL.

## NBA control sales vs the last Forbes value (analysis/output/transactions_vs_forbes.csv)

| agreed | team | buyer | deal valuation $M | Forbes $M (edition) | deal / Forbes | notes |
|---|---|---|---|---|---|---|
| 2022-12 | Phoenix Suns | Mat Ishbia group | 4000 |  |  | Includes the WNBA Mercury; approved Feb 2023 |
| 2023-06 | Charlotte Hornets | Gabe Plotkin / Rick Schnall group | 3000 |  |  | Majority stake from Michael Jordan who kept a minority share; approved Jul 2023 |
| 2023-11 | Dallas Mavericks | Adelson / Dumont families | 3500 |  |  | Mark Cuban kept 27%; approved Dec 2023 |
| 2025-03 | Boston Celtics | Bill Chisholm group | 6100 | 6000 (2024) | 1.017 | Approved Aug 2025; remaining shares by 2028 at up to about 7300; Sixth Street is in the group (next row) |
| 2025-06 | Los Angeles Lakers | Mark Walter | 10000 | 7100 (2024) | 1.408 | Approved Oct 2025; Buss family kept about 15% |
| 2025-08 | Portland Trail Blazers | Tom Dundon group | 4000 | 3500 (2024) | 1.143 | Approved Mar 2026; 80.1% at a 4.0bn valuation then the last 19.9% at 4.5bn by Sep 2028 (reported as about 4.25bn overall) |
| 2026-08 | Los Angeles Lakers | Josh Kushner / Bob Iger group | 12500 | 10000 (2025) | 1.250 | Walter selling 14 months after buying at 10bn; Buss family selling its last 17.8% at the same valuation; not yet approved by the NBA when entered (Nov 2026) |
| 2026-08 | Minnesota Timberwolves | Marc Stad | 4500 | 3600 (2025) | 1.250 | Includes the WNBA Lynx; buys most of Marc Lore's stake; not yet approved by the NBA when entered (Nov 2026) |

Source: one news link per deal in data/manual/transactions.csv. Compared only when the Forbes list was published less than 12 months before the deal.

## Other publishers vs Forbes (analysis/output/publisher_divergence.csv)

| publisher | list | Forbes edition | teams | mean diff | mean abs diff | max abs diff |
|---|---|---|---|---|---|---|
| cnbc | 2026 | 2025 | 15 | 0.041 | 0.0621 | 0.1193 |
| sportico | 2026 | 2026 | 4 | 0.0518 | 0.0518 | 0.1172 |

Source: Sportico values as reported by Bleacher Report (Oct 2026, 4 teams), CNBC values as republished by NBC Chicago (Feb 2026, 15 teams). Diff = publisher / Forbes - 1.

## EuroLeague budget rank vs regular-season position

| season | figure type | clubs | Spearman rho |
|---|---|---|---|
| 2021-22 | payroll_gross | 9 | 0.828 |
| 2021-22 | payroll_net | 14 | 0.7046 |
| 2021-22 | total_budget_gross | 14 | 0.6451 |
| 2024-25 | payroll_net | 18 | 0.7677 |
| 2024-25 | total_budget_gross | 18 | 0.6908 |
| 2025-26 | payroll_net | 20 | 0.5587 |

Clubs dropped from the join (all missing from that season's standings, none from the name mapping):
- 2021-22 payroll_gross: CSKA Moscow: not in 2021-22 standings (source gap); Zenit St Petersburg: not in 2021-22 standings (source gap)
- 2021-22 payroll_net: CSKA Moscow: not in 2021-22 standings (source gap); UNICS Kazan: not in 2021-22 standings (source gap); Zenit St Petersburg: not in 2021-22 standings (source gap)
- 2021-22 total_budget_gross: CSKA Moscow: not in 2021-22 standings (source gap); UNICS Kazan: not in 2021-22 standings (source gap); Zenit St Petersburg: not in 2021-22 standings (source gap)

Source: BasketNews budget research (midpoint of each reported range) and the official EuroLeague API standings.

## EuroLeague valuation (JB Capital, March 2026)

- EuroLeague (league entity) (2025-26): **€1410M**, JB Capital report; EBITDA multiple
- EuroLeague (league entity) (2026-27): **€1640M**, same multiple applied to estimated 2026-27 EBITDA
- All licensed clubs (aggregate) (2025-26): **€1800M**, revenue-based multiples; reported as approximately EUR 1.8B
- League + clubs combined (2025-26): **€3200M**, combined enterprise value; reported as over EUR 3.2B
- League + clubs combined (scenario) (2026-27): **€4300M**, scenario: franchise-model transition executes; same multiples
- Individual clubs (range) (2025-26): **€60M to €320M**, revenue-based multiples; reported as over EUR 60M to more than EUR 320M

Source: https://www.euroleaguebasketball.net/news/euroleague-and-clubs-valued-at-over-3-2-billion-according-to-jb-capital/

## French top division (LNB / DNCCG)

| club | budget 2024-25 €M | budget 2025-26 €M | payroll 2025-26 €M | payroll / budget |
|---|---|---|---|---|
| AS Monaco Basket | 29.375 | 38.715 | 20.134 | 52% |
| Paris Basketball | 18.885 | 28.883 | 7.970 | 28% |
| LDLC ASVEL | 16.223 | 18.689 | 4.546 | 24% |
| JL Bourg Basket | 7.806 | 8.122 | 2.300 | 28% |
| Le Mans Sarthe Basket | 6.468 | 7.510 | 2.282 | 30% |
| Elan Chalon | 6.175 | 7.188 | 2.034 | 28% |
| SIG Strasbourg | 7.118 | 7.071 | 1.864 | 26% |
| Cholet Basket | 6.389 | 6.460 | 1.631 | 25% |
| JDA Dijon | 6.396 | 6.370 | 1.965 | 31% |
| Limoges CSP | 5.417 | 6.180 | 1.848 | 30% |
| BCM Gravelines-Dunkerque | 5.475 | 5.858 | 1.778 | 30% |
| SLUC Nancy Basket | 5.769 | 5.836 | 1.733 | 30% |
| Nanterre 92 | 5.586 | 5.627 | 1.598 | 28% |
| Saint-Quentin Basket-Ball | 4.256 | 4.138 | 1.663 | 40% |
| Boulazac Basket Dordogne | promoted | 3.853 | 1.242 | 32% |
| ESSM Le Portel | 4.305 | 3.741 | 0.968 | 26% |

2025-26 average budget: €10.265M, median €6.415M (16 clubs).

- 2024-25 Betclic ELITE (all clubs), operating result: €-34.0M
- 2024-25 Betclic ELITE (all clubs), net result: €-0.8M
- 2024-25 EuroLeague clubs (Monaco + ASVEL + Paris), operating result: €-32.2M
- 2024-25 AS Monaco Basket, operating result: €-20.0M

Source: budgets https://cdn.lnb.fr/uploads/content-library/e0645ba3c01ab4ec93d0376812e175afc201fafa7958aa2b7264766ee102e1d0.pdf ; accounts https://cdn.lnb.fr/uploads/content-library/ae533f4f33a596f9863a45176bf64cc3e9ca72b58781c3e51a0a3933621622cc.pdf. Budget = total revenue filed in September; payroll = gross payroll for players and coaches as approved by the DNCCG.

## Spanish and Italian club budgets (reference only)

Different seasons and definitions from the French and EuroLeague numbers, so not comparable one-to-one.

| league | season | club | €M | figure |
|---|---|---|---|---|
| ACB | 2024-25 | Real Madrid | 45.0 | total_budget |
| ACB | 2024-25 | FC Barcelona | 32.0 | total_budget |
| ACB | 2024-25 | Valencia Basket | 27.5 | total_budget |
| ACB | 2024-25 | Baskonia | 16.0 | total_budget |
| ACB | 2024-25 | Unicaja Malaga | 15.0 | total_budget |
| ACB | 2024-25 | Gran Canaria | 10.3 | total_budget |
| ACB | 2024-25 | Joventut Badalona | 7.3 | total_budget |
| ACB | 2024-25 | BAXI Manresa | 3.8 | total_budget |
| LBA | 2021-22 | Olimpia Milano | 33.642 | revenue |
| LBA | 2021-22 | Virtus Bologna | 25.4 | total_budget |
| LBA | 2021-22 | Reyer Venezia | 10.432 | total_budget |
| LBA | 2021-22 | Derthona Tortona | 7.945 | total_budget |
| LBA | 2021-22 | Germani Brescia | 6.651 | total_budget |
| LBA | 2021-22 | Dinamo Sassari | 6.329 | total_budget |
| LBA | 2021-22 | Reggio Emilia | 6.203 | total_budget |
| LBA | 2021-22 | Napoli Basket | 5.177 | total_budget |
| LBA | 2021-22 | Treviso Basket | 5.112 | total_budget |
| LBA | 2021-22 | Aquila Trento | 4.251 | total_budget |

Sources: https://www.solobasket.com/liga-endesa/presupuestos-acb-top ; https://www.backdoorpodcast.com/legabasket-i-budget-delle-squadre-di-serie-a-milano-al-comando/ (citing La Prealpina).

## Chart files

One PNG per dashboard chart, named after the chart's id on the page.
