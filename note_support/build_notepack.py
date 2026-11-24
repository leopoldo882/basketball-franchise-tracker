"""Build note_support/: every dashboard chart as a PNG, plus facts.md.

facts.md is a list of the computed numbers with their sources and nothing
else. Every figure is read from the pipeline's CSVs, none are typed in.

PNG export needs kaleido, which is only in requirements-notepack.txt. The
monthly GitHub Action never builds this folder, so CI doesn't need kaleido.
"""

import pandas as pd

from collectors import common
from dashboard.build import build_figures, data_date, headline_stats

NOTE_DIR = common.PROJECT_ROOT / "note_support"
AOUT = common.PROJECT_ROOT / "analysis" / "output"
MANUAL = common.DATA_DIR / "manual"


def export_pngs():
    try:
        import kaleido  # noqa: F401  (plotly uses it behind the scenes)
    except ImportError:
        raise SystemExit("kaleido is not installed: pip install -r requirements-notepack.txt")
    names = []
    for div_id, _title, _note, fig in build_figures():
        path = NOTE_DIR / f"{div_id}.png"
        fig.write_image(path, width=1200, scale=2)
        names.append(path.name)
    return names


def text(value):
    """CSV cells that are empty come back as NaN; print them as nothing."""
    return value if isinstance(value, str) else ""


def table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return lines


