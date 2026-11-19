"""The Python API, on the same offline test data as the app tests."""

from datetime import date, datetime

import pandas as pd
import pytest
from test_app import COMPANIES, INFO, parsed_rows

import finance_analyzer as dd
from finance_analyzer import edgar, store

URL = "https://www.sec.gov/Archives/edgar/data/1/accn/accn-index.htm"  # AAPL's CIK is 1 in the test list


@pytest.fixture(autouse=True)
def offline(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "test.duckdb")
    monkeypatch.setattr(store, "annual_line_items", parsed_rows)
    monkeypatch.setattr(store, "company_currency", lambda ticker: "USD")
    monkeypatch.setattr(store, "company_is_financial", lambda ticker: False)
    monkeypatch.setattr(edgar, "facts_downloaded_at", lambda ticker: datetime(2020, 1, 1))
    monkeypatch.setattr(
        edgar, "fetch_company_info", lambda ticker: {**INFO.get(ticker, INFO["AAPL"]), "exchange": "Nasdaq"}
    )
    monkeypatch.setattr(edgar, "list_companies", lambda: COMPANIES)
    revenue = {
        "units": {"USD": [{"accn": "accn", "form": "10-K", "filed": "2026-10-31", "val": 1, "end": "2026-09-26"}]}
    }
    monkeypatch.setattr(edgar, "fetch_company_facts", lambda ticker: {"facts": {"us-gaap": {"Revenues": revenue}}})


def test_get_company_describes_it_and_its_stored_years():
    company = dd.get_company("aapl")
    assert (company.ticker, company.name, company.cik, company.sic, company.exchange, company.currency) == (
        "AAPL",
        "Apple Inc.",
        "0000000001",
        3571,
        "Nasdaq",
        "USD",
    )
    assert company.fiscal_year_ends[-1] == date(2026, 9, 26) and len(company.fiscal_year_ends) == 4


def test_line_items_carry_the_filing_they_were_read_from():
    items = dd.line_items("AAPL")
    assert list(items.columns) == [
        "fiscal_year_end",
        "item",
        "value",
        "unit",
        "derivation",
        "accession",
        "form",
        "filed",
        "source_url",
    ]
    revenue = items[(items["item"] == "revenue") & (items["fiscal_year_end"] == date(2026, 9, 26))].iloc[0]
    assert (revenue["value"], revenue["form"], revenue["filed"], revenue["source_url"]) == (
        478_834_000_000,
        "10-K",
        "2026-10-31",
        URL,
    )


def test_metrics_have_formula_inputs_reasons_and_sources():
    table = dd.metrics("AAPL")
    assert set(table["metric"]) == {n for group in dd.api.display.GROUPS.values() for n in group} | {"dupont"}
    net_margin = table[(table["metric"] == "net_margin") & (table["fiscal_year_end"] == date(2026, 9, 26))].iloc[0]
    assert round(net_margin["value"], 3) == 0.276 and net_margin["formula"] == "net income ÷ revenue"
    assert net_margin["inputs"]["revenue"] == 478_834_000_000 and net_margin["source_urls"] == [URL]
    coverage = table[(table["metric"] == "interest_coverage") & (table["fiscal_year_end"] == date(2026, 9, 26))].iloc[0]
    assert pd.isna(coverage["value"])
    assert coverage["reason"] == "interest_expense not reported for FY2026"


def test_red_flags_add_a_verdict():
    flags = dd.red_flags("AAPL")
    latest = flags[flags["fiscal_year_end"] == date(2026, 9, 26)].set_index("metric")
    assert latest.loc["accruals_ratio", "verdict"] == "No flag (10% or below)"
    assert latest.loc["altman_z", "verdict"] == ""  # the test data has no retained earnings


def test_search_and_unknown_tickers():
    assert dd.search("goldman")["ticker"].tolist() == ["GS"]
    with pytest.raises(ValueError, match="No SEC-listed company has the ticker 'NOPE'"):
        dd.line_items("nope")
