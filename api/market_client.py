"""Market price helpers for the dashboard ticker bar."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import requests

BINANCE_24H_TICKER_URL = "https://api.binance.com/api/v3/ticker/24hr"
COINGECKO_SIMPLE_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price"

MARKET_ASSETS = {
    "bitcoin": {"ticker": "BTC", "name": "Bitcoin", "binance_symbol": "BTCUSDT"},
    "ethereum": {"ticker": "ETH", "name": "Ethereum", "binance_symbol": "ETHUSDT"},
    "litecoin": {"ticker": "LTC", "name": "Litecoin", "binance_symbol": "LTCUSDT"},
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S UTC")


def _get_binance_prices() -> list[dict]:
    symbols = [meta["binance_symbol"] for meta in MARKET_ASSETS.values()]
    response = requests.get(
        BINANCE_24H_TICKER_URL,
        params={"symbols": json.dumps(symbols, separators=(",", ":"))},
        timeout=8,
    )
    response.raise_for_status()
    payload = response.json()
    by_symbol = {item["symbol"]: item for item in payload}

    rows = []
    for asset_id, meta in MARKET_ASSETS.items():
        item = by_symbol.get(meta["binance_symbol"], {})
        rows.append({
            "id": asset_id,
            "name": meta["name"],
            "ticker": meta["ticker"],
            "price_usd": float(item.get("lastPrice", 0.0) or 0.0),
            "change_24h": float(item.get("priceChangePercent", 0.0) or 0.0),
            "source": "Binance",
            "updated_at": _now_utc(),
        })
    return rows


def _get_coingecko_prices() -> list[dict]:
    response = requests.get(
        COINGECKO_SIMPLE_PRICE_URL,
        params={
            "ids": ",".join(MARKET_ASSETS),
            "vs_currencies": "usd",
            "include_24hr_change": "true",
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    rows = []
    for asset_id, meta in MARKET_ASSETS.items():
        item = payload.get(asset_id, {})
        rows.append({
            "id": asset_id,
            "name": meta["name"],
            "ticker": meta["ticker"],
            "price_usd": float(item.get("usd", 0.0) or 0.0),
            "change_24h": float(item.get("usd_24h_change", 0.0) or 0.0),
            "source": "CoinGecko",
            "updated_at": _now_utc(),
        })
    return rows


def get_market_prices() -> list[dict]:
    """Return USD price and 24h change for BTC, ETH and LTC."""
    try:
        return _get_binance_prices()
    except requests.RequestException:
        return _get_coingecko_prices()
