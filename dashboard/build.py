"""Build docs/index.html, the dashboard, from the CSVs in data/ and analysis/output/.

Plain HTML with plotly charts (plotly.js loaded from its CDN). Every number on
the page is read from the CSVs here, so rerunning the pipeline updates it.
Colours: European clubs blue, US companies green, benchmarks grey.
"""

import html

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import get_plotlyjs_version
from plotly.subplots import make_subplots

from collectors import common

# Use the standard-library JSON encoder for the chart data. If orjson is
# installed (kaleido pulls it in locally) plotly switches to it automatically,
# and it writes some characters differently, so local and CI builds of the
# same data would not match.
pio.json.config.default_engine = "json"

# Set this once the repo is on GitHub, e.g. "https://github.com/<user>/<repo>".
# While it's empty the page just doesn't link to the repository.
REPO_URL = ""

OUT_DIR = common.PROJECT_ROOT / "docs"
AOUT = common.PROJECT_ROOT / "analysis" / "output"
MANUAL = common.DATA_DIR / "manual"

BLUE = "#2a78d6"
BLUE_LIGHT = "#86b6ef"
GREEN = "#1baf7a"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"

CONFIG = {"responsive": True, "displayModeBar": False}

SERIES_LABELS = {
    "eu_football": "European football clubs (clubs join as they list)",
    "eu_football_fixed12": "European football clubs (same 12 throughout)",
    "us_holdco": "US sports companies",
    "sp500tr_eur": "S&P 500 with dividends (EUR)",
    "ieur_eur": "MSCI Europe ETF, IEUR (EUR)",
    "stoxx_eur": "STOXX Europe 600 (price only)",
}

EUROLEAGUE_FRENCH_CLUBS = ["AS Monaco Basket", "LDLC ASVEL", "Paris Basketball"]


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
    # a fixed div id keeps the HTML identical between builds of the same data
    return fig.to_html(full_html=False, include_plotlyjs=False, config=CONFIG, div_id=div_id)


def load_monthly():
    # Dates stay as ISO strings. Timestamps get serialised differently by
    # orjson and the standard encoder, which breaks identical builds.
    m = pd.read_csv(AOUT / "listed_index_monthly.csv")
    m["date"] = pd.PeriodIndex(m["date"], freq="M").to_timestamp().strftime("%Y-%m-%d")
    return m


def rebase(levels):
    return levels / levels.iloc[0] * 100


def window_label(y0, y1):
    return f"{y0}-{str(y1)[2:]}"


# ---------- charts ----------

def chart_common_window(monthly):
    fig = go.Figure()
    lines = {
        "eu_football_fixed12": dict(color=BLUE, width=2.5),
        "us_holdco": dict(color=GREEN, width=2),
        "sp500tr_eur": dict(color=INK_2, width=2, dash="dot"),
        "ieur_eur": dict(color=MUTED, width=2, dash="dash"),
    }
    for name, line in lines.items():
        s = monthly[(monthly.series == name) & (monthly.date >= "2012-09-01")].set_index("date").level_eur
        label = SERIES_LABELS[name]
        if s.index[0] > "2012-10-01":
            label += f", from {s.index[0][:7]}"
        fig.add_trace(go.Scatter(x=s.index, y=rebase(s).round(1), name=label, line=line))
    fig.update_xaxes(type="date")
    fig.update_yaxes(title_text="Index (EUR, start = 100)")
    return style(fig)


def chart_full_window(monthly):
    # member count goes in its own panel underneath rather than on a second y axis
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.06)
    lines = {
        "eu_football": dict(color=BLUE, width=2.5),
        "sp500tr_eur": dict(color=INK_2, width=2, dash="dot"),
        "stoxx_eur": dict(color=MUTED, width=2, dash="dash"),
    }
    for name, line in lines.items():
        s = monthly[monthly.series == name].set_index("date").level_eur
        fig.add_trace(go.Scatter(x=s.index, y=rebase(s).round(1), name=SERIES_LABELS[name], line=line),
                      row=1, col=1)
    eu = monthly[monthly.series == "eu_football"].set_index("date")
    fig.add_trace(go.Scatter(x=eu.index, y=eu.n_members, name="clubs in the index",
                             line=dict(color=MUTED, width=1.5, shape="hv")), row=2, col=1)
    fig.update_xaxes(type="date")
    fig.update_yaxes(title_text="Index (EUR, Jan 2004 = 100)", row=1, col=1)
    fig.update_yaxes(title_text="clubs", range=[8, 13], row=2, col=1)
    return style(fig, height=520)


