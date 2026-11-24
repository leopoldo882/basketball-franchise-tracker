"""Market value, enterprise value and revenue of the listed football clubs from
Yahoo Finance (yfinance's Ticker.info), for the EV/revenue comparison.

Yahoo only gives today's values, so every run replaces the file. I don't use
Yahoo's own EV/revenue figure: for Manchester United it divides an enterprise
value in dollars by revenue in pounds. The analysis converts both to euros.
"""

import datetime

import pandas as pd
import yfinance as yf

from . import common
from .market_data import TICKERS

CLUB_NAMES = {
    "MANU": "Manchester United",
    "JUVE.MI": "Juventus",
    "SSL.MI": "Lazio",
    "BVB.DE": "Borussia Dortmund",
    "AJAX.AS": "Ajax",
    "CCP.L": "Celtic",
    "SLBEN.LS": "Benfica",
    "FCP.LS": "FC Porto",
    "SCP.LS": "Sporting CP",
    "OLG.PA": "Olympique Lyonnais",
    "PARKEN.CO": "FC København (Parken)",
    "BIF.CO": "Brøndby",
}

OUTPUT_FILE = common.DATA_DIR / "club_fundamentals.csv"


def run():
    today = datetime.date.today().isoformat()
    rows = []
    for ticker, group in TICKERS.items():
        if group != "eu_football":
            continue
        try:
            info = yf.Ticker(ticker).info
        except Exception as error:  # yfinance raises many different error types
            print(f"  WARNING {ticker}: no fundamentals ({type(error).__name__})")
            continue
        if not info.get("enterpriseValue") or not info.get("totalRevenue"):
            print(f"  WARNING {ticker}: enterprise value or revenue missing")
            continue
        rows.append({
            "ticker": ticker,
            "club": CLUB_NAMES[ticker],
            "fetched_on": today,
            "market_cap": info.get("marketCap"),
            "enterprise_value": info["enterpriseValue"],
            "revenue_ttm": info["totalRevenue"],
            "trading_currency": info.get("currency"),
            "financial_currency": info.get("financialCurrency"),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"club_fundamentals: {len(df)} of 12 clubs -> {OUTPUT_FILE.name}")
    return df
