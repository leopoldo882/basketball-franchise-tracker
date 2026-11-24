# European Basketball Franchise Valuation Tracker

A data pipeline and dashboard on sports teams as an investment. It collects NBA franchise values
(Forbes, 2016 to 2026), EuroLeague and French club budgets, the one published valuation of
EuroLeague clubs and the share prices of 12 listed European football clubs, and compares them with
the S&P 500 and European equities.

**Live dashboard:** https://leopoldo882.github.io/basketball-franchise-tracker/

![Dashboard screenshot](docs/screenshot.png)

## What it covers

- An equal-weight index of 12 listed European football clubs in euros against the S&P 500 and MSCI
  Europe (with dividends): growth, volatility, Sharpe ratio, beta and drawdowns
- NBA team value growth, the gap between rich and poor teams, and value/revenue multiples over six
  Forbes editions, against the S&P 500 over the same months
- Revenue multiples side by side: NBA teams, NBA control sales and listed football clubs, plus each
  sale price against the last Forbes estimate
- EuroLeague budget rank vs league position for each season, the JB Capital valuation of the league,
  and French top-division budgets from the league's own filings

## Stack

Python: requests, BeautifulSoup, pandas, yfinance, plotly. The dashboard is a static HTML page on
GitHub Pages and a GitHub Action refreshes the share prices on the 3rd of each month. No database,
no web framework.

## Running it

```
pip install -r requirements.txt
python run_pipeline.py                # everything
python run_pipeline.py --market-only  # market data only, what the monthly Action runs
python run_pipeline.py --notepack     # also chart PNGs and facts.md in note_support/
python -m unittest discover -s tests  # checks on the core calculations
```

`--notepack` also needs `pip install -r requirements-notepack.txt`.

## Where things are

- `collectors/`: one script per data source
- `analysis/`: the calculations; results go to `analysis/output/`
- `dashboard/`: `charts.py` draws the charts, `build.py` writes `docs/index.html`
- `tests/`: unit tests for the calculations
- `data/`: clean CSVs. `data/manual/` holds hand-entered figures (columns explained in its
  README); `data/raw/` keeps downloaded pages locally and isn't committed
- `note_support/`: every chart as a PNG and a sheet of the computed numbers with sources

[methodology.md](methodology.md) explains each choice behind the numbers and the alternative I
didn't take. [data_inventory.md](data_inventory.md) covers where each source comes from and how it's
collected.

## Licence

The code is MIT licensed (see [LICENSE](LICENSE)). The figures in `data/` belong to the sources
listed in data_inventory.md and are used here for non-commercial research.
