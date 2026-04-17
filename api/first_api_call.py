"""Session 1 - Milestone 2: first API call. Prints live Bitcoin block data."""

import requests

url = "https://blockstream.info/api/blocks/tip/hash"
tip_hash = requests.get(url).text.strip()
block = requests.get(f"https://blockstream.info/api/block/{tip_hash}").json()

print(f"Block height : {block['height']}")
print(f"Block hash   : {block['id']}")
# Leading zeros: Bitcoin's PoW requires SHA256(SHA256(header)) to start with many zeros.
# The more zeros, the harder the puzzle — this is how difficulty is enforced.
print(f"Nonce        : {block['nonce']}")
print(f"Bits         : {hex(block['bits'])}")
# Bits encodes the target threshold in compact form: target = coefficient * 256^(exponent-3).
# A valid block hash must be below this target, which explains the leading zeros above.
print(f"Difficulty   : {block['difficulty']:.2e}")
print(f"Transactions : {block['tx_count']}")
