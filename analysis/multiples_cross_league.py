"""Valuation multiples across leagues.

- NBA: Forbes value / revenue per team (median per edition)
- Listed European football clubs: enterprise value / trailing 12-month revenue
  from Yahoo, both converted to euros first
- EuroLeague: JB Capital's figures are listed, but no multiple is computed
  because the press release doesn't give the revenue they are based on
"""

import pandas as pd

from collectors import common

OUTPUT_DIR = common.PROJECT_ROOT / "analysis" / "output"


def latest_fx():
    """Latest rate per currency, as units per 1 EUR."""
    fx = pd.read_csv(common.DATA_DIR / "fx_rates.csv")
    return fx.sort_values("date").groupby("currency").per_eur.last().to_dict()


def to_eur(amount, currency, fx):
    # Yahoo quotes London prices in pence (GBp) but gives market values in pounds
    if currency == "GBp":
        currency = "GBP"
    if currency == "EUR":
        return amount
    return amount / fx[currency]


def football_multiples():
    clubs = pd.read_csv(common.DATA_DIR / "club_fundamentals.csv")
    fx = latest_fx()
    rows = []
    for _, c in clubs.iterrows():
        ev = to_eur(c.enterprise_value, c.trading_currency, fx)
        revenue = to_eur(c.revenue_ttm, c.financial_currency, fx)
        rows.append({
            "ticker": c.ticker,
            "club": c.club,
            "fetched_on": c.fetched_on,
            "market_cap_eur_m": round(to_eur(c.market_cap, c.trading_currency, fx) / 1e6, 1),
            "ev_eur_m": round(ev / 1e6, 1),
            "revenue_eur_m": round(revenue / 1e6, 1),
            "ev_to_revenue": round(ev / revenue, 2),
        })
    return pd.DataFrame(rows).sort_values("ev_to_revenue", ascending=False)


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []

    nba = pd.read_csv(common.DATA_DIR / "nba_valuations.csv")
    for year, edition in nba.groupby("list_year"):
        source = edition.source_url.iloc[0]
        rows.append({"league": "NBA", "year": year, "metric": "median_value_rev_multiple",
                     "value": round((edition.value_usd_m / edition.revenue_usd_m).median(), 2),
                     "unit": "x revenue", "source_url": source})
        rows.append({"league": "NBA", "year": year, "metric": "league_avg_value",
                     "value": round(edition.value_usd_m.mean(), 1), "unit": "USD m",
                     "source_url": source})

    football = football_multiples()
    football.to_csv(OUTPUT_DIR / "football_multiples.csv", index=False)
    rows.append({"league": "Listed European football", "year": football.fetched_on.iloc[0],
                 "metric": "median_ev_to_revenue", "value": round(football.ev_to_revenue.median(), 2),
                 "unit": f"x revenue ({len(football)} clubs)", "source_url": "Yahoo Finance via yfinance"})

    el = pd.read_csv(common.DATA_DIR / "manual" / "euroleague_valuations.csv")
    for _, r in el.iterrows():
        if r.value_eur_m_low == r.value_eur_m_high:
            value = r.value_eur_m_low
        else:
            value = f"{r.value_eur_m_low}-{r.value_eur_m_high}"
        rows.append({"league": "EuroLeague", "year": r.season, "metric": f"jb_capital_{r.entity_type}",
                     "value": value, "unit": "EUR m", "source_url": r.source_url})
    rows.append({"league": "EuroLeague", "year": "2025-26", "metric": "value_rev_multiple",
                 "value": "n/a", "unit": "",
                 "source_url": "no revenue base published in the JB Capital press release"})

    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "multiples_summary.csv", index=False)
    print(f"multiples_cross_league: {len(rows)} rows, {len(football)} football clubs -> analysis/output/")
    return rows
