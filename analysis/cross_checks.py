"""Two sanity checks on the Forbes NBA numbers.

1. Publisher divergence: Sportico's and CNBC's values for the same teams,
   compared with Forbes.
2. Deals vs estimates: the valuation implied by each NBA control sale,
   compared with the latest Forbes value for that team published before the
   deal was agreed.
"""

import pandas as pd

from analysis.nba_growth import EDITION_MONTHS
from collectors import common

OUTPUT_DIR = common.PROJECT_ROOT / "analysis" / "output"

# Each publisher's list is compared with the Forbes edition closest in time.
# Sportico 2026 came out in October 2026, the same month as Forbes 2026.
# CNBC 2026 came out in February 2026, four months after Forbes 2025.
COMPARE_WITH_FORBES = {"sportico": 2026, "cnbc": 2025}

# A Forbes value older than this is too stale to compare with a deal price.
MAX_MONTHS_SINCE_FORBES = 12


def publisher_divergence(forbes):
    publishers = pd.read_csv(common.DATA_DIR / "manual" / "publisher_divergence.csv")
    rows = []
    for publisher, sub in publishers.groupby("publisher"):
        edition = COMPARE_WITH_FORBES[publisher]
        forbes_edition = forbes[forbes.list_year == edition][["team", "value_usd_m"]]
        merged = sub.merge(forbes_edition, on="team", suffixes=("", "_forbes"))

        missing = sorted(set(sub.team) - set(merged.team))
        if missing:
            print(f"  WARNING {publisher}: no Forbes {edition} match for {missing}")

        pct_diff = merged.value_usd_m / merged.value_usd_m_forbes - 1
        rows.append({
            "publisher": publisher,
            "publisher_list_year": int(sub.list_year.iloc[0]),
            "forbes_edition": edition,
            "n_teams": len(merged),
            "mean_pct_diff_vs_forbes": round(pct_diff.mean(), 4),
            "mean_abs_pct_diff_vs_forbes": round(pct_diff.abs().mean(), 4),
            "max_abs_pct_diff_vs_forbes": round(pct_diff.abs().max(), 4),
        })
    return pd.DataFrame(rows)


def latest_forbes_before(deal_month):
    """(edition, months between that edition and the deal), or (None, None)."""
    earlier = [(edition, (deal_month - pd.Period(month, "M")).n)
               for edition, month in EDITION_MONTHS.items()
               if pd.Period(month, "M") < deal_month]
    if not earlier:
        return None, None
    return min(earlier, key=lambda pair: pair[1])


def deals_vs_forbes(forbes):
    deals = pd.read_csv(common.DATA_DIR / "manual" / "transactions.csv")
    deals = deals[(deals.league == "NBA") & (deals.control == "y")
                  & deals.implied_valuation_usd_m.notna()]

    rows = []
    for _, deal in deals.iterrows():
        edition, months = latest_forbes_before(pd.Period(deal.date, "M"))
        forbes_value = None
        if edition is not None and months <= MAX_MONTHS_SINCE_FORBES:
            match = forbes[(forbes.list_year == edition) & (forbes.team == deal.team)]
            if not match.empty:
                forbes_value = float(match.value_usd_m.iloc[0])

        rows.append({
            "date": deal.date,
            "team": deal.team,
            "buyer": deal.buyer,
            "implied_valuation_usd_m": deal.implied_valuation_usd_m,
            "forbes_edition": edition if forbes_value else "",
            "forbes_value_usd_m": forbes_value if forbes_value else "",
            "months_after_forbes": months if forbes_value else "",
            "deal_over_forbes": round(deal.implied_valuation_usd_m / forbes_value, 3) if forbes_value else "",
            "notes": deal.notes,
        })
    return pd.DataFrame(rows).sort_values("date")


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    forbes = pd.read_csv(common.DATA_DIR / "nba_valuations.csv")

    divergence = publisher_divergence(forbes)
    divergence.to_csv(OUTPUT_DIR / "publisher_divergence.csv", index=False)

    deals = deals_vs_forbes(forbes)
    deals.to_csv(OUTPUT_DIR / "transactions_vs_forbes.csv", index=False)

    compared = (deals.deal_over_forbes != "").sum()
    print(f"cross_checks: {len(divergence)} publishers, {len(deals)} deals "
          f"({compared} with a recent Forbes value) -> analysis/output/")
    return divergence, deals
