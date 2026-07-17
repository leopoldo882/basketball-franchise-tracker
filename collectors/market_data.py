"""Daily adjusted close prices for listed sports companies and benchmarks, via yfinance.

Groups (see data_inventory.md decisions, 2026-07-15):
  eu_football — headline index members: European football clubs only.
                Turkish club stocks excluded (methodology.md).
  us_holdco   — separate labeled comparator line, never blended into the index.
  benchmark   — S&P 500 (price + total return), STOXX Europe 600, MSCI Europe ETF.

TKO rows before its 2023-09-12 listing are dropped: earlier history on the
ticker belongs to the legacy WWE listing (methodology.md).
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
    "EFG.PA": "eu_football",
    "PARKEN.CO": "eu_football",
    "BIF.CO": "eu_football",
    # US sports holdcos (separate comparator line)
    "MSGS": "us_holdco",
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
