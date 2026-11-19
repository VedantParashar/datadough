# Datadough

**Company financials you can trace back to the filing: every number links to the SEC document it came from.**

I built Datadough for students. It's a free, open-source research app. It reads a company's annual
reports from SEC EDGAR and puts them on one standard set of line items. Then it shows five years of
statements, 19 ratios, red-flag scores and valuation, each explained with the company's own numbers.

[Try the app](https://datadough.streamlit.app){ .md-button .md-button--primary }
[Source on GitHub](https://github.com/VedantParashar/datadough){ .md-button }

![Demo: search for AAPL, open a metric's sources, see the Source column, compare AAPL, KO and NVDA](demo.gif)

## In these docs

- **[Methodology](METHODOLOGY.md):** how each number is chosen from the SEC data, with real examples.
- **[Design decisions](design-decisions.md):** the ten decisions that shape the numbers most, and why.
- **[Accuracy](ACCURACY.md):** 95 figures for 10 companies checked against the filings themselves.
- **[Coverage](COVERAGE.md):** what's found and what's missing for 30 very different companies.
- **[Case study](case-study-apple-vs-coca-cola.md):** Apple vs Coca-Cola, made with the app's numbers.
- **[Python API](python-api.md):** the same numbers as pandas DataFrames, with their source filings.
- **[MCP server](mcp.md):** let Claude Desktop or another AI assistant look up the numbers and cite the filings.

Not investment advice. Figures can contain errors: every one links to its filing so you can check it.
