"""Central cryptocurrency configuration for the dashboard."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CryptoConfig:
    id: str
    name: str
    ticker: str
    symbol: str
    consensus: str
    primary_color: str
    secondary_color: str
    supported_modules: tuple[str, ...]
    data_source: str
    tagline: str
    methodology: str
    module_modes: dict[str, str]


MODULE_IDS = ("m1", "m2", "m3", "m4", "m5", "m6", "m7")


CRYPTO_CONFIGS: dict[str, CryptoConfig] = {
    "bitcoin": CryptoConfig(
        id="bitcoin",
        name="Bitcoin",
        ticker="BTC",
        symbol="₿",
        consensus="Proof of Work",
        primary_color="#F7931A",
        secondary_color="#00C2FF",
        supported_modules=MODULE_IDS,
        data_source="Blockstream Esplora API",
        tagline="Bitcoin blockchain analytics",
        methodology=(
            "Bitcoin is the reference implementation for the current dashboard. "
            "The PoW, difficulty, Merkle proof, anomaly and security modules use "
            "live Bitcoin block data and Nakamoto-style assumptions where applicable."
        ),
        module_modes={
            "m1": "native_pow",
            "m2": "native_pow_header",
            "m3": "native_difficulty",
            "m4": "native_inter_arrival_ai",
            "m5": "native_merkle",
            "m6": "native_pow_security",
            "m7": "native_difficulty_prediction",
        },
    ),
    "ethereum": CryptoConfig(
        id="ethereum",
        name="Ethereum",
        ticker="ETH",
        symbol="Ξ",
        consensus="Proof of Stake",
        primary_color="#627EEA",
        secondary_color="#8A92B2",
        supported_modules=MODULE_IDS,
        data_source="Ethereum JSON-RPC / public explorer API",
        tagline="Ethereum post-Merge network analytics",
        methodology=(
            "Ethereum has used Proof of Stake since The Merge on 2022-09-15. "
            "Its modules must be equivalent in purpose, not copies of Bitcoin PoW "
            "metrics: activity, gas, slots, finality and validator security replace "
            "hashrate, nonce search and difficulty retargeting."
        ),
        module_modes={
            "m1": "pos_network_activity",
            "m2": "pos_block_header",
            "m3": "pos_time_series",
            "m4": "pos_activity_anomaly_ai",
            "m5": "merkle_patricia_or_receipt_proof",
            "m6": "pos_economic_security",
            "m7": "pos_activity_prediction",
        },
    ),
    "litecoin": CryptoConfig(
        id="litecoin",
        name="Litecoin",
        ticker="LTC",
        symbol="Ł",
        consensus="Proof of Work",
        primary_color="#00D084",
        secondary_color="#C0C0C0",
        supported_modules=MODULE_IDS,
        data_source="Litecoin public explorer API",
        tagline="Litecoin PoW network analytics",
        methodology=(
            "Litecoin remains a Proof of Work network, so most Bitcoin modules can "
            "be adapted directly. The implementation still needs Litecoin-specific "
            "data sources, timing constants and Scrypt-aware security assumptions."
        ),
        module_modes={
            "m1": "pow_equivalent",
            "m2": "pow_header_equivalent",
            "m3": "difficulty_equivalent",
            "m4": "inter_arrival_ai_equivalent",
            "m5": "merkle_equivalent",
            "m6": "pow_security_scrypt",
            "m7": "difficulty_prediction_equivalent",
        },
    ),
}


DEFAULT_CRYPTO_ID = "bitcoin"


def get_crypto_config(crypto_id: str | None) -> CryptoConfig:
    """Return a crypto config, falling back to Bitcoin for unknown ids."""
    return CRYPTO_CONFIGS.get(crypto_id or DEFAULT_CRYPTO_ID, CRYPTO_CONFIGS[DEFAULT_CRYPTO_ID])
