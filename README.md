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

Requires Python 3.10+ and [`uv`](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/jiroamato/polymarket_mcp.git
cd polymarket_mcp
uv sync
```

## Usage

### Claude Code

The recommended way to add this server to Claude Code:

```bash
claude mcp add polymarket -- uv run --with fastmcp --with httpx fastmcp run src/polymarket_mcp/server.py
```

Or if you've cloned the repo locally:

```bash
claude mcp add polymarket -- uv run --project /path/to/polymarket_mcp fastmcp run src/polymarket_mcp/server.py
```

### Claude Desktop

Add the following to your `claude_desktop_config.json`:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

Restart Claude Desktop after saving.

### Standalone

```bash
uv run fastmcp run src/polymarket_mcp/server.py
```

### Direct Python

```bash
uv run python -m polymarket_mcp.server
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
