"""CryptoChain Analyzer — Streamlit dashboard entry point."""

import hashlib
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats
from streamlit_autorefresh import st_autorefresh

from config.crypto_config import CRYPTO_CONFIGS, DEFAULT_CRYPTO_ID, CryptoConfig, get_crypto_config
from modules.module_registry import ModuleSpec, module_by_label, supported_module_specs
from ui.theme import chart_colors, crypto_theme_css

# ── Page config — MUST be the very first Streamlit call ──────────────────────
st.set_page_config(
    page_title="CryptoChain Analyzer",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "active_crypto_id" not in st.session_state:
    st.session_state["active_crypto_id"] = DEFAULT_CRYPTO_ID
active_crypto = get_crypto_config(st.session_state["active_crypto_id"])

# ── Global CSS injection — immediately after set_page_config ─────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&family=Inter:wght@400;500&display=swap');

/* ── CSS variables ── */
:root {
    --bg-dark:      #0A0E1A;
    --bg-card:      #0F1629;
    --bg-card-alt:  #141C35;
    --border:       #1E2D5A;
    --accent-blue:  #00C2FF;
    --accent-green: #1CE87A;
    --accent-red:   #FF4560;
    --accent-gold:  #F7931A;
    --text-primary: #E8EDF5;
    --text-muted:   #6B7DA0;
    --text-mono:    #00C2FF;
}

/* ── App & background ── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: linear-gradient(180deg, #000000 0%, #000000 30%, #030d1c 60%, #091828 85%, #0A1830 100%) !important;
}
/* Kill every Streamlit wrapper that could add a box */
section.main > div,
[data-testid="stBlock"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="stBlockContainer"],
[data-testid="block-container"],
[data-testid="element-container"],
.block-container,
.main .block-container {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

/* Hide sidebar toggle and collapsed sidebar */
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"]        { display: none !important; }

/* ── Typography ── */
h1, h2, h3, h4 {
    font-family: 'Rajdhani', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}
p, li { font-family: 'Inter', sans-serif; color: var(--text-primary); }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-left: 3px solid var(--accent-blue) !important;
    border-radius: 8px !important;
    padding: 16px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease !important;
    cursor: default;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(0,194,255,0.4) !important;
    box-shadow: 0 4px 24px rgba(0,194,255,0.10), 0 1px 6px rgba(0,0,0,0.35) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Rajdhani', sans-serif !important;
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="stMetricValue"] {
    font-family: 'Rajdhani', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] { font-family: 'Rajdhani', sans-serif !important; }

/* ── DataFrame ── */
[data-testid="stDataFrame"] { background: var(--bg-card) !important; }
.dvn-scroller { background: var(--bg-card) !important; }

/* ── Captions ── */
.stCaption, [data-testid="stCaptionContainer"], small {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-muted) !important;
    font-size: 0.82rem !important;
}

/* ── Text inputs ── */
[data-testid="stTextInput"] input {
    background-color: var(--bg-card-alt) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-family: 'Share Tech Mono', monospace !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 2px rgba(0,194,255,0.18) !important;
}
[data-testid="stTextInput"] label {
    font-family: 'Rajdhani', sans-serif !important;
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Slider ── */
[data-testid="stSlider"] label {
    font-family: 'Rajdhani', sans-serif !important;
    color: var(--text-muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div {
    background-color: var(--border) !important;
    border-radius: 4px !important;
}
[data-testid="stProgressBar"] > div > div {
    background-color: var(--accent-blue) !important;
    border-radius: 4px !important;
}

/* ── Code tags ── */
code {
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--text-mono) !important;
    background: rgba(0,194,255,0.08) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.87em !important;
}

/* ── Scrollbars ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-dark); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-blue); }

/* ── Hr ── */
hr { border-color: var(--border) !important; opacity: 0.5; }

/* ── Premium Hero — glassmorphism / hedge-fund aesthetic ── */
@keyframes ph-float {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-5px); }
}
.ph-wrap {
    position: relative;
    border-radius: 0;
    border: none;
    overflow: hidden;
    margin-bottom: 0;
    box-shadow: none;
}
.ph-bg {
    position: absolute;
    inset: 0;
    background: transparent;
    background-image:
        linear-gradient(rgba(0,70,150,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,70,150,0.035) 1px, transparent 1px);
    background-size: 40px 40px;
}
#ph-canvas {
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 1;
}
.ph-glow-c {
    position: absolute;
    top: -40%; left: 50%;
    transform: translateX(-50%);
    width: 1100px; height: 600px;
    background: radial-gradient(ellipse, rgba(0,150,255,0.09) 0%, transparent 60%);
    pointer-events: none; z-index: 2;
}
.ph-glow-l {
    position: absolute;
    top: 0; left: -10%;
    width: 420px; height: 100%;
    background: radial-gradient(ellipse at left center, rgba(0,80,200,0.07) 0%, transparent 65%);
    pointer-events: none; z-index: 2;
}
.ph-glow-r {
    position: absolute;
    top: 0; right: -10%;
    width: 420px; height: 100%;
    background: radial-gradient(ellipse at right center, rgba(0,180,255,0.05) 0%, transparent 65%);
    pointer-events: none; z-index: 2;
}
.ph-glass {
    position: relative;
    z-index: 3;
    background: transparent;
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    padding: 56px 56px 46px;
    text-align: center;
}
.ph-headline {
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Rajdhani', sans-serif;
    font-size: 6.2rem;
    font-weight: 900;
    letter-spacing: 0.16em;
    line-height: 1;
    margin: 0 0 18px 0;
}
.ph-btc-sym {
    color: #F7931A;
    text-shadow:
        0 0 30px rgba(247,147,26,0.8),
        0 0 80px rgba(247,147,26,0.3),
        0 0 130px rgba(247,147,26,0.1);
    animation: ph-float 6s ease-in-out infinite;
}
.ph-sep {
    color: #00C2FF;
    opacity: 0.4;
    margin: 0 22px;
    font-weight: 300;
    font-size: 3rem;
    line-height: 1;
    letter-spacing: 0;
}
.ph-wordmark {
    background: linear-gradient(100deg, #E8F4FF 0%, #B8D8F4 40%, #6EC0FF 80%, #00C2FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 24px rgba(0,160,255,0.28));
}
.ph-ghost {
    position: absolute;
    bottom: -18px; left: 50%;
    transform: translateX(-50%);
    font-family: 'Rajdhani', sans-serif;
    font-size: 9.5rem; font-weight: 900;
    letter-spacing: 0.3em;
    color: rgba(0,80,160,0.03);
    white-space: nowrap;
    pointer-events: none; user-select: none;
    z-index: 2;
}
.ph-divider {
    position: relative;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(0,160,255,0.12) 20%, rgba(0,194,255,0.55) 50%, rgba(0,160,255,0.12) 80%, transparent 100%);
    margin: 16px auto 16px;
    width: 80%;
}
.ph-divider::after {
    content: '';
    position: absolute;
    top: -2px; left: 50%;
    transform: translateX(-50%);
    width: 80px; height: 5px;
    background: radial-gradient(ellipse, rgba(0,194,255,0.5) 0%, transparent 70%);
}
.ph-t2 {
    font-family: 'Inter', sans-serif;
    font-size: 0.64rem; letter-spacing: 0.28em;
    text-transform: uppercase;
    color: rgba(0,150,220,0.48);
    margin: 0 0 20px 0;
}
.ph-t2-sep { margin: 0 14px; opacity: 0.4; }
.ph-status {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: rgba(0,0,0,0.28);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 30px;
    padding: 5px 18px;
}
.ph-live-text {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.78rem; font-weight: 700;
    color: #1CE87A; letter-spacing: 0.07em;
    text-transform: uppercase;
}
.ph-time-text {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: rgba(0,130,190,0.6);
}
.ph-pipe { color: rgba(30,50,100,0.8); }

/* ── Pulsing live dot ── */
@keyframes pulse-live {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(28,232,122,0.5); }
    50%       { opacity: 0.75; box-shadow: 0 0 0 5px rgba(28,232,122,0); }
}
.live-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #1CE87A;
    animation: pulse-live 2s ease-in-out infinite;
    flex-shrink: 0;
}

/* ── Navigation buttons — centred two-row module grid ── */
.nav-row {
    max-width: 1240px;
    margin: 0 auto;
}
.nav-row-top {
    margin-top: 8px;
}
.nav-row-bottom {
    margin-top: 14px;
    margin-bottom: 24px;
}
div[data-testid="stButton"] > button {
    position: relative !important;
    overflow: hidden !important;
    width: 100% !important;
    min-height: 58px !important;
    background:
        linear-gradient(180deg, rgba(20,28,53,0.96) 0%, rgba(8,14,28,0.98) 100%) !important;
    border: 1px solid rgba(0,194,255,0.18) !important;
    border-radius: 12px !important;
    padding: 0 22px !important;
    box-sizing: border-box !important;
    white-space: nowrap !important;
    transition: border-color 0.22s ease, box-shadow 0.22s ease, transform 0.16s ease, color 0.2s ease !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    color: #6F86B5 !important;
    letter-spacing: 0.105em !important;
    text-transform: uppercase !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), 0 8px 24px rgba(0,0,0,0.22) !important;
}
div[data-testid="stButton"] > button::before {
    content: "" !important;
    position: absolute !important;
    inset: 0 !important;
    background:
        radial-gradient(circle at 18% 0%, rgba(0,194,255,0.13), transparent 38%),
        linear-gradient(90deg, rgba(247,147,26,0.00), rgba(247,147,26,0.05), rgba(0,194,255,0.00)) !important;
    opacity: 0 !important;
    transition: opacity 0.22s ease !important;
    pointer-events: none !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: rgba(0,194,255,0.48) !important;
    color: #A9DFFF !important;
    box-shadow: 0 10px 30px rgba(0,194,255,0.11), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    transform: translateY(-2px) !important;
}
div[data-testid="stButton"] > button:hover::before {
    opacity: 1 !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background:
        linear-gradient(180deg, rgba(0,194,255,0.15) 0%, rgba(9,20,39,0.98) 100%) !important;
    border-color: #00C2FF !important;
    color: #E8F7FF !important;
    box-shadow:
        0 0 0 1px rgba(0,194,255,0.18),
        0 0 28px rgba(0,194,255,0.18),
        inset 0 -2px 0 #F7931A !important;
}
div[data-testid="stButton"] > button[kind="primary"]::before {
    opacity: 1 !important;
}

/* ── Cards ── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 12px;
    transition: border-color 0.22s ease, box-shadow 0.22s ease, transform 0.15s ease;
}
.card:hover {
    border-color: rgba(0,194,255,0.3);
    box-shadow: 0 6px 30px rgba(0,194,255,0.07), 0 1px 6px rgba(0,0,0,0.4);
    transform: translateY(-1px);
}
.card-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--accent-blue);
    margin: 0 0 14px 0;
    padding-bottom: 9px;
    border: none;
    border-bottom: 1px solid transparent;
    background-image: linear-gradient(90deg, rgba(0,194,255,0.5) 0%, rgba(0,194,255,0.12) 60%, transparent 100%);
    background-size: 100% 1px;
    background-repeat: no-repeat;
    background-position: bottom;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Module divider — glowing line under every module title ── */
.module-divider {
    position: relative;
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(0,160,255,0.15) 15%, rgba(0,194,255,0.65) 50%, rgba(0,160,255,0.15) 85%, transparent 100%);
    margin: 4px 0 24px 0;
}
.module-divider::after {
    content: '';
    position: absolute;
    top: -2px; left: 50%;
    transform: translateX(-50%);
    width: 100px; height: 5px;
    background: radial-gradient(ellipse, rgba(0,194,255,0.55) 0%, transparent 70%);
}

/* ── Section separator — narrower glowing line between content blocks ── */
.glow-sep {
    position: relative;
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(0,160,255,0.08) 20%, rgba(0,194,255,0.30) 50%, rgba(0,160,255,0.08) 80%, transparent 100%);
    margin: 22px 0;
}
.glow-sep::after {
    content: '';
    position: absolute;
    top: -2px; left: 50%;
    transform: translateX(-50%);
    width: 60px; height: 4px;
    background: radial-gradient(ellipse, rgba(0,194,255,0.35) 0%, transparent 70%);
}

/* ── Field label / value ── */
.field-label {
    font-family: 'Rajdhani', sans-serif;
    color: var(--text-muted);
    font-size: 0.72rem;
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 10px 0 3px 0;
}
.field-val {
    font-family: 'Share Tech Mono', monospace;
    color: var(--text-mono);
    font-size: 0.82rem;
    background: rgba(0,194,255,0.05);
    padding: 6px 9px;
    border-radius: 5px;
    word-break: break-all;
    display: block;
    line-height: 1.45;
    border: 1px solid rgba(0,194,255,0.1);
    transition: background 0.2s ease, border-color 0.2s ease;
}
.field-val:hover {
    background: rgba(0,194,255,0.09);
    border-color: rgba(0,194,255,0.22);
}

/* ── PoW pipeline ── */
.pow-step {
    border-radius: 8px;
    padding: 14px 12px;
    text-align: center;
}
.pow-step-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.pow-step-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.74rem;
    word-break: break-all;
    line-height: 1.5;
}
.pow-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    color: var(--text-muted);
    padding-top: 20px;
}

/* ── Result banners ── */
.result-valid {
    background: rgba(28,232,122,0.09);
    border: 1px solid rgba(28,232,122,0.5);
    border-radius: 10px;
    padding: 16px 24px;
    text-align: center;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.45rem;
    font-weight: 700;
    color: #1CE87A;
    letter-spacing: 0.07em;
    margin: 14px 0;
}
.result-invalid {
    background: rgba(255,69,96,0.09);
    border: 1px solid rgba(255,69,96,0.5);
    border-radius: 10px;
    padding: 16px 24px;
    text-align: center;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.45rem;
    font-weight: 700;
    color: #FF4560;
    letter-spacing: 0.07em;
    margin: 14px 0;
}

