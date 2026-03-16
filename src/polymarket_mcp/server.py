import httpx
from fastmcp import FastMCP

GAMMA_API_BASE = "https://gamma-api.polymarket.com"

mcp = FastMCP(
    name="Polymarket MCP Server",
    instructions=(
        "This server provides tools for querying Polymarket prediction markets. "
        "Use it to search markets, browse active markets, and get detailed "
        "information about specific events or markets."
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
    Search Polymarket prediction markets, events, and profiles by keyword.

    - **query**: Free-text search query (e.g., "bitcoin", "election", "AI").
    - **limit**: Maximum number of results per type to return.

    :return: Matching events and markets from Polymarket.
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
    List active (open) prediction markets on Polymarket, sorted by a given field.

    - **limit**: Number of events to return (max ~100).
    - **offset**: Pagination offset.
    - **order**: Field to sort by. Common values: "volume", "liquidity", "start_date", "end_date", "competitive".
    - **ascending**: Sort direction.
    - **tag_slug**: Optional tag slug to filter by category (e.g., "politics", "crypto", "sports").
    - **volume_min**: Optional minimum total volume filter.

    :return: A list of active events with their nested markets.
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
    Get detailed information about a specific Polymarket event by its ID.

    - **event_id**: The event ID (e.g., "903").

    :return: Full event details including all associated markets and their prices.
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
    Get detailed information about a specific Polymarket market by its ID.

    - **market_id**: The market ID (e.g., "12").

    :return: Full market details including current prices, volume, and outcomes.
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
