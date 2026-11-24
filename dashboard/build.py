"""Build docs/index.html, the dashboard, from the CSVs in data/ and analysis/output/.

The charts are in dashboard/charts.py; this file lays out the page: the
headline figures, five chapters of charts and tables, sources and caveats.
Every number on the page is read from the CSVs, so rerunning the pipeline
updates it.
"""

import html

import pandas as pd
from plotly.offline import get_plotlyjs_version

from collectors import common
from dashboard.charts import AOUT, AXIS, CONFIG_DEFAULT, GRID, INK, INK_2, MANUAL, MUTED, PAGE, build_figures

# Set this once the repo is on GitHub, e.g. "https://github.com/<user>/<repo>".
# While it's empty the page shows file paths instead of links to the data.
REPO_URL = ""

OUT_DIR = common.PROJECT_ROOT / "docs"

RISK_NAMES = {
    "eu_football_fixed12": "European football clubs (12)",
    "us_holdco": "US sports companies",
    "sp500tr_eur": "S&P 500 with dividends",
    "ieur_eur": "MSCI Europe (IEUR ETF)",
}


# ---------- small helpers ----------

def esc(value):
    return html.escape(str(value))


def month_name(yyyy_mm):
    """'2015-11' -> 'Nov 2015'"""
    return pd.Period(yyyy_mm, "M").strftime("%b %Y")


def pct(x, digits=1):
    return f"{x * 100:.{digits}f}%"


def data_link(path):
    if REPO_URL:
        return f'<a href="{esc(REPO_URL)}/blob/main/{esc(path)}">{esc(path)}</a>'
    return f"<code>{esc(path)}</code>"


def link(url, text):
    return f'<a href="{esc(url)}">{esc(text)}</a>'


def table(headers, rows, left_cols=1):
    """Plain HTML table. The first `left_cols` columns are text, the rest numbers."""
    head = "".join(f"<th{' class=r' if i >= left_cols else ''}>{esc(h)}</th>" for i, h in enumerate(headers))
    body = ""
    for row in rows:
        cells = "".join(f"<td{' class=r' if i >= left_cols else ''}>{esc(c)}</td>" for i, c in enumerate(row))
        body += f"<tr>{cells}</tr>"
    return f"<div class=table-wrap><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def numbers(table_html):
    return f"<details><summary>Show the numbers</summary>{table_html}</details>"


def data_date():
    """Date of the newest market price, shown instead of the build time so that
    rebuilding unchanged data gives an identical file."""
    prices = pd.read_csv(common.DATA_DIR / "market_prices.csv", usecols=["date"])
    return pd.to_datetime(prices.date.max()).strftime("%d %b %Y").lstrip("0")


# ---------- headline figures ----------

def headline_stats():
    """(number, label, detail) for the strip at the top of the page."""
    growth = pd.read_csv(AOUT / "nba_growth.csv")
    first, last = growth.list_year_start.min(), growth.list_year_end.max()
    full = growth[(growth.list_year_start == first) & (growth.list_year_end == last)]
    nba = full[full.metric == "nba_avg_value_cagr"].value.iloc[0]
    sp = full[full.metric == "sp500tr_cagr_same_window"].value.iloc[0]

    risk = pd.read_csv(AOUT / "risk_return.csv").set_index("series")
    clubs, spx = risk.loc["eu_football_fixed12"], risk.loc["sp500tr_eur"]

    nba_multiple = growth[growth.metric == "median_value_rev_multiple"].value.iloc[-1]
    football_multiple = pd.read_csv(AOUT / "football_multiples.csv").ev_to_revenue.median()

    deals = pd.read_csv(AOUT / "transactions_vs_forbes.csv").dropna(subset=["deal_over_forbes"])
    corr = pd.read_csv(AOUT / "budget_rank_correlations.csv")
    el = pd.read_csv(MANUAL / "euroleague_valuations.csv")
    league = el[(el.entity_type == "league") & (el.season == "2025-26")].value_eur_m_low.iloc[0]

    return [
        (pct(nba), f"NBA average team value, growth per year (Forbes {first} to {last})",
         f"S&P 500 with dividends over the same months: {pct(sp)}"),
        (f"{clubs.sharpe:.2f}", "Sharpe ratio of the 12 listed European football clubs, in euros",
         f"S&P 500: {spx.sharpe:.2f}, {month_name(clubs.window_start)} to {month_name(clubs.window_end)}"),
        (f"{nba_multiple:.1f}x vs {football_multiple:.1f}x",
         "Median enterprise value / revenue, NBA teams vs listed European football clubs",
         f"Forbes {last}; Yahoo Finance, last 12 months"),
        (f"{deals.deal_over_forbes.min():.2f}x to {deals.deal_over_forbes.max():.2f}x",
         "NBA control sales vs the last Forbes value before the deal",
         f"{len(deals)} deals, {deals.date.min()[:4]} to {deals.date.max()[:4]}"),
        (f"{corr.spearman_rho.min():.2f} to {corr.spearman_rho.max():.2f}",
         "Rank correlation between EuroLeague budget and league position",
         "Spearman, by season and budget definition"),
        (f"€{league / 1000:.2f}bn", "Valuation of the EuroLeague league company, 2025-26",
         "JB Capital, March 2026"),
    ]