def chart_drawdown(monthly):
    fig = go.Figure()
    for name, color in [("eu_football_fixed12", BLUE), ("sp500tr_eur", INK_2)]:
        s = monthly[(monthly.series == name) & (monthly.date >= "2012-09-01")].set_index("date").level_eur
        level = rebase(s)
        drawdown = (level / level.cummax() - 1) * 100
        fig.add_trace(go.Scatter(x=drawdown.index, y=drawdown.round(1), name=SERIES_LABELS[name],
                                 line=dict(color=color, width=2)))
    fig.update_xaxes(type="date")
    fig.update_yaxes(title_text="Below previous peak (%)")
    return style(fig, height=340)


def chart_nba_values(growth):
    per_year = growth[growth.metric == "league_avg_value_usd_m"]
    fig = go.Figure(go.Bar(
        x=per_year.list_year_start.astype(str), y=per_year.value.round(0), marker_color=BLUE,
        text=[f"${v / 1000:.2f}bn" for v in per_year.value], textposition="outside"))
    fig.update_xaxes(title_text="Forbes edition")
    fig.update_yaxes(title_text="Average team value ($M)", range=[0, per_year.value.max() * 1.15])
    fig.update_layout(showlegend=False)
    return style(fig, height=360)


def chart_nba_cagr(growth):
    nba = growth[growth.metric == "nba_avg_value_cagr"]
    sp = growth[growth.metric == "sp500tr_cagr_same_window"]
    windows = [window_label(r.list_year_start, r.list_year_end) for _, r in nba.iterrows()]
    fig = go.Figure([
        go.Bar(x=windows, y=(nba.value * 100).round(1), name="NBA average team value", marker_color=BLUE),
        go.Bar(x=windows, y=(sp.value * 100).round(1), name="S&P 500 with dividends", marker_color=INK_2),
    ])
    fig.update_xaxes(title_text="Between Forbes editions")
    fig.update_yaxes(title_text="Growth per year (%)")
    fig.update_layout(barmode="group")
    return style(fig, height=360)


def chart_nba_dispersion(growth):
    ratio = growth[growth.metric == "top5_over_bottom5_ratio"]
    multiple = growth[growth.metric == "median_value_rev_multiple"]
    years = ratio.list_year_start.astype(str)
    fig = go.Figure([
        go.Scatter(x=years, y=ratio.value.round(2), name="Top 5 average value / bottom 5 average value",
                   line=dict(color=BLUE, width=2), mode="lines+markers+text",
                   text=ratio.value.round(1), textposition="top center"),
        go.Scatter(x=years, y=multiple.value.round(2), name="Median value / revenue",
                   line=dict(color=GREEN, width=2), mode="lines+markers+text",
                   text=multiple.value.round(1), textposition="top center"),
    ])
    fig.update_xaxes(title_text="Forbes edition")
    fig.update_yaxes(title_text="Multiple (x)", rangemode="tozero")
    return style(fig, height=360)


