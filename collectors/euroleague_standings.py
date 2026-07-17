"""EuroLeague regular-season standings from the official open XML API.

Endpoint: https://api-live.euroleague.net/v1/standings?seasonCode=EYYYY
No API key needed. Regular-season standings only (methodology.md ruling:
consistent basis across seasons, never post-playoff placements).
"""

import xml.etree.ElementTree as ET

import pandas as pd

from . import common

# EYYYY code -> human season label
SEASONS = {
    "E2021": "2021-22",
    "E2022": "2022-23",
    "E2023": "2023-24",
    "E2024": "2024-25",
    "E2025": "2025-26",
}

API_URL = "https://api-live.euroleague.net/v1/standings?seasonCode={code}"
OUTPUT_FILE = common.DATA_DIR / "euroleague_standings.csv"


def pick_regular_season_group(root):
    """The XML holds one <group> per phase; take the regular season one."""
    for group in root.findall("group"):
        if group.get("round") == "RS" or "Regular" in (group.get("name") or ""):
            return group
    return None


def run():
    by_api_code, _ = common.load_team_mapping()
    rows = []
    for code, season in SEASONS.items():
        xml_text = common.polite_get(API_URL.format(code=code), f"euroleague_standings_{code}.xml")
        group = pick_regular_season_group(ET.fromstring(xml_text))
        if group is None:
            print(f"  WARNING {season}: no regular-season group in API response")
            continue
        for team in group.findall("team"):
            team_code = team.findtext("code")
            rows.append({
                "season": season,
                "team_code": team_code,
                "team_name": team.findtext("name"),
                "canonical_name": by_api_code.get(team_code, ""),
                "rs_rank": int(team.findtext("ranking")),
                "wins": int(team.findtext("wins")),
                "losses": int(team.findtext("losses")),
            })
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"euroleague_standings: {len(df)} rows, {df['season'].nunique()} seasons -> {OUTPUT_FILE.name}")
    return df
