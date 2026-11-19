# Datadough

**Company financials you can trace back to the filing: every number links to the SEC document it came from.**

[![Try it](https://img.shields.io/badge/Try%20it-datadough.streamlit.app-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://datadough.streamlit.app)

[![tests](https://github.com/VedantParashar/finance-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/VedantParashar/finance-analyzer/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/VedantParashar/finance-analyzer)](https://github.com/VedantParashar/finance-analyzer/releases)
[![license](https://img.shields.io/github/license/VedantParashar/finance-analyzer)](LICENSE)
[![python](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

I built Datadough for students doing case studies, stock pitches and theses. It's free and open source.
Type a ticker and it reads the company's annual reports from SEC EDGAR. It puts them on one standard set
of line items and shows five years of statements, 19 ratios, red-flag scores and valuation. Each one is
explained in plain English with the company's own numbers.

![Demo: search for AAPL, open a metric's sources, see the Source column, compare AAPL, KO and NVDA](docs/demo.gif)

**Documentation:** https://vedantparashar.github.io/finance-analyzer/ (methodology, accuracy, case study,
Python API).

## How Datadough differs

- **Official SEC data.** Every statement figure comes from the XBRL data companies file with the US
  Securities and Exchange Commission (SEC EDGAR) with their annual reports. Nothing is scraped from
  other sites or estimated. Only today's share price and exchange rates come from elsewhere (Yahoo
  Finance), and only the five valuation ratios use them.
- **Traceable.** Every line item and every input to a ratio links to the filing it was read from, with
  the form type and filing date. That's true in the app and in the [Python API](docs/python-api.md).
  When the app calculates a value (say, a total the company doesn't report), it says how.
  [METHODOLOGY.md](docs/METHODOLOGY.md) explains each rule with real examples, including restatements
  and stock splits.
- **Validated.** [ACCURACY.md](docs/ACCURACY.md) checks 10 headline figures for 10 companies against
  the filings' own statements. 93 of 95 match, and both differences are explained. A balance check runs
  on every stored year. [COVERAGE.md](docs/COVERAGE.md) lists what's found and missing for 30 very
  different companies. A value that can't be calculated says why, and a missing value is never treated
  as zero.
- **Explained.** Every metric shows its formula with the company's own numbers, what it means, what a
  good value looks like and the common traps. It's written for students.

## Features

- **Company page** in tabs: Overview (headline cards with sparklines, revenue and profit, key ratios
  against the industry median), Financials (line items with their source), Ratios, Red flags,
  Valuation and Data checks. Switch between fiscal years and the trailing twelve months.
- **19 ratios:** margins, ROE, ROA, ROIC, liquidity, leverage, efficiency, free cash flow, growth and
  the DuPont breakdown. Each card's "How it's calculated" shows the formula with the real numbers, what
  it means, what's good, the common traps, and a link to report a number that looks wrong.
- **Red-flag scores** every year: Altman Z″, Piotroski F, Beneish M and the accruals ratio.
- **Valuation at today's price:** market cap, P/E, P/B, EV/EBIT and FCF yield.
- **Compare 2 to 4 companies**, with each company's colour kept across the table and the chart and the
  best and worst value in each row marked.
- **Excel export** whose metric cells are live formulas over the line items.
- **Shareable links** (`?ticker=AAPL`, `?compare=AAPL,KO`), peer suggestions, light and dark themes.
- **Use it from code or an AI assistant:** a [Python API](docs/python-api.md) (pandas DataFrames with
  source columns) and a read-only [MCP server](docs/mcp.md) for Claude Desktop.

## Supported companies

| | |
|---|---|
| ✅ **Works** | US companies that file annual reports (10-K) with the SEC, from about 2009 on. |
| ✅ **Works, in the company's own currency** | Foreign companies listed in the US that file a 20-F or 40-F, under US GAAP or IFRS (TSMC, ASML, SAP, Novo Nordisk, Toyota). Amounts stay in the reporting currency; only market cap is converted, for the valuation ratios. |
| ⚠️ **Works with a warning** | Banks, brokers and insurers (JPM, GS, BRK-B): many ratios don't apply to them. REITs get FFO (funds from operations) instead of the ratios that don't fit. |
| ❌ **Doesn't work** | ETFs and funds (no financial statements), companies not yet past their first annual report, and companies not listed in the US. The app says which it is. |

## Data sources

Financial statements from [SEC EDGAR](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
(XBRL company facts and submissions, free, no API key); share prices and exchange rates from Yahoo
Finance through [yfinance](https://github.com/ranaroussi/yfinance). Not investment advice.

## Run it on your computer

The SEC asks every program that reads its data to say who it is. Copy `.env.example` to `.env` and put
your name and email in `SEC_USER_AGENT`. With [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/VedantParashar/finance-analyzer.git
cd finance-analyzer
cp .env.example .env   # then edit it
uv run --env-file .env finance-analyzer
```

Then open http://localhost:8501. With Docker instead: `docker compose up --build`. Tests:
`uv run pytest`. To host your own copy for free, see [DEPLOY.md](DEPLOY.md).

## Limitations

- **SEC filers only**, and only what they tag in their XBRL data. A company that uses an unusual tag
  for a common line shows "—" with the reason.
- **IFRS filers have more gaps** (Toyota has no cost of revenue or capital expenditure in the data),
  and energy companies, utilities and REITs lay out their statements differently
  ([#27](https://github.com/VedantParashar/finance-analyzer/issues/27),
  [#31](https://github.com/VedantParashar/finance-analyzer/issues/31),
  [#33](https://github.com/VedantParashar/finance-analyzer/issues/33)). ExxonMobil can't be loaded
  ([#32](https://github.com/VedantParashar/finance-analyzer/issues/32)).
- **Valuation mixes dates:** today's share price against the last full fiscal year, so P/E differs
  from sites that use the last twelve months. Share prices come from Yahoo Finance, which is
  unofficial; if it fails, the valuation cards read "unavailable" and the rest still works.
- **Industry medians** use only the companies loaded into the app, so the sample is small.
- Known data issues are in the [issue list](https://github.com/VedantParashar/finance-analyzer/issues?q=is%3Aopen+label%3Adata-quality).

## How this was built

I designed Datadough and made the product, data and accounting decisions. Claude Code helped write the
code; I reviewed and tested every change. The main decisions and my reasons are in
[docs/design-decisions.md](docs/design-decisions.md). The terms I learned along the way are in
[LEARNING.md](LEARNING.md).

## Contributing and license

Wrong number? Use "Report a wrong number" in the app, or
[open an issue](https://github.com/VedantParashar/finance-analyzer/issues/new/choose) with the ticker.
See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and the pull request workflow, and
[CHANGELOG.md](CHANGELOG.md) for what each version added. [MIT](LICENSE) licensed.