def chart_budget_vs_rank():
    joined = pd.read_csv(AOUT / "budget_vs_performance.csv")
    corr = pd.read_csv(AOUT / "budget_rank_correlations.csv")
    panels = [("2021-22", "total_budget_gross"), ("2024-25", "total_budget_gross"), ("2025-26", "payroll_net")]
    titles = []
    for season, figure_type in panels:
        rho = corr[(corr.season == season) & (corr.figure_type == figure_type)].spearman_rho.iloc[0]
        label = "total budget" if figure_type == "total_budget_gross" else "net payroll"
        # three short lines so the titles don't collide on a phone screen
        titles.append(f"{season}<br>{label}<br>ρ = {rho:.2f}")
    fig = make_subplots(rows=1, cols=3, subplot_titles=titles, horizontal_spacing=0.08)
    for i, (season, figure_type) in enumerate(panels, start=1):
        sub = joined[(joined.season == season) & (joined.figure_type == figure_type)]
        fig.add_trace(go.Scatter(
            x=sub.budget_rank, y=sub.rs_rank, mode="markers",
            marker=dict(color=BLUE, size=9), showlegend=False,
            hovertemplate="%{customdata}<br>budget rank %{x}, finished %{y}<extra></extra>",
            customdata=sub.canonical_name), row=1, col=i)
        fig.update_xaxes(title_text="budget rank (1 = biggest)", row=1, col=i)
    fig.update_yaxes(title_text="regular-season position", row=1, col=1)
    fig.update_layout(hovermode="closest")
    fig.update_annotations(font_size=12)
    return style(fig, height=420, margin_top=90)


def chart_payrolls_latest():
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
    fig.update_xaxes(title_text="Net player payroll 2025-26 (€M)")
    fig.update_layout(showlegend=False)
    return style(fig, height=520)


def chart_budgets_growth():
    b = pd.read_csv(common.DATA_DIR / "euroleague_budgets.csv")
    tb = b[b.figure_type == "total_budget_gross"].copy()
    tb["mid"] = (tb.amount_low_eur_m + tb.amount_high_eur_m) / 2
    wide = tb.pivot(index="canonical_name", columns="season", values="mid").sort_values("2024-25")
    fig = go.Figure([
        go.Bar(x=wide["2021-22"].round(1), y=wide.index, orientation="h", name="2021-22", marker_color=BLUE_LIGHT),
        go.Bar(x=wide["2024-25"].round(1), y=wide.index, orientation="h", name="2024-25", marker_color=BLUE),
    ])
    fig.update_xaxes(title_text="Total budget, gross (€M)")
    fig.update_layout(barmode="group")
    return style(fig, height=560)


def chart_lnb_budgets():
    lnb = pd.read_csv(MANUAL / "lnb_dnccg.csv")
    budgets = lnb[lnb.figure_type == "budget_total"]
    wide = budgets.pivot(index="club", columns="season", values="amount_eur_m").sort_values("2025-26")
    order = list(wide.index)
    is_el = wide.index.isin(EUROLEAGUE_FRENCH_CLUBS)

    fig = go.Figure([
        go.Bar(x=wide.loc[is_el, "2025-26"], y=wide.index[is_el], orientation="h",
               name="2025-26, EuroLeague clubs", marker_color=BLUE,
               hovertemplate="%{y}: €%{x:.1f}M<extra></extra>"),
        go.Bar(x=wide.loc[~is_el, "2025-26"], y=wide.index[~is_el], orientation="h",
               name="2025-26, other clubs", marker_color=BLUE_LIGHT,
               hovertemplate="%{y}: €%{x:.1f}M<extra></extra>"),
        go.Scatter(x=wide["2024-25"], y=wide.index, mode="markers", name="2024-25",
                   marker=dict(color=INK, size=7, symbol="line-ns-open", line=dict(width=2)),
                   hovertemplate="%{y} 2024-25: €%{x:.1f}M<extra></extra>"),
    ])
    fig.update_yaxes(categoryorder="array", categoryarray=order)
    fig.update_xaxes(title_text="Budget = total revenue as filed with the league (€M)")
    fig.update_layout(barmode="overlay", hovermode="closest")
    return style(fig, height=520)


def chart_jb_capital():
    el = pd.read_csv(MANUAL / "euroleague_valuations.csv")
    keep = el[el.entity_type.isin(["league", "clubs_aggregate", "combined"])].copy()
    keep["label"] = keep.entity + ", " + keep.season
    colors = [BLUE_LIGHT if season == "2026-27" else BLUE for season in keep.season]
    fig = go.Figure(go.Bar(
        x=keep.value_eur_m_low, y=keep.label, orientation="h", marker_color=colors,
        text=[f"€{v / 1000:.2f}bn" for v in keep.value_eur_m_low], textposition="outside",
        hovertemplate="%{y}: €%{x}M<extra></extra>"))
    fig.update_xaxes(title_text="Valuation (€M)", range=[0, keep.value_eur_m_low.max() * 1.15])
    fig.update_layout(showlegend=False)
    return style(fig, height=340)


