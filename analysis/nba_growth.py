"""NBA franchise values: growth, spread between rich and poor teams, and
value/revenue multiples, with the S&P 500 total return over the same windows.

Everything here stays in USD because both sides of the comparison are US.
The windows run between the months each Forbes edition was published.
"""

import pandas as pd

from collectors import common

OUTPUT_DIR = common.PROJECT_ROOT / "analysis" / "output"

# Forbes edition -> month it was published (see collectors/forbes_wayback.py)
EDITION_MONTHS = {
    2016: "2016-02",
    2019: "2019-02",
    2022: "2021-10",
    2024: "2024-10",
    2025: "2025-10",
    2026: "2026-10",
}


def sp500tr_level(month):
    """Last ^SP500TR close in the given month, or None if there is no data."""
    prices = pd.read_csv(common.DATA_DIR / "market_prices.csv", parse_dates=["date"])
    sp = prices[prices.ticker == "^SP500TR"].copy()
    sp["month"] = sp["date"].dt.to_period("M").astype(str)
    row = sp[sp.month == month].sort_values("date").tail(1)
    if row.empty:
        return None
    return float(row.close_adj.iloc[0])


def cpi_level(month):
    cpi = pd.read_csv(common.DATA_DIR / "us_cpi.csv")
    row = cpi[cpi.month == month]
    if row.empty:
        return None
    return float(row.cpi.iloc[0])


def years_between(month_start, month_end):
    months = (pd.Period(month_end, "M") - pd.Period(month_start, "M")).n
    return months / 12


def cagr(start_value, end_value, years):
    return (end_value / start_value) ** (1 / years) - 1


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    nba = pd.read_csv(common.DATA_DIR / "nba_valuations.csv")
    years = sorted(int(y) for y in nba.list_year.unique() if y in EDITION_MONTHS)

    # per-team value/revenue multiple
    multiples = nba[["list_year", "team", "rank", "value_usd_m", "revenue_usd_m", "source"]].copy()
    multiples["value_rev_multiple"] = (multiples.value_usd_m / multiples.revenue_usd_m).round(2)
    multiples.to_csv(OUTPUT_DIR / "nba_multiples.csv", index=False)

    rows = []

    def add(metric, year_start, year_end, value, note=""):
        rows.append({"metric": metric, "list_year_start": year_start, "list_year_end": year_end,
                     "value": round(float(value), 4), "note": note})

    # one-edition metrics
    for y in years:
        edition = nba[nba.list_year == y].sort_values("rank")
        top5 = edition.head(5).value_usd_m.mean()
        bottom5 = edition.tail(5).value_usd_m.mean()
        add("league_avg_value_usd_m", y, y, edition.value_usd_m.mean())
        add("league_median_value_usd_m", y, y, edition.value_usd_m.median())
        add("top5_avg_value_usd_m", y, y, top5)
        add("bottom5_avg_value_usd_m", y, y, bottom5)
        add("top5_over_bottom5_ratio", y, y, top5 / bottom5)
        add("median_value_rev_multiple", y, y, (edition.value_usd_m / edition.revenue_usd_m).median())

    # growth between consecutive editions, plus first to last
    windows = list(zip(years, years[1:]))
    if len(years) > 2:
        windows.append((years[0], years[-1]))

    for y0, y1 in windows:
        m0, m1 = EDITION_MONTHS[y0], EDITION_MONTHS[y1]
        n_years = years_between(m0, m1)
        avg0 = nba[nba.list_year == y0].value_usd_m.mean()
        avg1 = nba[nba.list_year == y1].value_usd_m.mean()
        add("nba_avg_value_cagr", y0, y1, cagr(avg0, avg1, n_years), f"{m0} to {m1}")

        sp0, sp1 = sp500tr_level(m0), sp500tr_level(m1)
        if sp0 and sp1:
            add("sp500tr_cagr_same_window", y0, y1, cagr(sp0, sp1, n_years),
                f"{m0} to {m1}, USD total return")

        # inflation-adjusted version, full window only (used in facts.md, not the dashboard)
        cpi0, cpi1 = cpi_level(m0), cpi_level(m1)
        if cpi0 and cpi1 and (y0, y1) == (years[0], years[-1]):
            real = cagr(avg0 / cpi0, avg1 / cpi1, n_years)
            add("nba_avg_value_cagr_real", y0, y1, real, f"{m0} to {m1}, deflated with US CPI (CPIAUCSL)")

    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "nba_growth.csv", index=False)
    print(f"nba_growth: {len(rows)} metrics over editions {years} -> analysis/output/")
    return rows
