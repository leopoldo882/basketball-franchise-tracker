"""EuroLeague club budgets and payrolls from BasketNews' yearly research articles.

Each article has an HTML table, but the column names change from year to
year, so they're mapped onto a small set of figure types. Payroll and total
budget stay as separate rows (figure_type) and are never treated as one series.

I couldn't find a single roundup article for 2022-23 or 2023-24, so those
seasons are missing.
"""

import re

import pandas as pd
from bs4 import BeautifulSoup

from . import common

ARTICLES = [
    {
        "season": "2021-22",
        "url": "https://basketnews.com/news-159564-euroleague-team-budgets-2021-22-three-dominant-clubs.html",
        "cache": "basketnews_budgets_2021-22.html",
    },
    {
        "season": "2024-25",
        "url": "https://basketnews.com/news-204932-euroleague-teams-clubs-budgets.html",
        "cache": "basketnews_budgets_2024-25.html",
    },
    {
        "season": "2025-26",
        "url": "https://basketnews.com/news-233398-euroleague-budgets-payrolls-2026-biggest-spenders.html",
        "cache": "basketnews_budgets_2025-26.html",
    },
]

# column header (lowercase) -> figure_type
HEADER_TO_FIGURE_TYPE = {
    "total budget (gross)": "total_budget_gross",
    "players/coaches salaries (net)": "payroll_net",
    "salaries (gross)": "payroll_gross",
    "team payroll (players net)": "payroll_net",
}

# matches "€45M", "€26.5-27.0M", "€8-8.5M": a number and an optional range end
AMOUNT_PATTERN = re.compile(r"€\s*([\d.,]+)\s*(?:-\s*([\d.,]+))?\s*M", re.IGNORECASE)

OUTPUT_FILE = common.DATA_DIR / "euroleague_budgets.csv"


def parse_amount(cell_text):
    """'€26.5-27.0M' -> (26.5, 27.0); '€45M' -> (45.0, 45.0); no match -> None."""
    match = AMOUNT_PATTERN.search(cell_text)
    if not match:
        return None
    low = float(match.group(1).replace(",", "."))
    high = float(match.group(2).replace(",", ".")) if match.group(2) else low
    return low, high


def row_cells(tr):
    """Text of the row's own cells. The page puts tables inside tables, so
    without recursive=False an outer layout row would also pick up every
    cell of the budget table inside it."""
    return [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"], recursive=False)]


def parse_article(html, season, url, by_basketnews):
    """Find the header row of the budget table, then read the data rows below
    it until a row with a different number of cells ends the table."""
    soup = BeautifulSoup(html, "html.parser")
    all_rows = soup.find_all("tr")

    header_cells = None
    header_index = None
    for i, tr in enumerate(all_rows):
        texts = row_cells(tr)
        # the header has a cell that is exactly "Team" and a cell that is one of
        # the known figure columns; looser matching hits the page layout tables
        has_team_cell = any(t.lower().strip() in ("team", "teams") for t in texts)
        has_figure_cell = any(t.lower().strip() in HEADER_TO_FIGURE_TYPE for t in texts)
        if has_team_cell and has_figure_cell:
            header_cells = texts
            header_index = i
            break
    if header_cells is None:
        print(f"  WARNING {season}: no budget table found in {url}")
        return []

    # which column holds the team name, which columns hold figures
    team_col = next(i for i, h in enumerate(header_cells) if h.lower().strip() in ("team", "teams"))
    figure_cols = {
        i: HEADER_TO_FIGURE_TYPE[h.lower().strip()]
        for i, h in enumerate(header_cells)
        if h.lower().strip() in HEADER_TO_FIGURE_TYPE
    }

    rows = []
    for tr in all_rows[header_index + 1:]:
        cells = row_cells(tr)
        if len(cells) != len(header_cells):
            break  # end of the table's data rows
        team = cells[team_col]
        if not team:
            continue
        for col, figure_type in figure_cols.items():
            amount = parse_amount(cells[col])
            if amount is None:
                continue
            rows.append({
                "season": season,
                "team_basketnews": team,
                "canonical_name": by_basketnews.get(team, ""),
                "figure_type": figure_type,
                "amount_low_eur_m": amount[0],
                "amount_high_eur_m": amount[1],
                "source_url": url,
            })
    return rows


def run():
    _, by_basketnews = common.load_team_mapping()
    rows = []
    for article in ARTICLES:
        html = common.polite_get(article["url"], article["cache"])
        rows.extend(parse_article(html, article["season"], article["url"], by_basketnews))
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"basketnews_budgets: {len(df)} rows, {df['season'].nunique()} seasons -> {OUTPUT_FILE.name}")
    return df
