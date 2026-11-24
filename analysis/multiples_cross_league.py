"""One table with the NBA's value/revenue multiple and average value per
Forbes edition next to the JB Capital EuroLeague figures.

There is no EuroLeague value/revenue multiple because the JB Capital press
release doesn't give the revenue the valuation is based on.
"""

import pandas as pd

from collectors import common

OUTPUT_DIR = common.PROJECT_ROOT / "analysis" / "output"


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
    print(f"multiples_cross_league: {len(rows)} rows -> analysis/output/")
    return rows
