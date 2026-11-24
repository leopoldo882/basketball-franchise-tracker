"""Daily exchange rates from Yahoo Finance, used to convert prices to EUR.

Each rate is units of the other currency per 1 EUR, so price / rate = EUR.
EURGBP goes back to 1999 but EURUSD and EURDKK only to Dec 2003, which is
why the EUR index starts in January 2004.
"""

import pandas as pd
import yfinance as yf

from . import common

PAIRS = {
    "EURUSD=X": "USD",
    "EURGBP=X": "GBP",
    "EURDKK=X": "DKK",
}

OUTPUT_FILE = common.DATA_DIR / "fx_rates.csv"


def run():
    frames = []
    for pair, currency in PAIRS.items():
        history = yf.Ticker(pair).history(period="max", auto_adjust=True)
        if history.empty:
            print(f"  WARNING {pair}: no data returned")
            continue
        df = history[["Close"]].reset_index()
        df["date"] = pd.to_datetime(df["Date"]).dt.date
        df["currency"] = currency
        df["per_eur"] = df["Close"].round(6)
        frames.append(df[["date", "currency", "per_eur"]])

    out = pd.concat(frames, ignore_index=True)
    out.to_csv(OUTPUT_FILE, index=False)
    print(f"fx_rates: {len(out)} rows, {out['currency'].nunique()} currencies -> {OUTPUT_FILE.name}")
    return out
