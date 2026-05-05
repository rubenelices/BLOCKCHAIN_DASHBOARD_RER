"""M5 - Merkle Proof Verifier core logic."""

import hashlib


def double_sha256(data: bytes) -> bytes:
    """Return SHA256(SHA256(data))."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def txid_to_internal_bytes(txid: str) -> bytes:
    """Convert displayed txid hex to Bitcoin internal byte order."""
    return bytes.fromhex(txid)[::-1]


def internal_bytes_to_txid(hash_bytes: bytes) -> str:
    """Convert Bitcoin internal hash bytes to displayed big-endian hex."""
    return hash_bytes[::-1].hex()


def build_merkle_tree(txids: list[str]) -> list[list[bytes]]:
    """Build the full Bitcoin Merkle tree from displayed txids.

    Leaves and internal nodes are stored in Bitcoin internal byte order. If a
    level has an odd number of hashes, Bitcoin duplicates the last hash before
    computing the next level.
    """
    if not txids:
        raise ValueError("Cannot build a Merkle tree without transactions.")

    levels = [[txid_to_internal_bytes(txid) for txid in txids]]
    while len(levels[-1]) > 1:
        current = levels[-1]
        next_level = []
        for i in range(0, len(current), 2):
            left = current[i]
            right = current[i + 1] if i + 1 < len(current) else left
            next_level.append(double_sha256(left + right))
        levels.append(next_level)
    return levels


def get_merkle_root(txids: list[str]) -> str:
    """Return the displayed Merkle root for a list of displayed txids."""
    tree = build_merkle_tree(txids)
    return internal_bytes_to_txid(tree[-1][0])


def build_merkle_proof(txids: list[str], tx_index: int) -> list[dict]:
    """Return the sibling path needed to prove inclusion of txids[tx_index]."""
    if tx_index < 0 or tx_index >= len(txids):
        raise IndexError("Transaction index out of range.")

    tree = build_merkle_tree(txids)
    proof = []
    index = tx_index

    for level_idx, level in enumerate(tree[:-1]):
        sibling_index = index ^ 1
        if sibling_index >= len(level):
            sibling_index = index

        sibling = level[sibling_index]
        sibling_side = "right" if sibling_index > index else "left"

        proof.append({
            "level": level_idx,
            "index": index,
            "sibling_index": sibling_index,
            "sibling_side": sibling_side,
            "sibling_hash": internal_bytes_to_txid(sibling),
        })
        index //= 2

    return proof


def verify_merkle_proof(txid: str, proof: list[dict], merkle_root: str) -> dict:
    """Verify a Merkle proof and return every intermediate computation."""
    current = txid_to_internal_bytes(txid)
    steps = []

    for item in proof:
        sibling = txid_to_internal_bytes(item["sibling_hash"])
        current_before = internal_bytes_to_txid(current)

        if item["sibling_side"] == "right":
            left, right = current, sibling
        else:
            left, right = sibling, current

        parent = double_sha256(left + right)
        parent_display = internal_bytes_to_txid(parent)

        steps.append({
            "level": item["level"],
            "current_hash": current_before,
            "sibling_hash": item["sibling_hash"],
            "sibling_side": item["sibling_side"],
            "left_hash": internal_bytes_to_txid(left),
            "right_hash": internal_bytes_to_txid(right),
            "parent_hash": parent_display,
        })
        current = parent

    computed_root = internal_bytes_to_txid(current)
    return {
        "computed_root": computed_root,
        "expected_root": merkle_root,
        "valid": computed_root.lower() == merkle_root.lower(),
        "steps": steps,
    }


def build_and_verify_merkle_proof(
    txids: list[str],
    tx_index: int,
    merkle_root: str,
) -> dict:
    """Build and verify a Merkle proof for txids[tx_index]."""
    proof = build_merkle_proof(txids, tx_index)
    selected_txid = txids[tx_index]
    result = verify_merkle_proof(selected_txid, proof, merkle_root)
    result.update({
        "selected_txid": selected_txid,
        "tx_index": tx_index,
        "tx_count": len(txids),
        "proof": proof,
        "proof_length": len(proof),
    })
    return result


def render() -> None:
    import streamlit as st
    st.header("M5 - Merkle Proof Verifier")
    st.info("UI is implemented in app.py.")