def build_figures():
    """Every chart as (div_id, title, note, figure). The dashboard and the
    note-support PNG export both use this list."""
    monthly = load_monthly()
    growth = pd.read_csv(AOUT / "nba_growth.csv")
    return [
        ("chart-common-window",
         "Listed football clubs vs stock indices, since 2012",
         "Twelve clubs, equal weight, rebalanced monthly, in euros. Every line starts at 100.",
         chart_common_window(monthly)),
        ("chart-full-window",
         "The same index back to 2004",
         "Here clubs join the index in the month they list, so the early years hold fewer clubs "
         "(bottom panel).",
         chart_full_window(monthly)),
        ("chart-drawdown",
         "Drawdowns: football clubs vs the S&P 500",
         "How far each index is below its previous high, in euros.",
         chart_drawdown(monthly)),
        ("chart-nba-values",
         "Average NBA team value by Forbes edition",
         "Mean of all 30 teams.",
         chart_nba_values(growth)),
        ("chart-nba-cagr",
         "NBA value growth vs the S&P 500",
         "Growth per year between Forbes editions, against the S&P 500 with dividends over the "
         "same months (USD). The last pair of bars is the whole period.",
         chart_nba_cagr(growth)),
        ("chart-nba-dispersion",
         "Richest vs poorest NBA teams, and value per dollar of revenue",
         "",
         chart_nba_dispersion(growth)),
        ("chart-budget-vs-rank",
         "EuroLeague: budget rank vs league position",
         "One dot per club per season. Each panel uses a single budget definition; ρ is the "
         "Spearman rank correlation.",
         chart_budget_vs_rank()),
        ("chart-payrolls-2025-26",
         "EuroLeague net player payrolls, 2025-26",
         "BasketNews estimates. The whiskers show the range they reported.",
         chart_payrolls_latest()),
        ("chart-budgets-growth",
         "EuroLeague total budgets, 2021-22 and 2024-25",
         "Clubs with one bar have one season of data: the Russian clubs left after 2021-22 and "
         "the newer clubs have no 2021-22 figure.",
         chart_budgets_growth()),
        ("chart-lnb-budgets",
         "French top division (Betclic Élite) budgets",
         "Official LNB/DNCCG figures. Bars are 2025-26, ticks are 2024-25.",
         chart_lnb_budgets()),
        ("chart-jb-capital",
         "JB Capital's valuation of the EuroLeague",
         "One estimate from March 2026. Lighter bars are JB Capital's 2026-27 projections.",
         chart_jb_capital()),
    ]


# ---------- text and tables ----------

def headline_stats(growth, stats, corr):
    """(number, label, detail) for the row of figures at the top of the page."""
    first, last = growth.list_year_start.min(), growth.list_year_end.max()
    full = growth[(growth.list_year_start == first) & (growth.list_year_end == last)]
    nba = full[full.metric == "nba_avg_value_cagr"].value.iloc[0]
    sp = full[full.metric == "sp500tr_cagr_same_window"].value.iloc[0]

    fixed = stats[(stats.series == "eu_football_fixed12") & (stats.metric == "cagr")].iloc[0]
    multiple = growth[growth.metric == "median_value_rev_multiple"]

    el = pd.read_csv(MANUAL / "euroleague_valuations.csv")
    league = el[(el.entity_type == "league") & (el.season == "2025-26")].value_eur_m_low.iloc[0]

    deals = pd.read_csv(AOUT / "transactions_vs_forbes.csv").dropna(subset=["deal_over_forbes"])

    return [
        (f"{nba * 100:.1f}%", f"NBA average team value, growth per year ({first} to {last} Forbes editions)",
         f"S&P 500 with dividends, same months: {sp * 100:.1f}%"),
        (f"{fixed.value * 100:.1f}%", "12 listed European football clubs, growth per year in EUR",
         f"{fixed.window_start} to {fixed.window_end}"),
        (f"{multiple.value.iloc[-1]:.1f}x", f"Median NBA team value / revenue, {last} edition",
         f"{multiple.value.iloc[0]:.1f}x in the {first} edition"),
        (f"{deals.deal_over_forbes.min():.2f}x to {deals.deal_over_forbes.max():.2f}x",
         "NBA control sales vs the last Forbes value before the deal",
         f"{len(deals)} deals, {deals.date.min()[:4]} to {deals.date.max()[:4]}"),
        (f"{corr.spearman_rho.min():.2f} to {corr.spearman_rho.max():.2f}",
         "EuroLeague budget rank vs league position (Spearman)",
         "range across seasons and budget definitions"),
        (f"€{league / 1000:.2f}bn", "EuroLeague league company, 2025-26 valuation",
         "JB Capital, March 2026"),
    ]


