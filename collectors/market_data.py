"""Daily adjusted closing prices from Yahoo Finance (via yfinance) for the
listed sports companies and the benchmarks.

Each ticker belongs to one group:
  eu_football  European football clubs, the headline index (Turkish clubs left out)
  us_holdco    US sports holding companies, shown as a separate line
  benchmark    S&P 500 (price and total return), STOXX Europe 600, MSCI Europe ETF

Ticker changes in 2026 (the old symbols now return only a few months of data):
  MSGS -> MSGK    MSG Sports split off the Rangers in Oct 2026 and the Knicks
                  company kept the history under MSGK. Yahoo books the spin-off
                  as a 1.328 split, so the series has no artificial drop.
  EFG.PA -> OLG.PA  Eagle Football Group renamed OL Groupe (Lyon), Oct 2026.

TKO prices before 12 Sep 2023 belong to the old WWE listing, so they are dropped.
"""

import pandas as pd
import yfinance as yf

from . import common

TICKERS = {
    # European football clubs (headline index)
    "MANU": "eu_football",
    "JUVE.MI": "eu_football",
    "SSL.MI": "eu_football",
    "BVB.DE": "eu_football",
    "AJAX.AS": "eu_football",
    "CCP.L": "eu_football",
    "SLBEN.LS": "eu_football",
    "FCP.LS": "eu_football",
    "SCP.LS": "eu_football",
    "OLG.PA": "eu_football",
    "PARKEN.CO": "eu_football",
    "BIF.CO": "eu_football",
    # US sports holding companies (separate comparison line)
    "MSGK": "us_holdco",
    "BATRA": "us_holdco",
    "TKO": "us_holdco",
    "MSGE": "us_holdco",
    # Benchmarks
    "^GSPC": "benchmark",
    "^SP500TR": "benchmark",
    "^STOXX": "benchmark",
    "IEUR": "benchmark",
}

TKO_LISTING_DATE = "2023-09-12"

OUTPUT_FILE = common.DATA_DIR / "market_prices.csv"


def run():
    frames = []
    for ticker, group in TICKERS.items():
        t = yf.Ticker(ticker)
        history = t.history(period="max", auto_adjust=True)
        if history.empty:
            print(f"  WARNING {ticker}: no data returned")
            continue
        df = history[["Close"]].reset_index()
        df["date"] = pd.to_datetime(df["Date"]).dt.date
        df["ticker"] = ticker
        df["close_adj"] = df["Close"].round(4)
        df["currency"] = t.fast_info.get("currency", "")
        df["group"] = group
        if ticker == "TKO":
            df = df[df["date"] >= pd.to_datetime(TKO_LISTING_DATE).date()]
        frames.append(df[["date", "ticker", "close_adj", "currency", "group"]])

    out = pd.concat(frames, ignore_index=True)
    out.to_csv(OUTPUT_FILE, index=False)
    print(f"market_data: {len(out)} rows, {out['ticker'].nunique()} tickers -> {OUTPUT_FILE.name}")
    return out
