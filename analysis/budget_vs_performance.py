"""Does a bigger EuroLeague budget mean a better league position?

For each season and budget definition, clubs are ranked by budget (1 = biggest,
using the midpoint of BasketNews' range) and compared with their regular-season
position. The correlation is Spearman's: the Pearson correlation of the two
rank columns, which gives the same answer without needing scipy. Tied budgets
get the average of their ranks.

Clubs are joined on canonical_name only. Any club that drops out of a join is
listed with the reason, so a missing club is never silently lost.
"""

import pandas as pd

from collectors import common

OUTPUT_DIR = common.PROJECT_ROOT / "analysis" / "output"


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    budgets = pd.read_csv(common.DATA_DIR / "euroleague_budgets.csv")
    standings = pd.read_csv(common.DATA_DIR / "euroleague_standings.csv")

    budgets["amount_mid_eur_m"] = (budgets.amount_low_eur_m + budgets.amount_high_eur_m) / 2

    joined_rows = []
    corr_rows = []
    recon_rows = []
    for (season, figure_type), sub in budgets.groupby(["season", "figure_type"]):
        merged = sub.merge(standings[["season", "canonical_name", "rs_rank", "wins", "losses"]],
                           on=["season", "canonical_name"], how="inner")

        # explain every budget row that didn't find a standings row
        season_clubs = set(standings[standings.season == season].canonical_name)
        dropped = sorted(set(sub.canonical_name) - set(merged.canonical_name))
        reasons = []
        for club in dropped:
            if club not in season_clubs:
                reasons.append(f"{club}: not in {season} standings (source gap)")
            else:
                reasons.append(f"{club}: MAPPING FAILURE - check team_names.csv")
        no_figure = sorted(season_clubs - set(sub.canonical_name))
        recon_rows.append({
            "season": season, "figure_type": figure_type,
            "budget_rows": len(sub), "standings_rows": len(season_clubs),
            "joined": len(merged),
            "dropped_budget_rows": "; ".join(reasons),
            "standings_clubs_without_this_figure": "; ".join(no_figure),
        })

        if len(merged) < 5:
            continue
        merged["budget_rank"] = merged.amount_mid_eur_m.rank(ascending=False, method="average")
        rho = merged.budget_rank.corr(merged.rs_rank)
        corr_rows.append({"season": season, "figure_type": figure_type,
                          "n_clubs": len(merged), "spearman_rho": round(rho, 4)})
        joined_rows.append(merged[["season", "figure_type", "canonical_name",
                                   "amount_mid_eur_m", "budget_rank", "rs_rank", "wins", "losses"]])

    recon = pd.DataFrame(recon_rows)
    recon.to_csv(OUTPUT_DIR / "budget_join_reconciliation.csv", index=False)
    print("\n  clubs dropped from each join, and why:")
    for _, r in recon.iterrows():
        print(f"    {r.season} {r.figure_type}: {r.budget_rows} budget rows, "
              f"{r.standings_rows} standings rows -> {r.joined} joined")
        if r.dropped_budget_rows:
            print(f"      dropped: {r.dropped_budget_rows}")
        if r.standings_clubs_without_this_figure:
            print(f"      no {r.figure_type} figure: {r.standings_clubs_without_this_figure}")
    if recon.dropped_budget_rows.str.contains("MAPPING FAILURE").any():
        print("    !! at least one club was lost because of the name mapping")

    pd.concat(joined_rows, ignore_index=True).to_csv(OUTPUT_DIR / "budget_vs_performance.csv", index=False)
    pd.DataFrame(corr_rows).to_csv(OUTPUT_DIR / "budget_rank_correlations.csv", index=False)
    print(f"budget_vs_performance: {len(corr_rows)} season/figure combinations -> analysis/output/")
    return corr_rows
