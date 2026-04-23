import httpx
from fastmcp import FastMCP

GAMMA_API_BASE = "https://gamma-api.polymarket.com"

mcp = FastMCP(
    name="Polymarket MCP Server",
    instructions=(
        "Query live data from Polymarket, a prediction market where users trade "
        "shares on real-world outcomes. This server is read-only.\n\n"

        "DOMAIN MODEL:\n"
        "- An EVENT is a topic that groups one or more related MARKETS "
        "(e.g. event 'Democratic Nominee 2028' groups per-candidate markets).\n"
        "- A MARKET is a single binary question (usually Yes/No) with a share "
        "price in [0, 1] that reflects the crowd-estimated probability.\n\n"

        "PRICE SEMANTICS:\n"
        "- `outcome_prices` and `outcomes` are JSON-encoded strings, not lists. "
        "Parse with json.loads: e.g. '[\"0.0135\", \"0.9865\"]' -> [\"0.0135\", \"0.9865\"].\n"
        "- For binary markets, index 0 is YES, index 1 is NO; values sum to ~1.0.\n"
        "- `outcome_prices` is `null` for untraded markets.\n"
        "- `best_bid`, `best_ask`, `last_trade_price` are probabilities in [0, 1], not dollars.\n\n"

        "UNITS:\n"
        "- `volume`, `volume_24hr`, `liquidity` are USD (float, may be null).\n"
        "- `end_date` is ISO 8601 UTC (e.g. '2026-07-01T04:00:00Z') or null when "
        "sub-markets have staggered dates.\n\n"

        "TYPICAL WORKFLOW:\n"
        "1. Find a market by keyword with `search_markets`, or browse top markets "
        "with `get_active_markets`.\n"
        "2. Use the returned `id` with `get_event` (full event + all sub-markets) or "
        "`get_market` (one market, includes spread + weekly change).\n"
    ),
)