# ---------- tables ----------

def risk_table():
    risk = pd.read_csv(AOUT / "risk_return.csv")
    rows = [(RISK_NAMES[r.series], pct(r.cagr), pct(r.volatility), f"{r.sharpe:.2f}", pct(r.max_drawdown, 0),
             f"{r.beta_vs_sp500:.2f}", f"{r.beta_vs_msci_europe:.2f}") for _, r in risk.iterrows()]
    r0 = risk.iloc[0]
    caption = (f"Monthly returns in euros, {month_name(r0.window_start)} to {month_name(r0.window_end)} "
               f"({r0.n_months} months), the longest period all four series exist. The Sharpe ratio uses the "
               f"ECB deposit rate as the risk-free rate.")
    return (table(["", "Growth per year", "Volatility", "Sharpe", "Max drawdown", "Beta vs S&P 500",
                   "Beta vs MSCI Europe"], rows)
            + f"<p class=source>{esc(caption)} Data: {data_link('analysis/output/risk_return.csv')}</p>")


def deals_table():
    deals = pd.read_csv(AOUT / "transactions_vs_forbes.csv")
    rows = []
    for _, d in deals.iterrows():
        pending = isinstance(d.notes, str) and "not yet approved" in d.notes
        team = d.team + (" *" if pending else "")
        if pd.notna(d.deal_over_forbes):
            forbes = f"${d.forbes_value_usd_m / 1000:.2f}bn ({int(d.forbes_edition)})"
            ratio, multiple = f"{d.deal_over_forbes:.2f}x", f"{d.deal_ev_to_revenue:.1f}x"
        else:
            forbes, ratio, multiple = "no list in the 12 months before", "", ""
        rows.append((d.date, team, d.buyer, f"${d.implied_valuation_usd_m / 1000:.2f}bn", forbes, ratio, multiple))
    return (table(["Agreed", "Team", "Buyer", "Deal valuation", "Last Forbes value", "Deal / Forbes",
                   "Deal / revenue"], rows, left_cols=3)
            + "<p class=source>Deal valuation divided by the latest Forbes value for that team published "
              "before the deal was agreed, and by the revenue in that Forbes list. * not yet approved by the "
              f"NBA in November 2026. Data: {data_link('analysis/output/transactions_vs_forbes.csv')}</p>")


def nba_editions_table(growth):
    wide = growth[growth.list_year_start == growth.list_year_end].pivot(
        index="list_year_start", columns="metric", values="value")
    rows = [(e, f"${r.league_avg_value_usd_m / 1000:.2f}bn", f"${r.league_median_value_usd_m / 1000:.2f}bn",
             f"${r.top5_avg_value_usd_m / 1000:.2f}bn", f"${r.bottom5_avg_value_usd_m / 1000:.2f}bn",
             f"{r.top5_over_bottom5_ratio:.2f}x", f"{r.median_value_rev_multiple:.1f}x")
            for e, r in wide.iterrows()]
    return table(["Forbes edition", "Average", "Median", "Top 5 average", "Bottom 5 average",
                  "Top 5 / bottom 5", "Median value / revenue"], rows)


def cagr_table(growth):
    nba = growth[growth.metric == "nba_avg_value_cagr"].reset_index(drop=True)
    sp = growth[growth.metric == "sp500tr_cagr_same_window"].reset_index(drop=True)
    rows = [(f"{a} to {b}", note, pct(n), pct(s))
            for a, b, note, n, s in zip(nba.list_year_start, nba.list_year_end, nba.note, nba.value, sp.value)]
    return table(["Editions", "Months", "NBA average value", "S&P 500 with dividends"], rows, left_cols=2)


