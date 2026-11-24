# Methodology

Every choice that affects a number, why I made it, and the main alternative.
Source-by-source access notes are in [data_inventory.md](data_inventory.md).

## Listed clubs index

### Which companies are in it
The headline index is 12 European football clubs that are listed today: MANU, JUVE.MI, SSL.MI,
BVB.DE, AJAX.AS, CCP.L, SLBEN.LS, FCP.LS, SCP.LS, OLG.PA, PARKEN.CO and BIF.CO. There is no listed
European basketball club, so football clubs are the closest listed proxy for European club sport.

Alternative: a global "sports" index mixing in US companies. I kept the US companies (MSGK, BATRA,
TKO, MSGE) as a separate line because they are a different market, currency and business model
(arena and media companies, not clubs).

### Turkish clubs are left out
Fenerbahçe, Galatasaray, Beşiktaş and Trabzonspor trade in Istanbul. Lira depreciation and heavy
retail speculation drive their prices far more than the football business does, and their
basketball teams sit inside multi-sport club structures.

Alternative: include them converted to EUR. Conversion fixes the currency but not the
speculative swings.

### TKO before September 2023 is dropped
Before 12 Sep 2023 the TKO ticker's history is the old WWE listing, a different company.

Alternative: keep the full series with a footnote. Too easy to misread on a chart.

### Equal weight, rebalanced monthly
Each month the index return is the simple average of its members' returns. The clubs' market
values differ by about two orders of magnitude, so a value-weighted index would mostly follow the
two or three biggest clubs.

Alternative: value weighting, or equal weight bought once and never rebalanced (which drifts
towards the past winners and ends up value weighted anyway).

### Everything in euros
Prices are converted to EUR with daily Yahoo FX rates (month-end values used). One currency makes
a multi-currency index readable. Celtic is quoted in pence, so it's divided by 100 first.

Alternative: average the returns in local currency. That avoids FX noise per club but the index
level no longer corresponds to anything an investor could hold.

### Start date and the fixed-12 version
The index starts in January 2004, the first month all three FX rates exist. Clubs join in the month
they list, so early years have 9 to 11 members (shown on the chart). A second version uses only
months where all 12 trade, which starts in September 2012 after Manchester United listed. I also
measure the staggered index over exactly those months: if the two agree, the difference between the
2004 and 2012 numbers comes from the start date and not from which clubs are in.

Alternative: one fixed-membership index only. That throws away eight years of history.

### Benchmarks include dividends
The S&P 500 comparison uses ^SP500TR and Europe uses the IEUR ETF's adjusted close, because club
prices are adjusted closes with dividends reinvested. IEUR only exists from 2014 and carries ETF
fees. STOXX Europe 600 is shown for the years before that, but it is price only, so it understates
that benchmark; every STOXX row says so.

Alternative: price indices throughout (^GSPC, ^STOXX). Simpler but not like for like. I also didn't
splice STOXX and IEUR into one series, since joining a price index to a total-return one creates a
series that doesn't exist.

### Every statistic has its own window
Each row in listed_index_stats.csv has its start month, end month and number of months, and
correlations only use months where both series exist. That way two numbers over different periods
are never compared by accident.

### Ticker changes in 2026
In October 2026 MSG Sports spun off the Rangers and the Knicks company kept the price history
under the new ticker MSGK. Yahoo records the spin-off as a 1.328 split, which treats the Rangers
shares as if they were reinvested in the Knicks stock; the 2020 MSG Entertainment spin-off is
handled the same way. Eagle Football Group (Lyon) became OL Groupe, ticker OLG.PA. I checked both
new tickers against the old data: monthly returns match with a correlation above 0.9998. The new
Rangers stock (MSGR) is not added to the US line because its value is already inside MSGK's history.

Alternative: add MSGR as a fifth US member from October 2026. That would count the Rangers twice.

## NBA franchise values

### Forbes as the main series
Forbes has published values and revenue for all 30 teams every year since the 1990s, which no
other publisher does. I use a panel of editions rather than every year: 2016, 2019 and 2022 (three
years apart), then 2024, 2025 and 2026. The 2026 edition came out in October 2026 and was added
then.

Alternative: every edition from 2016. More points but most of the extra windows would be one year
long and noisy.

### Where the Forbes numbers come from
Forbes' list page loads its data from a JSON endpoint, and the Wayback Machine archived it. The
capture timestamps are pinned in collectors/forbes_wayback.py. I checked each capture against
published figures: league averages of $4.42bn, $5.36bn and $6.13bn for 2024 to 2026 match the
$4.4bn, $5.4bn and $6.1bn Forbes reported.

Alternative: type the lists in by hand from the articles. More work and more room for typos; the
manual file is still there for any year without an archived capture.

### Growth windows use publication months
The 2016 and 2019 lists came out in February, the 2022 list in October 2021 and the 2024 to 2026
lists in October of the same year. CAGRs run between those months, and the S&P 500 comparison uses
exactly the same months.

Alternative: treat every edition as one calendar year apart. That would misstate the 2019 to 2022
window, which is really 2 years 8 months.

