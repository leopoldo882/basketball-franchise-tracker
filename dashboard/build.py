"""Build docs/index.html — the static dashboard — from the committed CSVs.

Plain HTML + plotly (CDN), no framework. Every number on the page is read from
data/ or analysis/output/ at build time, so a pipeline refresh updates the page.
Colors follow entities consistently: European clubs = blue, US holdcos = aqua,
benchmarks = neutral grays (reference context, not competing series).
"""

import datetime

import pandas as pd
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs_version
from plotly.subplots import make_subplots

from collectors import common

OUT_DIR = common.PROJECT_ROOT / "docs"
AOUT = common.PROJECT_ROOT / "analysis" / "output"

# validated reference palette (light mode) + neutral inks
BLUE = "#2a78d6"
BLUE_LIGHT = "#86b6ef"
AQUA = "#1baf7a"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"

CONFIG = {"responsive": True, "displayModeBar": False}

SERIES_LABELS = {
    "eu_football": "European football clubs (staggered entry)",
    "eu_football_fixed12": "European football clubs (fixed 12)",
    "us_holdco": "US sports holdcos",
    "sp500tr_eur": "S&P 500 total return (EUR)",
    "ieur_eur": "MSCI Europe ETF (IEUR, EUR)",
    "stoxx_eur": "STOXX Europe 600 (price only)",
}


def style(fig, height=440, margin_top=30):
    fig.update_layout(
        template="plotly_white", paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(family='system-ui, -apple-system, "Segoe UI", sans-serif', color=INK_2, size=13),
        margin=dict(l=50, r=20, t=margin_top, b=40), height=height, autosize=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, linecolor=GRID, zeroline=False)
    return fig


def render(fig, div_id):
    """Figure -> embeddable HTML div with a stable id (deterministic builds)."""
    return fig.to_html(full_html=False, include_plotlyjs=False, config=CONFIG, div_id=div_id)


def load_monthly():
    m = pd.read_csv(AOUT / "listed_index_monthly.csv")
    m["date"] = pd.PeriodIndex(m["date"], freq="M").to_timestamp()
    return m


def rebase(levels):
    return levels / levels.iloc[0] * 100


def chart_common_window(monthly):
    """Index levels, all rebased to 100 at 2012-09 (or each series' later start)."""
    fig = go.Figure()
    styles = {
        "eu_football_fixed12": dict(color=BLUE, width=2.5),
        "us_holdco": dict(color=AQUA, width=2),
        "sp500tr_eur": dict(color=INK_2, width=2, dash="dot"),
        "ieur_eur": dict(color=MUTED, width=2, dash="dash"),
    }
    for name, line in styles.items():
        s = monthly[(monthly.series == name) & (monthly.date >= "2012-09-01")].set_index("date").level_eur
        label = SERIES_LABELS[name]
        if s.index[0] > pd.Timestamp("2012-10-01"):
            label += f" (from {s.index[0]:%Y-%m})"
        fig.add_trace(go.Scatter(x=s.index, y=rebase(s).round(1), name=label, line=line))
    fig.update_yaxes(title_text="Index level (EUR, 100 = start)")
    return style(fig)


