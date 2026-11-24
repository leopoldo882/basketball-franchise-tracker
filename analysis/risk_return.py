"""Risk and return of the listed series, all measured over the same months.

The window starts in the first month every series in SERIES has a return
(the US companies line starts last, in late 2015), so the rows of the table
can be compared directly.

  CAGR          growth per year implied by the monthly returns
  volatility    standard deviation of monthly returns x sqrt(12)
  Sharpe ratio  average monthly return above the ECB deposit rate, x 12,
                divided by the volatility (all returns are in euros)
  beta          covariance with the benchmark's monthly returns divided by
                the benchmark's variance
  max drawdown  worst fall from a previous high
"""

import math

import pandas as pd

from collectors import common

OUTPUT_DIR = common.PROJECT_ROOT / "analysis" / "output"

SERIES = ["eu_football_fixed12", "us_holdco", "sp500tr_eur", "ieur_eur"]


def monthly_returns():
    levels = pd.read_csv(OUTPUT_DIR / "listed_index_monthly.csv")
    wide = levels.pivot(index="date", columns="series", values="level_eur")[SERIES]
    # dropna keeps only the months where every series has a return
    return wide.pct_change(fill_method=None).dropna()


def monthly_risk_free(months):
    """ECB deposit rate for each month as a monthly decimal (2.4% a year -> 0.002)."""
    ecb = pd.read_csv(common.DATA_DIR / "ecb_deposit_rate.csv").set_index("month").rate_pct
    return ecb.reindex(months) / 100 / 12


def annual_volatility(returns):
    return returns.std() * math.sqrt(12)


def sharpe_ratio(returns, risk_free):
    return (returns - risk_free).mean() * 12 / annual_volatility(returns)


def beta(returns, benchmark):
    return returns.cov(benchmark) / benchmark.var()


def cagr(returns):
    return (1 + returns).prod() ** (12 / len(returns)) - 1


def max_drawdown(returns):
    # start the level at 1 so a fall in the very first month counts too
    level = pd.concat([pd.Series([1.0]), (1 + returns).cumprod()], ignore_index=True)
    return (level / level.cummax() - 1).min()


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    returns = monthly_returns()
    risk_free = monthly_risk_free(returns.index)
    if risk_free.isna().any():
        print(f"  WARNING risk_return: no ECB rate for {list(risk_free[risk_free.isna()].index)}")

    rows = []
    for name in SERIES:
        r = returns[name]
        rows.append({
            "series": name,
            "window_start": returns.index[0],
            "window_end": returns.index[-1],
            "n_months": len(r),
            "cagr": round(cagr(r), 4),
            "volatility": round(annual_volatility(r), 4),
            "sharpe": round(sharpe_ratio(r, risk_free), 3),
            "max_drawdown": round(max_drawdown(r), 4),
            "beta_vs_sp500": round(beta(r, returns["sp500tr_eur"]), 3),
            "beta_vs_msci_europe": round(beta(r, returns["ieur_eur"]), 3),
            "correlation_vs_sp500": round(r.corr(returns["sp500tr_eur"]), 3),
        })

    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "risk_return.csv", index=False)
    print(f"risk_return: {len(rows)} series, {returns.index[0]} to {returns.index[-1]} -> analysis/output/")
    return rows