### Average, not median, for growth
The headline growth rate uses the mean value of the 30 teams. The set of teams never changes, so
the mean is the value of the whole league divided by 30.

Alternative: the median team. It ignores how the top teams pull away; the chart of top 5 vs bottom
5 averages covers that spread separately.

### US dollars, nominal
NBA values stay in USD because both sides of the comparison are American. Everything on the
dashboard is nominal. The facts sheet adds one inflation-adjusted growth rate, deflated with US CPI
(FRED CPIAUCSL), so the note can quote a real figure.

Alternative: deflate every series. It would add a CPI step to every number for little extra
information.

## Checks on the NBA numbers

### Other publishers vs Forbes
Sportico and CNBC values are compared with the Forbes edition closest in time: Sportico's October
2026 list with Forbes 2026, CNBC's February 2026 list with Forbes October 2025. Only the teams whose
values were republished outside the publishers' own sites are included (4 Sportico, 15 CNBC), because
Sportico's terms forbid scraping and CNBC's full table is an embedded graphic.

Alternative: skip the check. The point is to show that valuations are estimates, so a partial
comparison with a stated sample size is better than none.

### Deal prices vs Forbes
For each NBA control sale I divide the implied 100% valuation by the latest Forbes value for that
team published before the deal was agreed. The deal date is the month the price was agreed, not the
month the NBA approved it. If the Forbes list is more than 12 months older than the deal, no ratio
is shown. The Trail Blazers row uses the $4.0bn valuation of the first 80.1% tranche (the rest is
priced at $4.5bn by 2028). Deals not yet approved are included and marked.

Alternative: interpolate between the Forbes editions either side of the deal. That uses
information that wasn't public when the price was agreed.

## EuroLeague

### Regular-season standings only
Budget rank is compared with regular-season position for every season. Playoffs are a short
knockout and the format has changed over the years.

Alternative: final placement after the playoffs. Inconsistent across seasons and much noisier.

### Payroll and total budget kept apart
BasketNews reports total club budgets for some seasons and net player payroll for others. They
are separate rows (figure_type) and never one series. Within net payroll, 2021-22 and 2024-25
include coaches and 2025-26 covers players only.

Alternative: one "budget" series with a footnote. The break in definition would be invisible on a
chart.

### Ranges, midpoints and the correlation
BasketNews often gives a range (e.g. €26.5-27.0M). Both ends are kept; ranks use the midpoint.
The correlation is Spearman's, computed as the Pearson correlation of the two rank columns, with
tied budgets given the average rank. That avoids adding scipy for one function.

### Team names
Sources spell club names differently, so every join goes through data/mappings/team_names.csv and
the pipeline lists any club that falls out of a join with the reason.

### JB Capital valuation
The only valuation of EuroLeague clubs I found is JB Capital's March 2026 report, as summarised in
the EuroLeague's press release. It's one snapshot, not a series, and the release doesn't give the
revenue it's based on, so no EuroLeague value/revenue multiple is computed.

## Domestic leagues

### France: filed budgets instead of audited accounts
The original plan was audited per-club accounts from the DNCCG report. The league only publishes
those as a Google Drive folder, which can't be downloaded without a browser, so I used the league's
official budget document instead: each club's budget (total revenue) and approved payroll as filed
in September, for 2024-25 and 2025-26. The audited loss figures that are shown come from the
league's own summary of the accounts (press release, January 2026).

Alternative: key the per-club accounts in by hand from the Drive folder. Worth doing if the note
needs club-level profit and loss.

### Spain and Italy: reference only
ACB (2024-25) and LBA (2021-22) budgets come from media reports with different seasons and
definitions. They're in data/manual/ and the facts sheet but not on any chart, because putting them
next to the French or EuroLeague figures would suggest a comparison the data can't support.

### Switzerland dropped
SB League clubs don't publish budgets or accounts.

## Known biases

- Survivorship: the listed index only contains clubs listed today. Clubs that delisted (AS Roma in
  2022 and any earlier) are missing from the whole history, so the index probably overstates what
  holding listed football clubs actually returned. No adjustment is attempted.
- Valuations are estimates by journalists and analysts, not prices. The publisher check shows how
  far apart they can be.
- Deal prices can include arenas or other businesses, so a deal/Forbes ratio above 1 isn't purely a
  premium.

## How the data is collected

- Scrapers send a descriptive user agent, wait 3 seconds between requests and keep every page in
  data/raw/, so parsing again never hits the site again. data/raw/ isn't committed (it's other
  people's content).
- Hand-entered figures live in data/manual/ with a source link on every row; the pipeline checks
  their columns, number fields and duplicates on every run.
- The monthly GitHub Action only refreshes market data. The PNG export for the note pack needs
  kaleido and only runs locally (`--notepack`).

## Changes

- Jul 2026: first version (Forbes 2016/2019/2022, BasketNews, EuroLeague API, listed index).
- Nov 2026: added Forbes 2024 to 2026 from the same archive, the publisher and deal checks, French,
  Spanish and Italian budgets; switched MSGS to MSGK and EFG.PA to OLG.PA after the 2026 ticker
  changes.