def football_table():
    clubs = pd.read_csv(AOUT / "football_multiples.csv")
    rows = [(c.club, f"{c.market_cap_eur_m:,.0f}", f"{c.ev_eur_m:,.0f}", f"{c.revenue_eur_m:,.0f}",
             f"{c.ev_to_revenue:.2f}x") for _, c in clubs.iterrows()]
    return table(["Club", "Market value €M", "Enterprise value €M", "Revenue €M (12 months)", "EV / revenue"], rows)


def correlation_table():
    corr = pd.read_csv(AOUT / "budget_rank_correlations.csv")
    names = {"total_budget_gross": "total budget (gross)", "payroll_net": "player payroll (net)",
             "payroll_gross": "payroll (gross)"}
    return table(["Season", "Budget figure", "Clubs", "Spearman ρ"],
                 [(r.season, names[r.figure_type], r.n_clubs, f"{r.spearman_rho:.2f}") for _, r in corr.iterrows()],
                 left_cols=2)


def payroll_table():
    b = pd.read_csv(common.DATA_DIR / "euroleague_budgets.csv")
    pay = b[(b.season == "2025-26") & (b.figure_type == "payroll_net")].sort_values("amount_high_eur_m", ascending=False)
    return table(["Club", "Low €M", "High €M"],
                 [(r.canonical_name, f"{r.amount_low_eur_m:.1f}", f"{r.amount_high_eur_m:.1f}") for _, r in pay.iterrows()])


def euroleague_budget_table():
    b = pd.read_csv(common.DATA_DIR / "euroleague_budgets.csv")
    tb = b[b.figure_type == "total_budget_gross"].copy()
    tb["mid"] = (tb.amount_low_eur_m + tb.amount_high_eur_m) / 2
    wide = tb.pivot(index="canonical_name", columns="season", values="mid").sort_values("2024-25", ascending=False)

    def cell(value):
        return f"{value:.1f}" if pd.notna(value) else "no figure"

    return table(["Club", "2021-22 €M", "2024-25 €M"],
                 [(club, cell(r["2021-22"]), cell(r["2024-25"])) for club, r in wide.iterrows()])


def jb_table():
    el = pd.read_csv(MANUAL / "euroleague_valuations.csv")
    rows = []
    for _, r in el.iterrows():
        value = (f"€{r.value_eur_m_low:,.0f}M" if r.value_eur_m_low == r.value_eur_m_high
                 else f"€{r.value_eur_m_low:,.0f}M to €{r.value_eur_m_high:,.0f}M")
        rows.append((r.entity, r.season, r.basis, value))
    return table(["What", "Season", "Basis", "Value"], rows, left_cols=3)


def lnb_table():
    lnb = pd.read_csv(MANUAL / "lnb_dnccg.csv")
    budget = lnb[lnb.figure_type == "budget_total"].pivot(index="club", columns="season", values="amount_eur_m")
    payroll = lnb[lnb.figure_type == "payroll_dnccg"].pivot(index="club", columns="season", values="amount_eur_m")
    budget = budget.sort_values("2025-26", ascending=False)
    rows = []
    for club, b in budget.iterrows():
        before = f"{b['2024-25']:.1f}" if pd.notna(b["2024-25"]) else "promoted"
        share = payroll.loc[club, "2025-26"] / b["2025-26"]
        rows.append((club, before, f"{b['2025-26']:.1f}", f"{payroll.loc[club, '2025-26']:.1f}", f"{share:.0%}"))
    return table(["Club", "Budget 2024-25 €M", "Budget 2025-26 €M", "Payroll 2025-26 €M", "Payroll / budget"], rows)


# ---------- sources and caveats ----------

