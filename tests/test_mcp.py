"""The MCP server's tools, on the same offline test data as the API tests."""

import asyncio
import json

import pytest

pytest.importorskip("mcp")  # an optional extra

from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402
from test_api import URL, offline  # noqa: E402, F401  (offline is an autouse fixture)

from finance_analyzer import mcp_server  # noqa: E402


def test_the_server_offers_three_read_only_tools():
    tools = asyncio.run(mcp_server.server.list_tools())
    assert sorted(tool.name for tool in tools) == ["company_metrics", "company_summary", "search_companies"]
    assert all(tool.annotations.read_only_hint and not tool.annotations.destructive_hint for tool in tools)


def test_search_companies():
    assert mcp_server.search_companies("goldman") == [
        {"ticker": "GS", "name": "Goldman Sachs Group Inc", "cik": "0000000003"}
    ]


def test_company_summary_has_headline_figures_and_ratios_with_sources():
    summary = mcp_server.company_summary("aapl")
    assert (summary["ticker"], summary["latest_fiscal_year_end"], summary["currency"]) == ("AAPL", "2026-09-26", "USD")
    revenue = next(row for row in summary["headline_figures"] if row["item"] == "revenue")
    assert (revenue["value"], revenue["form"], revenue["source_url"]) == (478_834_000_000, "10-K", URL)
    net_margin = next(row for row in summary["key_ratios"] if row["metric"] == "net_margin")
    assert round(net_margin["value"], 3) == 0.276 and net_margin["source_urls"] == [URL]
    json.dumps(summary)  # plain JSON: no dates, no NaN


def test_company_metrics_for_a_year_with_reasons_and_red_flags():
    result = mcp_server.company_metrics("AAPL", 2026)
    by_name = {row["metric"]: row for row in result["metrics"]}
    coverage = by_name["interest_coverage"]
    assert coverage["value"] is None and coverage["reason"] == "interest_expense not reported for FY2026"
    assert by_name["net_margin"]["formula"] == "net income ÷ revenue"
    flags = {row["metric"]: row["verdict"] for row in result["red_flags"]}
    assert flags["accruals_ratio"] == "No flag (10% or below)"
    json.dumps(result)


def test_errors_come_back_as_messages_the_assistant_can_pass_on():
    with pytest.raises(ToolError, match="No SEC-listed company has the ticker 'NOPE'"):
        mcp_server.company_summary("nope")
    with pytest.raises(ToolError, match="AAPL has no fiscal year ending in 1990"):
        mcp_server.company_metrics("AAPL", 1990)


def test_a_call_through_the_protocol_returns_structured_content():
    result = asyncio.run(mcp_server.server.call_tool("search_companies", {"query": "goldman"}))
    assert not result.is_error and "GS" in json.dumps(result.structured_content)
    summary = asyncio.run(mcp_server.server.call_tool("company_summary", {"ticker": "AAPL"}))
    assert summary.structured_content["ticker"] == "AAPL"  # structured, not only text
