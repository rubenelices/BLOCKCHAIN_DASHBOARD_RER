"""Litecoin API helpers.

Uses BlockCypher public Litecoin endpoints. The free public endpoint is enough
for classroom-scale dashboard polling, but may be rate limited.
"""

from __future__ import annotations

from datetime import datetime, timezone

import requests
from requests import HTTPError

BLOCKCYPHER_LTC_URL = "https://api.blockcypher.com/v1/ltc/main"
BLOCKCHAIR_LTC_URL = "https://api.blockchair.com/litecoin"
LITECOIN_MAX_TARGET = 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF


def _parse_time(value: str) -> int:
    clean = value.replace("Z", "+00:00")
    return int(datetime.fromisoformat(clean).timestamp())


def _compact_to_target(bits: int) -> int:
    exponent = bits >> 24
    coefficient = bits & 0x007FFFFF
    return coefficient * (256 ** (exponent - 3))


def _normalize_block(raw: dict) -> dict:
    bits_value = raw.get("bits", 0)
    bits = int(bits_value, 16) if isinstance(bits_value, str) else int(bits_value or 0)
    target = _compact_to_target(bits) if bits else 0
    raw_difficulty = raw.get("difficulty")
    difficulty = (
        float(raw_difficulty)
        if raw_difficulty not in (None, "")
        else (LITECOIN_MAX_TARGET / target if target else 0.0)
    )
    timestamp = _parse_time(raw["time"]) if raw.get("time") else 0
    return {
        "id": raw.get("hash", ""),
        "height": int(raw.get("height", 0)),
        "timestamp": timestamp,
        "datetime": datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else None,
        "difficulty": float(difficulty),
        "bits": bits,
        "nonce": int(raw.get("nonce", 0) or 0),
        "tx_count": int(raw.get("n_tx", 0) or 0),
        "size": int(raw.get("size", 0) or 0),
        "version": int(raw.get("ver", 0) or 0),
        "previous_hash": raw.get("prev_block", ""),
        "merkle_root": raw.get("mrkl_root", ""),
        "raw": raw,
    }


def _normalize_blockchair_block(raw: dict) -> dict:
    timestamp = _parse_time(raw["time"]) if raw.get("time") else 0
    bits = int(raw.get("bits", 0) or 0)
    return {
        "id": raw.get("hash", ""),
        "height": int(raw.get("id", 0)),
        "timestamp": timestamp,
        "datetime": datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else None,
        "difficulty": float(raw.get("difficulty", 0.0) or 0.0),
        "bits": bits,
        "nonce": int(raw.get("nonce", 0) or 0),
        "tx_count": int(raw.get("transaction_count", 0) or 0),
        "size": int(raw.get("size", 0) or 0),
        "version": int(raw.get("version", 0) or 0),
        "previous_hash": raw.get("previous_hash", ""),
        "merkle_root": raw.get("merkle_root", ""),
        "fee_total": int(raw.get("fee_total", 0) or 0),
        "reward": int(raw.get("reward", 0) or 0),
        "source": "Blockchair",
        "raw": raw,
    }


def get_recent_blocks_blockchair(count: int = 7) -> list[dict]:
    """Return recent Litecoin blocks from Blockchair in descending order."""
    count = max(1, min(count, 20))
    response = requests.get(
        f"{BLOCKCHAIR_LTC_URL}/blocks",
        params={"limit": count},
        timeout=12,
    )
    response.raise_for_status()
    data = response.json().get("data", [])
    return [_normalize_blockchair_block(item) for item in data]


def get_chain_info() -> dict:
    """Return Litecoin chain summary."""
    response = requests.get(BLOCKCYPHER_LTC_URL, timeout=12)
    response.raise_for_status()
    return response.json()


def get_block(block_hash: str) -> dict:
    """Return a normalized Litecoin block by hash."""
    response = requests.get(f"{BLOCKCYPHER_LTC_URL}/blocks/{block_hash}", timeout=12)
    response.raise_for_status()
    return _normalize_block(response.json())


def get_latest_block() -> dict:
    """Return the latest normalized Litecoin block."""
    blocks = get_recent_blocks_blockchair(1)
    if blocks:
        return blocks[0]
    chain = get_chain_info()
    return get_block(chain["hash"])


def get_recent_blocks(count: int = 20) -> list[dict]:
    """Return recent normalized Litecoin blocks in descending order."""
    count = max(1, min(count, 20))
    try:
        blocks = get_recent_blocks_blockchair(count)
        if blocks:
            return blocks
    except requests.RequestException:
        pass

    count = min(count, 7)
    blocks = []
    current = get_latest_block()
    while current and len(blocks) < count:
        blocks.append(current)
        previous_hash = current.get("previous_hash")
        if not previous_hash:
            break
        try:
            current = get_block(previous_hash)
        except HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 429 and blocks:
                break
            raise
    return blocks


def get_recent_blocks_paginated(count: int = 200) -> list[dict]:
    """Fetch up to ``count`` recent Litecoin blocks via Blockchair pagination.

    Blockchair allows up to 100 blocks per request. We page backwards from the
    tip until we have enough rows. Used by M4/M7 LTC, where bulk timing data
    is needed for proper distribution analysis.
    """
    if count <= 0:
        return []
    page_size = 100
    blocks: list[dict] = []
    offset = 0
    while len(blocks) < count:
        n = min(page_size, count - len(blocks))
        response = requests.get(
            f"{BLOCKCHAIR_LTC_URL}/blocks",
            params={"limit": n, "offset": offset},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json().get("data", [])
        if not data:
            break
        blocks.extend(_normalize_blockchair_block(item) for item in data)
        offset += len(data)
        if len(data) < n:
            break
    return blocks


def fetch_ltc_adjustment_blocks(n_periods: int = 24) -> list[dict]:
    """Fetch Litecoin blocks at every difficulty-adjustment height.

    Litecoin retargets every 2016 blocks just like Bitcoin. This walks
    backwards from the latest adjustment boundary and returns the minimal
    fields M3/M7 need: height, timestamp, difficulty, bits.
    """
    if n_periods <= 0:
        return []

    stats_resp = requests.get(f"{BLOCKCHAIR_LTC_URL}/stats", timeout=12)
    stats_resp.raise_for_status()
    stats_data = stats_resp.json().get("data", {})
    tip_height = int(stats_data.get("blocks", 0)) - 1
    if tip_height <= 0:
        return []
    latest_adj = (tip_height // 2016) * 2016

    blocks: list[dict] = []
    for i in range(n_periods):
        height = latest_adj - i * 2016
        if height < 0:
            break
        try:
            r = requests.get(
                f"{BLOCKCHAIR_LTC_URL}/dashboards/block/{height}",
                timeout=15,
            )
            r.raise_for_status()
            payload = r.json().get("data", {})
            entry = payload.get(str(height)) or next(iter(payload.values()), None) or {}
            block = entry.get("block") if isinstance(entry, dict) else None
            if not block:
                continue
            timestamp = _parse_time(block["time"]) if block.get("time") else 0
            difficulty = float(block.get("difficulty", 0.0) or 0.0)
            bits_raw = block.get("bits", 0)
            bits = int(bits_raw, 16) if isinstance(bits_raw, str) else int(bits_raw or 0)
            blocks.append({
                "height": height,
                "timestamp": timestamp,
                "difficulty": difficulty,
                "bits": bits,
            })
        except (requests.RequestException, ValueError, KeyError):
            continue

    blocks.sort(key=lambda b: b["height"])
    return blocks