/* ── Bit bar ── */
.bit-bar { line-height: 0; display: block; margin: 3px 0; }
</style>
""", unsafe_allow_html=True)
st.markdown(crypto_theme_css(active_crypto), unsafe_allow_html=True)

# ── Imports from project modules ──────────────────────────────────────────────
from api.blockchain_client import (
    get_block_blockstream,
    get_block_header_hex,
    get_block_txids,
    get_recent_blocks,
    get_tip_hash,
)
from api.ethereum_client import get_block_by_number as get_eth_block_by_number
from api.ethereum_client import get_recent_blocks as get_eth_recent_blocks
from api.litecoin_client import get_latest_block as get_ltc_latest_block
from api.litecoin_client import get_recent_blocks as get_ltc_recent_blocks
from api.market_client import get_market_prices
from modules.m1_pow_monitor import (
    bits_to_target,
    count_leading_zero_bits,
    estimate_hashrate,
    get_inter_block_times,
)
from modules.m2_block_header import parse_header, verify_proof_of_work
from modules.m3_difficulty_history import build_adjustment_dataframe, fetch_adjustment_blocks
from modules.m4_ai_component import (
    build_inter_arrival_df,
    detect_isolation_forest,
    detect_statistical,
    evaluate_synthetic_anomalies,
    fit_exponential,
)
from modules.m5_merkle_proof import build_and_verify_merkle_proof
from modules.m6_security_score import (
    build_cost_curve,
    build_probability_curve,
    classify_security,
    double_spend_probability,
    estimate_attack_hashrate,
    estimate_energy_cost_per_hour,
)
from modules.m7_difficulty_predictor import train_and_evaluate
from api.blockchain_client import get_blocks_paginated

# ── Cached API wrappers ───────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_recent_blocks(count: int) -> list[dict]:
    return get_recent_blocks(count)


@st.cache_data(ttl=60)
def load_block_header_hex(block_hash: str) -> str:
    return get_block_header_hex(block_hash)


@st.cache_data(ttl=60)
def load_block_data(block_hash: str) -> dict:
    return get_block_blockstream(block_hash)


@st.cache_data(ttl=3600)
def load_block_txids(block_hash: str) -> list[str]:
    return get_block_txids(block_hash)


@st.cache_data(ttl=3600)
def load_adjustment_blocks(n_periods: int) -> list[dict]:
    return fetch_adjustment_blocks(n_periods)


def _clear_adj_cache() -> None:
    load_adjustment_blocks.clear()


@st.cache_data(ttl=3600)
def load_m4_blocks(n_blocks: int) -> list[dict]:
    return get_blocks_paginated(n_blocks)


@st.cache_data(ttl=30)
def load_eth_recent_blocks(count: int) -> list[dict]:
    return get_eth_recent_blocks(count)


@st.cache_data(ttl=30)
def load_ltc_recent_blocks(count: int) -> list[dict]:
    return get_ltc_recent_blocks(count)


@st.cache_data(ttl=30)
def load_market_prices() -> list[dict]:
    return get_market_prices()


# ── Helpers ───────────────────────────────────────────────────────────────────

def render_market_ticker() -> None:
    try:
        prices = load_market_prices()
    except Exception:
        prices = []

    if not prices:
        return

    items = []
    source = prices[0].get("source", "Market API")
    updated_at = prices[0].get("updated_at", "UTC")
    for row in prices:
        change = float(row["change_24h"])
        direction = "up" if change > 0 else "down" if change < 0 else "flat"
        arrow = "▲" if change > 0 else "▼" if change < 0 else "■"
        price = float(row["price_usd"])
        price_str = f"${price:,.2f}" if price < 10_000 else f"${price:,.0f}"
        items.append(
            f'<div class="market-item">'
            f'<div class="market-symbol">{row["ticker"]} · {row["name"]}</div>'
            f'<div class="market-price">{price_str}</div>'
            f'<div class="market-change market-{direction}">{arrow} {change:+.2f}%</div>'
            f'</div>'
        )

    st.markdown(
        f'<div class="market-ticker">'
        f'<div class="market-ticker-meta">LIVE MARKET · {source} · UPDATED {updated_at}</div>'
        f'<div class="market-ticker-track">{"".join(items)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def apply_chart_style(fig: go.Figure) -> go.Figure:
    colors = chart_colors(active_crypto)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=colors["paper"],
        plot_bgcolor=colors["plot"],
        font=dict(family="Rajdhani", color=colors["text"]),
        xaxis=dict(gridcolor=colors["grid"], showgrid=True),
        yaxis=dict(gridcolor=colors["grid"], showgrid=True),
        margin=dict(t=30, b=40, l=50, r=20),
    )
    return fig


def render_error(msg: str) -> None:
    st.markdown(
        f'<div style="border-left:3px solid #FF4560;background:#0F1629;'
        f'padding:12px 16px;border-radius:8px;margin:8px 0;">'
        f'<span style="color:#FF4560;font-family:Rajdhani,sans-serif;font-weight:700;">'
        f'Error &mdash; </span>'
        f'<span style="color:#E8EDF5;font-family:Inter,sans-serif;font-size:0.88rem;">'
        f'{msg}</span></div>',
        unsafe_allow_html=True,
    )


def make_bit_bar(n_zeros: int, zero_color: str, free_color: str, total: int = 256) -> str:
    n_zeros = max(0, min(n_zeros, total))
    sq = "display:inline-block;width:4px;height:4px;margin:0.4px;border-radius:0.5px;"
    zeros = f'<div style="{sq}background:{zero_color};"></div>' * n_zeros
    free  = f'<div style="{sq}background:{free_color};"></div>' * (total - n_zeros)
    return f'<div class="bit-bar">{zeros}{free}</div>'


def fmt_time_ago(unix_ts: int) -> str:
    delta = max(0, int(time.time()) - int(unix_ts))
    if delta < 60:
        return f"{delta}s ago"
    m, s = divmod(delta, 60)
    if m < 60:
        return f"{m}m {s}s ago"
    h, m = divmod(m, 60)
    return f"{h}h {m}m ago"


def custom_metric(label: str, value: str, value_color: str = "#E8EDF5",
                  border_color: str = "#00C2FF") -> str:
    return (
        f'<div style="background:#0F1629;border:1px solid #1E2D5A;'
        f'border-left:3px solid {border_color};border-radius:8px;padding:16px;'
        f'transition:border-color 0.2s ease,box-shadow 0.2s ease,transform 0.15s ease;"'
        f' onmouseover="this.style.borderColor=\'{border_color}80\';'
        f'this.style.boxShadow=\'0 4px 22px rgba(0,194,255,0.09)\';'
        f'this.style.transform=\'translateY(-2px)\'"'
        f' onmouseout="this.style.borderColor=\'#1E2D5A\';'
        f'this.style.boxShadow=\'none\';this.style.transform=\'none\'">'
        f'<p style="font-family:Rajdhani,sans-serif;font-size:0.78rem;font-weight:400;'
        f'color:#6B7DA0;margin:0 0 4px 0;text-transform:uppercase;letter-spacing:0.07em;">'
        f'{label}</p>'
        f'<p style="font-family:Rajdhani,sans-serif;font-size:1.55rem;font-weight:700;'
        f'color:{value_color};margin:0;line-height:1.1;">'
        f'{value}</p></div>'
    )


def module_header(title: str) -> None:
    st.markdown(
        f'<h2 style="font-family:\'Rajdhani\',sans-serif;font-weight:700;'
        f'font-size:1.5rem;color:#E8EDF5;letter-spacing:0.05em;margin-bottom:4px;">'
        f'{title}</h2>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="module-divider">', unsafe_allow_html=True)


def render_pending_crypto_module(crypto: CryptoConfig, spec: ModuleSpec) -> None:
    module_header(spec.title)
    mode = crypto.module_modes.get(spec.id, "methodological_variant")
    st.markdown(
        f'<div class="card">'
        f'<div class="card-title">{crypto.name} variant pending implementation</div>'
        f'<p style="font-family:Inter,sans-serif;font-size:0.86rem;color:#6B7DA0;'
        f'line-height:1.65;margin:0 0 12px 0;">'
        f'This module is intentionally blocked for {crypto.name} until its data source '
        f'and methodology are implemented. The dashboard will not display Bitcoin '
        f'PoW calculations under a {crypto.ticker} label.</p>'
        f'<p class="field-label">Academic purpose</p>'
        f'<p class="field-val">{spec.academic_purpose}</p>'
        f'<p class="field-label">Required variant</p>'
        f'<p class="field-val">{mode}</p>'
        f'<p class="field-label">Planned data source</p>'
        f'<p class="field-val">{crypto.data_source}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Session state init ────────────────────────────────────────────────────────
if "m2_hash" not in st.session_state:
    try:
        st.session_state["m2_hash"] = get_tip_hash()
    except Exception:
        st.session_state["m2_hash"] = ""
if "m5_hash" not in st.session_state:
    st.session_state["m5_hash"] = st.session_state.get("m2_hash", "")
if not st.session_state.get("m5_hash"):
    try:
        st.session_state["m5_hash"] = get_tip_hash()
    except Exception:
        st.session_state["m5_hash"] = ""

# ── Auto-refresh ──────────────────────────────────────────────────────────────
st_autorefresh(interval=60_000, key="main_refresh")

# ── Hero Header ───────────────────────────────────────────────────────────────
now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

st.markdown(f"""
<div class="ph-wrap">
    <div class="ph-bg"></div>
    <canvas id="ph-canvas"></canvas>
    <div class="ph-glow-c"></div>
    <div class="ph-glow-l"></div>
    <div class="ph-glow-r"></div>
        <div class="ph-ghost">BLOCKCHAIN</div>
    <div class="ph-glass">
        <div class="ph-headline">
            <span class="ph-btc-sym">{active_crypto.symbol}</span>
            <span class="ph-sep">&mdash;</span>
            <span class="ph-wordmark">CRYPTOCHAIN ANALYZER</span>
        </div>
        <div class="ph-divider"></div>
        <p class="ph-t2">
            {active_crypto.tagline.upper()}
            <span class="ph-t2-sep">&middot;</span>
            RUBEN ELICES RODRIGUEZ
            <span class="ph-t2-sep">&middot;</span>
            INGENIER&Iacute;A MATEM&Aacute;TICA
        </p>
        <div class="ph-status">
            <span class="live-dot"></span>
            <span class="ph-live-text">Live &middot; auto-refresh 60s</span>
            <span class="ph-pipe">|</span>
            <span class="ph-time-text">{now_str}</span>
        </div>
    </div>
