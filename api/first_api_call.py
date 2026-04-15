"""Session 1 - Milestone 2: first API call. Prints live Bitcoin block data."""

import requests

url = "https://blockstream.info/api/blocks/tip/hash"
tip_hash = requests.get(url).text.strip()
block = requests.get(f"https://blockstream.info/api/block/{tip_hash}").json()

print(f"Block height : {block['height']}")
print(f"Block hash   : {block['id']}")
# The hash has many leading zeros — proof that SHA256(SHA256(header)) < target
print(f"Nonce        : {block['nonce']}")
# 'bits' is the compact encoding of the target threshold (exponent + coefficient)
print(f"Bits         : {hex(block['bits'])}")
print(f"Difficulty   : {block['difficulty']:.2e}")
print(f"Transactions : {block['tx_count']}")
