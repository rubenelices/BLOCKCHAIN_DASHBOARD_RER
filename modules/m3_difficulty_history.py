"""M3 - Difficulty History — core logic."""

import pandas as pd
import streamlit as st

from api.blockchain_client import get_block_by_height, get_block_blockstream, get_tip_hash

ADJUSTMENT_PERIOD  = 2016   # blocks per difficulty adjustment
TARGET_BLOCK_TIME  = 600    # seconds


def get_latest_adjustment_height() -> int:
    """Return the height of the most recent difficulty adjustment block."""
    tip = get_block_blockstream(get_tip_hash())
    return (tip["height"] // ADJUSTMENT_PERIOD) * ADJUSTMENT_PERIOD


def fetch_adjustment_blocks(n_periods: int = 10) -> list[dict]:
    """Return the last n_periods difficulty adjustment blocks as a list of dicts.

    Each dict contains: height, timestamp, difficulty, bits.
    Sorted ascending by height.
    """
    latest_adj = get_latest_adjustment_height()
    blocks = []
    for i in range(n_periods):
        height = latest_adj - i * ADJUSTMENT_PERIOD
        if height < 0:
            break
        block = get_block_by_height(height)
        blocks.append({
            "height":     height,
            "timestamp":  block["timestamp"],
            "difficulty": block["difficulty"],
            "bits":       block["bits"],
        })

    blocks.sort(key=lambda b: b["height"])
    return blocks


def build_adjustment_dataframe(blocks: list[dict], target_block_time: int = TARGET_BLOCK_TIME) -> pd.DataFrame:
    """Build a DataFrame with one row per adjustment period.

    The ``target_block_time`` argument lets non-Bitcoin chains reuse this
    helper. Bitcoin keeps the default of 600s; Litecoin passes 150s so the
    ratio column reflects the Litecoin retarget assumption rather than the
    Bitcoin one.

    Columns added beyond the raw block fields:
        date            — timestamp as datetime
        actual_period_s — seconds between this and the previous adjustment block
        ratio           — actual_period_s / (ADJUSTMENT_PERIOD * target_block_time)
        pct_change      — % change in difficulty vs previous period
        next_difficulty — predicted difficulty for the next period
    """
    df = pd.DataFrame(blocks)
    df["date"] = pd.to_datetime(df["timestamp"], unit="s")

    target_period = ADJUSTMENT_PERIOD * target_block_time

    df["actual_period_s"] = df["timestamp"].diff()
    df["ratio"]           = df["actual_period_s"] / target_period
    df["pct_change"]      = df["difficulty"].pct_change() * 100

    # Predicted next difficulty based on the retarget formula (capped at 4x)
    def predict_next(row):
        if pd.isna(row["ratio"]) or pd.isna(row["actual_period_s"]):
            return None
        raw = row["difficulty"] * target_period / row["actual_period_s"]
        return max(row["difficulty"] / 4, min(raw, row["difficulty"] * 4))

    df["next_difficulty"] = df.apply(predict_next, axis=1)

    return df


def render() -> None:
    st.header("M3 - Difficulty History")
    st.info("UI coming soon.")