def write_facts():
    growth = pd.read_csv(AOUT / "nba_growth.csv")
    stats = pd.read_csv(AOUT / "listed_index_stats.csv")
    corr = pd.read_csv(AOUT / "budget_rank_correlations.csv")
    recon = pd.read_csv(AOUT / "budget_join_reconciliation.csv")
    deals = pd.read_csv(AOUT / "transactions_vs_forbes.csv")
    divergence = pd.read_csv(AOUT / "publisher_divergence.csv")
    el = pd.read_csv(MANUAL / "euroleague_valuations.csv")
    lnb = pd.read_csv(MANUAL / "lnb_dnccg.csv")
    acb = pd.read_csv(MANUAL / "acb_budgets.csv")
    lba = pd.read_csv(MANUAL / "lba_budgets.csv")

    lines = [
        "# Facts sheet",
        "",
        f"Numbers computed by `python run_pipeline.py --notepack`, market data to {data_date()}.",
        "Each section says where its numbers come from. No commentary.",
        "",
        "## Headline numbers",
        "",
    ]
    for num, label, sub in headline_stats(growth, stats, corr):
        lines.append(f"- **{num}**: {label} ({sub})")

    lines += ["", "## Listed index (analysis/output/listed_index_stats.csv)", ""]
    lines += table(["series", "metric", "value", "window", "months", "note"],
                   [(r.series, r.metric, r.value, f"{r.window_start} to {r.window_end}", r.n_months, text(r.note))
                    for _, r in stats.iterrows()])
    lines += ["", "Source: Yahoo Finance adjusted closes via yfinance, converted to EUR with yfinance "
                  "FX rates. Index rules in methodology.md."]

    lines += ["", "## NBA team values (analysis/output/nba_growth.csv)", ""]
    rows = []
    for _, r in growth.iterrows():
        editions = str(r.list_year_start) if r.list_year_start == r.list_year_end \
            else f"{r.list_year_start} to {r.list_year_end}"
        rows.append((r.metric, editions, r.value, text(r.note)))
    lines += table(["metric", "editions", "value", "note"], rows)
    lines += ["", "Source: Forbes list data archived on the Wayback Machine (capture links in "
                  "data/nba_valuations.csv); S&P 500 total return = ^SP500TR in USD; inflation = FRED CPIAUCSL."]

    lines += ["", "## NBA control sales vs the last Forbes value (analysis/output/transactions_vs_forbes.csv)", ""]
    rows = []
    for _, d in deals.iterrows():
        compared = pd.notna(d.deal_over_forbes)
        rows.append((d.date, d.team, d.buyer, f"{d.implied_valuation_usd_m:.0f}",
                     f"{d.forbes_value_usd_m:.0f} ({int(d.forbes_edition)})" if compared else "",
                     f"{d.deal_over_forbes:.3f}" if compared else "", text(d.notes)))
    lines += table(["agreed", "team", "buyer", "deal valuation $M", "Forbes $M (edition)", "deal / Forbes", "notes"],
                   rows)
    lines += ["", "Source: one news link per deal in data/manual/transactions.csv. Compared only when "
                  "the Forbes list was published less than 12 months before the deal."]

    lines += ["", "## Other publishers vs Forbes (analysis/output/publisher_divergence.csv)", ""]
    lines += table(["publisher", "list", "Forbes edition", "teams", "mean diff", "mean abs diff", "max abs diff"],
                   [(r.publisher, r.publisher_list_year, r.forbes_edition, r.n_teams,
                     r.mean_pct_diff_vs_forbes, r.mean_abs_pct_diff_vs_forbes, r.max_abs_pct_diff_vs_forbes)
                    for _, r in divergence.iterrows()])
    lines += ["", "Source: Sportico values as reported by Bleacher Report (Oct 2026, 4 teams), CNBC values "
                  "as republished by NBC Chicago (Feb 2026, 15 teams). Diff = publisher / Forbes - 1."]

    lines += ["", "## EuroLeague budget rank vs regular-season position", ""]
    lines += table(["season", "figure type", "clubs", "Spearman rho"],
                   [(r.season, r.figure_type, r.n_clubs, r.spearman_rho) for _, r in corr.iterrows()])
    lines += ["", "Clubs dropped from the join (all missing from that season's standings, none from the "
                  "name mapping):"]
    for _, r in recon.iterrows():
        if text(r.dropped_budget_rows):
            lines.append(f"- {r.season} {r.figure_type}: {r.dropped_budget_rows}")
    lines += ["", "Source: BasketNews budget research (midpoint of each reported range) and the official "
                  "EuroLeague API standings."]

    lines += ["", "## EuroLeague valuation (JB Capital, March 2026)", ""]
    for _, r in el.iterrows():
        if r.value_eur_m_low == r.value_eur_m_high:
            value = f"€{r.value_eur_m_low:.0f}M"
        else:
            value = f"€{r.value_eur_m_low:.0f}M to €{r.value_eur_m_high:.0f}M"
        lines.append(f"- {r.entity} ({r.season}): **{value}**, {r.basis}")
    lines += ["", f"Source: {el.source_url.iloc[0]}"]

    lines += ["", "## French top division (LNB / DNCCG)", ""]
    budget = lnb[lnb.figure_type == "budget_total"].pivot(index="club", columns="season", values="amount_eur_m")
    payroll = lnb[lnb.figure_type == "payroll_dnccg"].pivot(index="club", columns="season", values="amount_eur_m")
    budget = budget.sort_values("2025-26", ascending=False)
    rows = []
    for club, b in budget.iterrows():
        share = payroll.loc[club, "2025-26"] / b["2025-26"]
        before = f"{b['2024-25']:.3f}" if pd.notna(b["2024-25"]) else "promoted"
        rows.append((club, before, f"{b['2025-26']:.3f}", f"{payroll.loc[club, '2025-26']:.3f}", f"{share:.0%}"))
    lines += table(["club", "budget 2024-25 €M", "budget 2025-26 €M", "payroll 2025-26 €M", "payroll / budget"],
                   rows)
    lines += ["", f"2025-26 average budget: €{budget['2025-26'].mean():.3f}M, median "
                  f"€{budget['2025-26'].median():.3f}M ({len(budget)} clubs).", ""]
    accounts = lnb[lnb.figure_type.isin(["operating_result", "net_result"])]
    for _, r in accounts.iterrows():
        lines.append(f"- {r.season} {r.club}, {r.figure_type.replace('_', ' ')}: €{r.amount_eur_m:.1f}M")
    lines += ["", f"Source: budgets {lnb[lnb.figure_type == 'budget_total'].source_url.iloc[0]} ; "
                  f"accounts {accounts.source_url.iloc[0]}. Budget = total revenue filed in September; "
                  "payroll = gross payroll for players and coaches as approved by the DNCCG."]

    lines += ["", "## Spanish and Italian club budgets (reference only)", "",
              "Different seasons and definitions from the French and EuroLeague numbers, so not comparable "
              "one-to-one.", ""]
    rows = [("ACB", r.season, r.club, r.amount_eur_m, r.figure_type) for _, r in acb.iterrows()]
    rows += [("LBA", r.season, r.club, r.amount_eur_m, r.figure_type) for _, r in lba.iterrows()]
    lines += table(["league", "season", "club", "€M", "figure"], rows)
    lines += ["", f"Sources: {acb.source_url.iloc[0]} ; {lba.source_url.iloc[0]} (citing La Prealpina)."]

    lines += ["", "## Chart files", "", "One PNG per dashboard chart, named after the chart's id on the page."]
    (NOTE_DIR / "facts.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def run():
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    pngs = export_pngs()
    n_lines = write_facts()
    print(f"note_support: {len(pngs)} PNGs + facts.md ({n_lines} lines) -> note_support/")


if __name__ == "__main__":
    run()
