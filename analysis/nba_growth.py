"""NBA valuation growth, dispersion, and value/revenue multiples, plus the
S&P 500 total-return comparison over matching windows.

NBA values are USD, so the S&P comparison here uses ^SP500TR in USD (no EUR
conversion — this is a US-domestic comparison; methodology.md).
CAGR windows use edition publication months: Forbes editions through 2020 came
out in February of the edition year; from 2021 onward in October of the
preceding calendar year (2022 edition = Oct 2021).
"""

import pandas as pd

from collectors import common

OUTPUT_DIR = common.PROJECT_ROOT / "analysis" / "output"

EDITION_MONTHS = {2016: "2016-02", 2019: "2019-02", 2022: "2021-10",
                  2024: "2024-10", 2025: "2025-10"}


def sp500tr_level(month):
    prices = pd.read_csv(common.DATA_DIR / "market_prices.csv", parse_dates=["date"])
    sp = prices[prices.ticker == "^SP500TR"].copy()
    sp["month"] = sp["date"].dt.to_period("M").astype(str)
    row = sp[sp.month == month].sort_values("date").tail(1)
    return None if row.empty else float(row.close_adj.iloc[0])


def cpi_level(month):
    cpi = pd.read_csv(common.DATA_DIR / "us_cpi.csv")
    row = cpi[cpi.month == month]
    return None if row.empty else float(row.cpi.iloc[0])


def years_between(m0, m1):
    p0, p1 = pd.Period(m0, "M"), pd.Period(m1, "M")
    return (p1 - p0).n / 12


def cagr(v0, v1, years):
    return (v1 / v0) ** (1 / years) - 1


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    n = pd.read_csv(common.DATA_DIR / "nba_valuations.csv")
    years = sorted(y for y in n.list_year.unique() if y in EDITION_MONTHS)

    # ---- per-team multiples table ----
    multiples = n[["list_year", "team", "rank", "value_usd_m", "revenue_usd_m", "source"]].copy()
    multiples["value_rev_multiple"] = (multiples.value_usd_m / multiples.revenue_usd_m).round(2)
    multiples.to_csv(OUTPUT_DIR / "nba_multiples.csv", index=False)

    # ---- growth / dispersion metrics ----
    rows = []

    def add(metric, year_start, year_end, value, note=""):
        rows.append({"metric": metric, "list_year_start": year_start, "list_year_end": year_end,
                     "value": round(float(value), 4), "note": note})

    for y in years:
        sub = n[n.list_year == y].sort_values("rank")
        add("league_avg_value_usd_m", y, y, sub.value_usd_m.mean())
        add("league_median_value_usd_m", y, y, sub.value_usd_m.median())
        add("top5_avg_value_usd_m", y, y, sub.head(5).value_usd_m.mean())
        add("bottom5_avg_value_usd_m", y, y, sub.tail(5).value_usd_m.mean())
        add("top5_over_bottom5_ratio", y, y, sub.head(5).value_usd_m.mean() / sub.tail(5).value_usd_m.mean())
        add("median_value_rev_multiple", y, y, (sub.value_usd_m / sub.revenue_usd_m).median())

    pairs = [(a, b) for a, b in zip(years, years[1:])] + ([(years[0], years[-1])] if len(years) > 2 else [])
    for y0, y1 in pairs:
        m0, m1 = EDITION_MONTHS[y0], EDITION_MONTHS[y1]
        yrs = years_between(m0, m1)
        avg0 = n[n.list_year == y0].value_usd_m.mean()
        avg1 = n[n.list_year == y1].value_usd_m.mean()
        add("nba_avg_value_cagr", y0, y1, cagr(avg0, avg1, yrs), f"{m0} to {m1}")

        sp0, sp1 = sp500tr_level(m0), sp500tr_level(m1)
        if sp0 and sp1:
            add("sp500tr_cagr_same_window", y0, y1, cagr(sp0, sp1, yrs), f"{m0} to {m1}, USD total return")

        cpi0, cpi1 = cpi_level(m0), cpi_level(m1)
        if cpi0 and cpi1 and (y0, y1) == (years[0], years[-1]):
            real = cagr(avg0 / cpi0, avg1 / cpi1, yrs)
            add("nba_avg_value_cagr_real", y0, y1, real,
                f"{m0} to {m1}, CPI-deflated (CPIAUCSL) — facts-sheet number, dashboard stays nominal")

    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "nba_growth.csv", index=False)
    print(f"nba_growth: {len(rows)} metrics over editions {years} -> analysis/output/")
    return rows
