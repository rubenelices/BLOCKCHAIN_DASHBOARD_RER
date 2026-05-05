"""Ethereum JSON-RPC helpers for post-Merge network activity."""

from __future__ import annotations

from datetime import datetime, timezone

import requests

ETHEREUM_RPC_URL = "https://ethereum.publicnode.com"


def _rpc(method: str, params: list) -> dict:
    response = requests.post(
        ETHEREUM_RPC_URL,
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        timeout=12,
    )
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(payload["error"].get("message", "Ethereum RPC error"))
    return payload["result"]


def _hex_int(value: str | None) -> int:
    if not value:
        return 0
    return int(value, 16)


def get_block_by_number(number: int | str = "latest", full_transactions: bool = True) -> dict:
    """Return a normalized Ethereum block by number or "latest"."""
    block_param = number if isinstance(number, str) else hex(number)
    raw = _rpc("eth_getBlockByNumber", [block_param, full_transactions])
    if raw is None:
        raise RuntimeError("Ethereum block not found")
    txs = raw.get("transactions", [])
    timestamp = _hex_int(raw.get("timestamp"))
    gas_used = _hex_int(raw.get("gasUsed"))
    gas_limit = _hex_int(raw.get("gasLimit"))
    base_fee_wei = _hex_int(raw.get("baseFeePerGas"))
    return {
        "number": _hex_int(raw.get("number")),
        "hash": raw.get("hash", ""),
        "parent_hash": raw.get("parentHash", ""),
        "timestamp": timestamp,
        "datetime": datetime.fromtimestamp(timestamp, tz=timezone.utc),
        "gas_used": gas_used,
        "gas_limit": gas_limit,
        "gas_utilization": gas_used / gas_limit if gas_limit else 0.0,
        "base_fee_gwei": base_fee_wei / 1e9,
        "tx_count": len(txs),
        "validator": raw.get("miner", ""),
        "state_root": raw.get("stateRoot", ""),
        "receipts_root": raw.get("receiptsRoot", ""),
        "transactions_root": raw.get("transactionsRoot", ""),
        "raw": raw,
    }


def get_recent_blocks(count: int = 20) -> list[dict]:
    """Return recent normalized Ethereum blocks in descending order."""
    latest = get_block_by_number("latest", full_transactions=True)
    blocks = [latest]
    for number in range(latest["number"] - 1, latest["number"] - count, -1):
        if number < 0:
            break
        blocks.append(get_block_by_number(number, full_transactions=True))
    return blocks
