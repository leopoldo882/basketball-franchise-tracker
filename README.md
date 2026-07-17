# European Basketball Franchise Valuation Tracker

Data pipeline and dashboard investigating "sports as an asset class", with
European basketball as the focus and the NBA and football as comparators.

**Stack:** Python (requests, beautifulsoup4, pandas, yfinance, plotly),
GitHub Actions + GitHub Pages. No databases, no frameworks.

**Status:** Phase 1 (data pipeline). Dashboard and analysis to follow.

## Run

```
pip install -r requirements.txt
python run_pipeline.py
```

## Data

- `data/*.csv` — clean datasets, one per source, committed.
- `data/manual/*.csv` — hand-keyed figures from sources that can't or shouldn't
  be scraped (see data_inventory.md per source); committed.
- `data/mappings/team_names.csv` — canonical team names used to join sources.
- `data/raw/` — cached raw HTML/XML from sources. **Local only, gitignored** —
  cached page content is copyrighted material and is never pushed to the repo.

Source-by-source access notes (what is scraped, what is manual, and why):
see [data_inventory.md](data_inventory.md). Methodological choices:
see [methodology.md](methodology.md).
