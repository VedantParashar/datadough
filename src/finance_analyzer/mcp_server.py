"""An MCP server (stdio) that lets an AI assistant look up Datadough's numbers, read-only. See docs/mcp.md.

Three tools: search_companies, company_summary and company_metrics. Every figure they return carries the
SEC filing it was read from. They read SEC data (and keep a local cache in ./data, like the app) and
change nothing anywhere else. Needs the `mcp` extra: pip install "datadough[mcp]".

Run: SEC_USER_AGENT="Your Name you@example.com" uv run --extra mcp datadough-mcp
"""

import math
from datetime import date
from typing import Any

import httpx
import pandas as pd

from finance_analyzer import api

try:
    from mcp.server.mcpserver import MCPServer
    from mcp.server.mcpserver.exceptions import ToolError
    from mcp.types import ToolAnnotations
except ImportError as error:  # the library and the app don't need it
    raise ImportError('The MCP server needs the "mcp" extra: pip install "datadough[mcp]"') from error

# Reads only; "open world" because it fetches from the SEC, whose data changes when companies file.
READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=True)
HEADLINE_ITEMS = ["revenue", "operating_income", "net_income", "diluted_eps", "total_assets", "operating_cash_flow"]
KEY_RATIOS = ["gross_margin", "operating_margin", "net_margin", "roe", "roic", "current_ratio", "debt_to_equity"]

server = MCPServer(
    name="datadough",
    instructions=(
        "Company financials from SEC filings (US companies and foreign filers listed in the US). Every number "
        "comes with the filing it was read from: cite those links. Ratios are fractions (0.276 = 27.6%). A null "
        "value comes with a reason; never treat it as zero. Not investment advice."
    ),
)


def _clean(value: Any) -> Any:
    """JSON-ready: dates as ISO text, NaN as null, lists and dicts cleaned all the way down."""
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, dict):
        return {key: _clean(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_clean(item) for item in value]
    return value


def _records(frame: pd.DataFrame) -> list[dict]:
    return [_clean(row) for row in frame.astype(object).to_dict("records")]


def _guard(ticker: str) -> api.Company:
    """The company, or a ToolError whose message the assistant can pass on (as the app's messages do)."""
    try:
        return api.get_company(ticker)
    except (ValueError, RuntimeError) as error:  # unknown ticker, fund, no annual report, no SEC_USER_AGENT
        raise ToolError(str(error)) from error
    except httpx.HTTPError as error:
        raise ToolError(f"Couldn't reach the SEC ({error}). Try again later.") from error


@server.tool(annotations=READ_ONLY)
def search_companies(query: str, limit: int = 8) -> list[dict]:
    """Find SEC-listed companies by ticker or name (e.g. "coca", "AAPL"), largest first."""
    return _records(api.search(query, max(1, min(limit, 25))))


@server.tool(annotations=READ_ONLY)
def company_summary(ticker: str) -> dict[str, Any]:
    """Who the company is, its latest fiscal year's headline figures and key ratios, each with its source filing."""
    company = _guard(ticker)
    latest = company.fiscal_year_ends[-1]
    items = api.line_items(company.ticker)
    items = items[(items["fiscal_year_end"] == latest) & items["item"].isin(HEADLINE_ITEMS)]
    ratios = api.metrics(company.ticker)
    ratios = ratios[(ratios["fiscal_year_end"] == latest) & ratios["metric"].isin(KEY_RATIOS)]
    return _clean(
        {
            "ticker": company.ticker,
            "name": company.name,
            "cik": company.cik,
            "industry": company.industry,
            "sic": company.sic,
            "exchange": company.exchange,
            "currency": company.currency,
            "fiscal_years_stored": [company.fiscal_year_ends[0], latest],
            "latest_fiscal_year_end": latest,
            "headline_figures": _records(items[["item", "value", "unit", "derivation", "form", "filed", "source_url"]]),
            "key_ratios": _records(ratios[["metric", "label", "value", "reason", "source_urls"]]),
        }
    )


@server.tool(annotations=READ_ONLY)
def company_metrics(ticker: str, fiscal_year: int | None = None) -> dict[str, Any]:
    """Every ratio and red-flag score for one fiscal year (default: the latest), with formula, inputs,
    the reason when a value is missing, and the filings the inputs came from. fiscal_year is the calendar
    year the fiscal year ends in (Apple's FY2026 ends in September 2026)."""
    company = _guard(ticker)
    ends = {end.year: end for end in company.fiscal_year_ends}
    if fiscal_year is not None and fiscal_year not in ends:
        raise ToolError(
            f"{company.ticker} has no fiscal year ending in {fiscal_year}; stored: {min(ends)}–{max(ends)}."
        )
    end = ends[fiscal_year] if fiscal_year else company.fiscal_year_ends[-1]
    columns = ["metric", "label", "value", "formula", "inputs", "reason", "notes", "source_urls"]
    ratios, flags = api.metrics(company.ticker), api.red_flags(company.ticker)
    return _clean(
        {
            "ticker": company.ticker,
            "name": company.name,
            "currency": company.currency,
            "fiscal_year_end": end,
            "metrics": _records(ratios[ratios["fiscal_year_end"] == end][columns]),
            "red_flags": _records(flags[flags["fiscal_year_end"] == end][[*columns, "verdict"]]),
        }
    )


def main() -> None:
    """Entry point for the `datadough-mcp` command: serve over stdio for Claude Desktop and other clients."""
    server.run("stdio")
