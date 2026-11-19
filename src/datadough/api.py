"""Datadough as a Python library: a company's line items, metrics and red-flag scores as pandas DataFrames.

Every figure keeps where it came from: the accession number, form type and filing date of the SEC filing,
and a link to it. The first call for a company downloads its filings from the SEC (set the
`SEC_USER_AGENT` environment variable to your name and email first, as the SEC asks); later calls read
the local cache in `./data`, refreshed by itself once it's 7 days old.

    >>> import datadough as dd
    >>> dd.get_company("AAPL").name
    'Apple Inc.'
    >>> dd.metrics("AAPL").query("metric == 'roe'")[["fiscal_year_end", "value"]].tail(1)
"""

from dataclasses import dataclass
from datetime import date

import pandas as pd

from datadough import display, edgar, parse, store
from datadough.metrics import FORMULA_TEXT, Metric, company_metrics

REIT_SIC = 6798  # funds from operations (FFO) is shown only for real estate investment trusts


@dataclass(frozen=True)
class Company:
    """Who the company is, and which fiscal years are stored for it."""

    ticker: str
    name: str
    cik: str  # the SEC's company number, 10 digits
    sic: int  # SEC industry code, e.g. 3571 for Apple
    industry: str
    exchange: str
    currency: str  # the currency the statements are in, e.g. "USD", "EUR"
    fiscal_year_ends: tuple[date, ...]  # oldest first


def _ticker(text: str) -> str:
    company = edgar.find_ticker(text)  # BRK.B, brk b and BRK-B all find BRK-B
    if company is None:
        raise ValueError(f"No SEC-listed company has the ticker {text.strip().upper()!r}; try search().")
    return company.ticker


def _sources(ticker: str) -> dict[str, tuple[str, str, str]]:
    """Accession number → (form, filing date, URL of the filing on the SEC site)."""
    cik = edgar.get_cik(ticker)
    return {
        accn: (form, filed, edgar.filing_url(cik, accn))
        for accn, (form, filed) in parse.filings(edgar.fetch_company_facts(ticker)).items()
    }


def search(text: str, limit: int = 8) -> pd.DataFrame:
    """Companies whose ticker or name matches the text, largest first: columns ticker, name, cik.

    >>> search("coca")
    """
    return pd.DataFrame([c._asdict() for c in edgar.search_companies(text, limit)], columns=["ticker", "name", "cik"])


def get_company(ticker: str) -> Company:
    """The company's name, SEC codes, reporting currency and stored fiscal years (loading it if needed)."""
    ticker = _ticker(ticker)
    info, rows = edgar.fetch_company_info(ticker), store.current_company(ticker)
    return Company(
        ticker,
        info["name"],
        edgar.get_cik(ticker),
        info["sic"],
        info["industry"],
        info.get("exchange", ""),
        display.currency(rows),
        tuple(sorted({row.fiscal_year_end for row in rows})),
    )


def line_items(ticker: str) -> pd.DataFrame:
    """Every stored line item, one row per item and fiscal year, with the filing it was read from.

    Columns: fiscal_year_end, item, value (in units: dollars, shares or dollars per share), unit,
    derivation (empty if read as reported, else how it was calculated), accession, form, filed, source_url.
    """
    ticker = _ticker(ticker)
    rows, sources = store.current_company(ticker), _sources(ticker)
    return pd.DataFrame(
        [
            {
                "fiscal_year_end": row.fiscal_year_end,
                "item": row.item,
                "value": row.value,
                "unit": row.unit,
                "derivation": row.derivation,
                "accession": row.accn,
                **dict(zip(("form", "filed", "source_url"), sources.get(row.accn, ("", "", "")))),
            }
            for row in rows
        ]
    ).sort_values(["item", "fiscal_year_end"], ignore_index=True)


def _metric_rows(name: str, end: date, metric: Metric, sources: dict) -> dict:
    urls = list(dict.fromkeys(sources[accn][2] for accn in metric.sources.values() if accn in sources))
    return {
        "fiscal_year_end": end,
        "metric": name,
        "label": display.LABELS[name],
        "value": metric.value,
        "formula": FORMULA_TEXT[name],
        "inputs": dict(metric.inputs),
        "reason": metric.reason,
        "notes": "; ".join(metric.notes),
        "source_urls": urls,
    }


def _table(ticker: str, names: list[str], extra=None) -> pd.DataFrame:
    ticker = _ticker(ticker)
    rows, sources = store.current_company(ticker), _sources(ticker)
    by_year = company_metrics(rows)
    table = [
        {**_metric_rows(name, end, year[name], sources), **(extra(name, year[name].value) if extra else {})}
        for end, year in by_year.items()
        for name in names
    ]
    return pd.DataFrame(table).sort_values(["metric", "fiscal_year_end"], ignore_index=True)


def metrics(ticker: str) -> pd.DataFrame:
    """The 19 ratios and the DuPont ROE for every stored fiscal year (FFO too for a REIT).

    Columns: fiscal_year_end, metric, label, value (a fraction: 0.276 = 27.6%; multiples as numbers; free
    cash flow in currency units), formula, inputs (each number used), reason (why value is missing),
    notes, source_urls (the filings the inputs came from). Valuation ratios need today's share price and
    aren't included.
    """
    names = [name for group in display.GROUPS.values() for name in group] + ["dupont"]
    if edgar.fetch_company_info(_ticker(ticker))["sic"] == REIT_SIC:
        names += display.REIT_METRICS
    return _table(ticker, names)


def red_flags(ticker: str) -> pd.DataFrame:
    """Altman Z″, Piotroski F, Beneish M and the accruals ratio for every stored year, with a verdict column.

    Same columns as metrics(), plus verdict ("Safe zone (above 2.6)", "⚠ Flag: above −1.78"…, empty when
    the score can't be calculated).
    """
    return _table(
        ticker,
        display.RED_FLAGS,
        lambda name, value: {"verdict": "" if value is None else display.verdict(name, value)},
    )
