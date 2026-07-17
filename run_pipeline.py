"""Refresh every dataset end to end: run all collectors, validate the
manual-entry CSVs and the team-name mapping coverage, then rebuild the
analysis outputs.

Usage: python run_pipeline.py
"""

import sys

import pandas as pd

from collectors import (basketnews_budgets, common, euroleague_standings, forbes_wayback,
                        fx_rates, market_data, us_cpi)
from analysis import budget_vs_performance, listed_index, multiples_cross_league, nba_growth

MANUAL_DIR = common.DATA_DIR / "manual"

# expected columns, numeric columns, and duplicate-key columns per manual file
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
        "columns": ["season", "club", "revenue_eur_m", "payroll_eur_m", "net_result_eur_m", "source_url"],
        "numeric": ["revenue_eur_m", "payroll_eur_m", "net_result_eur_m"],
        "key": ["season", "club"],
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
    """Schema-check every manual CSV. Returns the number of hard errors."""
    errors = 0
    print("\n-- manual file validation --")
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
            non_numeric = pd.to_numeric(values, errors="coerce").isna()
            if non_numeric.any():
                problems.append(f"non-numeric {col}: {values[non_numeric].tolist()}")
        duplicated = df.duplicated(subset=schema["key"])
        if duplicated.any():
            problems.append(f"duplicate keys on {schema['key']}: {df.loc[duplicated, schema['key']].values.tolist()}")
        if problems:
            for p in problems:
                print(f"ERROR   {filename}: {p}")
            errors += len(problems)
        elif len(df) == 0:
            print(f"OK      {filename}: template-only (0 data rows)")
        else:
            print(f"OK      {filename}: {len(df)} rows")
    return errors


def validate_mapping_coverage():
    """Every team in the budgets and standings CSVs must resolve to a canonical
    name via data/mappings/team_names.csv. Unmapped names are flagged."""
    print("\n-- team-name mapping coverage --")
    unmapped_total = 0
    checks = [
        (common.DATA_DIR / "euroleague_budgets.csv", "team_basketnews"),
        (common.DATA_DIR / "euroleague_standings.csv", "team_name"),
    ]
    for path, source_col in checks:
        df = pd.read_csv(path)
        unmapped = df[df["canonical_name"].isna() | (df["canonical_name"].astype(str).str.strip() == "")]
        if len(unmapped) == 0:
            print(f"OK      {path.name}: all {len(df)} rows mapped")
        else:
            names = sorted(unmapped[source_col].unique())
            print(f"FLAG    {path.name}: {len(unmapped)} unmapped rows — add to team_names.csv: {names}")
            unmapped_total += len(unmapped)
    return unmapped_total


def main():
    print("== collectors ==")
    euroleague_standings.run()
    basketnews_budgets.run()
    forbes_wayback.run()
    market_data.run()
    fx_rates.run()
    us_cpi.run()

    errors = validate_manual_files()
    validate_mapping_coverage()

    if errors:
        print(f"\nFAILED: {errors} schema error(s) in manual files")
        sys.exit(1)

    print("\n== analysis ==")
    listed_index.run()
    nba_growth.run()
    budget_vs_performance.run()
    multiples_cross_league.run()

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
