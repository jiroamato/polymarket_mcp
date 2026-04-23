# Polymarket MCP Server

An MCP (Model Context Protocol) server that exposes read-only tools for querying live [Polymarket](https://polymarket.com) prediction-market data via the public [Gamma API](https://gamma-api.polymarket.com). Built with [FastMCP](https://gofastmcp.com).

No API key required — the Gamma API is public and unauthenticated.

## Tools

All tools are read-only (`readOnlyHint: true`).

| Tool | Params | Purpose |
|------|--------|---------|
| `search_markets` | `query`, `limit=10` | Free-text search across event titles, market questions, and descriptions. Primary discovery tool when the user names a topic but not an ID. |
| `get_active_markets` | `limit=10`, `offset=0`, `order="volume"`, `ascending=False`, `tag_slug=None`, `volume_min=None` | Browse open, unresolved events sorted by a field. Use for "what's hot / most liquid / expiring soon". |
| `get_event` | `event_id` | Full detail for one event and all of its nested markets. Use when the user cares about a whole topic (all candidates, all strike brackets). |
| `get_market` | `market_id` | Full detail for a single market, including order-book edges (`best_bid`, `best_ask`, `spread`), `last_trade_price`, and 1d / 1w price change. |

### `get_active_markets` sort keys

| `order` | Meaning |
|---------|---------|
| `volume` (default) | Cumulative USD traded — "biggest overall" |
| `liquidity` | USD currently in the order book — "where you can trade now" |
| `end_date` | Resolution deadline — "expiring soonest" |
| `start_date` | Listing date |
| `competitive` | Closest to 50/50 — "most contested" (best-effort) |

Known `tag_slug` values: `politics`, `crypto`, `sports`, `elections`, `geopolitics`. Omit for all categories.

### Field coverage at a glance

Fields that require drilling down — `search_markets` returns less than the list/detail tools, and `get_event` returns less per-market than `get_market`:

| Field | `search_markets` | `get_active_markets` | `get_event` | `get_market` |
|-------|:---:|:---:|:---:|:---:|
| `best_bid` / `best_ask` / `last_trade_price` | ❌ | ✅ | ✅ | ✅ |
| `volume_24hr` | ❌ | ✅ (event-level) | ✅ (event-level) | ✅ |
| `one_day_price_change` | ❌ | ❌ | ✅ | ✅ |
| `spread`, `one_week_price_change` | ❌ | ❌ | ❌ | ✅ |
| Full market `description` / resolution rules | ❌ | ❌ | ❌ | ✅ |

## Domain model & data conventions

The server sends these conventions to clients on connect as part of its `instructions`, but they're worth knowing upfront:

- **Event vs. market.** An **event** is a topic that groups one or more related **markets** (e.g. event `Democratic Nominee 2028` groups per-candidate markets). A **market** is a single binary question with a share price in `[0, 1]` that reflects the crowd-estimated probability.
- **`outcome_prices` and `outcomes` are JSON-encoded strings, not lists.** Parse with `json.loads`, e.g. `'["0.0135", "0.9865"]'` → `["0.0135", "0.9865"]`. For binary markets, index 0 is **YES**, index 1 is **NO**, and values sum to ~1.0. `outcome_prices` is `null` for untraded markets.
- **Prices are probabilities, not dollars.** `best_bid`, `best_ask`, `last_trade_price`, and the parsed entries of `outcome_prices` are all in `[0, 1]`.
- **USD units.** `volume`, `volume_24hr`, `liquidity` are USD (float, may be `null`).
- **Dates.** `end_date` is ISO 8601 UTC (e.g. `"2026-07-01T04:00:00Z"`) or `null` when an event's sub-markets have staggered dates.

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| [fastmcp](https://gofastmcp.com) | `>=2.0.0` | MCP server framework |
| [httpx](https://www.python-httpx.org) | `>=0.27.0` | HTTP client for the Polymarket Gamma API |

## Installation

Requires Python 3.10+.

### With uv (recommended)

```bash
git clone https://github.com/jiroamato/polymarket_mcp.git
cd polymarket_mcp
uv sync
```

`uv sync` reads `pyproject.toml` and installs all dependencies into an isolated virtual environment automatically.

### With pip

```bash
git clone https://github.com/jiroamato/polymarket_mcp.git
cd polymarket_mcp
pip install -e .
```

Installing the package also registers a `polymarket-mcp` console script (see `pyproject.toml`) that you can use as the `command` in any MCP client config.

## Usage

There are three ways to wire this server into an MCP client, in increasing order of "how much JSON you touch".

### Option A — FastMCP CLI install (easiest)

FastMCP ships install commands that write the client config for you.

**Claude Code:**

```bash
fastmcp install claude-code src/polymarket_mcp/server.py
```

**Claude Desktop:**

```bash
fastmcp install claude-desktop src/polymarket_mcp/server.py --server-name "Polymarket"
```

Useful flags: `--python 3.11`, `--project /path/to/polymarket_mcp`, `--with httpx`, `--env KEY=VALUE`, `--env-file .env`. See `fastmcp install --help` for the full list.

### Option B — Direct Python

If you've already installed dependencies into a Python environment (via `uv sync` or `pip install -e .`), point the client directly at that interpreter.

**Claude Code** — add to your `.claude.json`:

```json
{
  "mcpServers": {
    "polymarket": {
      "command": "/path/to/python",
      "args": [
        "/absolute/path/to/polymarket_mcp/src/polymarket_mcp/server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Claude Desktop** — add to `claude_desktop_config.json`:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "polymarket": {
      "command": "/path/to/python",
      "args": [
        "/absolute/path/to/polymarket_mcp/src/polymarket_mcp/server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

Replace `/path/to/python` with the full path to your interpreter (e.g., `C:/Users/you/miniforge3/python.exe`, `/Users/you/.venv/bin/python`).

If you ran `pip install -e .`, you can instead use the installed console script:

```json
{
  "mcpServers": {
    "polymarket": {
      "command": "/path/to/polymarket-mcp"
    }
  }
}
```

**Standalone:**

```bash
python src/polymarket_mcp/server.py
# or, after `pip install -e .`:
polymarket-mcp
```

### Option C — `uv run` (no pre-installed deps)

[`uv`](https://docs.astral.sh/uv/) handles dependency isolation automatically — no need to install `fastmcp` or `httpx` yourself.

**Claude Code:**

```bash
claude mcp add polymarket -- uv run --with fastmcp --with httpx fastmcp run src/polymarket_mcp/server.py
```

Or add to your `.claude.json`:

```json
{
  "mcpServers": {
    "polymarket": {
      "command": "uv",
      "args": [
        "run",
        "--with", "fastmcp",
        "--with", "httpx",
        "fastmcp",
        "run",
        "/absolute/path/to/polymarket_mcp/src/polymarket_mcp/server.py"
      ]
    }
  }
}
```

**Claude Desktop** — add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "polymarket": {
      "command": "uv",
      "args": [
        "run",
        "--with", "fastmcp",
        "--with", "httpx",
        "fastmcp",
        "run",
        "/absolute/path/to/polymarket_mcp/src/polymarket_mcp/server.py"
      ]
    }
  }
}
```

**Standalone:**

```bash
uv run fastmcp run src/polymarket_mcp/server.py
```

## Example prompts

Once connected, try asking your AI assistant:

- "What are the top prediction markets on Polymarket right now?"
- "Search Polymarket for markets about AI."
- "Show me the most liquid crypto prediction markets."
- "Which politics markets on Polymarket are expiring soonest?"
- "Get details on Polymarket event 903 and summarize the candidates."
- "For Polymarket market 573655, what's the current spread and 1-day price change?"

## Development

```bash
# Install dependencies
uv sync

# Run the server locally
uv run fastmcp run src/polymarket_mcp/server.py

# Inspect tools interactively with the MCP Inspector (browser UI)
uv run fastmcp dev inspector src/polymarket_mcp/server.py
```

The server itself lives in a single file: `src/polymarket_mcp/server.py`. Each tool is a plain function decorated with `@mcp.tool(annotations={"readOnlyHint": True})`; FastMCP generates the JSON schema from the type hints and docstring automatically.
