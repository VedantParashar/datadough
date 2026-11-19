# MCP server: Datadough in Claude Desktop

Datadough includes a small [Model Context Protocol](https://modelcontextprotocol.io/) server, so an AI
assistant such as Claude Desktop can look up a company's figures and ratios itself, with the SEC filing
behind every number to cite. It runs on your computer over stdio and is **read-only**: it reads SEC data
(keeping the same local cache in `./data` as the app) and changes nothing anywhere else.

## Tools

| Tool | What it returns |
|---|---|
| `search_companies(query, limit=8)` | SEC-listed companies matching a ticker or name, largest first |
| `company_summary(ticker)` | who the company is, its latest fiscal year's headline figures (revenue, operating and net income, EPS, total assets, operating cash flow) and key ratios, each with its source filing |
| `company_metrics(ticker, fiscal_year=None)` | every ratio and red-flag score for one fiscal year (default: the latest), with formula, inputs, the reason when a value is missing, and the filings the inputs came from |

Ratios are fractions (0.276 = 27.6%). A missing value is `null` with a `reason`; it's never zero.
`fiscal_year` is the calendar year a fiscal year ends in (Apple's FY2026 ends in September 2026).

## Set up in Claude Desktop

1. Install [uv](https://docs.astral.sh/uv/) and clone this repository:

   ```bash
   git clone https://github.com/VedantParashar/datadough.git
   ```

2. Find two paths: the folder you cloned into (e.g. `/Users/you/datadough`) and uv itself
   (`which uv` on macOS and Linux, `where uv` on Windows). Claude Desktop doesn't always see your
   shell's `PATH`, so the full path to uv is the safe choice.

3. Open Claude Desktop → **Settings → Developer → Edit Config**. That opens
   `claude_desktop_config.json` (on macOS in `~/Library/Application Support/Claude/`, on Windows in
   `%APPDATA%\Claude\`). Add:

   ```json
   {
     "mcpServers": {
       "datadough": {
         "command": "/Users/you/.local/bin/uv",
         "args": ["--directory", "/Users/you/datadough", "run", "--extra", "mcp", "datadough-mcp"],
         "env": {"SEC_USER_AGENT": "Your Name you@example.com"}
       }
     }
   }
   ```

   `--directory` matters: the cache goes in `data/` inside that folder. `SEC_USER_AGENT` is your name and
   email, which the SEC asks every program to send.

4. Quit and reopen Claude Desktop. "datadough" appears under the tools (🔨) icon. Try:
   *"Using datadough, compare Apple's and Coca-Cola's net margins for their latest fiscal years and cite
   the filings."*

The first question about a company takes a few seconds while its filings download.

## Other clients

Any MCP client that can start a stdio server works with the same command:

```bash
SEC_USER_AGENT="Your Name you@example.com" uv run --extra mcp datadough-mcp
```

Once the package is on PyPI: `pip install "datadough[mcp]"`, then the command is just `datadough-mcp`
(run it from the folder where the cache should live).

## Good to know

- The numbers are the app's, chosen by the rules in [METHODOLOGY.md](METHODOLOGY.md). Valuation ratios
  (P/E and so on) aren't included, because they need a live share price.
- Errors come back as plain messages the assistant can pass on: an unknown ticker, a fund with no
  financial statements, a fiscal year that isn't stored, or the SEC being unreachable.
- Not investment advice.
