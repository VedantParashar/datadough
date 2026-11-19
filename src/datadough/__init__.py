"""Datadough: company financials from SEC filings, every number traceable to its filing.

Use it as a library (see docs/python-api.md):

    import datadough as dd
    dd.line_items("AAPL")   # pandas DataFrame, one row per line item and year, with source columns
    dd.metrics("AAPL")      # ratios with formula, inputs and the filings they came from
    dd.red_flags("AAPL")    # Altman Z″, Piotroski F, Beneish M, accruals ratio, with verdicts

or start the web app with `uv run datadough`.
"""

import sys
from pathlib import Path

from datadough.api import Company, get_company, line_items, metrics, red_flags, search

__all__ = ["Company", "get_company", "line_items", "metrics", "red_flags", "search", "main"]


def main() -> None:
    """Start the web app: the same as `streamlit run src/datadough/app.py`."""
    from streamlit.web import cli

    sys.argv = ["streamlit", "run", str(Path(__file__).with_name("app.py")), *sys.argv[1:]]
    sys.exit(cli.main())
