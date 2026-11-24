"""Run the whole project: collect data, check the hand-entered files, run the
analysis and rebuild the dashboard.

    python run_pipeline.py                everything
    python run_pipeline.py --market-only  only prices, FX, club fundamentals and
                                          rates (what the monthly GitHub Action
                                          runs; it never scrapes, there's no
                                          data/raw cache there)
    python run_pipeline.py --notepack     also export chart PNGs and facts.md to
                                          note_support/ (needs requirements-notepack.txt)
"""

import sys

import pandas as pd

from analysis import (budget_vs_performance, cross_checks, listed_index, multiples_cross_league,
                      nba_growth, risk_return)
from collectors import (basketnews_budgets, club_fundamentals, common, ecb_rate, euroleague_standings,
                        forbes_wayback, fx_rates, market_data, us_cpi)
from dashboard import build as dashboard_build

MANUAL_DIR = common.DATA_DIR / "manual"

# For each hand-entered file: the exact columns, which ones must be numbers,
# and which columns together should be unique.
MANUAL_SCHEMAS = {
    "nba_valuations_manual.csv": {
        "columns": ["list_year", "team", "rank", "value_usd_m", "revenue_usd_m", "source", "source_url"],
        "numeric": ["list_year", "value_usd_m", "revenue_usd_m"],
        "key": ["list_year", "team", "source"],
    },
    "publisher_divergence.csv": {
        "columns": ["publisher", "list_year", "team", "value_usd_m", "source_url"],
        "numeric": ["list_year", "value_usd_m"],
        "key": ["publisher", "list_year", "team"],
    },
    "lnb_dnccg.csv": {
        "columns": ["season", "club", "figure_type", "amount_eur_m", "source_url"],
        "numeric": ["amount_eur_m"],
        "key": ["season", "club", "figure_type"],
    },
    "euroleague_valuations.csv": {
        "columns": ["season", "entity", "entity_type", "value_eur_m_low", "value_eur_m_high", "basis", "source_url"],
        "numeric": ["value_eur_m_low", "value_eur_m_high"],
        "key": ["season", "entity"],
    },
    "transactions.csv": {
        "columns": ["date", "league", "team", "buyer", "buyer_type", "stake_pct", "control",
                    "price_usd_m", "implied_valuation_usd_m", "source_url", "notes"],
        "numeric": ["stake_pct", "price_usd_m", "implied_valuation_usd_m"],
        "key": ["date", "team", "buyer"],
    },
    "acb_budgets.csv": {
        "columns": ["season", "club", "amount_eur_m", "figure_type", "source_url"],
        "numeric": ["amount_eur_m"],
        "key": ["season", "club", "figure_type"],
    },
    "lba_budgets.csv": {
        "columns": ["season", "club", "amount_eur_m", "figure_type", "source_url"],
        "numeric": ["amount_eur_m"],
        "key": ["season", "club", "figure_type"],
    },
}


def validate_manual_files():
    """Check every file in data/manual/ against MANUAL_SCHEMAS.
    Returns the number of errors found."""
    errors = 0
    print("\n-- checking manual files --")
    for filename, schema in MANUAL_SCHEMAS.items():
        path = MANUAL_DIR / filename
        if not path.exists():
            print(f"ERROR   {filename}: missing")
            errors += 1
            continue

        df = pd.read_csv(path)
        if list(df.columns) != schema["columns"]:
            print(f"ERROR   {filename}: columns are {list(df.columns)}, expected {schema['columns']}")
            errors += 1
            continue

        problems = []
        for col in schema["numeric"]:
            values = df[col].dropna()
            values = values[values.astype(str).str.strip() != ""]
            not_numbers = pd.to_numeric(values, errors="coerce").isna()
            if not_numbers.any():
                problems.append(f"non-numeric {col}: {values[not_numbers].tolist()}")
        duplicates = df.duplicated(subset=schema["key"])
        if duplicates.any():
            problems.append(f"duplicate {schema['key']}: {df.loc[duplicates, schema['key']].values.tolist()}")

        for p in problems:
            print(f"ERROR   {filename}: {p}")
        errors += len(problems)
        if not problems:
            print(f"OK      {filename}: {len(df)} rows")
    return errors


def check_team_mapping():
    """Every team in the budgets and standings files needs a canonical name
    from data/mappings/team_names.csv, otherwise the join silently loses it."""
    print("\n-- checking team-name mapping --")
    unmapped_total = 0
    checks = [
        (common.DATA_DIR / "euroleague_budgets.csv", "team_basketnews"),
        (common.DATA_DIR / "euroleague_standings.csv", "team_name"),
    ]
    for path, name_col in checks:
        df = pd.read_csv(path)
        unmapped = df[df["canonical_name"].isna() | (df["canonical_name"].astype(str).str.strip() == "")]
        if len(unmapped) == 0:
            print(f"OK      {path.name}: all {len(df)} rows mapped")
        else:
            names = sorted(unmapped[name_col].unique())
            print(f"FLAG    {path.name}: {len(unmapped)} rows unmapped, add to team_names.csv: {names}")
            unmapped_total += len(unmapped)
    return unmapped_total


def main():
    market_only = "--market-only" in sys.argv

    print("== collecting ==")
    if not market_only:
        euroleague_standings.run()
        basketnews_budgets.run()
        forbes_wayback.run()
    market_data.run()
    fx_rates.run()
    club_fundamentals.run()
    us_cpi.run()
    ecb_rate.run()

    errors = validate_manual_files()
    check_team_mapping()
    if errors:
        print(f"\nStopped: {errors} problem(s) in the manual files")
        sys.exit(1)

    print("\n== analysis ==")
    listed_index.run()
    risk_return.run()
    nba_growth.run()
    budget_vs_performance.run()
    multiples_cross_league.run()
    cross_checks.run()

    print("\n== dashboard ==")
    dashboard_build.run()

    if "--notepack" in sys.argv:
        # imported here so normal runs don't need kaleido installed
        from note_support import build_notepack
        print("\n== note support ==")
        build_notepack.run()

    print("\nDone.")


if __name__ == "__main__":
    main()
