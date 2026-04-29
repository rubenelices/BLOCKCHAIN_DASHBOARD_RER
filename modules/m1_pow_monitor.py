"""M1 - Proof of Work Monitor — core logic."""

import numpy as np
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from api.blockchain_client import get_recent_blocks


def bits_to_target(bits: int) -> int:
    """Convert the compact bits field to a full 256-bit target integer.

    Format: first byte = exponent, next 3 bytes = coefficient.
    Target = coefficient * 256^(exponent - 3)
    """
    exponent = bits >> 24
    coefficient = bits & 0x007FFFFF
    return coefficient * (256 ** (exponent - 3))


def count_leading_zero_bits(hash_hex: str) -> int:
    """Count leading zero bits in a hex hash string (256-bit space)."""
    binary = bin(int(hash_hex, 16))[2:].zfill(256)
    return len(binary) - len(binary.lstrip("0"))


def estimate_hashrate(difficulty: float) -> float:
    """Estimate network hash rate in H/s from difficulty.

    Derivation: difficulty = hashrate * 600 / 2^32
    => hashrate = difficulty * 2^32 / 600
    """
    return difficulty * (2 ** 32) / 600


def get_inter_block_times(blocks: list[dict]) -> list[int]:
    """Return list of inter-arrival times (seconds) from a list of blocks."""
    timestamps = sorted(b["timestamp"] for b in blocks)
    return [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))]


def render() -> None:
    st.header("M1 - Proof of Work Monitor")
    st.info("UI coming soon.")