</div>
<script>
(function() {{
    var canvas = document.getElementById('ph-canvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var W, H;
    var particles = [];
    function resize() {{
        W = canvas.offsetWidth; H = canvas.offsetHeight;
        canvas.width = W; canvas.height = H;
    }}
    function Particle() {{
        this.x = Math.random() * W;
        this.y = Math.random() * H;
        this.r = Math.random() * 1.5 + 0.4;
        this.vx = (Math.random() - 0.5) * 0.25;
        this.vy = (Math.random() - 0.5) * 0.25;
        this.alpha = Math.random() * 0.35 + 0.05;
    }}
    Particle.prototype.update = function() {{
        this.x += this.vx; this.y += this.vy;
        if (this.x < 0) this.x = W;
        if (this.x > W) this.x = 0;
        if (this.y < 0) this.y = H;
        if (this.y > H) this.y = 0;
    }};
    resize();
    for (var i = 0; i < 45; i++) particles.push(new Particle());
    function draw() {{
        ctx.clearRect(0, 0, W, H);
        particles.forEach(function(p) {{
            p.update();
            var g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 3);
            g.addColorStop(0, 'rgba(0,180,255,' + p.alpha + ')');
            g.addColorStop(1, 'rgba(0,80,200,0)');
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r * 3, 0, Math.PI * 2);
            ctx.fillStyle = g;
            ctx.fill();
        }});
        requestAnimationFrame(draw);
    }}
    window.addEventListener('resize', resize);
    draw();
}})();
</script>
""", unsafe_allow_html=True)

render_market_ticker()

# ── Cryptocurrency selector + navigation pills ───────────────────────────────
def set_active_crypto(crypto_id: str) -> None:
    st.session_state["active_crypto_id"] = crypto_id
    crypto = get_crypto_config(crypto_id)
    module_specs = supported_module_specs(crypto.supported_modules)
    labels = [spec.label for spec in module_specs]
    if st.session_state.get("active_module") not in labels:
        st.session_state["active_module"] = labels[0]


def render_crypto_selector(configs: dict[str, CryptoConfig]) -> CryptoConfig:
    st.markdown('<div class="nav-row nav-row-top">', unsafe_allow_html=True)
    cols = st.columns([1.15, 1, 1, 1, 1.15], gap="medium")
    for col, crypto in zip(cols[1:4], configs.values()):
        with col:
            is_active = st.session_state["active_crypto_id"] == crypto.id
            st.button(
                f"{crypto.symbol} {crypto.name}",
                key=f"crypto_{crypto.id}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                on_click=set_active_crypto,
                args=(crypto.id,),
            )
    st.markdown("</div>", unsafe_allow_html=True)
    return get_crypto_config(st.session_state["active_crypto_id"])


active_crypto = render_crypto_selector(CRYPTO_CONFIGS)

st.markdown(
    f'<div class="crypto-context">'
    f'<p class="crypto-context-title">{active_crypto.name} · {active_crypto.ticker} · {active_crypto.consensus}</p>'
    f'<p class="crypto-context-copy">{active_crypto.methodology}</p>'
    f'</div>',
    unsafe_allow_html=True,
)

module_specs = supported_module_specs(active_crypto.supported_modules)
nav_options = [spec.label for spec in module_specs]
if "active_module" not in st.session_state:
    st.session_state["active_module"] = nav_options[0]
if st.session_state["active_module"] not in nav_options:
    st.session_state["active_module"] = nav_options[0]


def set_active_module(module_name: str) -> None:
    st.session_state["active_module"] = module_name


def render_navigation(options: list[str]) -> str:
    top_row = options[:4]
    bottom_row = options[4:]

    st.markdown('<div class="nav-row nav-row-top">', unsafe_allow_html=True)
    top_cols = st.columns([0.35, 1, 1, 1, 1, 0.35], gap="medium")
    for col, option in zip(top_cols[1:5], top_row):
        with col:
            is_active = st.session_state["active_module"] == option
            st.button(
                option,
                key=f"nav_{option}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                on_click=set_active_module,
                args=(option,),
            )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="nav-row nav-row-bottom">', unsafe_allow_html=True)
    bottom_cols = st.columns([0.9, 1, 1, 1, 0.9], gap="medium")
    for col, option in zip(bottom_cols[1:4], bottom_row):
        with col:
            is_active = st.session_state["active_module"] == option
            st.button(
                option,
                key=f"nav_{option}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                on_click=set_active_module,
                args=(option,),
            )
    st.markdown("</div>", unsafe_allow_html=True)

    return st.session_state["active_module"]


module = render_navigation(nav_options)
selected_module = module_by_label(module)


# ─────────────────────────────────────────────────────────────────────────────
# M1 — PROOF OF WORK MONITOR
# ─────────────────────────────────────────────────────────────────────────────
def render_m1() -> None:
    module_header("M1 — PROOF OF WORK MONITOR")

    try:
        blocks = load_recent_blocks(50)
    except Exception as e:
        render_error(str(e))
        return

    if not blocks:
        render_error("No block data returned from API.")
        return

    try:
        latest     = blocks[0]
        bits_int   = int(latest["bits"])
        difficulty = float(latest["difficulty"])
        target_int = bits_to_target(bits_int)
        target_hex = f"{target_int:064x}"
        hashrate   = estimate_hashrate(difficulty)

        required_zero_bits = count_leading_zero_bits(target_hex)
        block_hash         = latest["id"]
        actual_zero_bits   = count_leading_zero_bits(block_hash)

        inter_times = get_inter_block_times(blocks)
        avg_time    = int(np.mean(inter_times)) if inter_times else 0

        exponent    = bits_int >> 24
        coefficient = bits_int & 0x007FFFFF
    except Exception as e:
        render_error(f"Computation error: {e}")
        return

    # ── Row 1: Top metrics ────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Block Height",   f"{latest['height']:,}")
    c2.metric("Difficulty",     f"{difficulty:.2e}")
    c3.metric("Hash Rate",      f"{hashrate / 1e18:.1f} EH/s")
    c4.metric("Required Zeros", f"{required_zero_bits} bits")
    c5.metric("Avg Block Time", f"{avg_time} s")

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    # ── Row 2: Histogram + Target card ───────────────────────────────────────
    col_hist, col_card = st.columns([3, 2], gap="medium")

    with col_hist:
        st.markdown(
            '<div class="card"><div class="card-title">Block Arrival Times — Poisson Process</div>',
            unsafe_allow_html=True,
        )
        if len(inter_times) >= 2:
            observed_mean = float(np.mean(inter_times))
            x_max   = max(max(inter_times) * 1.1, 1500)
            x_curve = np.linspace(0, x_max, 500)
            lam     = 1 / 600
            y_curve = lam * np.exp(-lam * x_curve)

            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=inter_times,
                histnorm="probability density",
                nbinsx=20,
                name="Observed inter-block times",
                marker_color="rgba(0,194,255,0.70)",
                marker_line=dict(color="rgba(0,194,255,0.9)", width=0.5),
                hovertemplate="Interval: %{x:.0f}s<br>Density: %{y:.6f}<extra></extra>",
            ))
            fig.add_trace(go.Scatter(
                x=x_curve, y=y_curve,
                mode="lines",
                name="Exp(λ=1/600s) theoretical",
                line=dict(color="#F7931A", width=2.5),
                hovertemplate="t=%{x:.0f}s<br>PDF=%{y:.7f}<extra></extra>",
            ))
            fig.add_annotation(
                text="Expected: Exp(λ=1/600s) — Poisson process",
                xref="paper", yref="paper",
                x=0.98, y=0.97, showarrow=False,
                font=dict(family="Rajdhani", size=11, color="#F7931A"),
                align="right",
            )
            fig.add_annotation(
                text=f"Observed mean: {observed_mean:.0f}s",
                xref="paper", yref="paper",
                x=0.03, y=0.91, showarrow=False,
                bgcolor="#141C35",
                bordercolor="#1CE87A", borderwidth=1, borderpad=6,
                font=dict(family="Rajdhani", size=12, color="#1CE87A"),
                align="left",
            )
            apply_chart_style(fig)
            fig.update_layout(
                xaxis_title="Seconds between blocks",
                yaxis_title="Probability density",
                showlegend=True,
                legend=dict(
                    x=0.98, y=0.82, xanchor="right",
                    bgcolor="rgba(15,22,41,0.85)",
                    bordercolor="#1E2D5A", borderwidth=1,
                ),
                height=340,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(
                "<p style='color:#6B7DA0;font-family:Inter,sans-serif;'>"
                "Insufficient blocks for histogram.</p>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_card:
        st.markdown(
            '<div class="card"><div class="card-title">SHA-256 Target Threshold</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="field-label">Target threshold (bits decoded):</p>'
            f'<p class="field-val">{target_hex}</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="field-label">Latest block hash (SHA256d, big-endian):</p>'
            f'<p class="field-val">{block_hash}</p>',
            unsafe_allow_html=True,
        )

        target_bar = make_bit_bar(required_zero_bits, "#1E2D5A", "#00C2FF")
        hash_bar   = make_bit_bar(actual_zero_bits,   "#1CE87A", "#00C2FF")
        st.markdown(
            f'<div style="margin:12px 0 4px 0;">{target_bar}{hash_bar}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.74rem;color:#6B7DA0;'
            'margin-top:7px;line-height:1.55;">'
            '<strong style="color:#00C2FF;">Top</strong> = target threshold '
            '(minimum zeros required). '
            '<strong style="color:#1CE87A;">Bottom</strong> = actual block hash. '
            'Each square = 1 bit of the 256-bit SHA-256 output space.</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.78rem;'
            f'color:#6B7DA0;margin-top:12px;line-height:1.7;">'
            f'bits = <span style="color:#00C2FF;">0x{bits_int:08x}</span><br>'
            f'&nbsp;&nbsp;&rarr; exponent = <span style="color:#F7931A;">{exponent}</span><br>'
            f'&nbsp;&nbsp;&rarr; coefficient = '
            f'<span style="color:#F7931A;">0x{coefficient:06x}</span></p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    # ── Row 3: Latest blocks table ────────────────────────────────────────────
    st.markdown(
        '<div class="card"><div class="card-title">Latest Blocks</div>',
        unsafe_allow_html=True,
    )
    th = (
        "padding:8px 12px;text-align:left;font-family:Rajdhani,sans-serif;"
        "font-size:0.72rem;color:#6B7DA0;text-transform:uppercase;"
        "letter-spacing:0.08em;border-bottom:2px solid #1E2D5A;"
    )
    header_row = (
        '<table style="width:100%;border-collapse:collapse;"><thead><tr>'
        + "".join(f'<th style="{th}">{c}</th>'
                  for c in ["Height", "Hash", "Nonce", "Transactions", "Time ago"])
        + "</tr></thead><tbody>"
    )
    body_rows = []
    for b in blocks[:15]:
        h_short = b["id"][:20] + "..."
        body_rows.append(
            "<tr"
            " onmouseover=\"this.style.background='rgba(0,194,255,0.04)'\""
            " onmouseout=\"this.style.background='transparent'\">"
            f'<td style="padding:8px 12px;border-bottom:1px solid #1E2D5A;'
            f'font-family:Rajdhani,sans-serif;font-weight:600;color:#E8EDF5;">'
            f'{b["height"]:,}</td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #1E2D5A;'
            f'font-family:\'Share Tech Mono\',monospace;color:#00C2FF;font-size:0.82rem;">'
            f'{h_short}</td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #1E2D5A;'
            f'font-family:Rajdhani,sans-serif;color:#E8EDF5;">'
            f'{int(b["nonce"]):,}</td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #1E2D5A;'
            f'font-family:Rajdhani,sans-serif;color:#E8EDF5;">'
            f'{b.get("tx_count","—")}</td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #1E2D5A;'
            f'font-family:Rajdhani,sans-serif;color:#6B7DA0;">'
            f'{fmt_time_ago(b["timestamp"])}</td>'
            "</tr>"
        )
    st.markdown(
        header_row + "".join(body_rows) + "</tbody></table>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# M2 — BLOCK HEADER ANALYZER
# ─────────────────────────────────────────────────────────────────────────────
def render_m2() -> None:
    module_header("M2 — BLOCK HEADER ANALYZER")

    block_hash = st.text_input(
        "Block hash to analyze:",
        key="m2_hash",
        placeholder="Enter a 64-character block hash...",
    )

    if not block_hash or len(block_hash) != 64:
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.85rem;color:#6B7DA0;">'
            'Enter a valid 64-character block hash above to begin analysis.</p>',
            unsafe_allow_html=True,
        )
        return

    try:
        header_hex = load_block_header_hex(block_hash)
    except Exception as e:
        render_error(f"Could not fetch block header: {e}")
        return

    try:
        block_data = load_block_data(block_hash)
    except Exception as e:
        render_error(f"Could not fetch block data: {e}")
        return

    try:
        fields  = parse_header(header_hex)
        pow_res = verify_proof_of_work(header_hex)
    except Exception as e:
        render_error(f"Header parse/verify error: {e}")
        return

    difficulty = float(block_data.get("difficulty", 0))
    hashrate   = estimate_hashrate(difficulty)
    pow_valid  = pow_res["pow_valid"]
    computed   = pow_res["computed_hash"]
    target_hex = pow_res["target_hex"]
    zero_bits  = pow_res["leading_zero_bits"]

    # ── Row 1: Info bar ───────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("Block Height", f'{block_data.get("height", "?"):,}')
    c2.metric("Hash Rate",    f"{hashrate / 1e18:.1f} EH/s")

    pow_color  = "#1CE87A" if pow_valid else "#FF4560"
    pow_value  = "✓ VALID" if pow_valid else "✗ INVALID"
    pow_border = "#1CE87A" if pow_valid else "#FF4560"
    with c3:
        st.markdown(custom_metric("PoW Status", pow_value, pow_color, pow_border),
                    unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    # ── Row 2: Raw header card + Header fields card ───────────────────────────
    col_raw, col_fields = st.columns(2, gap="medium")

    SEG_COLORS = {
        "version":     "#5A6A8A",
        "prev_hash":   "#00C2FF",
        "merkle_root": "#F7931A",
        "timestamp":   "#1CE87A",
        "bits":        "#FF4560",
        "nonce":       "#A855F7",
    }
    SEGMENTS = [
        ("version",     8,  "version",     0,  4),
        ("prev_hash",   64, "prev_hash",   4,  32),
        ("merkle_root", 64, "merkle_root", 36, 32),
        ("timestamp",   8,  "timestamp",   68, 4),
        ("bits",        8,  "bits",        72, 4),
        ("nonce",       8,  "nonce",       76, 4),
    ]

    with col_raw:
        st.markdown(
            '<div class="card"><div class="card-title">Raw Header (80 bytes)</div>',
            unsafe_allow_html=True,
        )
        colored_hex = ""
        cursor = 0
        for field, char_len, _, _, _ in SEGMENTS:
            chunk = header_hex[cursor: cursor + char_len]
            colored_hex += (
                f'<span style="color:{SEG_COLORS[field]};" title="{field}">{chunk}</span>'
            )
            cursor += char_len

        st.markdown(
            f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.78rem;'
            f'line-height:1.65;word-break:break-all;background:#141C35;padding:12px 14px;'
            f'border-radius:7px;border:1px solid #1E2D5A;">{colored_hex}</div>',
            unsafe_allow_html=True,
        )

        legend_rows = "".join(
            f'<tr onmouseover="this.style.background=\'rgba(0,194,255,0.03)\'"'
            f' onmouseout="this.style.background=\'transparent\'">'
            f'<td style="padding:4px 8px;font-family:Rajdhani,sans-serif;'
            f'color:{SEG_COLORS[field]};font-weight:600;font-size:0.82rem;">{label}</td>'
            f'<td style="padding:4px 8px;font-family:\'Share Tech Mono\',monospace;'
            f'font-size:0.73rem;">'
            f'<span style="background:{SEG_COLORS[field]}28;padding:1px 7px;'
            f'border-radius:3px;color:{SEG_COLORS[field]};">{SEG_COLORS[field]}</span></td>'
            f'<td style="padding:4px 8px;font-family:Rajdhani,sans-serif;'
            f'color:#6B7DA0;font-size:0.8rem;">byte {offset}</td>'
            f'<td style="padding:4px 8px;font-family:Rajdhani,sans-serif;'
            f'color:#6B7DA0;font-size:0.8rem;">{blen} B</td>'
            f'</tr>'
            for field, _, label, offset, blen in SEGMENTS
        )
        th_s = (
            "padding:4px 8px;text-align:left;font-family:Rajdhani,sans-serif;"
            "font-size:0.7rem;color:#6B7DA0;text-transform:uppercase;"
            "letter-spacing:0.08em;border-bottom:1px solid #1E2D5A;"
        )
        st.markdown(
            f'<table style="width:100%;border-collapse:collapse;margin-top:14px;">'
            f'<thead><tr>'
            + "".join(f'<th style="{th_s}">{h}</th>' for h in ["Field", "Color", "Offset", "Size"])
            + f'</tr></thead><tbody>{legend_rows}</tbody></table>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_fields:
        st.markdown(
            '<div class="card"><div class="card-title">Header Fields</div>',
            unsafe_allow_html=True,
        )
        version     = fields["version"]
        prev_hash   = fields["prev_hash"]
        merkle_root = fields["merkle_root"]
        ts          = fields["timestamp"]
        bits_f      = fields["bits"]
        nonce_f     = fields["nonce"]

        exp_f   = bits_f >> 24
        coeff_f = bits_f & 0x007FFFFF
        ts_iso  = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        def trunc(h: str) -> str:
            return h[:20] + "..." + h[-8:]

        field_rows = [
            ("Version",     f"0x{version:08x}  (decimal: {version})"),
            ("Prev Hash",   trunc(prev_hash)),
            ("Merkle Root", trunc(merkle_root)),
            ("Timestamp",   f"{ts}  →  {ts_iso}"),
            ("Bits",        f"0x{bits_f:08x}  →  exp={exp_f}, coeff=0x{coeff_f:06x}"),
            ("Nonce",       f"{nonce_f:,}  (0x{nonce_f:08x})"),
        ]
        html_fields = "".join(
            f'<p class="field-label">{lbl}</p><p class="field-val">{val}</p>'
            for lbl, val in field_rows
        )
        st.markdown(html_fields, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    # ── Row 3: PoW Verification pipeline ─────────────────────────────────────
    st.markdown(
        '<div class="card"><div class="card-title">'
        'Manual PoW Verification — hashlib.sha256</div>',
        unsafe_allow_html=True,
    )

    raw_bytes    = bytes.fromhex(header_hex)
    intermediate = hashlib.sha256(raw_bytes).hexdigest()

    step_bg1 = "background:#141C35;border:1px solid #1E2D5A;"
    step_bg2 = "background:rgba(0,194,255,0.07);border:1px solid rgba(0,194,255,0.28);"
    step_bg3 = (
        "background:rgba(28,232,122,0.09);border:1px solid rgba(28,232,122,0.45);"
        if pow_valid else
        "background:rgba(255,69,96,0.09);border:1px solid rgba(255,69,96,0.45);"
    )
    step3_color = "#1CE87A" if pow_valid else "#FF4560"

    col_s1, col_a1, col_s2, col_a2, col_s3 = st.columns([10, 1, 10, 1, 10], gap="small")

    with col_s1:
        st.markdown(
            f'<div class="pow-step" style="{step_bg1}">'
            f'<div class="pow-step-label" style="color:#6B7DA0;">Step 1 — 80-byte header</div>'
            f'<div class="pow-step-value" style="color:#6B7DA0;">'
            f'{header_hex[:32]}...'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with col_a1:
        st.markdown('<div class="pow-arrow">&rarr;</div>', unsafe_allow_html=True)
    with col_s2:
        st.markdown(
            f'<div class="pow-step" style="{step_bg2}">'
            f'<div class="pow-step-label" style="color:#00C2FF;">'
            f'Step 2 — SHA256(SHA256(&middot;))</div>'
            f'<div class="pow-step-value" style="color:#00C2FF;">'
            f'{intermediate[:32]}...'
            f'<br><span style="color:#6B7DA0;font-size:0.68rem;">(first SHA256 pass)</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with col_a2:
        st.markdown('<div class="pow-arrow">&rarr;</div>', unsafe_allow_html=True)
    with col_s3:
        st.markdown(
            f'<div class="pow-step" style="{step_bg3}">'
            f'<div class="pow-step-label" style="color:{step3_color};">'
            f'Step 3 — Block Hash (reversed to big-endian)</div>'
            f'<div class="pow-step-value" style="color:{step3_color};">'
            f'{computed}'
            f'<br><span style="color:#6B7DA0;font-size:0.68rem;">'
            f'bytes[::-1].hex() &mdash; little-endian &rarr; big-endian display</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    # Hash < Target comparison
    st.markdown(
        '<p style="font-family:Rajdhani,sans-serif;font-weight:600;font-size:0.8rem;'
        'color:#6B7DA0;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">'
        'Hash &lt; Target? &mdash; first differing position highlighted</p>',
        unsafe_allow_html=True,
    )

    first_diff = next(
        (i for i, (ch, ct) in enumerate(zip(computed, target_hex)) if ch != ct),
        -1,
    )

    def build_cmp_str(s: str, is_hash: bool) -> str:
        parts = []
        for i, ch in enumerate(s):
            if i < first_diff or first_diff == -1:
                parts.append(f'<span style="color:#2E3E60;">{ch}</span>')
            elif i == first_diff:
                color = "#FF4560" if is_hash else "#1CE87A"
                parts.append(
                    f'<span style="color:{color};font-weight:700;'
                    f'text-decoration:underline;">{ch}</span>'
                )
            else:
                parts.append(f'<span style="color:#7888A8;">{ch}</span>')
        return "".join(parts)

    hash_cmp   = build_cmp_str(computed,   is_hash=True)
    target_cmp = build_cmp_str(target_hex, is_hash=False)

    st.markdown(
        f'<div style="background:#141C35;border:1px solid #1E2D5A;border-radius:7px;'
        f'padding:12px 14px;font-family:\'Share Tech Mono\',monospace;'
        f'font-size:0.77rem;line-height:2.3;word-break:break-all;">'
        f'<div style="margin-bottom:2px;">'
        f'<span style="color:#4A5E88;font-size:0.68rem;font-family:Rajdhani,sans-serif;'
        f'text-transform:uppercase;letter-spacing:0.07em;">hash&nbsp;&nbsp;&nbsp;:</span>'
        f'&nbsp;{hash_cmp}</div>'
        f'<div><span style="color:#4A5E88;font-size:0.68rem;font-family:Rajdhani,sans-serif;'
        f'text-transform:uppercase;letter-spacing:0.07em;">target:</span>'
        f'&nbsp;{target_cmp}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    banner_class = "result-valid" if pow_valid else "result-invalid"
    banner_text  = "✓ PROOF OF WORK VERIFIED" if pow_valid else "✗ PROOF OF WORK INVALID"
    st.markdown(f'<div class="{banner_class}">{banner_text}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<p style="font-family:Rajdhani,sans-serif;font-size:0.85rem;color:#6B7DA0;'
        f'margin-bottom:4px;">{zero_bits} / 256 leading bits are zero</p>',
        unsafe_allow_html=True,
    )
    st.progress(min(zero_bits / 256, 1.0))

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# M3 — DIFFICULTY HISTORY
# ─────────────────────────────────────────────────────────────────────────────
def render_m3() -> None:
    module_header("M3 — DIFFICULTY HISTORY")

    # Slider — inline in M3 content
    col_sl, col_sp = st.columns([2, 5])
    with col_sl:
        n_periods = st.slider(
            "Adjustment periods",
            min_value=5, max_value=20, value=12,
            key="m3_n_periods",
            on_change=_clear_adj_cache,
        )

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    try:
        blocks = load_adjustment_blocks(n_periods)
    except Exception as e:
        render_error(f"Could not fetch adjustment blocks: {e}")
        return

    if not blocks:
        render_error("No adjustment data returned.")
        return

    try:
        df = build_adjustment_dataframe(blocks)
    except Exception as e:
        render_error(f"DataFrame build error: {e}")
        return

    if df.empty:
        render_error("Empty adjustment DataFrame.")
        return

    latest    = df.iloc[-1]
    cur_diff  = float(latest["difficulty"])
    last_pct  = latest["pct_change"]
    last_ratio = latest["ratio"]
    next_diff  = latest["next_difficulty"]

    # ── Row 1: Summary metrics ────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Difficulty", f"{cur_diff:.3e}")

    pct_val   = f"{last_pct:+.2f}%" if not pd.isna(last_pct) else "N/A"
    pct_color = (
        "#1CE87A" if not pd.isna(last_pct) and last_pct > 0 else
        "#FF4560" if not pd.isna(last_pct) and last_pct < 0 else
        "#6B7DA0"
    )
    pct_border = pct_color if pct_color != "#6B7DA0" else "#00C2FF"
    with c2:
        st.markdown(custom_metric("Last Adj. Change", pct_val, pct_color, pct_border),
                    unsafe_allow_html=True)

    if not pd.isna(last_ratio):
        arrow       = " ↑" if last_ratio > 1 else " ↓"
        ratio_str   = f"{last_ratio:.4f}{arrow}"
        ratio_color = "#00C2FF" if last_ratio > 1 else "#FF4560"
    else:
        ratio_str = "N/A"; ratio_color = "#6B7DA0"
    with c3:
        st.markdown(custom_metric("Last Period Ratio", ratio_str, ratio_color, ratio_color if ratio_color != "#6B7DA0" else "#00C2FF"),
                    unsafe_allow_html=True)

    next_str = f"{float(next_diff):.3e}" if next_diff is not None and not pd.isna(next_diff) else "N/A"
    c4.metric("Next Predicted Diff.", next_str)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    # ── Row 2: Difficulty line chart ──────────────────────────────────────────
    st.markdown(
        '<div class="card"><div class="card-title">'
        'Bitcoin Mining Difficulty — Adjustment History</div>',
        unsafe_allow_html=True,
    )
    df_plot = df.dropna(subset=["date", "difficulty"])
    if not df_plot.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_plot["date"],
            y=df_plot["difficulty"],
            mode="lines+markers",
            name="Difficulty",
            line=dict(color="#00C2FF", width=2),
            fill="tozeroy",
            fillcolor="rgba(0,194,255,0.05)",
            marker=dict(symbol="diamond", color="#F7931A", size=10),
            customdata=df_plot["pct_change"].fillna(0).values,
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "Difficulty: %{y:.3e}<br>"
                "Change: %{customdata:+.2f}%"
                "<extra></extra>"
            ),
        ))
        apply_chart_style(fig)
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Difficulty",
            showlegend=False,
            height=360,
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    # ── Row 3: Ratio chart + Summary table ────────────────────────────────────
    col_ratio, col_table = st.columns(2, gap="medium")

    with col_ratio:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'Actual / Target Period Duration</div>',
            unsafe_allow_html=True,
        )
        df_ratio = df.dropna(subset=["ratio", "date"])
        if not df_ratio.empty:
            bar_colors = ["#1CE87A" if r >= 1 else "#FF4560" for r in df_ratio["ratio"]]
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df_ratio["date"],
                y=df_ratio["ratio"],
                name="Period ratio",
                marker_color=bar_colors,
                hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Ratio: %{y:.4f}<extra></extra>",
            ))
            fig2.add_hline(
                y=1.0,
                line_dash="dash",
                line_color="#6B7DA0",
                annotation_text="Target (600s)",
                annotation_font=dict(family="Rajdhani", color="#6B7DA0", size=11),
                annotation_position="top right",
            )
            apply_chart_style(fig2)
            fig2.update_layout(
                xaxis_title="Adjustment date",
                yaxis_title="Actual / Target period duration",
                showlegend=False,
                height=320,
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.caption(
                "ratio < 1: blocks faster than 600s target → next difficulty INCREASES. "
                "ratio > 1: blocks slower → difficulty DECREASES."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_table:
        st.markdown(
            '<div class="card"><div class="card-title">Adjustment Summary</div>',
            unsafe_allow_html=True,
        )
        display_cols = ["height", "date", "difficulty", "pct_change", "ratio", "next_difficulty"]
        df_tbl = df[display_cols].copy()
        df_tbl["date"] = df_tbl["date"].dt.strftime("%Y-%m-%d")

        th_s = (
            "padding:6px 10px;text-align:left;font-family:Rajdhani,sans-serif;"
            "font-size:0.7rem;color:#6B7DA0;text-transform:uppercase;"
            "letter-spacing:0.08em;border-bottom:2px solid #1E2D5A;"
        )
        headers = ["Height", "Date", "Difficulty", "Change %", "Ratio", "Next Pred."]
        thead   = (
            "<thead><tr>"
            + "".join(f'<th style="{th_s}">{h}</th>' for h in headers)
            + "</tr></thead>"
        )

        def td(val_str: str, color: str = "#E8EDF5") -> str:
            return (
                f'<td style="padding:6px 10px;border-bottom:1px solid #1E2D5A;'
                f'font-family:Rajdhani,sans-serif;font-size:0.85rem;color:{color};">'
                f'{val_str}</td>'
            )

        tbody_rows = []
        for _, row in df_tbl.iterrows():
            pct_v   = row["pct_change"]
            ratio_v = row["ratio"]
            next_v  = row["next_difficulty"]

            pct_c   = "#1CE87A" if not pd.isna(pct_v) and pct_v > 0 else "#FF4560" if not pd.isna(pct_v) and pct_v < 0 else "#6B7DA0"
            ratio_c = "#FF4560" if not pd.isna(ratio_v) and ratio_v < 1 else "#00C2FF" if not pd.isna(ratio_v) else "#6B7DA0"

            tbody_rows.append(
                "<tr"
                " onmouseover=\"this.style.background='rgba(0,194,255,0.04)'\""
                " onmouseout=\"this.style.background='transparent'\">"
                + td(f'{int(row["height"]):,}')
                + td(str(row["date"]), "#6B7DA0")
                + td(f'{float(row["difficulty"]):.3e}')
                + td(f'{pct_v:+.2f}%' if not pd.isna(pct_v) else "—", pct_c)
                + td(f'{ratio_v:.4f}' if not pd.isna(ratio_v) else "—", ratio_c)
                + td(f'{float(next_v):.3e}' if next_v is not None and not pd.isna(next_v) else "—")
                + "</tr>"
            )

        st.markdown(
            f'<div style="overflow-x:auto;">'
            f'<table style="width:100%;border-collapse:collapse;">'
            f'{thead}<tbody>{"".join(tbody_rows)}</tbody>'
            f'</table></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# M4 — AI COMPONENT: ANOMALY DETECTOR
# ─────────────────────────────────────────────────────────────────────────────
def render_m4() -> None:
    module_header("M4 — AI COMPONENT: ANOMALY DETECTOR")

    # Sidebar controls
    col_ctrl, _ = st.columns([2, 5])
    with col_ctrl:
        n_blocks = st.slider(
            "Blocks to analyze",
            min_value=100, max_value=500, value=300, step=50,
            key="m4_n_blocks",
        )

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    # -- Data loading ---------------------------------------------------------
    with st.spinner("Fetching block data from Blockstream..."):
        try:
            raw_blocks = load_m4_blocks(n_blocks)
        except Exception as e:
            render_error(f"Could not fetch block data: {e}")
            return

    if not raw_blocks:
        render_error("No block data returned from API.")
        return

    try:
        df    = build_inter_arrival_df(raw_blocks)
        times = df["inter_arrival"].values.astype(float)
        if len(times) < 20:
            render_error("Not enough inter-arrival samples for analysis.")
            return

        exp_fit   = fit_exponential(times)
        stat_mask = detect_statistical(times, exp_fit["lambda_hat"])
        if_mask, if_scores = detect_isolation_forest(df)
        synth_eval = evaluate_synthetic_anomalies(df, anomaly_fraction=0.05)
    except Exception as e:
        render_error(f"Model error: {e}")
        return

    df = df.copy()
    df["stat_anomaly"] = stat_mask
    df["if_anomaly"]   = if_mask
    df["if_score"]     = if_scores
    df["datetime"]     = pd.to_datetime(df["timestamp"], unit="s", utc=True)

    n_samples  = len(df)
    pct_stat   = 100.0 * stat_mask.sum() / n_samples
    pct_if     = 100.0 * if_mask.sum()   / n_samples
    ks_pval    = exp_fit["ks_pvalue"]
    mean_s     = exp_fit["mean_s"]

    # ── Row 1: Summary metrics ────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Blocks Analyzed",   f"{n_samples:,}")
    c2.metric("Mean Inter-arrival", f"{mean_s:.0f} s")
    c3.metric("Target (Poisson)",  "600 s")

    ks_color  = "#1CE87A" if ks_pval >= 0.05 else "#FF4560"
    ks_border = ks_color
    ks_label  = f"p = {ks_pval:.4f}"
    with c4:
        st.markdown(
            custom_metric("KS Test p-value", ks_label, ks_color, ks_border),
            unsafe_allow_html=True,
        )

    stat_color  = "#F7931A" if pct_stat > 7 else "#1CE87A"
    stat_border = stat_color
    with c5:
        st.markdown(
            custom_metric(
                "Stat. Anomalies",
                f"{pct_stat:.1f}% ({stat_mask.sum()})",
                stat_color, stat_border,
            ),
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    # ── Row 2: Histogram + QQ-plot ────────────────────────────────────────────
    col_hist, col_qq = st.columns([3, 2], gap="medium")

    with col_hist:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'Inter-Arrival Time Distribution — Fitted Exponential Baseline</div>',
            unsafe_allow_html=True,
        )
        lam_hat = exp_fit["lambda_hat"]
        x_max   = max(float(np.percentile(times, 99)) * 1.2, 1500.0)
        x_curve = np.linspace(0, x_max, 600)
        y_curve = lam_hat * np.exp(-lam_hat * x_curve)

        normal_times  = times[~stat_mask]
        anomaly_times = times[stat_mask]

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=normal_times,
            histnorm="probability density",
            nbinsx=30,
            name="Normal blocks",
            marker_color="rgba(0,194,255,0.65)",
            marker_line=dict(color="rgba(0,194,255,0.9)", width=0.5),
            hovertemplate="Interval: %{x:.0f}s<br>Density: %{y:.6f}<extra></extra>",
        ))
        fig.add_trace(go.Histogram(
            x=anomaly_times,
            histnorm="probability density",
            nbinsx=30,
            name="Stat. anomalies",
            marker_color="rgba(255,69,96,0.75)",
            marker_line=dict(color="rgba(255,69,96,0.9)", width=0.5),
            hovertemplate="Interval: %{x:.0f}s (anomaly)<br>Density: %{y:.6f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=x_curve, y=y_curve,
            mode="lines",
            name="Fitted Exp(λ̂)",
            line=dict(color="#F7931A", width=2.5),
            hovertemplate="t=%{x:.0f}s<br>PDF=%{y:.7f}<extra></extra>",
        ))

        low_bound  = stats.expon.ppf(0.025, scale=1/lam_hat)
        high_bound = stats.expon.ppf(0.975, scale=1/lam_hat)
        fig.add_vline(x=low_bound,  line_dash="dash", line_color="#FF4560",
                      annotation_text="2.5%",  annotation_font_color="#FF4560",
                      annotation_font_size=10)
        fig.add_vline(x=high_bound, line_dash="dash", line_color="#FF4560",
                      annotation_text="97.5%", annotation_font_color="#FF4560",
                      annotation_font_size=10)
        fig.add_annotation(
            text=f"Observed mean: {mean_s:.0f}s",
            xref="paper", yref="paper", x=0.97, y=0.95, showarrow=False,
            bgcolor="#141C35", bordercolor="#1CE87A", borderwidth=1, borderpad=6,
            font=dict(family="Rajdhani", size=12, color="#1CE87A"), align="right",
        )
        fig.add_annotation(
            text=f"KS p-value: {ks_pval:.4f} {'(fit OK)' if ks_pval >= 0.05 else '(poor fit)'}",
            xref="paper", yref="paper", x=0.97, y=0.84, showarrow=False,
            bgcolor="#141C35", bordercolor="#6B7DA0", borderwidth=1, borderpad=6,
            font=dict(family="Rajdhani", size=11, color="#6B7DA0"), align="right",
        )
        apply_chart_style(fig)
        fig.update_layout(
            xaxis_title="Seconds between consecutive blocks",
            yaxis_title="Probability density",
            barmode="overlay",
            showlegend=True,
            legend=dict(
                x=0.97, y=0.72, xanchor="right",
                bgcolor="rgba(15,22,41,0.85)",
                bordercolor="#1E2D5A", borderwidth=1,
            ),
            height=360,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.78rem;color:#6B7DA0;'
            'margin-top:0;line-height:1.55;">'
            'Red bars = blocks flagged as anomalous (outside 2.5–97.5% quantiles). '
            'Orange dashed lines = detection thresholds. '
            'Bitcoin mining is modelled as a Poisson process: inter-arrival times '
            'should be close to an exponential distribution with target mean 600s. '
            'Here λ is fitted from recent data. Deviations can indicate mining-pool bursts, '
            'network latency, or selfish mining (Eyal &amp; Sirer 2014).</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_qq:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'QQ-Plot — Empirical vs Exp(λ̂)</div>',
            unsafe_allow_html=True,
        )
        sorted_times = np.sort(times)
        n = len(sorted_times)
        probs = (np.arange(1, n + 1) - 0.5) / n
        theoretical_q = stats.expon.ppf(probs, scale=1.0 / lam_hat)
        qq_max = float(max(sorted_times.max(), theoretical_q.max())) * 1.05

        fig_qq = go.Figure()
        fig_qq.add_trace(go.Scatter(
            x=theoretical_q, y=sorted_times,
            mode="markers",
            name="Data quantiles",
            marker=dict(color="#00C2FF", size=4, opacity=0.7),
            hovertemplate="Theoretical: %{x:.0f}s<br>Observed: %{y:.0f}s<extra></extra>",
        ))
        fig_qq.add_trace(go.Scatter(
            x=[0, qq_max], y=[0, qq_max],
            mode="lines",
            name="Perfect fit (y=x)",
            line=dict(color="#F7931A", width=1.5, dash="dash"),
        ))
        apply_chart_style(fig_qq)
        fig_qq.update_layout(
            xaxis_title="Theoretical quantiles (s)",
            yaxis_title="Observed quantiles (s)",
            showlegend=True,
            legend=dict(
                x=0.05, y=0.95, xanchor="left",
                bgcolor="rgba(15,22,41,0.85)",
                bordercolor="#1E2D5A", borderwidth=1,
            ),
            height=360,
        )
        st.plotly_chart(fig_qq, use_container_width=True)
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.78rem;color:#6B7DA0;'
            'margin-top:0;line-height:1.55;">'
            'Points on the orange line = perfect exponential fit. '
            'Deviations in the upper tail indicate heavy-tailed behaviour '
            '(very long waits) or occasional network partitions.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    # ── Row 3: IsolationForest timeline + method comparison ───────────────────
    col_if, col_compare = st.columns([3, 2], gap="medium")

    with col_if:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'IsolationForest Anomaly Score Timeline</div>',
            unsafe_allow_html=True,
        )
        normal_df  = df[~df["if_anomaly"]]
        anomaly_df = df[df["if_anomaly"]]

        fig_if = go.Figure()
        fig_if.add_trace(go.Scatter(
            x=normal_df["datetime"], y=normal_df["inter_arrival"],
            mode="markers",
            name="Normal",
            marker=dict(color="rgba(0,194,255,0.55)", size=4),
            hovertemplate="%{x|%Y-%m-%d %H:%M}<br>%{y:.0f}s<extra>Normal</extra>",
        ))
        fig_if.add_trace(go.Scatter(
            x=anomaly_df["datetime"], y=anomaly_df["inter_arrival"],
            mode="markers",
            name="IF anomaly",
            marker=dict(color="#FF4560", size=7, symbol="x"),
            hovertemplate="%{x|%Y-%m-%d %H:%M}<br>%{y:.0f}s<extra>Anomaly</extra>",
        ))
        fig_if.add_hline(
            y=600, line_dash="dash", line_color="#F7931A",
            annotation_text="600s target",
            annotation_font=dict(family="Rajdhani", color="#F7931A", size=11),
            annotation_position="top right",
        )
        apply_chart_style(fig_if)
        fig_if.update_layout(
            xaxis_title="Date (UTC)",
            yaxis_title="Inter-arrival time (s)",
            showlegend=True,
            legend=dict(
                x=0.02, y=0.96, xanchor="left",
                bgcolor="rgba(15,22,41,0.85)",
                bordercolor="#1E2D5A", borderwidth=1,
            ),
            height=320,
        )
        st.plotly_chart(fig_if, use_container_width=True)
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.78rem;color:#6B7DA0;'
            'margin-top:0;line-height:1.55;">'
            'IsolationForest uses three features: log(inter_arrival), '
            'hour_of_day (UTC), and position within the 2016-block difficulty epoch. '
            'contamination=0.05 targets ~5% anomaly rate. '
            'Red &times; marks = blocks the model considers anomalous.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_compare:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'Method Comparison</div>',
            unsafe_allow_html=True,
        )
        both_mask    = stat_mask & if_mask
        only_stat    = stat_mask & ~if_mask
        only_if      = ~stat_mask & if_mask

        rows = [
            ("Blocks analyzed",             f"{n_samples:,}",                   "#E8EDF5"),
            ("Mean inter-arrival",          f"{mean_s:.0f} s",                  "#E8EDF5"),
            ("Exp fit — KS statistic",      f"{exp_fit['ks_stat']:.4f}",        "#6B7DA0"),
            ("Exp fit — KS p-value",        f"{ks_pval:.4f}",
             "#1CE87A" if ks_pval >= 0.05 else "#FF4560"),
            ("Statistical anomalies",
             f"{stat_mask.sum()} ({pct_stat:.1f}%)", "#F7931A"),
            ("IsolationForest anomalies",
             f"{if_mask.sum()} ({pct_if:.1f}%)",     "#FF4560"),
            ("Flagged by both methods",     f"{both_mask.sum()}",               "#00C2FF"),
            ("Only statistical",            f"{only_stat.sum()}",               "#6B7DA0"),
            ("Only IsolationForest",        f"{only_if.sum()}",                 "#6B7DA0"),
        ]
        if synth_eval:
            rows.extend([
                ("Synthetic labels injected", f"{synth_eval['n_injected']}",     "#E8EDF5"),
                ("Statistical F1",            f"{synth_eval['statistical']['f1']:.3f}", "#F7931A"),
                ("IsolationForest F1",        f"{synth_eval['isolation_forest']['f1']:.3f}", "#FF4560"),
            ])
        table_rows = "".join(
            f'<tr onmouseover="this.style.background=\'rgba(0,194,255,0.04)\'"'
            f' onmouseout="this.style.background=\'transparent\'">'
            f'<td style="padding:7px 10px;border-bottom:1px solid #1E2D5A;'
            f'font-family:Rajdhani,sans-serif;font-size:0.82rem;color:#6B7DA0;">{lbl}</td>'
            f'<td style="padding:7px 10px;border-bottom:1px solid #1E2D5A;'
            f'font-family:Rajdhani,sans-serif;font-size:0.9rem;font-weight:700;'
            f'color:{col};text-align:right;">{val}</td>'
            f'</tr>'
            for lbl, val, col in rows
        )
        st.markdown(
            f'<table style="width:100%;border-collapse:collapse;">'
            f'<tbody>{table_rows}</tbody></table>',
            unsafe_allow_html=True,
        )
        st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.77rem;color:#6B7DA0;'
            'line-height:1.6;">'
            '<strong style="color:#E8EDF5;">Statistical</strong> — '
            'interpretable, grounded in the Poisson mining model. '
            'Flags extreme univariate outliers.<br>'
            '<strong style="color:#E8EDF5;">IsolationForest</strong> — '
            'multivariate, captures joint anomalies across time, '
            'epoch position, and hour of day. '
            'Better at detecting mining-pool coordination patterns.<br>'
            '<strong style="color:#E8EDF5;">Evaluation</strong> — '
            'because real blocks have no anomaly labels, labelled anomalies are '
            'synthetically injected into real inter-arrival data and measured '
            'with precision, recall, and F1.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if synth_eval:
        st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
        st.markdown(
            '<div class="card"><div class="card-title">'
            'Synthetic Anomaly Evaluation — Precision / Recall / F1</div>',
            unsafe_allow_html=True,
        )
        sc1, sc2, sc3, sc4, sc5, sc6, sc7 = st.columns(7)
        stat_eval = synth_eval["statistical"]
        if_eval = synth_eval["isolation_forest"]
        sc1.metric("Injected Labels", f"{synth_eval['n_injected']}")
        sc2.metric("Stat Precision", f"{stat_eval['precision']:.3f}")
        sc3.metric("Stat Recall", f"{stat_eval['recall']:.3f}")
        sc4.metric("Stat F1", f"{stat_eval['f1']:.3f}")
        sc5.metric("IF Precision", f"{if_eval['precision']:.3f}")
        sc6.metric("IF Recall", f"{if_eval['recall']:.3f}")
        sc7.metric("IF F1", f"{if_eval['f1']:.3f}")
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.78rem;color:#6B7DA0;'
            'margin-top:10px;line-height:1.55;">'
            'Evaluation uses the same recent Bitcoin block sample, then injects '
            'controlled fast-block and slow-block anomalies into 5% of intervals. '
            'This gives known labels without pretending that real-world anomaly '
            'labels are available.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    # ── Row 4: Top anomalies table ────────────────────────────────────────────
    st.markdown(
        '<div class="card"><div class="card-title">'
        'Top Anomalous Blocks (by inter-arrival time)</div>',
        unsafe_allow_html=True,
    )
    top_df = (
        df[df["stat_anomaly"] | df["if_anomaly"]]
        .assign(abs_dev=lambda d: (d["inter_arrival"] - 600).abs())
        .sort_values("abs_dev", ascending=False)
        .head(15)
    )

    if top_df.empty:
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.85rem;color:#6B7DA0;">'
            'No anomalies detected in this dataset.</p>',
            unsafe_allow_html=True,
        )
    else:
        th_s = (
            "padding:7px 12px;text-align:left;font-family:Rajdhani,sans-serif;"
            "font-size:0.72rem;color:#6B7DA0;text-transform:uppercase;"
            "letter-spacing:0.08em;border-bottom:2px solid #1E2D5A;"
        )
        thead = (
            "<thead><tr>"
            + "".join(
                f'<th style="{th_s}">{h}</th>'
                for h in ["Height", "Date (UTC)", "Inter-arrival (s)",
                           "Dev. from 600s", "Stat.", "IF"]
            )
            + "</tr></thead>"
        )
        tbody_rows = []
        for _, row in top_df.iterrows():
            dt_str  = pd.Timestamp(row["datetime"]).strftime("%Y-%m-%d %H:%M")
            iat     = int(row["inter_arrival"])
            dev     = iat - 600
            dev_col = "#FF4560" if dev > 0 else "#1CE87A"
            stat_v  = '<span style="color:#FF4560;">YES</span>' if row["stat_anomaly"] else '<span style="color:#6B7DA0;">—</span>'
            if_v    = '<span style="color:#FF4560;">YES</span>' if row["if_anomaly"]   else '<span style="color:#6B7DA0;">—</span>'
            tbody_rows.append(
                '<tr onmouseover="this.style.background=\'rgba(0,194,255,0.04)\'"'
                ' onmouseout="this.style.background=\'transparent\'">'
                f'<td style="padding:7px 12px;border-bottom:1px solid #1E2D5A;'
                f'font-family:Rajdhani,sans-serif;font-weight:600;color:#E8EDF5;">'
                f'{int(row["height"]):,}</td>'
                f'<td style="padding:7px 12px;border-bottom:1px solid #1E2D5A;'
                f'font-family:Rajdhani,sans-serif;color:#6B7DA0;">{dt_str}</td>'
                f'<td style="padding:7px 12px;border-bottom:1px solid #1E2D5A;'
                f'font-family:\'Share Tech Mono\',monospace;color:#00C2FF;">{iat:,}</td>'
                f'<td style="padding:7px 12px;border-bottom:1px solid #1E2D5A;'
                f'font-family:Rajdhani,sans-serif;color:{dev_col};font-weight:700;">'
                f'{dev:+,}</td>'
                f'<td style="padding:7px 12px;border-bottom:1px solid #1E2D5A;'
                f'text-align:center;">{stat_v}</td>'
                f'<td style="padding:7px 12px;border-bottom:1px solid #1E2D5A;'
                f'text-align:center;">{if_v}</td>'
                "</tr>"
            )
        st.markdown(
            f'<div style="overflow-x:auto;">'
            f'<table style="width:100%;border-collapse:collapse;">'
            f'{thead}<tbody>{"".join(tbody_rows)}</tbody>'
            f'</table></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# M5 — MERKLE PROOF VERIFIER
# ─────────────────────────────────────────────────────────────────────────────
def render_m5() -> None:
    module_header("M5 — MERKLE PROOF VERIFIER")

    def short_hash(value: str) -> str:
        return value[:14] + "..." + value[-10:]

    block_hash = st.text_input(
        "Block hash for Merkle proof:",
        key="m5_hash",
        placeholder="Enter a 64-character block hash...",
    )
    block_hash = block_hash.strip().lower()

    if not block_hash or len(block_hash) != 64:
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.85rem;color:#6B7DA0;">'
            'Enter a valid 64-character block hash to verify a transaction inclusion proof.</p>',
            unsafe_allow_html=True,
        )
        return

    try:
        header_hex = load_block_header_hex(block_hash)
        block_data = load_block_data(block_hash)
        txids = load_block_txids(block_hash)
    except Exception as e:
        render_error(f"Could not fetch Merkle proof data: {e}")
        return

    if not txids:
        render_error("No transaction IDs returned for this block.")
        return

    try:
        fields = parse_header(header_hex)
        merkle_root = fields["merkle_root"]
    except Exception as e:
        render_error(f"Could not parse block header: {e}")
        return

    default_index = min(len(txids) // 2, len(txids) - 1)
    col_sl, col_sp = st.columns([2, 5])
    with col_sl:
        tx_index = st.slider(
            "Transaction index",
            min_value=0,
            max_value=len(txids) - 1,
            value=default_index,
            key=f"m5_tx_index_{block_hash}",
        )

    try:
        proof_result = build_and_verify_merkle_proof(txids, tx_index, merkle_root)
    except Exception as e:
        render_error(f"Merkle proof computation error: {e}")
        return

    selected_txid = proof_result["selected_txid"]
    computed_root = proof_result["computed_root"]
    proof_valid = proof_result["valid"]

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Block Height", f'{block_data.get("height", "?"):,}')
    c2.metric("Transactions", f"{len(txids):,}")
    c3.metric("Selected Index", f"{tx_index:,}")
    c4.metric("Proof Length", f'{proof_result["proof_length"]} hashes')
    status_color = "#1CE87A" if proof_valid else "#FF4560"
    status_text = "VALID" if proof_valid else "INVALID"
    with c5:
        st.markdown(
            custom_metric("Merkle Proof", status_text, status_color, status_color),
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    col_summary, col_theory = st.columns([3, 2], gap="medium")
    with col_summary:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'Proof Target — Selected Transaction</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="field-label">Selected txid</p>'
            f'<p class="field-val">{selected_txid}</p>'
            '<p class="field-label">Computed Merkle root</p>'
            f'<p class="field-val">{computed_root}</p>'
            '<p class="field-label">Merkle root from block header</p>'
            f'<p class="field-val">{merkle_root}</p>',
            unsafe_allow_html=True,
        )
        banner_class = "result-valid" if proof_valid else "result-invalid"
        banner_text = "MERKLE PROOF VERIFIED" if proof_valid else "MERKLE PROOF INVALID"
        st.markdown(f'<div class="{banner_class}">{banner_text}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_theory:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'Why This Proves Inclusion</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.82rem;color:#6B7DA0;'
            'line-height:1.65;margin:0;">'
            'A Merkle proof uses only the selected transaction ID and one sibling hash '
            'per tree level. Each parent is computed as '
            '<code>SHA256(SHA256(left || right))</code>. If the final hash equals the '
            'Merkle root stored in the 80-byte block header, the transaction is included '
            'in that block. Bitcoin displays hashes in big-endian form, but Merkle '
            'computations use internal little-endian byte order, so txids are reversed '
            'before hashing and reversed back for display.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    st.markdown(
        '<div class="card"><div class="card-title">'
        'Merkle Proof Path — From Transaction To Root</div>',
        unsafe_allow_html=True,
    )

    steps = proof_result["steps"]
    if steps:
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_symbol = []
        edge_x = []
        edge_y = []

        current_x = -0.55
        sibling_x = 0.55
        parent_x = 0.0

        for idx, step in enumerate(steps):
            y = len(steps) - idx
            parent_y = y - 0.72

            node_x.extend([current_x, sibling_x, parent_x])
            node_y.extend([y, y, parent_y])
            node_text.extend([
                "Current<br>" + short_hash(step["current_hash"]),
                f"Sibling ({step['sibling_side']})<br>" + short_hash(step["sibling_hash"]),
                "Parent<br>" + short_hash(step["parent_hash"]),
            ])
            node_color.extend(["#00C2FF", "#F7931A", "#1CE87A"])
            node_symbol.extend(["circle", "diamond", "square"])

            edge_x.extend([current_x, parent_x, None, sibling_x, parent_x, None])
            edge_y.extend([y, parent_y, None, y, parent_y, None])

        fig_path = go.Figure()
        fig_path.add_trace(go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(color="rgba(107,125,160,0.55)", width=1.5),
            hoverinfo="skip",
            showlegend=False,
        ))
        fig_path.add_trace(go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            marker=dict(
                size=18,
                color=node_color,
                symbol=node_symbol,
                line=dict(color="#0A0E1A", width=2),
            ),
            text=node_text,
            textposition="top center",
            textfont=dict(family="Share Tech Mono", size=9, color="#E8EDF5"),
            hovertemplate="%{text}<extra></extra>",
            showlegend=False,
        ))
        fig_path.add_annotation(
            x=0,
            y=0,
            text="Merkle root<br>" + short_hash(computed_root),
            showarrow=False,
            bgcolor="rgba(28,232,122,0.10)",
            bordercolor="#1CE87A",
            borderwidth=1,
            borderpad=7,
            font=dict(family="Share Tech Mono", size=10, color="#1CE87A"),
        )
        apply_chart_style(fig_path)
        fig_path.update_layout(
            height=max(420, 90 * min(len(steps), 12)),
            xaxis=dict(visible=False, range=[-1.05, 1.05]),
            yaxis=dict(visible=False, range=[-0.4, len(steps) + 1.2]),
            margin=dict(t=30, b=20, l=20, r=20),
        )
        st.plotly_chart(fig_path, use_container_width=True)
    else:
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.85rem;color:#6B7DA0;">'
            'This block has a single transaction, so the transaction ID is already the Merkle root.</p>',
            unsafe_allow_html=True,
        )
    st.markdown(
        '<p style="font-family:Inter,sans-serif;font-size:0.78rem;color:#6B7DA0;'
        'margin-top:0;line-height:1.55;">'
        'Blue nodes are the running hash, orange nodes are sibling hashes from the proof, '
        'and green nodes are the double-SHA256 parents computed at each level.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    st.markdown(
        '<div class="card"><div class="card-title">'
        'Step-by-Step Merkle Path Computation</div>',
        unsafe_allow_html=True,
    )

    th_s = (
        "padding:7px 12px;text-align:left;font-family:Rajdhani,sans-serif;"
        "font-size:0.72rem;color:#6B7DA0;text-transform:uppercase;"
        "letter-spacing:0.08em;border-bottom:2px solid #1E2D5A;"
    )
    thead = (
        "<thead><tr>"
        + "".join(
            f'<th style="{th_s}">{h}</th>'
            for h in ["Level", "Current hash", "Sibling side", "Sibling hash", "Parent hash"]
        )
        + "</tr></thead>"
    )

    rows = []
    for step in proof_result["steps"]:
        side_color = "#1CE87A" if step["sibling_side"] == "right" else "#F7931A"
        rows.append(
            '<tr onmouseover="this.style.background=\'rgba(0,194,255,0.04)\'"'
            ' onmouseout="this.style.background=\'transparent\'">'
            f'<td style="padding:7px 12px;border-bottom:1px solid #1E2D5A;'
            f'font-family:Rajdhani,sans-serif;font-weight:700;color:#E8EDF5;">'
            f'{int(step["level"])}</td>'
            f'<td style="padding:7px 12px;border-bottom:1px solid #1E2D5A;'
            f'font-family:\'Share Tech Mono\',monospace;color:#00C2FF;">'
            f'{short_hash(step["current_hash"])}</td>'
            f'<td style="padding:7px 12px;border-bottom:1px solid #1E2D5A;'
            f'font-family:Rajdhani,sans-serif;font-weight:700;color:{side_color};">'
            f'{step["sibling_side"].upper()}</td>'
            f'<td style="padding:7px 12px;border-bottom:1px solid #1E2D5A;'
            f'font-family:\'Share Tech Mono\',monospace;color:#F7931A;">'
            f'{short_hash(step["sibling_hash"])}</td>'
            f'<td style="padding:7px 12px;border-bottom:1px solid #1E2D5A;'
            f'font-family:\'Share Tech Mono\',monospace;color:#1CE87A;">'
            f'{short_hash(step["parent_hash"])}</td>'
            "</tr>"
        )

    st.markdown(
        f'<div style="overflow-x:auto;">'
        f'<table style="width:100%;border-collapse:collapse;">'
        f'{thead}<tbody>{"".join(rows)}</tbody></table></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-family:Inter,sans-serif;font-size:0.78rem;color:#6B7DA0;'
        'margin-top:12px;line-height:1.55;">'
        'Each row hashes the current value with its sibling. The sibling side tells '
        'whether the sibling is placed on the left or right before double-SHA256.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# M6 — SECURITY SCORE
# ─────────────────────────────────────────────────────────────────────────────
def render_m6() -> None:
    module_header("M6 — SECURITY SCORE")

    try:
        blocks = load_recent_blocks(1)
    except Exception as e:
        render_error(f"Could not fetch current network data: {e}")
        return

    if not blocks:
        render_error("No block data returned from API.")
        return

    latest = blocks[0]
    difficulty = float(latest["difficulty"])
    network_hashrate = estimate_hashrate(difficulty)

    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns(4)
    with col_ctrl1:
        attacker_percent = st.slider(
            "Attacker share q",
            min_value=5,
            max_value=49,
            value=30,
            step=1,
            key="m6_attacker_percent",
        )
    with col_ctrl2:
        confirmations = st.slider(
            "Confirmations",
            min_value=1,
            max_value=20,
            value=6,
            step=1,
            key="m6_confirmations",
        )
    with col_ctrl3:
        efficiency = st.slider(
            "ASIC efficiency (J/TH)",
            min_value=10.0,
            max_value=60.0,
            value=20.0,
            step=1.0,
            key="m6_efficiency",
        )
    with col_ctrl4:
        electricity_price = st.slider(
            "Electricity (USD/kWh)",
            min_value=0.01,
            max_value=0.30,
            value=0.05,
            step=0.01,
            key="m6_electricity",
        )

    q = attacker_percent / 100.0
    attack_hashrate = estimate_attack_hashrate(network_hashrate, q)
    energy = estimate_energy_cost_per_hour(
        attack_hashrate,
        efficiency,
        electricity_price,
    )
    attack_prob = double_spend_probability(q, confirmations)
    security_label = classify_security(attack_prob)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Network Hash Rate", f"{network_hashrate / 1e18:.1f} EH/s")
    c2.metric("Attack Hash Rate", f"{attack_hashrate / 1e18:.1f} EH/s")
    c3.metric("Energy / Hour", f"{energy['kwh_per_hour'] / 1e6:.2f}M kWh")
    c4.metric("Cost / Hour", f"${energy['cost_usd_per_hour'] / 1e6:.2f}M")
    sec_color = (
        "#1CE87A" if security_label in {"Very high", "High"} else
        "#F7931A" if security_label == "Moderate" else
        "#FF4560"
    )
    with c5:
        st.markdown(
            custom_metric("Security Level", security_label.upper(), sec_color, sec_color),
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    col_cost, col_prob = st.columns(2, gap="medium")

    with col_cost:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'Energy-Only Attack Cost Lower Bound</div>',
            unsafe_allow_html=True,
        )
        cost_df = build_cost_curve(
            network_hashrate,
            efficiency,
            electricity_price,
            min_share=0.05,
            max_share=0.51,
            points=35,
        )
        fig_cost = go.Figure()
        fig_cost.add_trace(go.Scatter(
            x=cost_df["attacker_percent"],
            y=cost_df["cost_usd_per_hour"],
            mode="lines",
            fill="tozeroy",
            name="Energy cost / hour",
            line=dict(color="#00C2FF", width=2.5),
            fillcolor="rgba(0,194,255,0.08)",
            hovertemplate=(
                "Attacker share: %{x:.1f}%<br>"
                "Cost/hour: $%{y:,.0f}<extra></extra>"
            ),
        ))
        fig_cost.add_vline(
            x=51,
            line_dash="dash",
            line_color="#FF4560",
            annotation_text="51%",
            annotation_font=dict(family="Rajdhani", color="#FF4560", size=11),
        )
        fig_cost.add_vline(
            x=attacker_percent,
            line_dash="dot",
            line_color="#F7931A",
            annotation_text=f"Selected {attacker_percent}%",
            annotation_font=dict(family="Rajdhani", color="#F7931A", size=11),
        )
        apply_chart_style(fig_cost)
        fig_cost.update_layout(
            xaxis_title="Attacker share q of total post-attack hash power (%)",
            yaxis_title="USD per hour",
            showlegend=False,
            height=350,
        )
        st.plotly_chart(fig_cost, use_container_width=True)
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.78rem;color:#6B7DA0;'
            'margin-top:0;line-height:1.55;">'
            'The x-axis is Nakamoto q: attacker fraction of total post-attack hash power. '
            'Required attacker hash rate is q/(1-q) times the current honest network. '
            'This is an energy-only lower bound. It excludes ASIC purchase, hardware '
            'availability, cooling, facilities, pool coordination, and market impact.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_prob:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'Double-Spend Probability vs Confirmations</div>',
            unsafe_allow_html=True,
        )
        prob_df = build_probability_curve([0.10, 0.20, 0.30, 0.40, q], max_confirmations=20)
        fig_prob = go.Figure()
        colors = {
            10.0: "#1CE87A",
            20.0: "#00C2FF",
            30.0: "#F7931A",
            40.0: "#FF4560",
            round(attacker_percent, 1): "#E8EDF5",
        }
        for pct, group in prob_df.groupby("attacker_percent"):
            pct_rounded = round(float(pct), 1)
            line_width = 4 if abs(pct_rounded - attacker_percent) < 0.001 else 2
            fig_prob.add_trace(go.Scatter(
                x=group["confirmations"],
                y=group["probability"],
                mode="lines+markers",
                name=f"q={pct_rounded:.0f}%",
                line=dict(color=colors.get(pct_rounded, "#E8EDF5"), width=line_width),
                marker=dict(size=5),
                hovertemplate=(
                    "Confirmations: %{x}<br>"
                    "Success probability: %{y:.6f}<extra></extra>"
                ),
            ))
        fig_prob.add_vline(
            x=confirmations,
            line_dash="dot",
            line_color="#6B7DA0",
            annotation_text=f"{confirmations} conf.",
            annotation_font=dict(family="Rajdhani", color="#6B7DA0", size=11),
        )
        apply_chart_style(fig_prob)
        fig_prob.update_layout(
            xaxis_title="Confirmations",
            yaxis_title="Attack success probability",
            yaxis_type="log",
            yaxis=dict(gridcolor="#1E2D5A", showgrid=True, type="log"),
            showlegend=True,
            legend=dict(
                x=0.98, y=0.98, xanchor="right",
                bgcolor="rgba(15,22,41,0.85)",
                bordercolor="#1E2D5A", borderwidth=1,
            ),
            height=350,
        )
        st.plotly_chart(fig_prob, use_container_width=True)
        st.markdown(
            f'<p style="font-family:Inter,sans-serif;font-size:0.78rem;color:#6B7DA0;'
            f'margin-top:0;line-height:1.55;">'
            f'For q={attacker_percent}% and {confirmations} confirmations, Nakamoto '
            f'catch-up probability is <strong style="color:{sec_color};">'
            f'{attack_prob:.6f}</strong>. The y-axis is logarithmic because security '
            f'improves exponentially as confirmations increase.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    col_table, col_formula = st.columns([3, 2], gap="medium")
    with col_table:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'Confirmation Risk Table</div>',
            unsafe_allow_html=True,
        )
        risk_rows = []
        q_values = [0.10, 0.20, 0.30, 0.40, q]
        q_values = sorted(set(round(v, 4) for v in q_values))
        for z in [1, 2, 3, 6, 10, 15, 20]:
            row = {"confirmations": z}
            for qv in q_values:
                row[f"q={qv*100:.0f}%"] = double_spend_probability(qv, z)
            risk_rows.append(row)
        risk_df = pd.DataFrame(risk_rows)

        th_s = (
            "padding:7px 10px;text-align:left;font-family:Rajdhani,sans-serif;"
            "font-size:0.72rem;color:#6B7DA0;text-transform:uppercase;"
            "letter-spacing:0.08em;border-bottom:2px solid #1E2D5A;"
        )
        headers = list(risk_df.columns)
        thead = (
            "<thead><tr>"
            + "".join(f'<th style="{th_s}">{h}</th>' for h in headers)
            + "</tr></thead>"
        )
        body = []
        for _, row in risk_df.iterrows():
            cells = [
                f'<td style="padding:7px 10px;border-bottom:1px solid #1E2D5A;'
                f'font-family:Rajdhani,sans-serif;font-weight:700;color:#E8EDF5;">'
                f'{int(row["confirmations"])}</td>'
            ]
            for col in headers[1:]:
                prob = float(row[col])
                color = "#1CE87A" if prob < 0.001 else "#00C2FF" if prob < 0.01 else "#F7931A" if prob < 0.05 else "#FF4560"
                cells.append(
                    f'<td style="padding:7px 10px;border-bottom:1px solid #1E2D5A;'
                    f'font-family:\'Share Tech Mono\',monospace;color:{color};">'
                    f'{prob:.6f}</td>'
                )
            body.append("<tr>" + "".join(cells) + "</tr>")
        st.markdown(
            f'<div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;">'
            f'{thead}<tbody>{"".join(body)}</tbody></table></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_formula:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'Model Assumptions</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.82rem;color:#6B7DA0;'
            'line-height:1.65;margin:0;">'
            'The network hash rate is estimated from current difficulty as '
            '<code>difficulty · 2^32 / 600</code>. Double-spend probability uses '
            'Nakamoto 2008 section 11 with a Poisson approximation. Here '
            '<code>q = A/(A+H)</code> is attacker fraction of total post-attack hash '
            'power, <code>p=1-q</code>, and <code>z</code> is confirmation depth. '
            'To reach q against current honest hash rate H, the attacker needs '
            '<code>A = q/(1-q) · H</code>. If <code>q ≥ 0.5</code>, the attacker '
            'eventually catches up with probability 1.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# M7 — DIFFICULTY PREDICTOR
# ─────────────────────────────────────────────────────────────────────────────
def render_m7() -> None:
    module_header("M7 — DIFFICULTY PREDICTOR")

    col_ctrl1, col_ctrl2, _ = st.columns([2, 2, 3])
    with col_ctrl1:
        n_periods = st.slider(
            "Historical adjustment periods",
            min_value=12,
            max_value=40,
            value=24,
            step=2,
            key="m7_n_periods",
            on_change=_clear_adj_cache,
        )
    with col_ctrl2:
        test_fraction_pct = st.slider(
            "Holdout test split",
            min_value=20,
            max_value=40,
            value=30,
            step=5,
            key="m7_test_fraction",
        )

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    try:
        blocks = load_adjustment_blocks(n_periods)
        df = build_adjustment_dataframe(blocks)
        result = train_and_evaluate(df, test_fraction=test_fraction_pct / 100.0)
    except Exception as e:
        render_error(f"Difficulty predictor error: {e}")
        return

    evaluations = result["evaluations"]
    best_name = result["best_model_name"]
    best_eval = evaluations[best_name]
    dataset = result["dataset"]
    train_df = result["train_df"]
    test_df = result["test_df"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Usable Samples", f"{len(dataset):,}")
    c2.metric("Train / Test", f"{len(train_df)} / {len(test_df)}")
    c3.metric("Best Model", best_name)
    c4.metric("Holdout MAE", f"{best_eval['mae']:.3f} pp")
    forecast_color = "#1CE87A" if result["latest_pct_change"] >= 0 else "#FF4560"
    with c5:
        st.markdown(
            custom_metric(
                "Latest Retarget Pred.",
                f"{result['latest_pct_change']:+.2f}%",
                forecast_color,
                forecast_color,
            ),
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    col_chart, col_metrics = st.columns([3, 2], gap="medium")
    with col_chart:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'Holdout Prediction — Retarget Change Backtest</div>',
            unsafe_allow_html=True,
        )
        holdout = result["holdout_predictions"].copy()
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(
            x=holdout["date"],
            y=holdout["target_pct_change"],
            mode="lines+markers",
            name="Actual retarget change",
            line=dict(color="#1CE87A", width=2.5),
            marker=dict(size=8),
            hovertemplate="%{x|%Y-%m-%d}<br>Actual: %{y:+.3f}%<extra></extra>",
        ))
        model_colors = {
            "Linear Regression": "#00C2FF",
            "Random Forest": "#F7931A",
        }
        for model_name in evaluations:
            col_name = f"{model_name} prediction"
            fig_pred.add_trace(go.Scatter(
                x=holdout["date"],
                y=holdout[col_name],
                mode="lines+markers",
                name=model_name,
                line=dict(
                    color=model_colors.get(model_name, "#E8EDF5"),
                    width=2,
                    dash="dash",
                ),
                marker=dict(size=6),
                hovertemplate=f"{model_name}<br>%{{x|%Y-%m-%d}}<br>Pred: %{{y:+.3f}}%<extra></extra>",
            ))
        fig_pred.add_hline(
            y=0,
            line_dash="dot",
            line_color="#6B7DA0",
        )
        apply_chart_style(fig_pred)
        fig_pred.update_layout(
            xaxis_title="Adjustment date",
            yaxis_title="Difficulty retarget change (%)",
            height=360,
            legend=dict(
                x=0.02, y=0.98, xanchor="left",
                bgcolor="rgba(15,22,41,0.85)",
                bordercolor="#1E2D5A", borderwidth=1,
            ),
        )
        st.plotly_chart(fig_pred, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_metrics:
        st.markdown(
            '<div class="card"><div class="card-title">'
            'Regression Metrics</div>',
            unsafe_allow_html=True,
        )
        rows = []
        for model_name, evaluation in evaluations.items():
            is_best = model_name == best_name
            rows.extend([
                (f"{model_name} MAE", f"{evaluation['mae']:.3f} pp", "#1CE87A" if is_best else "#E8EDF5"),
                (f"{model_name} RMSE", f"{evaluation['rmse']:.3f} pp", "#00C2FF"),
                (f"{model_name} R²", "N/A" if pd.isna(evaluation["r2"]) else f"{evaluation['r2']:.3f}", "#F7931A"),
            ])
        rows.extend([
            ("Previous Difficulty", f"{result['previous_difficulty']:.3e}", "#E8EDF5"),
            ("Actual Difficulty", f"{result['actual_difficulty']:.3e}", "#E8EDF5"),
            ("Predicted Adjusted Difficulty", f"{result['predicted_adjusted_difficulty']:.3e}", forecast_color),
        ])
        table_rows = "".join(
            f'<tr onmouseover="this.style.background=\'rgba(0,194,255,0.04)\'"'
            f' onmouseout="this.style.background=\'transparent\'">'
            f'<td style="padding:7px 10px;border-bottom:1px solid #1E2D5A;'
            f'font-family:Rajdhani,sans-serif;font-size:0.82rem;color:#6B7DA0;">{label}</td>'
            f'<td style="padding:7px 10px;border-bottom:1px solid #1E2D5A;'
            f'font-family:Rajdhani,sans-serif;font-size:0.9rem;font-weight:700;'
            f'color:{color};text-align:right;">{value}</td>'
            f'</tr>'
            for label, value, color in rows
        )
        st.markdown(
            f'<table style="width:100%;border-collapse:collapse;">'
            f'<tbody>{table_rows}</tbody></table>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.77rem;color:#6B7DA0;'
            'line-height:1.6;margin-top:12px;">'
            'The split is chronological: older adjustment periods train the model, '
            'newer periods form the holdout test set. This avoids training on future data.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)

    st.markdown(
        '<div class="card"><div class="card-title">'
        'Feature Set And Model Rationale</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-family:Inter,sans-serif;font-size:0.82rem;color:#6B7DA0;'
        'line-height:1.65;margin:0;">'
        'M7 is a second AI approach, different from M4. M4 is unsupervised anomaly '
        'detection on block inter-arrival times; M7 is supervised regression on '
        'historical difficulty adjustment periods. Features include the previous '
        'difficulty, actual/target period ratio, previous percentage changes, and '
        '3-period rolling averages. The target is the retarget percentage change '
        'applied at each completed adjustment event.<br><br>'
        '<strong style="color:#E8EDF5;">Why include Linear Regression?</strong> '
        'It is a simple baseline, not the expected best model. If Random Forest '
        'does not beat the linear baseline, then the extra model complexity is not '
        'adding value. If Random Forest clearly improves MAE/RMSE/R², that is '
        'evidence that the difficulty retarget behaviour is better captured by a '
        'non-linear model.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_ethereum_m1() -> None:
    module_header("M1 — ETHEREUM PROOF OF STAKE ACTIVITY MONITOR")
    try:
        blocks = load_eth_recent_blocks(24)
    except Exception as e:
        render_error(f"Could not fetch Ethereum data: {e}")
        return
    if not blocks:
        render_error("No Ethereum block data returned.")
        return

    latest = blocks[0]
    ordered = sorted(blocks, key=lambda b: b["number"])
    block_times = [
        ordered[i]["timestamp"] - ordered[i - 1]["timestamp"]
        for i in range(1, len(ordered))
        if ordered[i]["timestamp"] > ordered[i - 1]["timestamp"]
    ]
    avg_block_time = float(np.mean(block_times)) if block_times else 0.0
    latest_gas_pct = latest["gas_utilization"] * 100
    base_fee = latest["base_fee_gwei"]
    stress_score = max(latest_gas_pct, min(base_fee * 8, 100))
    if stress_score >= 75:
        stress_label = "HIGH"
        banner_text = "Gas demand above normal range"
        banner_copy = "Recent blocks are close to the EIP-1559 gas target or fees are elevated."
        banner_color = "#FF4560"
    elif stress_score >= 45:
        stress_label = "MEDIUM"
        banner_text = "Gas demand inside normal range"
        banner_copy = "Demand is close to the target gas budget."
        banner_color = "#1CE87A"
    else:
        stress_label = "LOW"
        banner_text = "Gas demand below normal range"
        banner_copy = "Recent blocks are using a modest share of available gas."
        banner_color = "#00D084"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Block Height", f"{latest['number']:,}")
    c2.metric("Base Fee", f"{base_fee:.2f} gwei")
    c3.metric("Gas Used", f"{latest_gas_pct:.1f}%")
    c4.metric("Block Time", f"{avg_block_time:.1f} s")

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    col_info, col_stress = st.columns([3, 2], gap="medium")
    with col_info:
        st.markdown(
            '<div class="card"><div class="card-title">Latest Block Snapshot</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="field-label">Hash</p>'
            f'<p class="field-val">{latest["hash"]}</p>'
            '<p class="field-label">Timestamp</p>'
            f'<p class="field-val">{latest["datetime"].strftime("%Y-%m-%d %H:%M:%S UTC")}</p>',
            unsafe_allow_html=True,
        )
        ic1, ic2 = st.columns(2)
        ic1.metric("Transactions", f"{latest['tx_count']:,}")
        ic2.metric("Gas Price", f"{base_fee:.2f} gwei")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_stress:
        st.markdown(
            '<div class="card"><div class="card-title">Network Stress</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="background:{banner_color}22;border:1px solid {banner_color}88;'
            f'border-radius:8px;padding:16px;margin-bottom:18px;'
            f'font-family:Rajdhani,sans-serif;font-size:1.1rem;font-weight:700;'
            f'color:{banner_color};">{banner_text}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            custom_metric("Network Stress", stress_label, banner_color, banner_color),
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p style="font-family:Inter,sans-serif;font-size:0.8rem;color:#6B7DA0;'
            f'line-height:1.6;margin-top:14px;">{banner_copy}</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    st.markdown(
        '<div class="card"><div class="card-title">Recent Gas Utilization</div>',
        unsafe_allow_html=True,
    )
    df = pd.DataFrame({
        "time": [b["datetime"] for b in ordered],
        "gas_used_pct": [b["gas_utilization"] * 100 for b in ordered],
        "block": [b["number"] for b in ordered],
    })
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["gas_used_pct"],
        mode="lines",
        line=dict(color=active_crypto.primary_color, width=3, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(98,126,234,0.18)",
        hovertemplate="Block %{customdata}<br>Gas used: %{y:.1f}%<extra></extra>",
        customdata=df["block"],
        name="Gas used",
    ))
    fig.add_hline(
        y=50,
        line_dash="dash",
        line_color=active_crypto.secondary_color,
        annotation_text="EIP-1559 target utilization",
        annotation_font=dict(family="Rajdhani", color=active_crypto.secondary_color, size=11),
    )
    apply_chart_style(fig)
    fig.update_layout(
        xaxis_title="Recent blocks",
        yaxis_title="Gas used %",
        height=340,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("50% is the EIP-1559 target utilization. Ethereum block production is PoS; gas pressure replaces PoW hash-rate pressure here.")
    st.markdown("</div>", unsafe_allow_html=True)


def render_ethereum_m2() -> None:
    module_header("M2 — ETHEREUM BLOCK HEADER ANALYZER")
    try:
        latest = load_eth_recent_blocks(1)[0]
    except Exception as e:
        render_error(f"Could not fetch Ethereum block header data: {e}")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Block Number", f"{latest['number']:,}")
    c2.metric("Transactions", f"{latest['tx_count']:,}")
    c3.metric("Gas Limit", f"{latest['gas_limit']:,}")
    c4.metric("Base Fee", f"{latest['base_fee_gwei']:.2f} gwei")

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    col_fields, col_roots = st.columns(2, gap="medium")
    with col_fields:
        st.markdown('<div class="card"><div class="card-title">Execution Block Fields</div>', unsafe_allow_html=True)
        rows = [
            ("Hash", latest["hash"]),
            ("Parent Hash", latest["parent_hash"]),
            ("Timestamp", latest["datetime"].strftime("%Y-%m-%d %H:%M:%S UTC")),
            ("Fee Recipient", latest["validator"]),
            ("Gas Used / Limit", f"{latest['gas_used']:,} / {latest['gas_limit']:,}"),
        ]
        st.markdown(
            "".join(f'<p class="field-label">{k}</p><p class="field-val">{v}</p>' for k, v in rows),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with col_roots:
        st.markdown('<div class="card"><div class="card-title">State Commitments</div>', unsafe_allow_html=True)
        rows = [
            ("State Root", latest["state_root"]),
            ("Transactions Root", latest["transactions_root"]),
            ("Receipts Root", latest["receipts_root"]),
        ]
        st.markdown(
            "".join(f'<p class="field-label">{k}</p><p class="field-val">{v}</p>' for k, v in rows),
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.78rem;color:#6B7DA0;'
            'line-height:1.55;">These roots are Ethereum Merkle-Patricia trie commitments. '
            'They are the Ethereum analogue of committing to transaction/state data, but '
            'they are not Bitcoin-style binary Merkle trees.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def render_litecoin_m1() -> None:
    module_header("M1 — LITECOIN SCRYPT PROOF OF WORK MONITOR")
    try:
        blocks = load_ltc_recent_blocks(7)
    except Exception as e:
        render_error(f"Could not fetch Litecoin data: {e}")
        return
    if not blocks:
        render_error("No Litecoin block data returned.")
        return

    latest = blocks[0]
    difficulty = float(latest["difficulty"])
    hashrate = difficulty * (2 ** 32) / 150
    inter_times = get_inter_block_times(blocks)
    avg_time = int(np.mean(inter_times)) if inter_times else 0
    target_hex = f"{bits_to_target(int(latest['bits'])):064x}" if latest.get("bits") else "N/A"
    ratio = avg_time / 150 if avg_time else 0
    if ratio >= 1.25:
        stress_label = "MEDIUM"
        banner_text = "Block time above target"
        banner_copy = "Recent Litecoin block production is slower than the 150s target."
        banner_color = "#F7931A"
    elif ratio <= 0.75 and ratio > 0:
        stress_label = "MEDIUM"
        banner_text = "Block time below target"
        banner_copy = "Recent Litecoin blocks are arriving faster than the 150s target."
        banner_color = "#1CE87A"
    else:
        stress_label = "LOW"
        banner_text = "Block time inside normal range"
        banner_copy = "Recent Litecoin block timing is close to target."
        banner_color = active_crypto.primary_color

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Block Height", f"{latest['height']:,}")
    c2.metric("Difficulty", f"{difficulty:.2e}")
    c3.metric("Est. Hash Rate", f"{hashrate / 1e12:.2f} TH/s")
    c4.metric("Block Time", f"{avg_time} s")

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    col_info, col_stress = st.columns([3, 2], gap="medium")
    with col_info:
        st.markdown('<div class="card"><div class="card-title">Latest Block Snapshot</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="field-label">Hash</p>'
            f'<p class="field-val">{latest["id"]}</p>'
            '<p class="field-label">Timestamp</p>'
            f'<p class="field-val">{latest["datetime"].strftime("%Y-%m-%d %H:%M:%S UTC") if latest["datetime"] else "N/A"}</p>',
            unsafe_allow_html=True,
        )
        ic1, ic2 = st.columns(2)
        ic1.metric("Transactions", f"{latest['tx_count']:,}")
        ic2.metric("Nonce", f"{latest['nonce']:,}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_stress:
        st.markdown('<div class="card"><div class="card-title">Scrypt PoW Context</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:{banner_color}22;border:1px solid {banner_color}88;'
            f'border-radius:8px;padding:16px;margin-bottom:18px;'
            f'font-family:Rajdhani,sans-serif;font-size:1.1rem;font-weight:700;'
            f'color:{banner_color};">{banner_text}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(custom_metric("Network Stress", stress_label, banner_color, banner_color), unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-family:Inter,sans-serif;font-size:0.8rem;color:#6B7DA0;'
            f'line-height:1.6;margin-top:14px;">{banner_copy}</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">Litecoin Block Arrival Times</div>', unsafe_allow_html=True)
    if inter_times:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(inter_times) + 1)),
            y=inter_times,
            mode="lines",
            line=dict(color=active_crypto.primary_color, width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(0,208,132,0.14)",
            name="Inter-block time",
            hovertemplate="Interval %{x}<br>%{y:.0f}s<extra></extra>",
        ))
        fig.add_hline(
            y=150,
            line_dash="dash",
            line_color=active_crypto.secondary_color,
            annotation_text="150s target",
            annotation_font=dict(family="Rajdhani", color=active_crypto.secondary_color, size=11),
        )
        apply_chart_style(fig)
        fig.update_layout(xaxis_title="Most recent intervals", yaxis_title="Seconds", height=340, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        '<p style="font-family:Inter,sans-serif;font-size:0.78rem;color:#6B7DA0;line-height:1.55;">'
        'Litecoin is PoW like Bitcoin, but uses Scrypt and targets 150 seconds per block. '
        'Difficulty/target logic is comparable; mining hardware assumptions are not.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">Decoded Target Threshold</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="field-label">Target threshold from bits</p>'
        f'<p class="field-val">{target_hex}</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_litecoin_m2() -> None:
    module_header("M2 — LITECOIN BLOCK HEADER ANALYZER")
    try:
        latest = load_ltc_recent_blocks(1)[0]
    except Exception as e:
        render_error(f"Could not fetch Litecoin block data: {e}")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Height", f"{latest['height']:,}")
    c2.metric("Version", f"{latest['version']}")
    c3.metric("Nonce", f"{latest['nonce']:,}")
    c4.metric("Size", f"{latest['size']:,} bytes")

    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">Litecoin Header Fields From Explorer API</div>', unsafe_allow_html=True)
    rows = [
        ("Block Hash", latest["id"]),
        ("Previous Hash", latest["previous_hash"]),
        ("Merkle Root", latest["merkle_root"]),
        ("Timestamp", latest["datetime"].strftime("%Y-%m-%d %H:%M:%S UTC") if latest["datetime"] else "N/A"),
        ("Bits", f"0x{latest['bits']:08x}"),
        ("Nonce", f"{latest['nonce']:,}"),
    ]
    st.markdown("".join(f'<p class="field-label">{k}</p><p class="field-val">{v}</p>' for k, v in rows), unsafe_allow_html=True)
    st.markdown(
        '<p style="font-family:Inter,sans-serif;font-size:0.78rem;color:#6B7DA0;line-height:1.55;">'
        'This is the Litecoin analogue of the Bitcoin header view. Full manual PoW verification '
        'requires reconstructing the raw 80-byte header and applying Litecoin Scrypt PoW, not '
        'Bitcoin double-SHA256. That distinction is intentional.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_crypto_variant_note(crypto: CryptoConfig, spec: ModuleSpec) -> None:
    module_header(spec.title.replace("DIFFICULTY", "CONSENSUS"))
    mode = crypto.module_modes.get(spec.id, "methodological_variant")
    st.markdown(
        f'<div class="card"><div class="card-title">{crypto.name} module variant</div>'
        f'<p style="font-family:Inter,sans-serif;font-size:0.84rem;color:#6B7DA0;line-height:1.65;">'
        f'This module needs a {crypto.name}-specific implementation before it can be graded as a '
        f'full analytical module. It is registered here with the correct academic mapping so the '
        f'next implementation phase does not copy Bitcoin assumptions blindly.</p>'
        f'<p class="field-label">Purpose</p><p class="field-val">{spec.academic_purpose}</p>'
        f'<p class="field-label">Variant</p><p class="field-val">{mode}</p>'
        f'<p class="field-label">Data source</p><p class="field-val">{crypto.data_source}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_ethereum_m3() -> None:
    module_header("M3 — ETHEREUM GAS AND BLOCK ACTIVITY HISTORY")
    try:
        blocks = load_eth_recent_blocks(40)
    except Exception as e:
        render_error(f"Could not fetch Ethereum history: {e}")
        return
    ordered = sorted(blocks, key=lambda b: b["number"])
    df = pd.DataFrame({
        "number": [b["number"] for b in ordered],
        "time": [b["datetime"] for b in ordered],
        "gas_utilization": [b["gas_utilization"] * 100 for b in ordered],
        "base_fee_gwei": [b["base_fee_gwei"] for b in ordered],
        "tx_count": [b["tx_count"] for b in ordered],
    })
    df["block_time"] = pd.Series([b["timestamp"] for b in ordered]).diff().fillna(0)
    df["fee_change_pct"] = df["base_fee_gwei"].pct_change() * 100
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Blocks Sampled", f"{len(df):,}")
    c2.metric("Avg Gas Util.", f"{df['gas_utilization'].mean():.1f}%")
    c3.metric("Avg Base Fee", f"{df['base_fee_gwei'].mean():.2f} gwei")
    c4.metric("Avg Block Time", f"{df['block_time'].iloc[1:].mean():.1f} s")
    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    col_chart, col_table = st.columns([3, 2], gap="medium")
    with col_chart:
        st.markdown('<div class="card"><div class="card-title">Gas Market History</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["time"], y=df["gas_utilization"], mode="lines+markers", name="Gas utilization (%)", line=dict(color=active_crypto.primary_color, width=2.5)))
        fig.add_trace(go.Scatter(x=df["time"], y=df["base_fee_gwei"], mode="lines+markers", name="Base fee (gwei)", line=dict(color=active_crypto.secondary_color, width=2), yaxis="y2"))
        fig.add_hline(y=50, line_dash="dash", line_color="#6B7DA0", annotation_text="EIP-1559 target")
        apply_chart_style(fig)
        fig.update_layout(height=360, xaxis_title="Time", yaxis_title="Gas utilization (%)", yaxis2=dict(title="Base fee (gwei)", overlaying="y", side="right", gridcolor="#1E2D5A"), legend=dict(bgcolor="rgba(15,22,41,0.85)"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_table:
        st.markdown('<div class="card"><div class="card-title">Recent Blocks</div>', unsafe_allow_html=True)
        rows = []
        for _, row in df.tail(10).iloc[::-1].iterrows():
            rows.append(
                f'<tr><td style="padding:6px 8px;border-bottom:1px solid #1E2D5A;color:#E8EDF5;font-family:Rajdhani,sans-serif;">{int(row["number"]):,}</td>'
                f'<td style="padding:6px 8px;border-bottom:1px solid #1E2D5A;color:{active_crypto.primary_color};font-family:Rajdhani,sans-serif;">{row["gas_utilization"]:.1f}%</td>'
                f'<td style="padding:6px 8px;border-bottom:1px solid #1E2D5A;color:{active_crypto.secondary_color};font-family:Rajdhani,sans-serif;">{row["base_fee_gwei"]:.2f}</td>'
                f'<td style="padding:6px 8px;border-bottom:1px solid #1E2D5A;color:#6B7DA0;font-family:Rajdhani,sans-serif;">{int(row["tx_count"]):,}</td></tr>'
            )
        st.markdown(
            '<table style="width:100%;border-collapse:collapse;">'
            '<thead><tr><th>Block</th><th>Gas</th><th>Fee</th><th>Tx</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>',
            unsafe_allow_html=True,
        )
        st.caption("Ethereum has no Bitcoin-style difficulty retarget after The Merge; gas pressure and base fee are the meaningful history.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_litecoin_m3() -> None:
    module_header("M3 — LITECOIN DIFFICULTY AND TIMING HISTORY")
    try:
        blocks = load_ltc_recent_blocks(20)
    except Exception as e:
        render_error(f"Could not fetch Litecoin history: {e}")
        return
    ordered = sorted(blocks, key=lambda b: b["height"])
    df = pd.DataFrame(ordered)
    df["block_time"] = df["timestamp"].diff()
    df["hashrate_ths"] = df["difficulty"] * (2 ** 32) / 150 / 1e12
    df["time_ratio"] = df["block_time"] / 150
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Blocks Sampled", f"{len(df):,}")
    c2.metric("Latest Difficulty", f"{float(df['difficulty'].iloc[-1]):.2e}")
    c3.metric("Avg Block Time", f"{df['block_time'].dropna().mean():.0f} s")
    c4.metric("Est. Hash Rate", f"{df['hashrate_ths'].iloc[-1]:.2f} TH/s")
    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    col_time, col_hash = st.columns(2, gap="medium")
    with col_time:
        st.markdown('<div class="card"><div class="card-title">Recent Litecoin Timing</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["height"], y=df["block_time"], marker_color=active_crypto.primary_color, name="Block time"))
        fig.add_hline(y=150, line_dash="dash", line_color=active_crypto.secondary_color, annotation_text="150s target")
        apply_chart_style(fig)
        fig.update_layout(height=330, xaxis_title="Height", yaxis_title="Seconds", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_hash:
        st.markdown('<div class="card"><div class="card-title">Difficulty And Estimated Hash Rate</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df["height"], y=df["difficulty"], mode="lines+markers", name="Difficulty", line=dict(color=active_crypto.primary_color, width=2.5)))
        fig2.add_trace(go.Scatter(x=df["height"], y=df["hashrate_ths"], mode="lines+markers", name="TH/s", line=dict(color=active_crypto.secondary_color, width=2), yaxis="y2"))
        apply_chart_style(fig2)
        fig2.update_layout(height=330, xaxis_title="Height", yaxis_title="Difficulty", yaxis2=dict(title="TH/s", overlaying="y", side="right", gridcolor="#1E2D5A"), legend=dict(bgcolor="rgba(15,22,41,0.85)"))
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Litecoin keeps PoW difficulty, but uses a 150-second target and Scrypt mining.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_ethereum_m4() -> None:
    module_header("M4 — ETHEREUM ACTIVITY ANOMALY DETECTOR")
    try:
        blocks = load_eth_recent_blocks(60)
    except Exception as e:
        render_error(f"Could not fetch Ethereum activity data: {e}")
        return
    ordered = sorted(blocks, key=lambda b: b["number"])
    df = pd.DataFrame({
        "number": [b["number"] for b in ordered],
        "time": [b["datetime"] for b in ordered],
        "gas_utilization": [b["gas_utilization"] * 100 for b in ordered],
        "tx_count": [b["tx_count"] for b in ordered],
        "base_fee_gwei": [b["base_fee_gwei"] for b in ordered],
    })
    df["gas_z"] = stats.zscore(df["gas_utilization"], nan_policy="omit")
    df["fee_z"] = stats.zscore(df["base_fee_gwei"], nan_policy="omit")
    df["anomaly"] = df["gas_z"].abs() >= 2.0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Blocks Analyzed", f"{len(df):,}")
    c2.metric("Mean Gas Util.", f"{df['gas_utilization'].mean():.1f}%")
    c3.metric("Std. Dev.", f"{df['gas_utilization'].std():.1f} pp")
    c4.metric("Gas Anomalies", f"{int(df['anomaly'].sum())}")
    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    col_timeline, col_dist = st.columns([3, 2], gap="medium")
    with col_timeline:
        st.markdown('<div class="card"><div class="card-title">Gas Utilization Anomaly Timeline</div>', unsafe_allow_html=True)
        fig = go.Figure()
        normal = df[~df["anomaly"]]
        anomalous = df[df["anomaly"]]
        fig.add_trace(go.Scatter(x=normal["time"], y=normal["gas_utilization"], mode="markers", marker=dict(color=active_crypto.secondary_color, size=6), name="Normal"))
        fig.add_trace(go.Scatter(x=anomalous["time"], y=anomalous["gas_utilization"], mode="markers", marker=dict(color="#FF4560", size=10, symbol="x"), name="|z| >= 2"))
        fig.add_hline(y=df["gas_utilization"].mean(), line_dash="dash", line_color="#6B7DA0", annotation_text="Mean")
        apply_chart_style(fig)
        fig.update_layout(height=340, xaxis_title="Time", yaxis_title="Gas utilization (%)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_dist:
        st.markdown('<div class="card"><div class="card-title">Distribution And Scores</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(x=df["gas_utilization"], nbinsx=18, marker_color=active_crypto.primary_color, name="Gas util."))
        fig2.add_vline(x=df["gas_utilization"].mean(), line_dash="dash", line_color=active_crypto.secondary_color, annotation_text="Mean")
        apply_chart_style(fig2)
        fig2.update_layout(height=260, xaxis_title="Gas utilization (%)", yaxis_title="Blocks", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Ethereum anomaly detection uses gas pressure z-scores. This is the PoS/EIP-1559 analogue of timing anomaly analysis.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_litecoin_m4() -> None:
    module_header("M4 — LITECOIN INTER-ARRIVAL ANOMALY DETECTOR")
    try:
        blocks = load_ltc_recent_blocks(20)
    except Exception as e:
        render_error(f"Could not fetch Litecoin timing data: {e}")
        return
    df = build_inter_arrival_df(blocks)
    if df.empty:
        render_error("Not enough Litecoin intervals for anomaly detection.")
        return
    times = df["inter_arrival"].values.astype(float)
    lam = 1 / float(times.mean())
    mask = detect_statistical(times, lam)
    df["anomaly"] = mask
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Intervals", f"{len(df):,}")
    c2.metric("Mean", f"{times.mean():.0f} s")
    c3.metric("Target", "150 s")
    c4.metric("Anomalies", f"{int(mask.sum())}")
    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    col_timeline, col_hist = st.columns([3, 2], gap="medium")
    with col_timeline:
        st.markdown('<div class="card"><div class="card-title">Litecoin Timing Outliers</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[~mask]["datetime"], y=df[~mask]["inter_arrival"], mode="markers+lines", marker=dict(color=active_crypto.secondary_color, size=6), line=dict(color=active_crypto.secondary_color, width=1), name="Normal"))
        fig.add_trace(go.Scatter(x=df[mask]["datetime"], y=df[mask]["inter_arrival"], mode="markers", marker=dict(color="#FF4560", size=10, symbol="x"), name="Anomaly"))
        fig.add_hline(y=150, line_dash="dash", line_color=active_crypto.primary_color, annotation_text="150s target")
        apply_chart_style(fig)
        fig.update_layout(height=340, xaxis_title="Time", yaxis_title="Seconds")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_hist:
        st.markdown('<div class="card"><div class="card-title">Inter-Arrival Distribution</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(x=times, nbinsx=12, marker_color=active_crypto.primary_color))
        fig2.add_vline(x=150, line_dash="dash", line_color=active_crypto.secondary_color, annotation_text="150s")
        apply_chart_style(fig2)
        fig2.update_layout(height=260, xaxis_title="Seconds", yaxis_title="Count", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Same anomaly idea as Bitcoin, but with Litecoin's 150-second target and recent Scrypt PoW blocks.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_ethereum_m5() -> None:
    module_header("M5 — ETHEREUM STATE COMMITMENTS")
    render_ethereum_m2()


def render_litecoin_m5() -> None:
    module_header("M5 — LITECOIN MERKLE PROOF")
    try:
        latest = load_ltc_recent_blocks(1)[0]
        txids = latest["raw"].get("txids", [])
    except Exception as e:
        render_error(f"Could not fetch Litecoin Merkle data: {e}")
        return
    if not txids:
        c1, c2, c3 = st.columns(3)
        c1.metric("Height", f"{latest['height']:,}")
        c2.metric("Transactions", f"{latest['tx_count']:,}")
        c3.metric("Data Source", latest.get("source", "Explorer"))
        st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
        st.markdown('<div class="card"><div class="card-title">Litecoin Merkle Commitment</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="field-label">Block hash</p>'
            f'<p class="field-val">{latest["id"]}</p>'
            '<p class="field-label">Merkle root</p>'
            f'<p class="field-val">{latest["merkle_root"]}</p>'
            '<p style="font-family:Inter,sans-serif;font-size:0.82rem;color:#6B7DA0;line-height:1.6;">'
            'The current Litecoin source returns block-level Merkle commitments but not the full txid list. '
            'So this view shows the authenticated root instead of fabricating an inclusion proof.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return
    tx_index = min(len(txids) // 2, len(txids) - 1)
    try:
        proof = build_and_verify_merkle_proof(txids, tx_index, latest["merkle_root"])
    except Exception as e:
        render_error(f"Merkle computation error: {e}")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Height", f"{latest['height']:,}")
    c2.metric("Transactions", f"{len(txids):,}")
    c3.metric("Proof Length", f"{proof['proof_length']} hashes")
    c4.metric("Status", "VALID" if proof["valid"] else "INVALID")
    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">Litecoin Transaction Inclusion</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="field-label">Selected txid</p>'
        f'<p class="field-val">{proof["selected_txid"]}</p>'
        '<p class="field-label">Computed root</p>'
        f'<p class="field-val">{proof["computed_root"]}</p>'
        '<p class="field-label">Header root</p>'
        f'<p class="field-val">{latest["merkle_root"]}</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_ethereum_m6() -> None:
    module_header("M6 — ETHEREUM POS SECURITY SCORE")
    try:
        blocks = load_eth_recent_blocks(32)
    except Exception as e:
        render_error(f"Could not fetch Ethereum data: {e}")
        return
    latest = blocks[0]
    ordered = sorted(blocks, key=lambda b: b["number"])
    gas_values = np.array([b["gas_utilization"] * 100 for b in ordered], dtype=float)
    fee_values = np.array([b["base_fee_gwei"] for b in ordered], dtype=float)
    fee_pressure = min(float(np.mean(fee_values)) * 8, 100)
    gas_pressure = float(np.mean(gas_values))
    liveness_score = max(0.0, 100.0 - abs(float(np.mean(np.diff([b["timestamp"] for b in ordered]))) - 12.0) * 4)
    stress_index = 0.45 * gas_pressure + 0.35 * fee_pressure + 0.20 * (100 - liveness_score)
    security_label = "HIGH" if stress_index < 45 else "MEDIUM" if stress_index < 70 else "ELEVATED"
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Latest Block", f"{latest['number']:,}")
    c2.metric("Avg Gas Util.", f"{gas_pressure:.1f}%")
    c3.metric("Avg Base Fee", f"{np.mean(fee_values):.2f} gwei")
    c4.metric("Security State", security_label)
    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    col_score, col_model = st.columns([3, 2], gap="medium")
    with col_score:
        st.markdown('<div class="card"><div class="card-title">PoS Network Pressure Index</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Gas pressure", "Fee pressure", "Liveness"],
            y=[gas_pressure, fee_pressure, liveness_score],
            marker_color=[active_crypto.primary_color, active_crypto.secondary_color, "#1CE87A"],
        ))
        fig.add_hline(y=70, line_dash="dash", line_color="#FF4560", annotation_text="elevated")
        apply_chart_style(fig)
        fig.update_layout(height=320, yaxis_title="Score / 100", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_model:
        st.markdown('<div class="card"><div class="card-title">Model Assumptions</div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.82rem;color:#6B7DA0;line-height:1.65;">'
            'Ethereum security is economic stake security, not ASIC energy cost. This score uses observable '
            'network pressure as a dashboard proxy: gas utilization, base fee pressure, and block-production '
            'liveness. A full research-grade PoS score would add validator stake, finality, slashing and client diversity.</p>',
            unsafe_allow_html=True,
        )
        st.markdown(custom_metric("Composite Stress", f"{stress_index:.1f}/100", active_crypto.primary_color, active_crypto.primary_color), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_litecoin_m6() -> None:
    module_header("M6 — LITECOIN SECURITY SCORE")
    try:
        latest = load_ltc_recent_blocks(1)[0]
    except Exception as e:
        render_error(f"Could not fetch Litecoin data: {e}")
        return
    network_hashrate = float(latest["difficulty"]) * (2 ** 32) / 150
    attack_hashrate = estimate_attack_hashrate(network_hashrate, 0.30)
    prob_6 = double_spend_probability(0.30, 6)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Network Hash Rate", f"{network_hashrate / 1e12:.2f} TH/s")
    c2.metric("30% Attack Hashrate", f"{attack_hashrate / 1e12:.2f} TH/s")
    c3.metric("P(success), 6 conf.", f"{prob_6:.4f}")
    c4.metric("Hash Function", "Scrypt")
    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    col_prob, col_note = st.columns([3, 2], gap="medium")
    with col_prob:
        st.markdown('<div class="card"><div class="card-title">Double-Spend Probability Curve</div>', unsafe_allow_html=True)
        prob_df = build_probability_curve([0.10, 0.20, 0.30, 0.40], max_confirmations=20)
        fig = go.Figure()
        for pct, group in prob_df.groupby("attacker_percent"):
            fig.add_trace(go.Scatter(x=group["confirmations"], y=group["probability"], mode="lines+markers", name=f"q={pct:.0f}%"))
        apply_chart_style(fig)
        fig.update_layout(height=330, xaxis_title="Confirmations", yaxis_title="Attack success probability", yaxis_type="log", legend=dict(bgcolor="rgba(15,22,41,0.85)"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_note:
        st.markdown('<div class="card"><div class="card-title">Scrypt Security Caveat</div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:0.82rem;color:#6B7DA0;line-height:1.65;">'
            'The Nakamoto attacker-share probability model transfers to Litecoin as PoW. The cost model does not transfer directly from Bitcoin, because Litecoin mining uses Scrypt-specific hardware economics.</p>',
            unsafe_allow_html=True,
        )
        st.markdown(custom_metric("Consensus", "PoW / Scrypt", active_crypto.primary_color, active_crypto.primary_color), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_ethereum_m7() -> None:
    module_header("M7 — ETHEREUM GAS UTILIZATION PREDICTOR")
    try:
        blocks = load_eth_recent_blocks(60)
    except Exception as e:
        render_error(f"Could not fetch Ethereum prediction data: {e}")
        return
    ordered = sorted(blocks, key=lambda b: b["number"])
    y = np.array([b["gas_utilization"] * 100 for b in ordered], dtype=float)
    x = np.arange(len(y), dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = intercept + slope * x
    pred = float(intercept + slope * len(y))
    mae = float(np.mean(np.abs(y - fitted)))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Samples", f"{len(y):,}")
    c2.metric("Current Gas Util.", f"{y[-1]:.1f}%")
    c3.metric("Next Forecast", f"{max(0, min(100, pred)):.1f}%")
    c4.metric("In-sample MAE", f"{mae:.2f} pp")
    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">Gas Utilization Forecast Backtest</div>', unsafe_allow_html=True)
    fig = go.Figure()
    times = [b["datetime"] for b in ordered]
    fig.add_trace(go.Scatter(x=times, y=y, mode="lines+markers", name="Observed gas utilization", line=dict(color=active_crypto.primary_color, width=2.5)))
    fig.add_trace(go.Scatter(x=times, y=fitted, mode="lines", name="Linear fit", line=dict(color=active_crypto.secondary_color, width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=[times[-1], times[-1] + pd.Timedelta(seconds=12)], y=[y[-1], max(0, min(100, pred))], mode="lines+markers", name="Next forecast", line=dict(color="#1CE87A", width=3)))
    fig.add_hline(y=50, line_dash="dot", line_color="#6B7DA0", annotation_text="EIP-1559 target")
    apply_chart_style(fig)
    fig.update_layout(height=360, xaxis_title="Recent blocks", yaxis_title="Gas utilization (%)", legend=dict(bgcolor="rgba(15,22,41,0.85)"))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("This Ethereum-specific second AI variant predicts near-term gas pressure, not PoW difficulty.")
    st.markdown("</div>", unsafe_allow_html=True)


def render_litecoin_m7() -> None:
    module_header("M7 — LITECOIN BLOCK TIME PREDICTOR")
    try:
        blocks = load_ltc_recent_blocks(20)
    except Exception as e:
        render_error(f"Could not fetch Litecoin prediction data: {e}")
        return
    df = build_inter_arrival_df(blocks)
    if len(df) < 3:
        render_error("Not enough Litecoin intervals for prediction.")
        return
    y = df["inter_arrival"].values.astype(float)
    x = np.arange(len(y), dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = intercept + slope * x
    pred = float(intercept + slope * len(y))
    mae = float(np.mean(np.abs(y - fitted)))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Samples", f"{len(y):,}")
    c2.metric("Recent Mean", f"{y.mean():.0f} s")
    c3.metric("Next Forecast", f"{max(0, pred):.0f} s")
    c4.metric("In-sample MAE", f"{mae:.0f} s")
    st.markdown('<hr class="glow-sep">', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">Litecoin Block-Time Forecast Backtest</div>', unsafe_allow_html=True)
    fig = go.Figure()
    heights = df["height"].values
    fig.add_trace(go.Scatter(x=heights, y=y, mode="lines+markers", name="Observed inter-arrival", line=dict(color=active_crypto.primary_color, width=2.5)))
    fig.add_trace(go.Scatter(x=heights, y=fitted, mode="lines", name="Linear fit", line=dict(color=active_crypto.secondary_color, width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=[heights[-1], heights[-1] + 1], y=[y[-1], max(0, pred)], mode="lines+markers", name="Next forecast", line=dict(color="#1CE87A", width=3)))
    fig.add_hline(y=150, line_dash="dot", line_color="#6B7DA0", annotation_text="150s target")
    apply_chart_style(fig)
    fig.update_layout(height=360, xaxis_title="Block height", yaxis_title="Seconds", legend=dict(bgcolor="rgba(15,22,41,0.85)"))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("This predictor is about Litecoin block timing. It is not a Bitcoin difficulty-retarget model copied blindly.")
    st.markdown("</div>", unsafe_allow_html=True)


# ── Module routing ─────────────────────────────────────────────────────────────
BITCOIN_RENDERERS = {
    "m1": render_m1,
    "m2": render_m2,
    "m3": render_m3,
    "m4": render_m4,
    "m5": render_m5,
    "m6": render_m6,
    "m7": render_m7,
}

ETHEREUM_RENDERERS = {
    "m1": render_ethereum_m1,
    "m2": render_ethereum_m2,
    "m3": render_ethereum_m3,
    "m4": render_ethereum_m4,
    "m5": render_ethereum_m5,
    "m6": render_ethereum_m6,
    "m7": render_ethereum_m7,
}

LITECOIN_RENDERERS = {
    "m1": render_litecoin_m1,
    "m2": render_litecoin_m2,
    "m3": render_litecoin_m3,
    "m4": render_litecoin_m4,
    "m5": render_litecoin_m5,
    "m6": render_litecoin_m6,
    "m7": render_litecoin_m7,
}

if active_crypto.id == "bitcoin":
    BITCOIN_RENDERERS[selected_module.id]()
elif active_crypto.id == "ethereum" and selected_module.id in ETHEREUM_RENDERERS:
    ETHEREUM_RENDERERS[selected_module.id]()
elif active_crypto.id == "litecoin" and selected_module.id in LITECOIN_RENDERERS:
    LITECOIN_RENDERERS[selected_module.id]()
else:
    render_crypto_variant_note(active_crypto, selected_module)
