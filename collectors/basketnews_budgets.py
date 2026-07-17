"""EuroLeague club budget/payroll figures from BasketNews annual research articles.

Each article carries an HTML table. Column headers differ by season, so headers
are mapped to a controlled figure_type vocabulary. Per methodology.md ruling,
payroll and total-budget figures stay in separate rows (figure_type column) and
are never merged into one series.

Seasons 2022-23 and 2023-24 had no single roundup article; those go in the
manual template (data/manual/) instead.

Note: BasketNews serves 403 to the default python-requests user agent; the
custom UA in common.py is required.
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

# header text (lowercased) -> figure_type
HEADER_TO_FIGURE_TYPE = {
    "total budget (gross)": "total_budget_gross",
    "players/coaches salaries (net)": "payroll_net",
    "salaries (gross)": "payroll_gross",
    "team payroll (players net)": "payroll_net",
}

# e.g. "€45M", "€26.5-27.0M", "€8-8.5M"; first number, optional range end
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
    """Direct td/th children only: the page nests tables, and a recursive
    find_all would make outer layout rows swallow the budget table's cells."""
    return [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"], recursive=False)]


def parse_article(html, season, url, by_basketnews):
    """Find the budget table: a header row containing 'Team' plus 'budget' or
    'payroll', then data rows with the same number of cells."""
    soup = BeautifulSoup(html, "html.parser")
    all_rows = soup.find_all("tr")

    header_cells = None
    header_index = None
    for i, tr in enumerate(all_rows):
        texts = row_cells(tr)
        # a real header row: one cell IS "Team" and another names a known figure
        # column (loose "contains" matching would hit page-layout wrapper tables)
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