def deals_table():
    deals = pd.read_csv(AOUT / "transactions_vs_forbes.csv")
    rows = []
    for _, d in deals.iterrows():
        pending = isinstance(d.notes, str) and "not yet approved" in d.notes
        team = html.escape(d.team) + (" *" if pending else "")
        if pd.notna(d.deal_over_forbes):
            forbes = f"${d.forbes_value_usd_m / 1000:.2f}bn ({int(d.forbes_edition)})"
            ratio = f"{d.deal_over_forbes:.2f}x"
        else:
            forbes, ratio = "no list within 12 months", ""
        rows.append(f"<tr><td>{d.date}</td><td>{team}</td><td>{html.escape(d.buyer)}</td>"
                    f"<td class=r>${d.implied_valuation_usd_m / 1000:.2f}bn</td>"
                    f"<td class=r>{forbes}</td><td class=r>{ratio}</td></tr>")
    return ("<div class=table-wrap><table><thead><tr><th>Agreed</th><th>Team</th><th>Buyer</th>"
            "<th class=r>Deal valuation</th><th class=r>Last Forbes value</th>"
            "<th class=r>Deal / Forbes</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table></div>")


def pct(x):
    return f"{x * 100:.1f}%"


def caveats(stats):
    common_window = stats[(stats.series == "eu_football_common_window") & (stats.metric == "cagr")].iloc[0]
    fixed = stats[(stats.series == "eu_football_fixed12") & (stats.metric == "cagr")].iloc[0]
    staggered = stats[(stats.series == "eu_football") & (stats.metric == "cagr")].iloc[0]
    if abs(common_window.value - fixed.value) < 0.00005:
        same_window = (f"over the same months ({fixed.window_start} to {fixed.window_end}) the two "
                       f"give the same result, so the gap comes from the start date, not from which clubs are in")
    else:
        same_window = (f"over the same months ({fixed.window_start} to {fixed.window_end}) they give "
                       f"{pct(common_window.value)} and {pct(fixed.value)} a year")

    div = pd.read_csv(AOUT / "publisher_divergence.csv").set_index("publisher")
    sportico, cnbc = div.loc["sportico"], div.loc["cnbc"]
    lnb = pd.read_csv(MANUAL / "lnb_dnccg.csv")
    op = lnb[lnb.figure_type == "operating_result"].set_index("club").amount_eur_m

    items = [
        "The listed index only holds clubs that are still listed today. Clubs that delisted, like AS Roma "
        "in 2022, are missing from the whole history, so the index probably flatters what an investor "
        "would actually have earned.",
        f"Start dates change the answer a lot. From 2004 the index grows {pct(staggered.value)} a year, "
        f"from 2012 {pct(fixed.value)}; {same_window}.",
        "Club prices, the S&P 500 and IEUR include dividends. STOXX Europe 600 is price only and so "
        "understates that benchmark. It is only there to cover the years before IEUR started (2014).",
        "EuroLeague budgets are BasketNews estimates with a stated margin of error, and I keep the ranges "
        "they report. Payroll and total budget are never mixed in one series. The 2025-26 payroll counts "
        "players only, earlier seasons include coaches.",
        "The 2021-22 standings leave out the three Russian clubs expelled during the season, and Baskonia "
        "published no figures for 2021-22.",
        f"Valuations are estimates, not prices, and the publishers disagree. Sportico's Oct 2026 values are "
        f"on average {pct(sportico.mean_pct_diff_vs_forbes)} above Forbes for the {int(sportico.n_teams)} "
        f"teams whose figures I could find published; CNBC's Feb 2026 values are "
        f"{pct(cnbc.mean_pct_diff_vs_forbes)} above Forbes' Oct 2025 list for {int(cnbc.n_teams)} teams. "
        f"Neither full list is available outside the publishers' own sites.",
        "A deal valuation and a Forbes value aren't the same measure: deals can include arenas or other "
        "businesses, and some are paid in stages (the Trail Blazers row uses the first tranche).",
        f"French budgets are what clubs filed with the league each September, not audited accounts. "
        f"The audited club accounts sit in a separate download; the loss figures here come from the "
        f"league's own summary of them: a €{-op['Betclic ELITE (all clubs)']:.1f}M operating loss for the "
        f"division in 2024-25, €{-op['EuroLeague clubs (Monaco + ASVEL + Paris)']:.1f}M of it from the "
        f"three EuroLeague clubs.",
        "Two tickers changed in 2026. MSG Sports (Knicks) trades as MSGK after spinning off the Rangers, "
        "and Eagle Football Group (Lyon) is now OL Groupe (OLG). Both keep their full price history.",
        "Index membership is a judgement call: Turkish clubs are left out (currency swings and speculative "
        "trading), TKO's pre-2023 WWE history is dropped, and the US companies are kept separate from the "
        "European index. methodology.md explains each choice and the alternative.",
        "The Swiss SB League is left out because its clubs don't publish financial figures.",
    ]
    return "<ul>" + "".join(f"<li>{html.escape(i)}</li>" for i in items) + "</ul>"