def caveats():
    stats = pd.read_csv(AOUT / "listed_index_stats.csv")
    common_window = stats[(stats.series == "eu_football_common_window") & (stats.metric == "cagr")].iloc[0]
    fixed = stats[(stats.series == "eu_football_fixed12") & (stats.metric == "cagr")].iloc[0]
    staggered = stats[(stats.series == "eu_football") & (stats.metric == "cagr")].iloc[0]
    if abs(common_window.value - fixed.value) < 0.00005:
        same_window = (f"over the same months ({month_name(fixed.window_start)} to {month_name(fixed.window_end)}) "
                       f"the two give the same result, so the gap comes from the start date, not from which clubs are in")
    else:
        same_window = (f"over the same months they give {pct(common_window.value)} and {pct(fixed.value)} a year")

    div = pd.read_csv(AOUT / "publisher_divergence.csv").set_index("publisher")
    sportico, cnbc = div.loc["sportico"], div.loc["cnbc"]
    lnb = pd.read_csv(MANUAL / "lnb_dnccg.csv")
    op = lnb[lnb.figure_type == "operating_result"].set_index("club").amount_eur_m

    items = [
        "The listed index only holds clubs that are still listed today. Clubs that delisted, like AS Roma in "
        "2022, are missing from the whole history, so the index probably flatters what an investor would "
        "actually have earned.",
        f"Start dates change the answer. From 2004 the index grows {pct(staggered.value)} a year, from 2012 "
        f"{pct(fixed.value)}; {same_window}.",
        "Forbes values are estimates made once a year, so they move much more smoothly than share prices. "
        "Volatility, Sharpe ratios and betas are only computed for the listed series: the same calculation on "
        "yearly estimates would make NBA teams look far less risky than they are.",
        "The NBA and football multiples aren't measured the same way. Forbes values a controlling stake and "
        "counts things like arena income; a listed club's enterprise value is the price of small minority "
        "stakes plus net debt, and Yahoo's revenue figure may leave out player sales.",
        "Club prices, the S&P 500 and IEUR include dividends. STOXX Europe 600 is price only and so understates "
        "that benchmark; it only covers the years before IEUR started (2014).",
        "EuroLeague budgets are BasketNews estimates with a stated margin of error, and I keep the ranges they "
        "report. Payroll and total budget are never mixed in one series. The 2025-26 payroll counts players "
        "only, earlier seasons include coaches.",
        "The 2021-22 standings leave out the three Russian clubs expelled during the season, and Baskonia "
        "published no figures for 2021-22.",
        f"Valuations are estimates, not prices, and publishers disagree. Sportico's Oct 2026 values are on "
        f"average {pct(sportico.mean_pct_diff_vs_forbes)} above Forbes for the {int(sportico.n_teams)} teams "
        f"whose figures I could find published; CNBC's Feb 2026 values are {pct(cnbc.mean_pct_diff_vs_forbes)} "
        f"above Forbes' Oct 2025 list for {int(cnbc.n_teams)} teams.",
        "A deal valuation and a Forbes value aren't the same measure: deals can include arenas or other "
        "businesses, and some are paid in stages (the Trail Blazers row uses the first tranche).",
        f"French budgets are what clubs filed with the league each September, not audited accounts. The loss "
        f"figures come from the league's own summary of the audited accounts: a "
        f"€{-op['Betclic ELITE (all clubs)']:.1f}M operating loss for the division in 2024-25, "
        f"€{-op['EuroLeague clubs (Monaco + ASVEL + Paris)']:.1f}M of it from the three EuroLeague clubs.",
        "Two tickers changed in 2026. MSG Sports (Knicks) trades as MSGK after spinning off the Rangers, and "
        "Eagle Football Group (Lyon) is now OL Groupe (OLG). Both keep their full price history.",
        "Index membership is a judgement call: Turkish clubs are left out (currency swings and speculative "
        "trading), TKO's pre-2023 WWE history is dropped, and the US companies are kept separate from the "
        "European index. methodology.md explains each choice and the alternative.",
        "The Swiss SB League is left out because its clubs don't publish financial figures.",
    ]
    return "<ol class=notes>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ol>"