def chart_full_window(monthly):
    """Staggered index vs benchmarks since 2004, with the member count as its
    own strip below (one axis per panel — never a dual axis)."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.06)
    lines = {
        "eu_football": dict(color=BLUE, width=2.5),
        "sp500tr_eur": dict(color=INK_2, width=2, dash="dot"),
        "stoxx_eur": dict(color=MUTED, width=2, dash="dash"),
    }
    eu = monthly[monthly.series == "eu_football"].set_index("date")
    for name, line in lines.items():
        s = monthly[monthly.series == name].set_index("date").level_eur
        fig.add_trace(go.Scatter(x=s.index, y=rebase(s).round(1), name=SERIES_LABELS[name], line=line), row=1, col=1)
    fig.add_trace(go.Scatter(x=eu.index, y=eu.n_members, name="index members (count)",
                             line=dict(color=MUTED, width=1.5, shape="hv"), showlegend=True), row=2, col=1)
    fig.update_yaxes(title_text="Index level (EUR, 100 = 2004)", row=1, col=1)
    fig.update_yaxes(title_text="members", range=[8, 13], row=2, col=1)
    return style(fig, height=520)


def chart_drawdown(monthly):
    fig = go.Figure()
    for name, color in [("eu_football_fixed12", BLUE), ("sp500tr_eur", INK_2)]:
        s = monthly[(monthly.series == name) & (monthly.date >= "2012-09-01")].set_index("date").level_eur
        level = rebase(s)
        dd = (level / level.cummax() - 1) * 100
        fig.add_trace(go.Scatter(x=dd.index, y=dd.round(1), name=SERIES_LABELS[name],
                                 line=dict(color=color, width=2)))
    fig.update_yaxes(title_text="Drawdown from peak (%)")
    return style(fig, height=340)


def chart_nba_values(growth):
    per_year = growth[growth.metric == "league_avg_value_usd_m"]
    fig = go.Figure(go.Bar(x=per_year.list_year_start.astype(str), y=per_year.value.round(0),
                           marker_color=BLUE, name="League average value ($M)",
                           text=[f"${v:,.0f}M" for v in per_year.value], textposition="outside"))
    fig.update_yaxes(title_text="Average franchise value ($M)")
    fig.update_layout(showlegend=False)
    return style(fig, height=360)


def chart_nba_cagr(growth):
    nba = growth[growth.metric == "nba_avg_value_cagr"]
    sp = growth[growth.metric == "sp500tr_cagr_same_window"]
    windows = [f"{r.list_year_start}→{r.list_year_end}" for _, r in nba.iterrows()]
    fig = go.Figure([
        go.Bar(x=windows, y=(nba.value * 100).round(1), name="NBA avg value CAGR", marker_color=BLUE),
        go.Bar(x=windows, y=(sp.value * 100).round(1), name="S&P 500 TR CAGR (same window)", marker_color=INK_2),
    ])
    fig.update_yaxes(title_text="CAGR (%)")
    fig.update_layout(barmode="group")
    return style(fig, height=360)


def chart_nba_dispersion(growth):
    ratio = growth[growth.metric == "top5_over_bottom5_ratio"]
    mult = growth[growth.metric == "median_value_rev_multiple"]
    years = ratio.list_year_start.astype(str)
    fig = go.Figure([
        go.Scatter(x=years, y=ratio.value.round(2), name="Top-5 / bottom-5 value ratio (×)",
                   line=dict(color=BLUE, width=2), mode="lines+markers+text",
                   text=ratio.value.round(2), textposition="top center"),
        go.Scatter(x=years, y=mult.value.round(2), name="Median value / revenue multiple (×)",
                   line=dict(color=AQUA, width=2), mode="lines+markers+text",
                   text=mult.value.round(2), textposition="top center"),
    ])
    fig.update_yaxes(title_text="Multiple (×)", rangemode="tozero")
    return style(fig, height=360)


def chart_budget_vs_rank():
    joined = pd.read_csv(AOUT / "budget_vs_performance.csv")
    corr = pd.read_csv(AOUT / "budget_rank_correlations.csv")
    panels = [("2021-22", "total_budget_gross"), ("2024-25", "total_budget_gross"), ("2025-26", "payroll_net")]
    titles = []
    for season, ft in panels:
        rho = corr[(corr.season == season) & (corr.figure_type == ft)].spearman_rho.iloc[0]
        label = "total budget" if ft == "total_budget_gross" else "net payroll"
        titles.append(f"{season} ({label})<br>Spearman ρ = {rho:.2f}")
    fig = make_subplots(rows=1, cols=3, subplot_titles=titles, horizontal_spacing=0.08)
    for i, (season, ft) in enumerate(panels, start=1):
        sub = joined[(joined.season == season) & (joined.figure_type == ft)]
        fig.add_trace(go.Scatter(
            x=sub.budget_rank, y=sub.rs_rank, mode="markers",
            marker=dict(color=BLUE, size=9), name=season, showlegend=False,
            hovertemplate="%{customdata}<br>budget rank %{x}, standing %{y}<extra></extra>",
            customdata=sub.canonical_name), row=1, col=i)
        fig.update_xaxes(title_text="budget rank (1 = biggest)", row=1, col=i)
    fig.update_yaxes(title_text="regular-season rank (1 = best)", row=1, col=1)
    fig.update_layout(hovermode="closest")
    return style(fig, height=400, margin_top=70)


def chart_budgets_latest():
    b = pd.read_csv(common.DATA_DIR / "euroleague_budgets.csv")
    pay = b[(b.season == "2025-26") & (b.figure_type == "payroll_net")].copy()
    pay["mid"] = (pay.amount_low_eur_m + pay.amount_high_eur_m) / 2
    pay = pay.sort_values("mid")
    fig = go.Figure(go.Bar(
        x=pay.mid.round(2), y=pay.canonical_name, orientation="h", marker_color=BLUE,
        error_x=dict(type="data", symmetric=False,
                     array=(pay.amount_high_eur_m - pay.mid).round(2),
                     arrayminus=(pay.mid - pay.amount_low_eur_m).round(2), color=INK_2),
        hovertemplate="%{y}: €%{x}M<extra></extra>"))
    fig.update_xaxes(title_text="Net player payroll 2025-26 (€M, BasketNews estimate range)")
    fig.update_layout(showlegend=False)
    return style(fig, height=520)


def chart_budgets_growth():
    b = pd.read_csv(common.DATA_DIR / "euroleague_budgets.csv")
    tb = b[b.figure_type == "total_budget_gross"].copy()
    tb["mid"] = (tb.amount_low_eur_m + tb.amount_high_eur_m) / 2
    wide = tb.pivot(index="canonical_name", columns="season", values="mid").sort_values("2024-25")
    fig = go.Figure([
        go.Bar(x=wide["2021-22"].round(1), y=wide.index, orientation="h",
               name="2021-22", marker_color=BLUE_LIGHT),
        go.Bar(x=wide["2024-25"].round(1), y=wide.index, orientation="h",
               name="2024-25", marker_color=BLUE),
    ])
    fig.update_xaxes(title_text="Total budget, gross (€M)")
    fig.update_layout(barmode="group", height=560)
    return style(fig, height=560)


def chart_jb_capital():
    el = pd.read_csv(common.DATA_DIR / "manual" / "euroleague_valuations.csv")
    keep = el[el.entity_type.isin(["league", "clubs_aggregate", "combined"])].copy()
    keep["label"] = keep.entity + " (" + keep.season + ")"
    colors = [BLUE_LIGHT if "scenario" in e.lower() or s == "2026-27" else BLUE
              for e, s in zip(keep.entity, keep.season)]
    fig = go.Figure(go.Bar(
        x=keep.value_eur_m_low, y=keep.label, orientation="h", marker_color=colors,
        text=[f"€{v / 1000:.2f}B" for v in keep.value_eur_m_low], textposition="outside",
        hovertemplate="%{y}: €%{x}M<extra></extra>"))
    fig.update_xaxes(title_text="Valuation (€M) — JB Capital via EuroLeague press release, Mar 2026",
                     range=[0, keep.value_eur_m_low.max() * 1.15])
    fig.update_layout(showlegend=False)
    return style(fig, height=340)


def headline_stats(growth, stats, corr):
    """The 4-5 numbers a recruiter sees in the first 90 seconds."""
    nba = growth[(growth.metric == "nba_avg_value_cagr")
                 & (growth.list_year_start == growth.list_year_start.min())
                 & (growth.list_year_end == growth.list_year_end.max())].value.iloc[0]
    sp = growth[(growth.metric == "sp500tr_cagr_same_window")
                & (growth.list_year_start == growth.list_year_start.min())
                & (growth.list_year_end == growth.list_year_end.max())].value.iloc[0]
    fixed = stats[(stats.series == "eu_football_fixed12") & (stats.metric == "cagr")]
    idx_cagr = fixed.value.iloc[0]
    idx_win = f"{fixed.window_start.iloc[0]} → {fixed.window_end.iloc[0]}"
    rho_min, rho_max = corr.spearman_rho.min(), corr.spearman_rho.max()
    league_val = pd.read_csv(common.DATA_DIR / "manual" / "euroleague_valuations.csv")
    league = league_val[(league_val.entity_type == "league") & (league_val.season == "2025-26")].value_eur_m_low.iloc[0]
    mult = growth[growth.metric == "median_value_rev_multiple"]
    m0, m1 = mult.value.iloc[0], mult.value.iloc[-1]
    y_lo = growth.list_year_start.min()
    y_hi = growth.list_year_end.max()
    return [
        (f"{nba * 100:.1f}%", f"NBA avg franchise value CAGR, {y_lo}→{y_hi} editions",
         f"S&P 500 total return over the same window: {sp * 100:.1f}%"),
        (f"{idx_cagr * 100:.1f}%", "Listed European football clubs CAGR (EUR, fixed 12 members)", idx_win),
        (f"{m0:.1f}× → {m1:.1f}×", "NBA median value/revenue multiple",
         f"{y_lo} edition vs {y_hi} edition"),
        (f"{rho_min:.2f}–{rho_max:.2f}", "EuroLeague budget rank ↔ standings (Spearman)",
         "across seasons and figure definitions"),
        (f"€{league / 1000:.2f}B", "EuroLeague league-entity valuation 2025-26",
         "JB Capital, via official press release"),
    ]


CAVEATS = """
<ul>
<li><strong>Survivorship bias:</strong> the listed-clubs index contains only clubs listed today; clubs that delisted (e.g. AS Roma, Sep 2022) are absent from the whole history, so the index likely overstates the historical experience.</li>
<li><strong>Window effects dominate:</strong> the staggered index (2004→) and fixed-12 index (2012→) tell different stories; over the identical 2012-09→2026-07 window their results are the same to four decimals — the gap is a window effect, not composition.</li>
<li><strong>Benchmark forms:</strong> club prices and ^SP500TR/IEUR are total-return style; STOXX Europe 600 is shown price-only for pre-2014 context and understates the benchmark.</li>
<li><strong>EuroLeague figures are estimates:</strong> BasketNews research with a stated margin of error; ranges are kept. Payroll and total-budget definitions are never merged; 2025-26 payroll covers players only, earlier seasons players+coaches.</li>
<li><strong>Standings gaps:</strong> the 2021-22 season excludes the three expelled Russian clubs; Baskonia disclosed no 2021-22 figures.</li>
<li><strong>Valuations are opinions:</strong> Forbes/JB Capital values are published estimates, not transactions; valuation publishers disagree (a divergence check vs Sportico/CNBC is pending manual entry).</li>
<li><strong>Index membership is a choice:</strong> Turkish club stocks are excluded (TRY/speculative noise), TKO's pre-2023 legacy-WWE history is dropped, and US holdcos are never blended into the European index — each ruling and its alternative is in methodology.md.</li>
<li><strong>Small leagues:</strong> Swiss SB League dropped entirely — no published club financials exist.</li>
</ul>
"""

SOURCES = """
<ul>
<li>Forbes NBA team valuations — 2016/2019/2022 editions via Wayback-archived Forbes list data; value and revenue per team.</li>
<li>BasketNews EuroLeague budget research — 2021-22, 2024-25, 2025-26 season articles (cached once, custom user-agent, estimate ranges preserved).</li>
<li>EuroLeague standings — official api-live.euroleague.net XML API, regular season only.</li>
<li>JB Capital EuroLeague valuation — official EuroLeague press release, March 2026.</li>
<li>Market prices &amp; FX — Yahoo Finance via yfinance (adjusted closes; EUR conversion documented in methodology.md).</li>
<li>US CPI — FRED (CPIAUCSL), used only for one real-terms CAGR in the note support pack.</li>
<li>Full source-by-source access notes: <a href="https://github.com/">data_inventory.md</a> in the repository; every methodological choice and its alternative: methodology.md.</li>
</ul>
"""


def build_figures():
    """The chart registry: (div_id, title, note, figure) for every chart —
    the single source of truth shared by the dashboard (HTML) and the
    note-support pack (PNG export)."""
    monthly = load_monthly()
    growth = pd.read_csv(AOUT / "nba_growth.csv")
    return [
        ("chart-common-window",
         "Listed clubs vs public equities — common window (2012→, EUR)",
         "Equal-weight, monthly-rebalanced. All series rebased to 100; series starting later are labeled.",
         chart_common_window(monthly)),
        ("chart-full-window",
         "The full window (2004→) and why it looks different",
         "Staggered membership: clubs enter the index when they list. The strip below shows the member count.",
         chart_full_window(monthly)),
        ("chart-drawdown",
         "Drawdowns — fixed-12 clubs vs S&P 500 TR (EUR)", "", chart_drawdown(monthly)),
        ("chart-nba-values",
         "NBA franchise values by Forbes edition", "30-team league averages.", chart_nba_values(growth)),
        ("chart-nba-cagr",
         "NBA value growth vs the stock market",
         "CAGR between Forbes editions vs S&P 500 total return over the identical windows (USD).",
         chart_nba_cagr(growth)),
        ("chart-nba-dispersion",
         "NBA dispersion and pricing", "Top-5 vs bottom-5 spread, and what a dollar of revenue is valued at.",
         chart_nba_dispersion(growth)),
        ("chart-budget-vs-rank",
         "EuroLeague: does budget buy standings?",
         "Each dot is a club-season. Rank 1 = biggest budget / best record. Consistent in-season figure per panel.",
         chart_budget_vs_rank()),
        ("chart-payrolls-2025-26",
         "EuroLeague net player payrolls, 2025-26", "BasketNews estimates; whiskers show the reported range.",
         chart_budgets_latest()),
        ("chart-budgets-growth",
         "EuroLeague total budgets, 2021-22 vs 2024-25",
         "Single bars are one-season data: Russian clubs left the league after 2021-22; "
         "newer entrants have no 2021-22 figure.",
         chart_budgets_growth()),
        ("chart-jb-capital",
         "What is European basketball worth?", "The only club-level valuation dataset that exists.",
         chart_jb_capital()),
    ]


def run():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    growth = pd.read_csv(AOUT / "nba_growth.csv")
    stats = pd.read_csv(AOUT / "listed_index_stats.csv")
    corr = pd.read_csv(AOUT / "budget_rank_correlations.csv")

    cards = "".join(
        f'<div class="card"><div class="num">{num}</div><div class="lbl">{label}</div>'
        f'<div class="sub">{sub}</div></div>'
        for num, label, sub in headline_stats(growth, stats, corr)
    )
    built = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    sections = build_figures()
    body = "".join(
        f'<section><h2>{title}</h2>{f"<p class=note>{note}</p>" if note else ""}{render(fig, div_id)}</section>'
        for div_id, title, note, fig in sections
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>European Basketball Franchise Valuation Tracker</title>
<script src="https://cdn.plot.ly/plotly-{get_plotlyjs_version()}.min.js"></script>
<style>
  body {{ margin: 0; background: #f9f9f7; color: {INK};
         font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 1080px; margin: 0 auto; padding: 24px 16px 64px; }}
  h1 {{ margin: 8px 0 4px; font-size: 1.7rem; }}
  h2 {{ margin: 40px 0 4px; font-size: 1.2rem; }}
  .tagline {{ color: {INK_2}; margin: 0 0 4px; }}
  .updated {{ color: {MUTED}; font-size: 0.85rem; margin: 0 0 20px; }}
  .cards {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 16px 0 8px; }}
  .card {{ background: {SURFACE}; border: 1px solid rgba(11,11,11,0.10); border-radius: 8px;
          padding: 14px 16px; flex: 1 1 180px; min-width: 160px; }}
  .card .num {{ font-size: 1.5rem; font-weight: 650; }}
  .card .lbl {{ color: {INK_2}; font-size: 0.85rem; margin-top: 4px; }}
  .card .sub {{ color: {MUTED}; font-size: 0.78rem; margin-top: 2px; }}
  .note {{ color: {INK_2}; font-size: 0.9rem; margin: 0 0 8px; }}
  section > div {{ background: {SURFACE}; border: 1px solid rgba(11,11,11,0.10); border-radius: 8px; }}
  .prose ul {{ color: {INK_2}; font-size: 0.92rem; line-height: 1.55; }}
  a {{ color: {BLUE}; }}
  footer {{ color: {MUTED}; font-size: 0.85rem; margin-top: 48px; }}
</style>
</head>
<body>
<main>
<h1>European Basketball Franchise Valuation Tracker</h1>
<p class="tagline">Does "sports as an alternative asset class" hold up? European basketball,
with the NBA and listed football clubs as comparators — every number traceable to a public source.</p>
<p class="updated">Data last updated: {built}</p>
<div class="cards">{cards}</div>
{body}
<section class="prose"><h2>Data sources</h2>{SOURCES}</section>
<section class="prose"><h2>Caveats — read before quoting anything</h2>{CAVEATS}</section>
<footer>Built with Python (requests, pandas, yfinance, plotly). Pipeline, methodology log and
data inventory live in the repository. Market data refreshes monthly via GitHub Actions;
annual sources update by commit.</footer>
</main>
</body>
</html>
"""
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"dashboard: {len(sections)} charts -> docs/index.html ({len(html) // 1024} KB)")


if __name__ == "__main__":
    run()