def link(url, text):
    return f'<a href="{html.escape(url)}">{html.escape(text)}</a>'


def sources():
    bn = pd.read_csv(common.DATA_DIR / "euroleague_budgets.csv")
    bn_links = ", ".join(link(u, s) for s, u in
                         bn[["season", "source_url"]].drop_duplicates().itertuples(index=False))
    el = pd.read_csv(MANUAL / "euroleague_valuations.csv").source_url.iloc[0]
    lnb = pd.read_csv(MANUAL / "lnb_dnccg.csv")
    lnb_budget = lnb[lnb.figure_type == "budget_total"].source_url.iloc[0]
    lnb_accounts = lnb[lnb.figure_type == "operating_result"].source_url.iloc[0]
    pub = pd.read_csv(MANUAL / "publisher_divergence.csv").groupby("publisher").source_url.first()

    items = [
        "Forbes NBA team valuations, 2016 to 2026 editions, from archived copies of the data behind "
        "Forbes' list page on the Wayback Machine (one link per row in data/nba_valuations.csv).",
        f"BasketNews EuroLeague budget research: {bn_links}.",
        f"EuroLeague standings from the league's open API ({link('https://api-live.euroleague.net/v1/standings?seasonCode=E2025', 'api-live.euroleague.net')}), regular season only.",
        f"JB Capital valuation: {link(el, 'EuroLeague press release, March 2026')}.",
        f"French league: {link(lnb_budget, 'LNB/DNCCG budgets 2025-26')} and "
        f"{link(lnb_accounts, 'DNCCG accounts summary 2024-25')}.",
        f"Sportico and CNBC values as republished by {link(pub['sportico'], 'Bleacher Report')} and "
        f"{link(pub['cnbc'], 'NBC Chicago')}.",
        "NBA deal prices: ESPN, Sports Illustrated, Hoops Rumors, Axios; one link per deal in "
        "data/manual/transactions.csv.",
        "Share prices and exchange rates: Yahoo Finance, through the yfinance library.",
        "US inflation: FRED series CPIAUCSL (used for one number in the note pack only).",
    ]
    if REPO_URL:
        items.append(f"Code, data and methodology: {link(REPO_URL, REPO_URL.replace('https://', ''))}.")
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def data_date():
    """Date of the newest market price, shown on the page instead of the build
    time so that rebuilding unchanged data gives an identical file."""
    prices = pd.read_csv(common.DATA_DIR / "market_prices.csv", usecols=["date"])
    return pd.to_datetime(prices.date.max()).strftime("%d %b %Y").lstrip("0")


