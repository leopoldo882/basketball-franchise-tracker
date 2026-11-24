"""Listed sports clubs vs stock market benchmarks.

All prices are converted to EUR. The club index is equal weight and
rebalanced monthly, which just means each month's index return is the
average of the members' returns that month.

Series built here:
  eu_football          headline index; clubs join in the month they list
  eu_football_fixed12  only the months where all 12 clubs trade (from Sep 2012)
  us_holdco            US sports companies, kept separate
  sp500tr_eur          S&P 500 total return, in EUR
  ieur_eur             iShares MSCI Europe ETF in EUR (exists from 2014)
  stoxx_eur            STOXX Europe 600, price only, for the years before IEUR

Every statistic is saved with its own start month, end month and number of
months, so two numbers measured over different periods are never mixed up.
"""

import pandas as pd

from collectors import common

OUTPUT_DIR = common.PROJECT_ROOT / "analysis" / "output"

INDEX_START = "2004-01"   # first month all three FX rates exist on Yahoo
BENCHMARKS = ["sp500tr_eur", "ieur_eur", "stoxx_eur"]


def monthly_eur_prices():
    """Month-end price of every ticker in EUR, one column per ticker."""
    prices = pd.read_csv(common.DATA_DIR / "market_prices.csv", parse_dates=["date"])
    fx = pd.read_csv(common.DATA_DIR / "fx_rates.csv", parse_dates=["date"])

    prices["month"] = prices["date"].dt.to_period("M")
    monthly = prices.sort_values("date").groupby(["ticker", "month"]).last().reset_index()
    fx["month"] = fx["date"].dt.to_period("M")
    fx_monthly = (fx.sort_values("date").groupby(["currency", "month"]).last()
                  .reset_index().pivot(index="month", columns="currency", values="per_eur"))

    # Celtic is quoted in pence on the London exchange
    is_pence = monthly["currency"] == "GBp"
    monthly.loc[is_pence, "close_adj"] = monthly.loc[is_pence, "close_adj"] / 100
    monthly.loc[is_pence, "currency"] = "GBP"

    def to_eur(row):
        if row["currency"] == "EUR":
            return row["close_adj"]
        if row["month"] not in fx_monthly.index:
            return None
        rate = fx_monthly.at[row["month"], row["currency"]]
        if pd.isna(rate):
            return None
        return row["close_adj"] / rate

    monthly["close_eur"] = monthly.apply(to_eur, axis=1)
    wide = monthly.pivot(index="month", columns="ticker", values="close_eur")
    groups = prices.groupby("ticker")["group"].first()
    return wide[wide.index >= pd.Period(INDEX_START)], groups


def equal_weight_returns(returns, members, require_all=False):
    """Average monthly return of the members, plus how many members had a
    return each month. With require_all=True, months where any member is
    missing are dropped."""
    sub = returns[members]
    if require_all:
        sub = sub.dropna(how="any")
        return sub.mean(axis=1), sub.notna().sum(axis=1)
    index_return = sub.mean(axis=1, skipna=True)
    return index_return[sub.notna().any(axis=1)], sub.notna().sum(axis=1)


def to_level(returns):
    """Turn monthly returns into an index level starting from 100."""
    return 100 * (1 + returns).cumprod()


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

    # monthly index levels
    rows = []
    for name, ret in series.items():
        for month, level in to_level(ret).items():
            rows.append({
                "date": str(month),
                "series": name,
                "level_eur": round(level, 4),
                "n_members": int(counts[name].get(month, 0)) if name in counts else "",
            })
    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "listed_index_monthly.csv", index=False)

    # summary statistics, each with its own window
    stats = []

    def add(series_name, metric, value, window, note=""):
        stats.append({
            "series": series_name, "metric": metric, "value": round(float(value), 4),
            "window_start": str(window.index[0]), "window_end": str(window.index[-1]),
            "n_months": len(window), "note": note,
        })

    notes = {"stoxx_eur": "price-only index, not total return",
             "ieur_eur": "ETF used as a total return proxy, exists from 2014"}
    for name, ret in series.items():
        level = to_level(ret)
        add(name, "cumulative_return", level.iloc[-1] / 100 - 1, ret, notes.get(name, ""))
        add(name, "cagr", cagr(level, len(ret)), ret, notes.get(name, ""))
        add(name, "max_drawdown", max_drawdown(level), ret, notes.get(name, ""))

    # The staggered index over the fixed-12 months. If this matches
    # eu_football_fixed12, any gap between the two headline indices comes from
    # the different start dates, not from which clubs are in them.
    common_window = series["eu_football"].loc[series["eu_football_fixed12"].index]
    note = "staggered index measured over the fixed-12 months"
    level = to_level(common_window)
    add("eu_football_common_window", "cumulative_return", level.iloc[-1] / 100 - 1, common_window, note)
    add("eu_football_common_window", "cagr", cagr(level, len(common_window)), common_window, note)
    add("eu_football_common_window", "max_drawdown", max_drawdown(level), common_window, note)

    # correlation of monthly returns, only over months where both series exist
    for line in ["eu_football", "eu_football_fixed12", "us_holdco"]:
        for bench in BENCHMARKS:
            overlap = pd.concat([series[line], series[bench]], axis=1, keys=[line, bench]).dropna()
            if len(overlap) < 12:
                continue
            add(line, f"correlation_vs_{bench}", overlap[line].corr(overlap[bench]), overlap, notes.get(bench, ""))

    pd.DataFrame(stats).to_csv(OUTPUT_DIR / "listed_index_stats.csv", index=False)
    print(f"listed_index: {len(rows)} monthly rows, {len(stats)} stats -> analysis/output/")
    return stats
