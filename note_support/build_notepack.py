"""Build /note_support: every dashboard chart as a PNG plus facts.md.

facts.md holds computed numbers with source attribution and nothing editorial —
the investment note itself is written by hand, not here. Every number below is
read from the pipeline's CSVs at build time, never typed in.

PNG export needs kaleido, which is deliberately a LOCAL-ONLY dependency
(requirements-notepack.txt): the monthly CI refresh never builds this pack.
This module is imported only behind run_pipeline.py's --notepack flag.
"""

import datetime

import pandas as pd

from collectors import common
from dashboard.build import build_figures, headline_stats

NOTE_DIR = common.PROJECT_ROOT / "note_support"
AOUT = common.PROJECT_ROOT / "analysis" / "output"

FORBES_ARCHIVE_NOTE = ("Forbes NBA list data via Wayback-archived Forbes AJAX JSON "
                       "(capture URLs in data/nba_valuations.csv, source_url column)")
JB_URL = ("https://www.euroleaguebasketball.net/news/"
          "euroleague-and-clubs-valued-at-over-3-2-billion-according-to-jb-capital/")


def export_pngs():
    try:
        import kaleido  # noqa: F401 — presence check only; plotly calls it internally
    except ImportError:
        raise SystemExit("kaleido not installed — run: pip install -r requirements-notepack.txt")
    names = []
    for div_id, _title, _note, fig in build_figures():
        path = NOTE_DIR / f"{div_id}.png"
        fig.write_image(path, width=1200, scale=2)
        names.append(path.name)
    return names


def pct(x):
    return f"{x * 100:.1f}%"


def write_facts():
    growth = pd.read_csv(AOUT / "nba_growth.csv")
    stats = pd.read_csv(AOUT / "listed_index_stats.csv")
    corr = pd.read_csv(AOUT / "budget_rank_correlations.csv")
    recon = pd.read_csv(AOUT / "budget_join_reconciliation.csv")
    el = pd.read_csv(common.DATA_DIR / "manual" / "euroleague_valuations.csv")

    built = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Facts sheet — computed numbers with sources",
        "",
        f"Generated {built} by `python run_pipeline.py --notepack`. Every number",
        "regenerates from the pipeline CSVs; nothing here is editorial.",
        "",
        "## Headline numbers",
        "",
    ]
    for num, label, sub in headline_stats(growth, stats, corr):
        lines.append(f"- **{num}** — {label} ({sub})")

    lines += ["", "## Listed index statistics (analysis/output/listed_index_stats.csv)",
              "", "| series | metric | value | window | months | note |", "|---|---|---|---|---|---|"]
    for _, r in stats.iterrows():
        note = r.note if isinstance(r.note, str) else ""
        lines.append(f"| {r.series} | {r.metric} | {r.value} | {r.window_start} → {r.window_end} | {r.n_months} | {note} |")
    lines += ["", "Source: Yahoo Finance adjusted closes via yfinance; EUR conversion via "
                  "yfinance FX pairs; construction rules in methodology.md."]

    lines += ["", "## NBA valuation metrics (analysis/output/nba_growth.csv)",
              "", "| metric | editions | value | note |", "|---|---|---|---|"]
    for _, r in growth.iterrows():
        note = r.note if isinstance(r.note, str) else ""
        span = f"{r.list_year_start}" if r.list_year_start == r.list_year_end else f"{r.list_year_start}→{r.list_year_end}"
        lines.append(f"| {r.metric} | {span} | {r.value} | {note} |")
    lines += ["", f"Source: {FORBES_ARCHIVE_NOTE}; S&P 500 total return = ^SP500TR (USD); "
                  "real-terms deflator = FRED CPIAUCSL."]

    lines += ["", "## EuroLeague budget rank vs regular-season standing",
              "", "| season | figure type | clubs joined | Spearman rho |", "|---|---|---|---|"]
    for _, r in corr.iterrows():
        lines.append(f"| {r.season} | {r.figure_type} | {r.n_clubs} | {r.spearman_rho} |")
    lines += ["", "Join drops (all source gaps, no mapping failures):"]
    for _, r in recon.iterrows():
        if isinstance(r.dropped_budget_rows, str) and r.dropped_budget_rows:
            lines.append(f"- {r.season} {r.figure_type}: {r.dropped_budget_rows}")
    lines += ["", "Source: BasketNews budget research (estimate ranges; midpoints used for "
                  "ranks) × official EuroLeague API standings, joined on canonical names."]

    lines += ["", "## EuroLeague valuations (JB Capital, March 2026)", ""]
    for _, r in el.iterrows():
        val = (f"€{r.value_eur_m_low:.0f}M" if r.value_eur_m_low == r.value_eur_m_high
               else f"€{r.value_eur_m_low:.0f}–{r.value_eur_m_high:.0f}M")
        lines.append(f"- {r.entity} ({r.season}): **{val}** — {r.basis}")
    lines += ["", f"Source: official EuroLeague press release: {JB_URL}"]

    lines += ["", "## Chart files", "",
              "One PNG per dashboard chart, same identifiers as the dashboard div ids.", ""]
    (NOTE_DIR / "facts.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def run():
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    pngs = export_pngs()
    n_lines = write_facts()
    print(f"note_support: {len(pngs)} PNGs + facts.md ({n_lines} lines) -> note_support/")


if __name__ == "__main__":
    run()