def run():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    growth = pd.read_csv(AOUT / "nba_growth.csv")
    stats = pd.read_csv(AOUT / "listed_index_stats.csv")
    corr = pd.read_csv(AOUT / "budget_rank_correlations.csv")

    cards = "".join(
        f'<div class="card"><div class="num">{html.escape(num)}</div>'
        f'<div class="lbl">{html.escape(label)}</div><div class="sub">{html.escape(sub)}</div></div>'
        for num, label, sub in headline_stats(growth, stats, corr)
    )

    figures = build_figures()
    sections = []
    for div_id, title, note, fig in figures:
        note_html = f"<p class=note>{html.escape(note)}</p>" if note else ""
        sections.append(f"<section><h2>{html.escape(title)}</h2>{note_html}{render(fig, div_id)}</section>")
        if div_id == "chart-nba-dispersion":
            sections.append(
                "<section><h2>NBA control sales vs the last Forbes value</h2>"
                "<p class=note>Deal valuation divided by the most recent Forbes value for that team "
                "published before the deal was agreed, where that list is under 12 months old. "
                "* = not yet approved by the NBA as of November 2026.</p>"
                f"{deals_table()}</section>")
    body = "".join(sections)

    page = f"""<!DOCTYPE html>
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
  h1 {{ margin: 8px 0 6px; font-size: 1.6rem; }}
  h2 {{ margin: 40px 0 4px; font-size: 1.15rem; }}
  .intro {{ color: {INK_2}; margin: 0 0 4px; max-width: 760px; line-height: 1.5; }}
  .updated {{ color: {MUTED}; font-size: 0.85rem; margin: 6px 0 20px; }}
  .cards {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 16px 0 8px; }}
  .card {{ background: {SURFACE}; border: 1px solid rgba(11,11,11,0.10); border-radius: 6px;
          padding: 12px 14px; flex: 1 1 200px; min-width: 160px; }}
  .card .num {{ font-size: 1.4rem; font-weight: 650; }}
  .card .lbl {{ color: {INK_2}; font-size: 0.85rem; margin-top: 4px; }}
  .card .sub {{ color: {MUTED}; font-size: 0.78rem; margin-top: 2px; }}
  .note {{ color: {INK_2}; font-size: 0.9rem; margin: 0 0 8px; }}
  section > div {{ background: {SURFACE}; border: 1px solid rgba(11,11,11,0.10); border-radius: 6px; }}
  .table-wrap {{ overflow-x: auto; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.88rem; }}
  th, td {{ text-align: left; padding: 7px 10px; border-bottom: 1px solid {GRID}; white-space: nowrap; }}
  th {{ color: {INK_2}; font-weight: 600; }}
  td.r, th.r {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .prose ul {{ color: {INK_2}; font-size: 0.92rem; line-height: 1.55; padding-left: 20px; }}
  .prose li {{ margin-bottom: 6px; }}
  a {{ color: {BLUE}; }}
  footer {{ color: {MUTED}; font-size: 0.85rem; margin-top: 48px; }}
</style>
</head>
<body>
<main>
<h1>European Basketball Franchise Valuation Tracker</h1>
<p class="intro">Data on sports teams as an investment: NBA franchise values from Forbes, EuroLeague and
French club budgets, the one published valuation of EuroLeague clubs, and listed football club shares
compared with stock indices. The sources and the main caveats are at the bottom of the page.</p>
<p class="updated">Market data to {data_date()}</p>
<div class="cards">{cards}</div>
{body}
<section class="prose"><h2>Sources</h2>{sources()}</section>
<section class="prose"><h2>Caveats</h2>{caveats(stats)}</section>
<footer>Python, pandas and plotly. Share prices refresh on the 3rd of each month through GitHub
Actions; the yearly data is updated by hand.</footer>
</main>
</body>
</html>
"""
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")
    print(f"dashboard: {len(figures)} charts + deals table -> docs/index.html ({len(page) // 1024} KB)")


if __name__ == "__main__":
    run()
