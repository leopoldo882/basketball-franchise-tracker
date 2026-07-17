"""NBA valuations panel: Forbes list data for 2016 / 2019 / 2022 from the
Wayback Machine, merged with manually keyed rows (2024 + 2025 editions).

The Forbes list page itself was JavaScript-rendered, so archived page HTML is
an empty shell. But the Wayback Machine also archived the JSON endpoint the
page loaded its data from (found via the Wayback CDX index):
    forbes.com/ajax/list/data?year=YYYY&uri=nba-valuations&type=organization
Each capture is the full 30-team list with value and revenue. Snapshot
timestamps are pinned below so the pipeline is reproducible; the `id_` flag
in the URL returns the original response bytes without Wayback banners.
"""

import json

import pandas as pd

from . import common

# list edition year -> pinned Wayback capture timestamp (verified 200, application/json)
ARCHIVED_CAPTURES = {
    2016: "20180210041436",
    2019: "20190401155819",
    2022: "20211109185923",
}

FETCH_URL = ("https://web.archive.org/web/{ts}id_/https://www.forbes.com/"
             "ajax/list/data?year={year}&uri=nba-valuations&type=organization")
CITE_URL = ("https://web.archive.org/web/{ts}/https://www.forbes.com/"
            "ajax/list/data?year={year}&uri=nba-valuations&type=organization")

MANUAL_FILE = common.DATA_DIR / "manual" / "nba_valuations_manual.csv"
OUTPUT_FILE = common.DATA_DIR / "nba_valuations.csv"


def run():
    rows = []
    for year, ts in ARCHIVED_CAPTURES.items():
        text = common.polite_get(FETCH_URL.format(ts=ts, year=year), f"forbes_nba_api_{year}.json")
        teams = json.loads(text)
        if len(teams) != 30:
            print(f"  WARNING {year}: expected 30 teams, got {len(teams)}")
        for item in teams:
            rows.append({
                "list_year": year,
                "team": item.get("name"),
                "rank": item.get("rank") or item.get("position"),
                "value_usd_m": item.get("valueList") or item.get("value"),
                "revenue_usd_m": item.get("revenue"),
                "source": "forbes_wayback",
                "source_url": CITE_URL.format(ts=ts, year=year),
            })

    manual = pd.read_csv(MANUAL_FILE)
    frames = [pd.DataFrame(rows)] + ([manual] if len(manual) else [])
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(OUTPUT_FILE, index=False)
    print(f"forbes_wayback: {len(rows)} scraped + {len(manual)} manual rows -> {OUTPUT_FILE.name}")
    return combined
