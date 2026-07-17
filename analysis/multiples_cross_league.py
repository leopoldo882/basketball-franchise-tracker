"""Cross-league valuation summary: NBA multiples by year alongside the JB
Capital EuroLeague figures.

No EuroLeague value/revenue multiple is computed: the official press release
gives no revenue base (stated limitation; revisit if the report PDF is found).
Football rows join later only if a Deloitte collector is added.
"""

import pandas as pd

from collectors import common

OUTPUT_DIR = common.PROJECT_ROOT / "analysis" / "output"


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []

    nba = pd.read_csv(common.DATA_DIR / "nba_valuations.csv")
    for y, sub in nba.groupby("list_year"):
        rows.append({"league": "NBA", "year": y, "metric": "median_value_rev_multiple",
                     "value": round((sub.value_usd_m / sub.revenue_usd_m).median(), 2),
                     "unit": "x revenue", "source_url": sub.source_url.iloc[0]})
        rows.append({"league": "NBA", "year": y, "metric": "league_avg_value",
                     "value": round(sub.value_usd_m.mean(), 1), "unit": "USD m",
                     "source_url": sub.source_url.iloc[0]})

    el = pd.read_csv(common.DATA_DIR / "manual" / "euroleague_valuations.csv")
    for _, r in el.iterrows():
        rows.append({"league": "EuroLeague", "year": r.season, "metric": f"jb_capital_{r.entity_type}",
                     "value": f"{r.value_eur_m_low}-{r.value_eur_m_high}" if r.value_eur_m_low != r.value_eur_m_high else r.value_eur_m_low,
                     "unit": "EUR m", "source_url": r.source_url})
    rows.append({"league": "EuroLeague", "year": "2025-26", "metric": "value_rev_multiple",
                 "value": "n/a", "unit": "",
                 "source_url": "no club revenue base published in the JB Capital press release"})

    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "multiples_summary.csv", index=False)
    print(f"multiples_cross_league: {len(rows)} rows -> analysis/output/")
    return rows