def sources():
    bn = pd.read_csv(common.DATA_DIR / "euroleague_budgets.csv")
    bn_links = ", ".join(link(u, s) for s, u in bn[["season", "source_url"]].drop_duplicates().itertuples(index=False))
    el_url = pd.read_csv(MANUAL / "euroleague_valuations.csv").source_url.iloc[0]
    lnb = pd.read_csv(MANUAL / "lnb_dnccg.csv")
    lnb_budget = lnb[lnb.figure_type == "budget_total"].source_url.iloc[0]
    lnb_accounts = lnb[lnb.figure_type == "operating_result"].source_url.iloc[0]
    pub = pd.read_csv(MANUAL / "publisher_divergence.csv").groupby("publisher").source_url.first()
    fetched = pd.read_csv(common.DATA_DIR / "club_fundamentals.csv").fetched_on.iloc[0]

    items = [
        "Forbes NBA team valuations, 2016 to 2026 editions, from archived copies of the data behind Forbes' "
        "list page on the Wayback Machine (one link per row in data/nba_valuations.csv).",
        f"BasketNews EuroLeague budget research: {bn_links}.",
        f"EuroLeague standings: the league's open API "
        f"({link('https://api-live.euroleague.net/v1/standings?seasonCode=E2025', 'api-live.euroleague.net')}), "
        f"regular season only.",
        f"JB Capital valuation: {link(el_url, 'EuroLeague press release, March 2026')}.",
        f"French league: {link(lnb_budget, 'LNB/DNCCG budgets 2025-26')} and "
        f"{link(lnb_accounts, 'DNCCG accounts summary 2024-25')}.",
        f"Sportico and CNBC values as republished by {link(pub['sportico'], 'Bleacher Report')} and "
        f"{link(pub['cnbc'], 'NBC Chicago')}.",
        "NBA deal prices: ESPN, Sports Illustrated, Hoops Rumors, Axios; one link per deal in "
        "data/manual/transactions.csv.",
        f"Share prices, exchange rates and the clubs' enterprise value and revenue (fetched {fetched}): "
        f"Yahoo Finance, through the yfinance library.",
        f"Risk-free rate: ECB deposit facility rate from the "
        f"{link('https://data.ecb.europa.eu/data/datasets/FM', 'ECB Data Portal')}.",
        "US inflation: FRED series CPIAUCSL (one number in the note pack only).",
    ]
    if REPO_URL:
        items.append(f"Code, data and methodology: {link(REPO_URL, REPO_URL.replace('https://', ''))}.")
    return "<ul class=notes>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


# ---------- page ----------

def figure_html(number, div_id, fig, title, subtitle, source, data_path, details=""):
    chart = fig.to_html(full_html=False, include_plotlyjs=False, config=CONFIG_DEFAULT, div_id=div_id)
    return (f"<figure><figcaption><span class=fig-no>Figure {number}</span>"
            f"<span class=fig-title>{esc(title)}</span><span class=fig-sub>{esc(subtitle)}</span></figcaption>"
            f"{chart}<p class=source>Source: {esc(source)}. Data: {data_link(data_path)}</p>{details}</figure>")


