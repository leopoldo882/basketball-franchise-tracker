"""Listed sports index vs benchmarks: EUR-converted, equal-weight, monthly
rebalanced (methodology.md rulings, 2026-07-17).

Series built here:
  eu_football          headline index, staggered entry (members join on listing)
  eu_football_fixed12  robustness: only months where all 12 members trade
  us_holdco            separate comparator line (never blended)
  sp500tr_eur          ^SP500TR converted to EUR (total return)
  ieur_eur             IEUR adjusted close in EUR (Europe TR proxy, 2014+)
  stoxx_eur            ^STOXX (EUR already) — PRICE-ONLY secondary comparator
                       for pre-2014 context; TR-vs-price mismatch is logged

Every stats row carries its own explicit window (start, end, n_months) — no
silent mixed-window comparisons.
"""

import pathlib

import pandas as pd

from collectors import common

OUTPUT_DIR = common.PROJECT_ROOT / "analysis" / "output"

INDEX_START = "2004-01"   # earliest month all needed FX pairs exist
BENCHMARKS = ["sp500tr_eur", "ieur_eur", "stoxx_eur"]


def monthly_eur_prices():
    """Month-end adjusted closes for every ticker, converted to EUR."""
    prices = pd.read_csv(common.DATA_DIR / "market_prices.csv", parse_dates=["date"])
    fx = pd.read_csv(common.DATA_DIR / "fx_rates.csv", parse_dates=["date"])

    # month-end observations
    prices["month"] = prices["date"].dt.to_period("M")
    monthly = prices.sort_values("date").groupby(["ticker", "month"]).last().reset_index()
    fx["month"] = fx["date"].dt.to_period("M")
    fx_monthly = (fx.sort_values("date").groupby(["currency", "month"]).last()
                  .reset_index().pivot(index="month", columns="currency", values="per_eur"))

    # London quotes in pence: to GBP before converting
    is_pence = monthly["currency"] == "GBp"
    monthly.loc[is_pence, "close_adj"] = monthly.loc[is_pence, "close_adj"] / 100
    monthly.loc[is_pence, "currency"] = "GBP"

    def to_eur(row):
        if row["currency"] == "EUR":
            return row["close_adj"]
        rate = fx_monthly.at[row["month"], row["currency"]] if row["month"] in fx_monthly.index else None
        if rate is None or pd.isna(rate):
            return None
        return row["close_adj"] / rate

    monthly["close_eur"] = monthly.apply(to_eur, axis=1)
    wide = monthly.pivot(index="month", columns="ticker", values="close_eur")
    groups = prices.groupby("ticker")["group"].first()
    return wide[wide.index >= pd.Period(INDEX_START)], groups


def equal_weight_returns(returns, members, require_all=False):
    """Equal-weight monthly-rebalanced index return: mean of member returns.
    require_all=True keeps only months where every member has a return."""
    sub = returns[members]
    if require_all:
        sub = sub.dropna(how="any")
        return sub.mean(axis=1), sub.notna().sum(axis=1)
    idx = sub.mean(axis=1, skipna=True)
    return idx[sub.notna().any(axis=1)], sub.notna().sum(axis=1)


def to_level(series):
    """Cumulate returns to an index level, 100 at the month before the first return."""
    return 100 * (1 + series).cumprod()


def max_drawdown(level):
    return (level / level.cummax() - 1).min()


def cagr(level, n_months):
    return (level.iloc[-1] / 100) ** (12 / n_months) - 1


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    wide, groups = monthly_eur_prices()
    returns = wide.pct_change()

    eu = sorted(groups[groups == "eu_football"].index)
    us = sorted(groups[groups == "us_holdco"].index)

    series = {}
    counts = {}
    series["eu_football"], counts["eu_football"] = equal_weight_returns(returns, eu)
    series["eu_football_fixed12"], counts["eu_football_fixed12"] = equal_weight_returns(returns, eu, require_all=True)
    series["us_holdco"], counts["us_holdco"] = equal_weight_returns(returns, us)
    series["sp500tr_eur"] = returns["^SP500TR"].dropna()
    series["ieur_eur"] = returns["IEUR"].dropna()
    series["stoxx_eur"] = returns["^STOXX"].dropna()

    # ---- monthly levels output ----
    rows = []
    for name, ret in series.items():
        level = to_level(ret)
        for month, lvl in level.items():
            rows.append({
                "date": str(month),
                "series": name,
                "level_eur": round(lvl, 4),
                "n_members": int(counts[name].get(month, 0)) if name in counts else "",
            })
    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "listed_index_monthly.csv", index=False)

    # ---- stats with explicit windows ----
    stats = []

    def add(series_name, metric, value, window, note=""):
        stats.append({
            "series": series_name, "metric": metric, "value": round(float(value), 4),
            "window_start": str(window.index[0]), "window_end": str(window.index[-1]),
            "n_months": len(window), "note": note,
        })

    notes = {"stoxx_eur": "price-only index, not total return",
             "ieur_eur": "investable ETF TR proxy, exists 2014+"}
    for name, ret in series.items():
        level = to_level(ret)
        add(name, "cumulative_return", level.iloc[-1] / 100 - 1, ret, notes.get(name, ""))
        add(name, "cagr", cagr(level, len(ret)), ret, notes.get(name, ""))
        add(name, "max_drawdown", max_drawdown(level), ret, notes.get(name, ""))

    # staggered eu_football restricted to the fixed-12 window: comparing this
    # against eu_football_fixed12 over the identical window separates the
    # window effect from the composition effect
    common = series["eu_football"].loc[series["eu_football_fixed12"].index]
    common_note = "staggered composition over the fixed-12 window (window vs composition split)"
    common_level = to_level(common)
    add("eu_football_common_window", "cumulative_return", common_level.iloc[-1] / 100 - 1, common, common_note)
    add("eu_football_common_window", "cagr", cagr(common_level, len(common)), common, common_note)
    add("eu_football_common_window", "max_drawdown", max_drawdown(common_level), common, common_note)

    # correlations: each index line vs each benchmark, on their overlap only
    for line in ["eu_football", "eu_football_fixed12", "us_holdco"]:
        for bench in BENCHMARKS:
            overlap = pd.concat([series[line], series[bench]], axis=1, keys=[line, bench]).dropna()
            if len(overlap) < 12:
                continue
            note = notes.get(bench, "")
            add(line, f"correlation_vs_{bench}", overlap[line].corr(overlap[bench]), overlap, note)

    pd.DataFrame(stats).to_csv(OUTPUT_DIR / "listed_index_stats.csv", index=False)
    print(f"listed_index: {len(rows)} monthly rows, {len(stats)} stats -> analysis/output/")
    return stats
