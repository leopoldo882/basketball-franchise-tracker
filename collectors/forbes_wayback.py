"""Forbes NBA team valuations (value and revenue for all 30 teams).

The Forbes list page builds itself with JavaScript, so an archived copy of the
page is empty. The data comes from a JSON endpoint the page calls:

    forbes.com/ajax/list/data?year=YYYY&uri=nba-valuations&type=organization

and the Wayback Machine has archived that endpoint for most years. I found the
captures through the Wayback CDX index and pinned the timestamps below so the
same run always gets the same data. The "id_" in the URL asks Wayback for the
original response without its toolbar.

Any year with no usable capture can be typed into
data/manual/nba_valuations_manual.csv instead; those rows are appended.
"""

import json

import pandas as pd

from . import common

# Forbes edition -> Wayback capture timestamp.
# Edition labels follow Forbes: 2016 and 2019 lists came out in February of
# that year, the 2022 list in October 2021, the 2024-2026 lists in October of
# the same year. I checked each capture against the published Warriors value.
ARCHIVED_CAPTURES = {
    2016: "20180210041436",
    2019: "20190401155819",
    2022: "20211109185923",
    2024: "20250702165507",
    2025: "20261021083103",
    2026: "20261021083152",
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
    frames = [pd.DataFrame(rows)]
    if len(manual) > 0:
        frames.append(manual)
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(OUTPUT_FILE, index=False)
    print(f"forbes_wayback: {len(rows)} archived + {len(manual)} manual rows -> {OUTPUT_FILE.name}")
    return combined
