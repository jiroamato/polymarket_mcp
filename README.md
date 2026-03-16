# Polymarket MCP Server

An MCP (Model Context Protocol) server that provides tools for querying [Polymarket](https://polymarket.com) prediction market data. Built with [FastMCP](https://gofastmcp.com).

## Tools

| Tool | Description |
|------|-------------|
| `search_markets` | Search markets, events, and profiles by keyword |
| `get_active_markets` | List active markets sorted by volume, liquidity, etc. |
| `get_event` | Get detailed info about a specific event by ID |
| `get_market` | Get detailed info about a specific market by ID |

## Installation

Requires Python 3.10+.

```bash
git clone https://github.com/jiroamato/polymarket_mcp.git
cd polymarket_mcp
pip install -e .
```

## Usage

### Option 1: Direct Python (recommended)

If you already have `fastmcp` and `httpx` installed in your Python environment, you can point directly at the server script.

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

**Claude Desktop** — add to your `claude_desktop_config.json`:

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

> Replace `python` with the full path to your interpreter if needed (e.g., `C:/Users/you/miniforge3/python`).

**Standalone:**

```bash
python src/polymarket_mcp/server.py
```

### Option 2: Using uv (no pre-installed dependencies needed)

[`uv`](https://docs.astral.sh/uv/) handles dependency isolation automatically — no need to install `fastmcp` or `httpx` yourself.

**Claude Code:**

```bash
claude mcp add polymarket -- uv run --with fastmcp --with httpx fastmcp run src/polymarket_mcp/server.py
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

## Example Prompts

Once connected, try asking your AI assistant:

- "What are the top prediction markets on Polymarket right now?"
- "Search Polymarket for markets about AI"
- "Get details on Polymarket event 903"
- "Show me the most liquid crypto prediction markets"

## Development

```bash
# Install dev dependencies
uv sync

# Run the server locally
uv run fastmcp run src/polymarket_mcp/server.py

# Inspect available tools
uv run fastmcp dev src/polymarket_mcp/server.py
```
