"""Monthly US consumer prices (CPIAUCSL) from FRED's public CSV download.

Only used for one number: the inflation-adjusted NBA growth rate in the
facts sheet. Everything on the dashboard is in nominal terms.
"""

import io

import pandas as pd
import requests

from . import common

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"
OUTPUT_FILE = common.DATA_DIR / "us_cpi.csv"


def run():
    response = requests.get(FRED_URL, headers={"User-Agent": common.USER_AGENT}, timeout=30)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    df.columns = ["month", "cpi"]
    df["month"] = pd.to_datetime(df["month"]).dt.strftime("%Y-%m")
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"us_cpi: {len(df)} rows ({df['month'].iloc[0]} to {df['month'].iloc[-1]}) -> {OUTPUT_FILE.name}")
    return df