@mcp.tool(
    annotations={"readOnlyHint": True},
)
def search_markets(
    query: str,
    limit: int = 10,
) -> list[dict]:
    """
    Search events and markets by free-text keyword.

    Use this as the primary discovery tool when the user names a topic but not
    an event/market ID. Matches against event titles, market questions, and
    descriptions.

    - **query**: Free-text query. Short topical terms work best ("bitcoin",
      "ukraine", "nba mvp"). Not fuzzy — overly-specific queries may return
      nothing.
    - **limit**: Max results per result type (default 10, typical useful 5-20).

    Returns a list of event dicts with nested markets. Key fields:
    - `id`: event ID for `get_event`.
    - `markets[].id`: market ID for `get_market`.
    - `markets[].outcome_prices`: JSON-encoded probability list (see server
      instructions); can be null for untraded markets.

    Does NOT include `best_bid` / `best_ask` / `last_trade_price` /
    `volume_24hr` / `spread`. Call `get_event` or `get_market` on a result
    `id` for order-book data.
    """
    resp = httpx.get(
        f"{GAMMA_API_BASE}/public-search",
        params={"q": query, "limit_per_type": limit},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    results = []
    for event in data.get("events", []):
        markets = event.get("markets", [])
        results.append(
            {
                "type": "event",
                "id": event.get("id"),
                "title": event.get("title"),
                "slug": event.get("slug"),
                "description": event.get("description"),
                "active": event.get("active"),
                "closed": event.get("closed"),
                "volume": event.get("volume"),
                "liquidity": event.get("liquidity"),
                "end_date": event.get("endDate"),
                "markets": [
                    {
                        "id": m.get("id"),
                        "question": m.get("question"),
                        "outcome_prices": m.get("outcomePrices"),
                        "outcomes": m.get("outcomes"),
                        "volume": m.get("volumeNum"),
                        "liquidity": m.get("liquidityNum"),
                    }
                    for m in markets
                ],
            }
        )

    return results


@mcp.tool(
    annotations={"readOnlyHint": True},
)
def get_active_markets(
    limit: int = 10,
    offset: int = 0,
    order: str = "volume",
    ascending: bool = False,
    tag_slug: str | None = None,
    volume_min: float | None = None,
) -> list[dict]:
    """
    Browse active (open, unresolved) events sorted by a field.

    Use this for discovery when the user asks "what's hot / most liquid /
    expiring soon" without naming a topic. For keyword search, use
    `search_markets`.

    - **limit**: Events to return (default 10, max ~100).
    - **offset**: Pagination offset (default 0). Page by incrementing `offset`
      by `limit`.
    - **order**: Sort field. Supported values:
        - "volume"      — cumulative USD traded (default; "biggest overall")
        - "liquidity"   — USD in the order book now ("where you can trade")
        - "end_date"    — resolution deadline ("expiring soonest")
        - "start_date"  — listing date
        - "competitive" — closest to 50/50 ("most contested"; best-effort
          semantics)
    - **ascending**: False (default) returns largest/latest first.
    - **tag_slug**: Category filter. Known slugs include "politics", "crypto",
      "sports", "elections", "geopolitics". Omit for all categories.
    - **volume_min**: Minimum cumulative USD volume. Useful to exclude
      long-tail markets with near-zero activity.

    Returns a list of event dicts with nested markets. Each event has `id`,
    `end_date`, `volume`, `volume_24hr`, `liquidity`, and `markets[]`. Each
    nested market has `id`, `outcomes`, `outcome_prices`, `best_bid`,
    `best_ask`, `last_trade_price`.

    Does NOT include event-level `active` / `closed` / `category`, or
    market-level `closed` / `liquidity` / `one_day_price_change`. Call
    `get_market` for those.
    """
    params: dict = {
        "active": True,
        "closed": False,
        "limit": limit,
        "offset": offset,
        "order": order,
        "ascending": ascending,
    }
    if tag_slug:
        params["tag_slug"] = tag_slug
    if volume_min is not None:
        params["volume_min"] = volume_min

    resp = httpx.get(
        f"{GAMMA_API_BASE}/events",
        params=params,
        timeout=15,
    )
    resp.raise_for_status()
    events = resp.json()

    return [
        {
            "id": e.get("id"),
            "title": e.get("title"),
            "slug": e.get("slug"),
            "description": e.get("description"),
            "end_date": e.get("endDate"),
            "volume": e.get("volume"),
            "volume_24hr": e.get("volume24hr"),
            "liquidity": e.get("liquidity"),
            "markets": [
                {
                    "id": m.get("id"),
                    "question": m.get("question"),
                    "outcomes": m.get("outcomes"),
                    "outcome_prices": m.get("outcomePrices"),
                    "volume": m.get("volumeNum"),
                    "best_bid": m.get("bestBid"),
                    "best_ask": m.get("bestAsk"),
                    "last_trade_price": m.get("lastTradePrice"),
                }
                for m in e.get("markets", [])
            ],
        }
        for e in events
    ]


@mcp.tool(
    annotations={"readOnlyHint": True},
)
def get_event(event_id: str) -> dict:
    """
    Get one event with all of its nested markets.

    Use when the user cares about a whole topic (all candidates, all strike
    brackets, etc.). For one specific sub-question, use `get_market`.

    - **event_id**: Numeric string ID (e.g. "36173"). Obtain from
      `search_markets` or `get_active_markets` (returned as `id`).

    Returns the event dict with its full `markets[]`. Notable fields:
    - `volume`, `volume_24hr`, `liquidity`: USD floats (may be null).
    - `active`, `closed`: state flags; `closed` = all sub-markets resolved.
    - `end_date`: ISO 8601 UTC; null when sub-markets have staggered dates.
    - `markets[].outcome_prices`: JSON-encoded probability list; null if
      untraded.
    - `markets[].best_bid`, `best_ask`, `last_trade_price`: probabilities in
      [0, 1].
    - `markets[].one_day_price_change`: 24h absolute change in probability
      (float).
    - `markets[].closed`: true once that individual market has resolved.

    Does NOT include per-market `spread`, `one_week_price_change`, or full
    market `description` / `slug`. Use `get_market` for those.
    """
    resp = httpx.get(
        f"{GAMMA_API_BASE}/events/{event_id}",
        timeout=15,
    )
    resp.raise_for_status()
    e = resp.json()

    return {
        "id": e.get("id"),
        "title": e.get("title"),
        "slug": e.get("slug"),
        "description": e.get("description"),
        "active": e.get("active"),
        "closed": e.get("closed"),
        "end_date": e.get("endDate"),
        "volume": e.get("volume"),
        "volume_24hr": e.get("volume24hr"),
        "liquidity": e.get("liquidity"),
        "category": e.get("category"),
        "markets": [
            {
                "id": m.get("id"),
                "question": m.get("question"),
                "outcomes": m.get("outcomes"),
                "outcome_prices": m.get("outcomePrices"),
                "volume": m.get("volumeNum"),
                "liquidity": m.get("liquidityNum"),
                "best_bid": m.get("bestBid"),
                "best_ask": m.get("bestAsk"),
                "last_trade_price": m.get("lastTradePrice"),
                "one_day_price_change": m.get("oneDayPriceChange"),
                "closed": m.get("closed"),
            }
            for m in e.get("markets", [])
        ],
    }


@mcp.tool(
    annotations={"readOnlyHint": True},
)
def get_market(market_id: str) -> dict:
    """
    Get full details for one market, including order-book edges and momentum.

    Use when the user cares about a single specific question (one candidate's
    odds, one strike price). For the whole topic, use `get_event`.

    - **market_id**: Numeric string ID (e.g. "573655"). Obtain from
      `search_markets`, `get_event`, or `get_active_markets` (returned as `id`
      or `markets[].id`).

    Returns a single market dict. Notable fields:
    - `question`: the prediction question itself.
    - `description`: full resolution rules (can be long — tells you how the
      market settles).
    - `outcome_prices`, `outcomes`: JSON-encoded string lists (see server
      instructions).
    - `best_bid`, `best_ask`: order-book edges as probabilities in [0, 1].
    - `spread`: `best_ask` - `best_bid` (narrower = more liquid).
    - `last_trade_price`: most recent fill price (probability).
    - `one_day_price_change`, `one_week_price_change`: absolute change in
      probability.
    - `volume`, `volume_24hr`, `liquidity`: USD floats.
    - `end_date`: ISO 8601 UTC resolution deadline.
    - `active`, `closed`: tradeability + resolution state.
    """
    resp = httpx.get(
        f"{GAMMA_API_BASE}/markets/{market_id}",
        timeout=15,
    )
    resp.raise_for_status()
    m = resp.json()

    return {
        "id": m.get("id"),
        "question": m.get("question"),
        "slug": m.get("slug"),
        "description": m.get("description"),
        "outcomes": m.get("outcomes"),
        "outcome_prices": m.get("outcomePrices"),
        "active": m.get("active"),
        "closed": m.get("closed"),
        "end_date": m.get("endDate"),
        "volume": m.get("volumeNum"),
        "volume_24hr": m.get("volume24hr"),
        "liquidity": m.get("liquidityNum"),
        "best_bid": m.get("bestBid"),
        "best_ask": m.get("bestAsk"),
        "last_trade_price": m.get("lastTradePrice"),
        "spread": m.get("spread"),
        "one_day_price_change": m.get("oneDayPriceChange"),
        "one_week_price_change": m.get("oneWeekPriceChange"),
        "category": m.get("category"),
    }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