def run():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    figs = dict(build_figures())
    growth = pd.read_csv(AOUT / "nba_growth.csv")
    count = iter(range(1, 100))

    def fig(div_id, title, subtitle, source, data_path, details=""):
        return figure_html(next(count), div_id, figs[div_id], title, subtitle, source, data_path, details)

    chapters = [
        ("listed", "Listed football clubs vs equities",
         "Twelve European football clubs trade on stock exchanges. Here they are treated as one portfolio, "
         "equal weight and rebalanced monthly, in euros, against the S&P 500 and MSCI Europe with dividends "
         "reinvested. The US sports companies (MSG Knicks, Atlanta Braves, TKO, MSG Entertainment) are shown "
         "as a separate line.",
         [fig("chart-listed-2012", "Twelve listed clubs vs stock indices since 2012",
              "Index level in euros, every line starting at 100.",
              "Yahoo Finance; equal-weight index, rebalanced monthly", "analysis/output/listed_index_monthly.csv"),
          fig("chart-listed-2004", "The same index back to 2004",
              "Clubs join in the month they list, so the early years hold fewer clubs (bottom panel).",
              "Yahoo Finance", "analysis/output/listed_index_monthly.csv"),
          fig("chart-drawdown", "Drawdowns: football clubs vs the S&P 500",
              "How far each index is below its previous high, in euros.",
              "Yahoo Finance", "analysis/output/listed_index_monthly.csv"),
          "<h3>Risk and return</h3>" + risk_table()]),
        ("nba", "NBA franchise values",
         "Forbes estimates the value and revenue of all 30 NBA teams every year. Six editions from 2016 to "
         "2026 are used here, compared with the S&P 500 over exactly the same months.",
         [fig("chart-nba-values", "Average NBA team value",
              "Mean of the 30 teams in each Forbes edition, placed at the month it was published.",
              "Forbes via the Wayback Machine", "analysis/output/nba_growth.csv", numbers(nba_editions_table(growth))),
          fig("chart-nba-cagr", "NBA value growth vs the S&P 500",
              "Growth per year between Forbes editions, and the S&P 500 with dividends over the same months (USD).",
              "Forbes; Yahoo Finance (^SP500TR)", "analysis/output/nba_growth.csv", numbers(cagr_table(growth))),
          fig("chart-nba-spread", "Richest vs poorest teams, and value per dollar of revenue",
              "Two measures, so two panels.", "Forbes via the Wayback Machine", "analysis/output/nba_growth.csv")]),
        ("multiples", "Deals and multiples",
         "What teams actually change hands for, and what they are worth relative to revenue: NBA control sales "
         "against Forbes' estimates, and NBA multiples next to listed European football clubs.",
         ["<h3>NBA control sales vs the last Forbes value</h3>" + deals_table(),
          fig("chart-multiples", "Enterprise value as a multiple of revenue",
              "Each dot is a team, a sale or a club; the black tick marks the median.",
              "Forbes; deal reports; Yahoo Finance", "analysis/output/football_multiples.csv",
              numbers(football_table()))]),
        ("euroleague", "EuroLeague",
         "No EuroLeague club is listed and few publish accounts. What exists: BasketNews' yearly budget "
         "estimates, the league's standings and one valuation by JB Capital.",
         [fig("chart-budget-vs-rank", "Budget rank vs league position",
              "One dot per club per season. The grey line is where budget rank and position would be equal.",
              "BasketNews; EuroLeague API", "analysis/output/budget_vs_performance.csv", numbers(correlation_table())),
          fig("chart-payrolls-2025-26", "Net player payrolls, 2025-26",
              "BasketNews estimates; the whiskers show the range they reported.",
              "BasketNews", "data/euroleague_budgets.csv", numbers(payroll_table())),
          fig("chart-euroleague-budgets", "Total budgets, 2021-22 and 2024-25",
              "Clubs with one dot have one season of data: the Russian clubs left after 2021-22 and newer "
              "clubs have no 2021-22 figure.", "BasketNews", "data/euroleague_budgets.csv",
              numbers(euroleague_budget_table())),
          fig("chart-jb-capital", "JB Capital's valuation of the EuroLeague",
              "The only published valuation of EuroLeague clubs: one estimate from March 2026.",
              "EuroLeague press release", "data/manual/euroleague_valuations.csv", numbers(jb_table()))]),
        ("france", "French league",
         "The French league publishes every club's budget and payroll each September. Three of its clubs "
         "played in the EuroLeague in 2025-26: Monaco, Paris and ASVEL (in bold below).",
         [fig("chart-lnb-budgets", "Betclic Élite budgets, 2024-25 and 2025-26",
              "Budget as defined by the league: total revenue, as filed in September.",
              "LNB / DNCCG", "data/manual/lnb_dnccg.csv", numbers(lnb_table()))]),
    ]

    strip = "".join(f"<div><p class=big>{esc(n)}</p><p class=lbl>{esc(l)}</p><p class=sub>{esc(s)}</p></div>"
                    for n, l, s in headline_stats())
    contents = " ".join(f'<a href="#{cid}"><span>{i}</span> {esc(title)}</a>'
                        for i, (cid, title, _, _) in enumerate(chapters, start=1))
    contents += ' <a href="#sources">Sources</a> <a href="#caveats">Caveats</a>'
    body = "".join(
        f'<section id="{cid}"><h2><span class=ch-no>{i}</span>{esc(title)}</h2><p class=lede>{esc(lede)}</p>'
        + "".join(parts) + "</section>"
        for i, (cid, title, lede, parts) in enumerate(chapters, start=1))
    repo_note = f" · {link(REPO_URL, 'Code and data on GitHub')}" if REPO_URL else ""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>European Basketball Franchise Valuation Tracker</title>
