"""
Blockchain API client.

Provides helper functions to fetch blockchain data from public APIs.
Primary source: Blockstream (https://blockstream.info/api) — no API key required.
Fallback source: Blockchain.info (https://blockchain.info) — aggregated stats.
"""

import requests

BLOCKSTREAM_URL = "https://blockstream.info/api"
BLOCKCHAIN_INFO_URL = "https://blockchain.info"


# ---------------------------------------------------------------------------
# Blockstream API helpers
# ---------------------------------------------------------------------------

def get_tip_hash() -> str:
    """Return the hash of the most recent block (chain tip)."""
    response = requests.get(f"{BLOCKSTREAM_URL}/blocks/tip/hash", timeout=10)
    response.raise_for_status()
    return response.text.strip()


def get_block_blockstream(block_hash: str) -> dict:
    """Return full block data from Blockstream for a given hash."""
    response = requests.get(f"{BLOCKSTREAM_URL}/block/{block_hash}", timeout=10)
    response.raise_for_status()
    return response.json()


def get_recent_blocks(count: int = 10) -> list[dict]:
    """Return the *count* most recent blocks from Blockstream."""
    tip_hash = get_tip_hash()
    response = requests.get(f"{BLOCKSTREAM_URL}/blocks/{tip_hash}", timeout=10)
    response.raise_for_status()
    return response.json()[:count]


# ---------------------------------------------------------------------------
# Blockchain.info API helpers (aggregated stats & difficulty history)
# ---------------------------------------------------------------------------

def get_latest_block() -> dict:
    """Return the latest block summary from Blockchain.info."""
    response = requests.get(f"{BLOCKCHAIN_INFO_URL}/latestblock", timeout=10)
    response.raise_for_status()
    return response.json()


def get_block(block_hash: str) -> dict:
    """Return full details for a block from Blockchain.info."""
    response = requests.get(
        f"{BLOCKCHAIN_INFO_URL}/rawblock/{block_hash}", timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_difficulty_history(n_points: int = 100) -> list[dict]:
    """Return the last *n_points* difficulty values as a list of dicts."""
    response = requests.get(
        f"{BLOCKCHAIN_INFO_URL}/charts/difficulty",
        params={"timespan": "1year", "format": "json", "sampled": "true"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("values", [])[-n_points:]


# ---------------------------------------------------------------------------
# Session 1 - Milestone 2: first API call (~10 lines), prints live block data
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Fetch the latest block from Blockstream (no API key needed)
    tip = get_tip_hash()
    block = get_block_blockstream(tip)

    print(f"Block height   : {block['height']}")
    print(f"Block hash     : {block['id']}")
    # The hash starts with many leading zeros — this is the Proof of Work result.
    # Bitcoin requires SHA256(SHA256(header)) < target. More leading zeros = harder puzzle.
    print(f"Leading zeros  : {len(block['id']) - len(block['id'].lstrip('0'))} hex digits")
    print(f"Nonce          : {block['nonce']}")
    # 'bits' encodes the compact form of the target threshold (see Section 6 of notes).
    # Format: first byte = exponent, next 3 bytes = coefficient → target = coeff * 256^(exp-3)
    print(f"Bits (target)  : {hex(block['bits'])}")
    print(f"Difficulty     : {block['difficulty']:.2e}")
    print(f"Transactions   : {block['tx_count']}")
    print(f"Timestamp      : {block['timestamp']}")
