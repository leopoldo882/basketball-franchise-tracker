# Data inventory

What data exists for this project, where it comes from, and how it gets into the pipeline. First
checked in July 2026, updated in November 2026. "Scraped" means the pipeline downloads it; "manual"
means I typed the figures into a CSV in data/manual/ with a source link on every row.

## NBA franchise values

**Forbes.** The only publisher with values and revenue for all 30 teams every year (since 1991-92).
Forbes' list page is built with JavaScript, so an archived copy of the page itself is empty, but
the Wayback Machine also archived the JSON endpoint the page reads
(`forbes.com/ajax/list/data?year=YYYY&uri=nba-valuations&type=organization`). I found the captures
through the Wayback CDX index. Captures exist for most years from 2016 to 2026; the pipeline uses
2016, 2019, 2022, 2024, 2025 and 2026 with pinned timestamps. Forbes' robots.txt allows article
pages, and the pipeline never contacts forbes.com directly, only archive.org.
Scraped. Updated yearly (October).

**Sportico.** Values for all teams since 2020, but the publisher's terms of use (PMC) ban
"spidering" and "screen scraping", and robots.txt blocks AI crawlers. Only used for the publisher
cross-check, from values republished by Bleacher Report (4 teams for October 2026). Manual.

**CNBC.** Started its own list in 2025. The full table is an embedded graphic that can't be read
as text, so the cross-check uses the 15 teams republished by NBC Chicago (February 2026). Manual.

## European basketball

**BasketNews EuroLeague budget research.** One article a year with a full table of club budgets
or payrolls. Articles used: 2021-22 (news-159564), 2024-25 (news-204932), 2025-26 (news-233398). I
couldn't find a full roundup for 2022-23 or 2023-24, only individual club announcements. The table
is in the page HTML; the BN+ paywall only covers an audio player. robots.txt is permissive, but
the site returns 403 to the default python-requests user agent, so the scraper sends its own. The
figure definition changes between years (total budget vs net payroll), which is why figure_type is
a column. Scraped, cached once in data/raw/.

**EuroLeague standings.** The league's open XML API, no key needed:
`https://api-live.euroleague.net/v1/standings?seasonCode=E2024`. Tested back to 2005. The public
website is behind bot protection, but the API isn't. Scraped, seasons 2021-22 to 2025-26.

**JB Capital valuation (March 2026).** League plus clubs valued at over €3.2bn, the league company
at €1.41bn for 2025-26, clubs from over €60M to over €320M on revenue multiples, and a €4.3bn
scenario if the franchise model goes ahead. Source: the EuroLeague's own press release
(euroleaguebasketball.net). It's the only valuation of EuroLeague clubs I found, and a single
snapshot. Manual.

**France (LNB / DNCCG).** The French league's financial watchdog publishes more than any other
European league: club budgets and approved payrolls every September, and audited accounts every
January. The budgets come as a PDF on cdn.lnb.fr; the audited per-club accounts are only in a
Google Drive folder linked from the press release, so I used the budgets plus the league-level
loss figures from the January 2026 press release. Manual (keyed from the PDFs, no PDF library).

**Spain (ACB).** No official per-club figures. Solobasket reported 2024-25 budgets for 8 clubs
(Real Madrid €45M down to Manresa €3.8M). Manual, reference only.

**Italy (LBA).** No official per-club figures. The most complete list I found is from La
Prealpina, via Backdoor Podcast: 10 clubs for 2021-22. Manual, reference only.

**Switzerland (SB League).** Nothing published. Left out.

## Listed sports companies

All checked with yfinance in July 2026 and again in November 2026.

| Ticker | Company | Notes | Prices from |
|---|---|---|---|
| MANU | Manchester United | NYSE, USD | 2012-08 |
| JUVE.MI | Juventus | | 2001-12 |
| SSL.MI | Lazio | | 1998-07 |
| BVB.DE | Borussia Dortmund | | 2000-10 |
| AJAX.AS | Ajax | | 1998-07 |
| CCP.L | Celtic | quoted in pence | 1995-09 |
| SLBEN.LS | Benfica | also has a basketball section | 2007-05 |
| FCP.LS | FC Porto | also has a basketball section | 2000-01 |
| SCP.LS | Sporting CP | | 2000-01 |
| OLG.PA | OL Groupe (Lyon) | was EFG.PA until Oct 2026 | 2007-02 |
| PARKEN.CO | Parken Sport (FC København) | | 2000-01 |
| BIF.CO | Brøndby | | 2000-01 |
| MSGK | MSG Knicks | was MSGS until the Oct 2026 Rangers spin-off | 2015-09 |
| BATRA | Atlanta Braves Holdings | MLB | 2016-04 |
| TKO | TKO Group | UFC/WWE; pre-Sep 2023 data is old WWE, dropped | 2023-09 |
| MSGE | MSG Entertainment | arenas | 2023-04 |

Not used: the four Turkish clubs (FENER.IS, GSRAY.IS, BJKAS.IS, TSPOR.IS; see methodology.md),
MSGR (the Rangers spin-off, from Oct 2026), AS Roma (delisted in 2022) and AGF Aarhus (no data).
There is no listed European basketball club anywhere. Since the spin-off MSGK holds only the Knicks
business, which makes it the only listed basketball team in the dataset.

Benchmarks: ^SP500TR (S&P 500 total return, from 1988), ^GSPC (price), ^STOXX (STOXX Europe 600,
price only, from 2004), IEUR (iShares Core MSCI Europe ETF, from 2014). FX: EURUSD=X, EURGBP=X,
EURDKK=X. All scraped, refreshed monthly by GitHub Actions.

**Club fundamentals.** Market value, enterprise value and trailing 12-month revenue for the 12
clubs, from yfinance's `Ticker.info`. Current values only, no history, so each monthly run replaces
the file. Watch out for currencies: Manchester United trades in USD but reports in GBP, and Yahoo's
own EV/revenue ratio doesn't convert. Scraped.

**Rates and inflation.** ECB deposit facility rate from the ECB Data Portal
(`data-api.ecb.europa.eu`, series FM.D.U2.EUR.4F.KR.DFR.LEV, daily from 1999, no key), used as the
euro risk-free rate. US CPI from FRED (CPIAUCSL). FRED's download was down for a while during
testing in November 2026, so both collectors keep their last saved file if the source doesn't
respond. Scraped.

## Deals

There is no free deal database (PitchBook and Sportico's tracker are paid). data/manual/transactions.csv
has one row per deal with stake, control or minority, implied valuation and a news link: the NBA
control sales from 2022 to 2026 (Suns, Hornets, Mavericks, Celtics, Lakers twice, Trail Blazers,
Timberwolves), Arctos' minority stakes, the NBA Europe franchise bids and Dubai Basketball's
EuroLeague entry. NBA rules let one fund own up to 20% of a team and stakes in up to five teams.
Manual, updated when a deal happens.

## Football comparators (not used yet)

Deloitte's Football Money League (top 20 clubs by revenue; the 2026 edition is the 29th:
€12.4bn combined, Real Madrid €1.161bn) is tabulated on Wikipedia and would be easy to add. I
haven't, because nothing on the dashboard needs football revenue yet.
