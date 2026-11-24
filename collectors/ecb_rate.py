"""ECB deposit facility rate, used as the risk-free rate for the Sharpe ratios
(every return in the risk table is in euros).

Daily series from the ECB's own data API (no key needed), averaged by month.
If the download fails the existing CSV is kept, so a short outage doesn't stop
the monthly refresh.
"""

import io

import pandas as pd
import requests

from . import common

ECB_URL = ("https://data-api.ecb.europa.eu/service/data/FM/D.U2.EUR.4F.KR.DFR.LEV"
           "?format=csvdata&detail=dataonly&startPeriod=2003-12")
OUTPUT_FILE = common.DATA_DIR / "ecb_deposit_rate.csv"


def run():
    try:
        response = requests.get(ECB_URL, headers={"User-Agent": common.USER_AGENT}, timeout=60)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"  WARNING ecb_rate: download failed ({type(error).__name__}), keeping the old {OUTPUT_FILE.name}")
        return pd.read_csv(OUTPUT_FILE)

    daily = pd.read_csv(io.StringIO(response.text), usecols=["TIME_PERIOD", "OBS_VALUE"])
    daily["month"] = pd.to_datetime(daily["TIME_PERIOD"]).dt.strftime("%Y-%m")
    monthly = daily.groupby("month", as_index=False)["OBS_VALUE"].mean()
    monthly.columns = ["month", "rate_pct"]
    monthly["rate_pct"] = monthly["rate_pct"].round(4)
    monthly.to_csv(OUTPUT_FILE, index=False)
    print(f"ecb_rate: {len(monthly)} months ({monthly.month.iloc[0]} to {monthly.month.iloc[-1]}) -> {OUTPUT_FILE.name}")
    return monthly
