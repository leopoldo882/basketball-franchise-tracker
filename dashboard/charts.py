"""Every chart on the dashboard, built with plotly.

Colour follows the subject across the whole page:
  blue    European football clubs
  orange  NBA teams and US sports companies
  teal    European basketball (EuroLeague, French league)
  greys   benchmarks and other context
I checked the three hues with a colour-blindness simulator: every pair stays
distinguishable and each has at least 3:1 contrast against the page.
Lines are 2px, bars are thin, and only a few values are written on the
charts: the rest are in the hover tooltips and in the tables under each chart.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from analysis.nba_growth import EDITION_MONTHS
from collectors import common

# Use the standard-library JSON encoder for the chart data. If orjson is
# installed (kaleido pulls it in locally) plotly switches to it automatically,
# and it writes some characters differently, so local and CI builds of the
# same data would not match.
pio.json.config.default_engine = "json"

AOUT = common.PROJECT_ROOT / "analysis" / "output"
MANUAL = common.DATA_DIR / "manual"

FOOTBALL = "#2d63a8"
NBA = "#de6b2a"
EURO_BASKET = "#00876c"
BENCHMARK = "#4a4843"   # S&P 500
CONTEXT = "#8f8b82"     # other benchmarks, earlier seasons, projections
INK = "#1c1b19"
INK_2 = "#4a4843"
MUTED = "#7d7970"
GRID = "#e6e2d8"
AXIS = "#c9c4b8"
PAGE = "#f8f6f1"
# IBM Plex Sans is loaded by the page; the PNG export falls back to Helvetica/Arial
FONT = '"IBM Plex Sans", "Helvetica Neue", Arial, sans-serif'

EUROLEAGUE_FRENCH_CLUBS = ["AS Monaco Basket", "LDLC ASVEL", "Paris Basketball"]

# plotly settings for the page: resize with the window, no toolbar
CONFIG_DEFAULT = {"responsive": True, "displayModeBar": False}

SERIES_LABELS = {
    "eu_football": "European football clubs (join as they list)",
    "eu_football_fixed12": "European football clubs (same 12)",
    "us_holdco": "US sports companies",
    "sp500tr_eur": "S&P 500",
    "ieur_eur": "MSCI Europe (IEUR)",
    "stoxx_eur": "STOXX Europe 600, price only",
}


# ---------- shared styling ----------

def style(fig, height, legend=True, hover="x unified", margin=None):
    fig.update_layout(
        template="none", paper_bgcolor=PAGE, plot_bgcolor=PAGE,
        font=dict(family=FONT, size=12, color=INK_2),
        height=height, autosize=True,
        margin=margin or dict(l=52, r=56, t=36, b=40),
        showlegend=legend,
        legend=dict(orientation="h", x=0, xanchor="left", y=1.02, yanchor="bottom",
                    font=dict(size=12, color=INK_2), bgcolor="rgba(0,0,0,0)"),
        hovermode=hover,
        hoverlabel=dict(bgcolor="#fffdf8", bordercolor=AXIS, font=dict(family=FONT, size=12, color=INK)),
        barcornerradius=1,
    )
    # automargin grows the margin when tick labels are longer than it allows
    fig.update_xaxes(showgrid=False, showline=True, linecolor=AXIS, ticks="outside", tickcolor=AXIS,
                     ticklen=4, zeroline=False, automargin=True, tickfont=dict(color=MUTED),
                     title_font=dict(size=12, color=INK_2))
    fig.update_yaxes(showgrid=True, gridcolor=GRID, gridwidth=1, showline=False, zeroline=False,
                     automargin=True, tickfont=dict(color=MUTED), title_font=dict(size=12, color=INK_2))
    return fig


def horizontal(fig):
    """For horizontal bars and dot plots: grid on the value axis, names in darker text."""
    fig.update_xaxes(showgrid=True, gridcolor=GRID, showline=False, ticks="")
    fig.update_yaxes(showgrid=False, tickfont=dict(color=INK_2))
    return fig


def time_axis(fig):
    fig.update_xaxes(type="date", showspikes=True, spikemode="across", spikesnap="cursor",
                     spikethickness=1, spikecolor=MUTED, spikedash="solid")
    return fig


def mark_end(fig, x, y, color, text, row=None, col=None):
    """Dot at the end of a line with its value beside it. The value is in
    text grey, not the line colour; the dot carries the colour."""
    fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers", showlegend=False, hoverinfo="skip",
                             marker=dict(size=8, color=color, line=dict(width=2, color=PAGE))),
                  row=row, col=col)
    fig.add_annotation(x=x, y=y, text=text, showarrow=False, xanchor="left", xshift=7,
                       font=dict(size=12, color=INK_2), row=row, col=col)


def load_monthly():
    # Dates stay as ISO strings. Timestamps get serialised differently by
    # orjson and the standard encoder, which breaks identical builds.
    m = pd.read_csv(AOUT / "listed_index_monthly.csv")
    m["date"] = pd.PeriodIndex(m["date"], freq="M").to_timestamp().strftime("%Y-%m-%d")
    return m


def rebase(levels):
    return levels / levels.iloc[0] * 100


def edition_dates(editions):
    """Forbes edition -> first day of the month it was published, as text."""
    return [EDITION_MONTHS[int(e)] + "-01" for e in editions]


def dumbbell(wide, before, after, color, bold=()):
    """One row per club: a grey dot for `before`, a coloured dot for `after`,
    joined by a line. `wide` is indexed by club and sorted bottom to top."""
    fig = go.Figure()
    xs, ys = [], []
    for club, row in wide.iterrows():
        if pd.notna(row[before]) and pd.notna(row[after]):
            xs += [row[before], row[after], None]
            ys += [club, club, None]
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=AXIS, width=2),
                             hoverinfo="skip", showlegend=False))
    for season, dot_color in [(before, CONTEXT), (after, color)]:
        fig.add_trace(go.Scatter(
            x=wide[season], y=wide.index, mode="markers", name=season,
            marker=dict(size=10, color=dot_color, line=dict(width=2, color=PAGE)),
            hovertemplate=f"%{{y}}, {season}: €%{{x:.1f}}M<extra></extra>"))
    labels = [f"<b>{club}</b>" if club in bold else club for club in wide.index]
    fig.update_yaxes(type="category", categoryorder="array", categoryarray=list(wide.index),
                     tickvals=list(wide.index), ticktext=labels)
    fig.update_xaxes(rangemode="tozero")
    return fig


# ---------- 1. listed clubs ----------

def chart_listed_since_2012(monthly):
    fig = go.Figure()
    lines = [("eu_football_fixed12", FOOTBALL), ("us_holdco", NBA), ("sp500tr_eur", BENCHMARK),
             ("ieur_eur", CONTEXT)]
    for name, color in lines:
        s = monthly[(monthly.series == name) & (monthly.date >= "2012-09-01")].set_index("date").level_eur
        s = rebase(s)
        label = SERIES_LABELS[name]
        if s.index[0] > "2012-10-01":
            label += f" (from {s.index[0][:4]})"
        fig.add_trace(go.Scatter(x=s.index, y=s.round(1), name=label, mode="lines",
                                 line=dict(color=color, width=2), hovertemplate="%{y:.0f}"))
        mark_end(fig, s.index[-1], round(s.iloc[-1], 1), color, f"{s.iloc[-1]:.0f}")
    time_axis(fig)
    fig.update_yaxes(title_text="EUR, start = 100")
    return style(fig, 440)


def chart_listed_since_2004(monthly):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.78, 0.22], vertical_spacing=0.07)
    lines = [("eu_football", FOOTBALL, "solid"), ("sp500tr_eur", BENCHMARK, "solid"),
             ("stoxx_eur", CONTEXT, "dot")]
    for name, color, dash in lines:
        s = rebase(monthly[monthly.series == name].set_index("date").level_eur)
        fig.add_trace(go.Scatter(x=s.index, y=s.round(1), name=SERIES_LABELS[name], mode="lines",
                                 line=dict(color=color, width=2, dash=dash), hovertemplate="%{y:.0f}"),
                      row=1, col=1)
        # STOXX ends next to the clubs line, so it gets no end label (the two would overlap)
        if name != "stoxx_eur":
            mark_end(fig, s.index[-1], round(s.iloc[-1], 1), color, f"{s.iloc[-1]:.0f}", row=1, col=1)
    members = monthly[monthly.series == "eu_football"].set_index("date").n_members
    fig.add_trace(go.Scatter(x=members.index, y=members, name="clubs in the index", mode="lines",
                             line=dict(color=CONTEXT, width=1.5, shape="hv"), hovertemplate="%{y:.0f} clubs"),
                  row=2, col=1)
    time_axis(fig)
    fig.update_yaxes(title_text="EUR, Jan 2004 = 100", row=1, col=1)
    fig.update_yaxes(title_text="clubs", range=[8, 13], dtick=2, row=2, col=1)
    return style(fig, 500)


def chart_drawdown(monthly):
    fig = go.Figure()
    for name, color, fill in [("eu_football_fixed12", FOOTBALL, "rgba(45,99,168,0.10)"),
                              ("sp500tr_eur", BENCHMARK, None)]:
        s = monthly[(monthly.series == name) & (monthly.date >= "2012-09-01")].set_index("date").level_eur
        level = rebase(s)
        drawdown = (level / level.cummax() - 1) * 100
        fig.add_trace(go.Scatter(x=drawdown.index, y=drawdown.round(1), name=SERIES_LABELS[name], mode="lines",
                                 line=dict(color=color, width=2), fill="tozeroy" if fill else None,
                                 fillcolor=fill, hovertemplate="%{y:.1f}%"))
        if name == "eu_football_fixed12":
            low = drawdown.idxmin()
            low_month = pd.Period(low[:7], "M").strftime("%b %Y")
            fig.add_annotation(x=low, y=drawdown[low], text=f"{drawdown[low]:.0f}% ({low_month})", showarrow=False,
                               yanchor="top", yshift=-6, font=dict(size=12, color=INK_2))
    time_axis(fig)
    style(fig, 320)
    fig.update_yaxes(ticksuffix="%", zeroline=True, zerolinecolor=AXIS, zerolinewidth=1)
    return fig


# ---------- 2. NBA franchise values ----------

def chart_nba_values(growth):
    avg = growth[growth.metric == "league_avg_value_usd_m"]
    x = edition_dates(avg.list_year_start)
    y = (avg.value / 1000).round(2)
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="lines+markers", line=dict(color=NBA, width=2),
        marker=dict(size=9, color=NBA, line=dict(width=2, color=PAGE)),
        customdata=avg.list_year_start, hovertemplate="Forbes %{customdata}: $%{y:.2f}bn<extra></extra>"))
    for i in [0, len(x) - 1]:
        fig.add_annotation(x=x[i], y=y.iloc[i], text=f"${y.iloc[i]:.2f}bn", showarrow=False, yshift=16,
                           font=dict(size=12, color=INK_2))
    time_axis(fig)
    fig.update_yaxes(tickprefix="$", ticksuffix="bn", rangemode="tozero")
    return style(fig, 340, legend=False, hover="closest")


def chart_nba_cagr(growth):
    nba = growth[growth.metric == "nba_avg_value_cagr"].reset_index(drop=True)
    sp = growth[growth.metric == "sp500tr_cagr_same_window"].reset_index(drop=True)
    windows = [f"{a}-{str(b)[2:]}" for a, b in zip(nba.list_year_start, nba.list_year_end)]
    windows[-1] += " (all)"
    fig = go.Figure()
    for name, values, color in [("NBA average team value", nba.value, NBA), ("S&P 500 with dividends", sp.value, BENCHMARK)]:
        fig.add_trace(go.Bar(x=windows, y=(values * 100).round(1), name=name, marker_color=color,
                             hovertemplate="%{y:.1f}%"))
    # only the whole-period pair is labelled; the table under the chart has the rest
    top = max(nba.value.iloc[-1], sp.value.iloc[-1]) * 100
    fig.add_annotation(x=windows[-1], y=top, yshift=14, showarrow=False, font=dict(size=12, color=INK_2),
                       text=f"{nba.value.iloc[-1] * 100:.1f}% vs {sp.value.iloc[-1] * 100:.1f}%")
    fig.update_xaxes(title_text="Between Forbes editions")
    fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    fig.update_layout(barmode="group", bargap=0.6, bargroupgap=0.12)
    return style(fig, 340)


def chart_nba_spread(growth):
    titles = ["Top 5 average value / bottom 5 average", "Median value / revenue"]
    fig = make_subplots(rows=1, cols=2, subplot_titles=titles, horizontal_spacing=0.12)
    fig.update_annotations(font=dict(size=12, color=INK_2))
    for col, metric in [(1, "top5_over_bottom5_ratio"), (2, "median_value_rev_multiple")]:
        rows = growth[growth.metric == metric]
        x = edition_dates(rows.list_year_start)
        y = rows.value.round(2)
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", line=dict(color=NBA, width=2),
                                 marker=dict(size=8, color=NBA, line=dict(width=2, color=PAGE)),
                                 customdata=rows.list_year_start, showlegend=False,
                                 hovertemplate="Forbes %{customdata}: %{y:.1f}x<extra></extra>"),
                      row=1, col=col)
        fig.add_annotation(x=x[-1], y=y.iloc[-1], text=f"{y.iloc[-1]:.1f}x", showarrow=False, xanchor="left",
                           xshift=8, font=dict(size=12, color=INK_2), row=1, col=col)
    time_axis(fig)
    fig.update_yaxes(rangemode="tozero", ticksuffix="x")
    return style(fig, 300, legend=False, hover="closest", margin=dict(l=44, r=44, t=40, b=40))


# ---------- 3. deals and multiples ----------

def chart_multiples():
    nba = pd.read_csv(AOUT / "nba_multiples.csv")
    latest = int(nba.list_year.max())
    teams = nba[nba.list_year == latest]
    deals = pd.read_csv(AOUT / "transactions_vs_forbes.csv").dropna(subset=["deal_ev_to_revenue"])
    clubs = pd.read_csv(AOUT / "football_multiples.csv")
    rows = [
        (f"NBA teams<br>Forbes {latest}", teams.value_rev_multiple, teams.team, NBA, "circle"),
        ("NBA control<br>sales", deals.deal_ev_to_revenue, deals.team + ", " + deals.date, NBA, "diamond"),
        ("Listed European<br>football clubs", clubs.ev_to_revenue, clubs.club, FOOTBALL, "circle"),
    ]
    fig = go.Figure()
    for i, (label, values, names, color, symbol) in enumerate(rows):
        y = len(rows) - 1 - i   # first row drawn at the top
        values = values.reset_index(drop=True)
        names = names.reset_index(drop=True)
        # fixed small vertical offsets so dots with similar values don't hide each
        # other (no random jitter, so every build draws the same picture)
        offsets = (values.rank(method="first").astype(int) % 3 - 1) * 0.13
        fig.add_trace(go.Scatter(x=values, y=y + offsets, mode="markers", showlegend=False,
                                 marker=dict(size=10, color=color, symbol=symbol, line=dict(width=2, color=PAGE)),
                                 text=names, hovertemplate="%{text}: %{x:.1f}x<extra></extra>"))
        median = values.median()
        fig.add_trace(go.Scatter(x=[median], y=[y], mode="markers", showlegend=False,
                                 marker=dict(symbol="line-ns", size=30, line=dict(width=2, color=INK)),
                                 hovertemplate=f"median {median:.1f}x<extra></extra>"))
        fig.add_annotation(x=median, y=y + 0.36, text=f"median {median:.1f}x", showarrow=False,
                           font=dict(size=12, color=INK))
    fig.update_yaxes(tickvals=list(range(len(rows))), ticktext=[r[0] for r in rows][::-1],
                     range=[-0.6, len(rows) - 0.3])
    fig.update_xaxes(title_text="Enterprise value / revenue (x)", rangemode="tozero")
    style(fig, 320, legend=False, hover="closest", margin=dict(l=118, r=24, t=16, b=44))
    return horizontal(fig)


# ---------- 4. EuroLeague ----------

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
    fig = make_subplots(rows=1, cols=3, subplot_titles=titles, horizontal_spacing=0.07)
    fig.update_annotations(font=dict(size=12, color=INK_2))
    for i, (season, figure_type) in enumerate(panels, start=1):
        sub = joined[(joined.season == season) & (joined.figure_type == figure_type)]
        n = int(max(sub.budget_rank.max(), sub.rs_rank.max()))
        # grey diagonal: where budget rank and league position would be equal
        fig.add_shape(type="line", x0=1, y0=1, x1=n, y1=n, line=dict(color=AXIS, width=1), row=1, col=i)
        fig.add_trace(go.Scatter(
            x=sub.budget_rank, y=sub.rs_rank, mode="markers", showlegend=False,
            marker=dict(color=EURO_BASKET, size=9, line=dict(width=2, color=PAGE)),
            customdata=sub.canonical_name,
            hovertemplate="%{customdata}<br>budget rank %{x:.0f}, finished %{y}<extra></extra>"), row=1, col=i)
        fig.update_xaxes(title_text="budget rank", row=1, col=i)
    fig.update_yaxes(autorange="reversed")
    fig.update_yaxes(title_text="league position", row=1, col=1)
    style(fig, 400, legend=False, hover="closest", margin=dict(l=52, r=16, t=84, b=44))
    fig.update_xaxes(showgrid=True, gridcolor=GRID, showline=False, ticks="")
    return fig


def chart_payrolls():
    b = pd.read_csv(common.DATA_DIR / "euroleague_budgets.csv")
    pay = b[(b.season == "2025-26") & (b.figure_type == "payroll_net")].copy()
    pay["mid"] = (pay.amount_low_eur_m + pay.amount_high_eur_m) / 2
    pay = pay.sort_values("mid")
    fig = go.Figure(go.Bar(
        x=pay.mid.round(2), y=pay.canonical_name, orientation="h", marker_color=EURO_BASKET,
        error_x=dict(type="data", symmetric=False, thickness=1.5, width=3, color=INK_2,
                     array=(pay.amount_high_eur_m - pay.mid).round(2),
                     arrayminus=(pay.mid - pay.amount_low_eur_m).round(2)),
        customdata=pay[["amount_low_eur_m", "amount_high_eur_m"]],
        hovertemplate="%{y}: €%{customdata[0]}M to €%{customdata[1]}M<extra></extra>"))
    fig.update_xaxes(title_text="€M, net of tax")
    fig.update_layout(bargap=0.35)
    style(fig, 540, legend=False, hover="closest", margin=dict(l=150, r=24, t=16, b=44))
    return horizontal(fig)


def chart_euroleague_budgets():
    b = pd.read_csv(common.DATA_DIR / "euroleague_budgets.csv")
    tb = b[b.figure_type == "total_budget_gross"].copy()
    tb["mid"] = (tb.amount_low_eur_m + tb.amount_high_eur_m) / 2
    wide = tb.pivot(index="canonical_name", columns="season", values="mid")
    wide = wide.sort_values(["2024-25", "2021-22"], na_position="first")
    fig = dumbbell(wide, "2021-22", "2024-25", EURO_BASKET)
    fig.update_xaxes(title_text="Total budget, €M gross")
    style(fig, 560, hover="closest", margin=dict(l=150, r=24, t=36, b=44))
    return horizontal(fig)


JB_LABELS = {
    "league": "League company",
    "clubs_aggregate": "All clubs",
    "combined": "League + clubs",
}


def chart_jb_capital():
    el = pd.read_csv(MANUAL / "euroleague_valuations.csv")
    keep = el[el.entity_type.isin(JB_LABELS)].iloc[::-1].copy()
    keep["label"] = keep.entity_type.map(JB_LABELS) + ", " + keep.season
    fig = go.Figure()
    for season, color, name in [("2025-26", EURO_BASKET, "2025-26 estimate"), ("2026-27", CONTEXT, "2026-27 projection")]:
        rows = keep[keep.season == season]
        fig.add_trace(go.Bar(
            x=rows.value_eur_m_low / 1000, y=rows.label, orientation="h", name=name,
            marker_color=color, text=[f"€{v / 1000:.2f}bn" for v in rows.value_eur_m_low], textposition="outside",
            textfont=dict(color=INK_2), cliponaxis=False, customdata=rows.entity,
            hovertemplate="%{customdata}: €%{x:.2f}bn<extra></extra>"))
    fig.update_yaxes(categoryorder="array", categoryarray=list(keep.label))
    fig.update_xaxes(tickprefix="€", ticksuffix="bn", range=[0, keep.value_eur_m_low.max() / 1000 * 1.2])
    fig.update_layout(barmode="overlay", bargap=0.4)
    style(fig, 300, hover="closest", margin=dict(l=150, r=24, t=36, b=40))
    return horizontal(fig)


# ---------- 5. French league ----------

def chart_lnb_budgets():
    lnb = pd.read_csv(MANUAL / "lnb_dnccg.csv")
    wide = (lnb[lnb.figure_type == "budget_total"]
            .pivot(index="club", columns="season", values="amount_eur_m")
            .sort_values("2025-26"))
    fig = dumbbell(wide, "2024-25", "2025-26", EURO_BASKET, bold=EUROLEAGUE_FRENCH_CLUBS)
    fig.update_xaxes(title_text="Budget (total revenue filed with the league), €M")
    style(fig, 520, hover="closest", margin=dict(l=170, r=24, t=36, b=44))
    return horizontal(fig)


def build_figures():
    """Every chart as (div_id, figure), in page order. The dashboard and the
    note-support PNG export both use this list."""
    monthly = load_monthly()
    growth = pd.read_csv(AOUT / "nba_growth.csv")
    return [
        ("chart-listed-2012", chart_listed_since_2012(monthly)),
        ("chart-listed-2004", chart_listed_since_2004(monthly)),
        ("chart-drawdown", chart_drawdown(monthly)),
        ("chart-nba-values", chart_nba_values(growth)),
        ("chart-nba-cagr", chart_nba_cagr(growth)),
        ("chart-nba-spread", chart_nba_spread(growth)),
        ("chart-multiples", chart_multiples()),
        ("chart-budget-vs-rank", chart_budget_vs_rank()),
        ("chart-payrolls-2025-26", chart_payrolls()),
        ("chart-euroleague-budgets", chart_euroleague_budgets()),
        ("chart-jb-capital", chart_jb_capital()),
        ("chart-lnb-budgets", chart_lnb_budgets()),
    ]
