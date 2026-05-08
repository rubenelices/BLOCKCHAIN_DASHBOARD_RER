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


def _normalize_eth_block(raw: dict) -> dict:
    txs = raw.get("transactions", [])
    timestamp = _hex_int(raw.get("timestamp"))
    gas_used = _hex_int(raw.get("gasUsed"))
    gas_limit = _hex_int(raw.get("gasLimit"))
    base_fee_wei = _hex_int(raw.get("baseFeePerGas"))
    if isinstance(txs, list):
        tx_count = len(txs)
    else:
        tx_count = int(txs) if txs else 0
    return {
        "number": _hex_int(raw.get("number")),
        "hash": raw.get("hash", ""),
        "parent_hash": raw.get("parentHash", ""),
        "timestamp": timestamp,
        "datetime": datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else None,
        "gas_used": gas_used,
        "gas_limit": gas_limit,
        "gas_utilization": gas_used / gas_limit if gas_limit else 0.0,
        "base_fee_gwei": base_fee_wei / 1e9,
        "tx_count": tx_count,
        "validator": raw.get("miner", ""),
        "state_root": raw.get("stateRoot", ""),
        "receipts_root": raw.get("receiptsRoot", ""),
        "transactions_root": raw.get("transactionsRoot", ""),
        "raw": raw,
    }


def get_block_by_number(number: int | str = "latest", full_transactions: bool = True) -> dict:
    """Return a normalized Ethereum block by number or "latest"."""
    block_param = number if isinstance(number, str) else hex(number)
    raw = _rpc("eth_getBlockByNumber", [block_param, full_transactions])
    if raw is None:
        raise RuntimeError("Ethereum block not found")
    return _normalize_eth_block(raw)


def get_recent_blocks(count: int = 20) -> list[dict]:
    """Return recent normalized Ethereum blocks in descending order."""
    latest = get_block_by_number("latest", full_transactions=True)
    blocks = [latest]
    for number in range(latest["number"] - 1, latest["number"] - count, -1):
        if number < 0:
            break
        blocks.append(get_block_by_number(number, full_transactions=True))
    return blocks


def get_recent_blocks_batched(count: int = 200, chunk_size: int = 80) -> list[dict]:
    """Return recent Ethereum blocks via JSON-RPC batched requests.

    JSON-RPC supports sending an array of requests and getting an array of
    responses, which collapses N round trips into one. For large counts we
    split into chunks so a single oversized POST does not exceed the public
    node limits.
    """
    if count <= 0:
        return []
    latest = get_block_by_number("latest", full_transactions=False)
    head = latest["number"]
    numbers = [head - i for i in range(count) if head - i >= 0]
    if not numbers:
        return [latest]

    by_number: dict[int, dict] = {}
    for chunk_start in range(0, len(numbers), chunk_size):
        chunk = numbers[chunk_start:chunk_start + chunk_size]
        payload = [
            {
                "jsonrpc": "2.0",
                "id": idx,
                "method": "eth_getBlockByNumber",
                "params": [hex(n), False],
            }
            for idx, n in enumerate(chunk)
        ]
        response = requests.post(ETHEREUM_RPC_URL, json=payload, timeout=30)
        response.raise_for_status()
        results = response.json()
        if not isinstance(results, list):
            raise RuntimeError("Unexpected JSON-RPC batch response shape")
        for item in results:
            if not isinstance(item, dict) or "result" not in item:
                continue
            raw = item["result"]
            if not raw:
                continue
            normalized = _normalize_eth_block(raw)
            by_number[normalized["number"]] = normalized

    return [by_number[n] for n in numbers if n in by_number]