<meta name="description" content="NBA franchise values, EuroLeague budgets and listed football clubs compared with the stock market.">
<script src="https://cdn.plot.ly/plotly-{get_plotlyjs_version()}.min.js"></script>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: {PAGE}; color: {INK}; line-height: 1.5;
         font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 920px; margin: 0 auto; padding: 40px 16px 80px; }}
  a {{ color: #1f5fae; text-underline-offset: 2px; }}
  code {{ font-size: 0.85em; color: {INK_2}; }}
  header .kicker {{ margin: 0 0 6px; font-size: 0.85rem; color: {MUTED}; }}
  h1 {{ margin: 0 0 10px; font-size: 2rem; line-height: 1.15; letter-spacing: -0.01em; }}
  .dek {{ margin: 0 0 18px; max-width: 680px; font-size: 1.05rem; color: {INK_2}; }}
  nav {{ display: flex; flex-wrap: wrap; gap: 4px 18px; padding: 10px 0; font-size: 0.9rem;
         border-top: 1px solid {INK}; border-bottom: 1px solid {AXIS}; }}
  nav a {{ color: {INK}; text-decoration: none; }}
  nav a:hover {{ text-decoration: underline; }}
  nav span {{ color: {MUTED}; }}
  .strip {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px 32px; margin: 32px 0 8px; }}
  .strip div {{ border-top: 2px solid {INK}; padding-top: 10px; }}
  .strip p {{ margin: 0; }}
  .strip .big {{ font-size: 1.65rem; font-weight: 650; line-height: 1.2; }}
  .strip .lbl {{ margin-top: 4px; font-size: 0.88rem; color: {INK}; }}
  .strip .sub {{ margin-top: 2px; font-size: 0.8rem; color: {MUTED}; }}
  section {{ margin-top: 64px; }}
  h2 {{ display: flex; align-items: baseline; gap: 12px; margin: 0 0 8px; padding-top: 14px;
        border-top: 1px solid {INK}; font-size: 1.45rem; letter-spacing: -0.005em; }}
  .ch-no {{ color: {MUTED}; font-weight: 500; }}
  h3 {{ margin: 36px 0 10px; font-size: 1.02rem; }}
  .lede {{ margin: 0 0 8px; max-width: 700px; color: {INK_2}; }}
  figure {{ margin: 36px 0 0; }}
  figcaption {{ display: flex; flex-direction: column; margin-bottom: 6px; }}
  .fig-no {{ font-size: 0.78rem; color: {MUTED}; }}
  .fig-title {{ font-size: 1.02rem; font-weight: 650; }}
  .fig-sub {{ font-size: 0.9rem; color: {INK_2}; }}
  .source {{ margin: 6px 0 0; font-size: 0.8rem; color: {MUTED}; }}
  details {{ margin-top: 6px; font-size: 0.85rem; }}
  summary {{ cursor: pointer; color: #1f5fae; width: fit-content; }}
  .table-wrap {{ overflow-x: auto; margin-top: 8px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.86rem; }}
  th {{ text-align: left; font-weight: 600; color: {INK_2}; padding: 6px 10px 6px 0;
        border-bottom: 1px solid {INK}; vertical-align: bottom; }}
  td {{ padding: 6px 10px 6px 0; border-bottom: 1px solid {GRID}; white-space: nowrap; }}
  th.r, td.r {{ text-align: right; font-variant-numeric: tabular-nums; padding-right: 0; padding-left: 14px; }}
  .notes {{ padding-left: 20px; font-size: 0.9rem; color: {INK_2}; max-width: 760px; }}
  .notes li {{ margin-bottom: 8px; }}
  footer {{ margin-top: 56px; padding-top: 12px; border-top: 1px solid {AXIS}; font-size: 0.82rem; color: {MUTED}; }}
  @media (max-width: 760px) {{
    main {{ padding-top: 24px; }}
    h1 {{ font-size: 1.6rem; }}
    .strip {{ grid-template-columns: 1fr 1fr; gap: 20px 18px; }}
    .strip .big {{ font-size: 1.35rem; }}
  }}
  @media (max-width: 460px) {{ .strip {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<main>
<header>
<p class="kicker">Research project · market data to {data_date()}{repo_note}</p>
<h1>European Basketball Franchise Valuation Tracker</h1>
<p class="dek">How NBA franchises, EuroLeague clubs and listed football clubs are valued, and how those values
compare with the stock market. Built from public sources; every figure says where its numbers come from.</p>
<nav aria-label="Contents">{contents}</nav>
</header>
<div class="strip">{strip}</div>
{body}
<section id="sources"><h2>Sources</h2>{sources()}</section>
<section id="caveats"><h2>Caveats</h2>{caveats()}</section>
<footer>Built with Python (requests, BeautifulSoup, pandas, yfinance, plotly). Share prices refresh on the
3rd of each month through GitHub Actions; the yearly data is updated by hand. Not investment advice.</footer>
</main>
</body>
</html>
"""
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")
    print(f"dashboard: {len(figs)} charts -> docs/index.html ({len(page) // 1024} KB)")


if __name__ == "__main__":
    run()
