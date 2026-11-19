# Python API

Datadough's numbers are available as a Python library: a company's line items, ratios and red-flag scores
as [pandas](https://pandas.pydata.org/) DataFrames, with the SEC filing behind every figure.

## Install

```bash
pip install datadough          # once it's published on PyPI (see PUBLISHING.md)
pip install git+https://github.com/VedantParashar/finance-analyzer.git   # works today
```

The package installs as `datadough` and is imported as `finance_analyzer` (the name the code has always
had). Python 3.12 or newer.

The SEC asks every program that downloads its data to say who it is. Set your name and email first:

```bash
export SEC_USER_AGENT="Your Name you@example.com"
```

The first call for a company downloads its filings, which takes a second or two. After that everything
comes from a local cache in `./data`, under the folder you run Python from. The cache refreshes itself
once it's 7 days old.

## Quick start

```python
import finance_analyzer as dd

ko = dd.get_company("KO")
ko.name, ko.currency, ko.fiscal_year_ends[-1]
# ('COCA COLA CO', 'USD', datetime.date(2025, 12, 31))

m = dd.metrics("KO")
m[m.metric == "roe"][["fiscal_year_end", "value", "source_urls"]].tail(1)
#   fiscal_year_end   value  source_urls
#        2025-12-31  0.4597  ['https://www.sec.gov/Archives/edgar/data/21344/000162828026010047/0001628280-26-010047-index.htm']
```

## Functions

### `search(text, limit=8)`

Companies whose ticker or name matches, largest first. Columns: `ticker`, `name`, `cik`.

```python
dd.search("coca")["ticker"].tolist()
# ['KO', 'CCEP', 'COKE', 'KOF', 'COCSF']
```

### `get_company(ticker)`

A `Company` with `ticker`, `name`, `cik`, `sic` (SEC industry code), `industry`, `exchange`, `currency`
(the statements' currency) and `fiscal_year_ends` (oldest first). Tickers can be typed loosely:
`"brk.b"`, `"BRK B"` and `"BRK-B"` are the same company. An unknown ticker raises `ValueError`.

### `line_items(ticker)`

One row per line item and fiscal year, every year stored.

| Column | Meaning |
|---|---|
| `fiscal_year_end` | the last day of the fiscal year |
| `item` | the standard line item, e.g. `revenue`, `total_liabilities` |
| `value` | in units: currency, shares, or currency per share |
| `unit` | e.g. `USD`, `EUR`, `USD/shares`, `shares` |
| `derivation` | empty if read as reported; otherwise how it was calculated |
| `accession`, `form`, `filed`, `source_url` | the SEC filing it was read from |

```python
li = dd.line_items("KO")
li[li.item == "total_liabilities"].iloc[-1][["value", "derivation", "form", "filed"]]
# value         70541000000.0
# derivation    liabilities = total − equity
# form          10-K
# filed         2026-02-20
```

### `metrics(ticker)`

The 19 ratios and the DuPont ROE for every stored year (plus FFO for a REIT), one row per metric and
year. Valuation ratios (P/E and so on) need today's share price and aren't included.

| Column | Meaning |
|---|---|
| `metric`, `label` | e.g. `net_margin`, "Net margin" |
| `value` | a fraction for percentages (0.276 = 27.6%), a number for multiples, currency for free cash flow; empty when it can't be calculated |
| `formula` | the formula in words |
| `inputs` | every number used, as a dict |
| `reason` | why the value is missing, e.g. "interest_expense not reported for FY2026" |
| `notes` | caveats that didn't stop the calculation, e.g. a derived input |
| `source_urls` | the filings the inputs came from |

### `red_flags(ticker)`

Altman Z″, Piotroski F, Beneish M and the accruals ratio for every stored year: the same columns as
`metrics()`, plus `verdict`.

```python
f = dd.red_flags("KO")
f[f.fiscal_year_end == f.fiscal_year_end.max()][["metric", "value", "verdict"]]
#         metric     value                  verdict
# accruals_ratio  0.055501   No flag (10% or below)
#       altman_z  4.503573    Safe zone (above 2.6)
#      beneish_m -2.349870 No flag (−1.78 or below)
#    piotroski_f  7.000000          Strong (7 to 9)
```

## Good to know

- The numbers are the same as in the web app, chosen by the rules in [METHODOLOGY.md](METHODOLOGY.md).
- Missing is never zero: a value that can't be calculated is empty, and `reason` says why.
- Banks, brokers and insurers load, but many ratios don't apply to them.
