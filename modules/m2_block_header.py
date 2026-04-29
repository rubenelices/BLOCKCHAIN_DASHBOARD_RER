"""M2 - Block Header Analyzer — core logic."""

import hashlib
import struct

import streamlit as st



def parse_header(header_hex: str) -> dict:
    """Parse the 80-byte block header into its 6 fields.

    Wire format is little-endian. prev_hash and merkle_root are reversed
    to big-endian for display (standard convention).

    Layout:
        version       4 bytes  LE
        prev_hash    32 bytes  LE  (reversed for display)
        merkle_root  32 bytes  LE  (reversed for display)
        timestamp     4 bytes  LE
        bits          4 bytes  LE
        nonce         4 bytes  LE
    """
    raw = bytes.fromhex(header_hex)
    assert len(raw) == 80, f"Expected 80 bytes, got {len(raw)}"

    version,    = struct.unpack_from("<I", raw, 0)
    prev_hash   = raw[4:36][::-1].hex()
    merkle_root = raw[36:68][::-1].hex()
    timestamp,  = struct.unpack_from("<I", raw, 68)
    bits,       = struct.unpack_from("<I", raw, 72)
    nonce,      = struct.unpack_from("<I", raw, 76)

    return {
        "version":     version,
        "prev_hash":   prev_hash,
        "merkle_root": merkle_root,
        "timestamp":   timestamp,
        "bits":        bits,
        "nonce":       nonce,
    }


def double_sha256(data: bytes) -> bytes:
    """Return SHA256(SHA256(data))."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def bits_to_target(bits: int) -> int:
    """Convert compact bits to 256-bit target integer."""
    exponent   = bits >> 24
    coefficient = bits & 0x007FFFFF
    return coefficient * (256 ** (exponent - 3))


def count_leading_zero_bits(hash_hex: str) -> int:
    """Count leading zero bits in a 256-bit hash given as hex."""
    binary = bin(int(hash_hex, 16))[2:].zfill(256)
    return len(binary) - len(binary.lstrip("0"))


def verify_proof_of_work(header_hex: str) -> dict:
    """Manually verify PoW for a block header.

    Returns a dict with:
        computed_hash   — double SHA256 of header, big-endian hex
        target          — 256-bit target as int
        target_hex      — target as 64-char hex string
        pow_valid       — True if computed_hash < target
        leading_zero_bits — number of leading zero bits in computed_hash
    """
    raw         = bytes.fromhex(header_hex)
    fields      = parse_header(header_hex)
    hash_bytes  = double_sha256(raw)
    computed    = hash_bytes[::-1].hex()   # reverse to big-endian
    target      = bits_to_target(fields["bits"])
    zero_bits   = count_leading_zero_bits(computed)

    return {
        "computed_hash":    computed,
        "target":           target,
        "target_hex":       f"{target:064x}",
        "pow_valid":        int(computed, 16) < target,
        "leading_zero_bits": zero_bits,
    }


def render() -> None:
    st.header("M2 - Block Header Analyzer")
    st.info("UI coming soon.")
