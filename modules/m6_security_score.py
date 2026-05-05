"""M6 - Security Score and 51% attack cost core logic."""

import math

import pandas as pd


def estimate_attack_hashrate(honest_hashrate_hs: float, attacker_fraction: float) -> float:
    """Return attacker H/s needed to reach q of total post-attack hash power.

    Nakamoto's q is the attacker's fraction of total hash power after the
    attacker joins: q = A / (A + H). Solving for attacker hash rate A gives
    A = q / (1 - q) * H, where H is the current honest network hash rate.
    """
    if honest_hashrate_hs < 0:
        raise ValueError("honest_hashrate_hs must be non-negative.")
    if attacker_fraction < 0 or attacker_fraction >= 1:
        raise ValueError("attacker_fraction must be in [0, 1).")
    return honest_hashrate_hs * attacker_fraction / (1.0 - attacker_fraction)


def estimate_energy_cost_per_hour(
    hashrate_hs: float,
    efficiency_j_per_th: float,
    electricity_usd_kwh: float,
) -> dict:
    """Estimate energy-only mining cost per hour.

    efficiency_j_per_th means joules needed per tera-hash. This is an energy
    lower bound and excludes ASIC purchase, cooling, facilities, and logistics.
    """
    if hashrate_hs < 0:
        raise ValueError("hashrate_hs must be non-negative.")
    if efficiency_j_per_th <= 0:
        raise ValueError("efficiency_j_per_th must be positive.")
    if electricity_usd_kwh < 0:
        raise ValueError("electricity_usd_kwh must be non-negative.")

    terahashes_per_second = hashrate_hs / 1e12
    watts = terahashes_per_second * efficiency_j_per_th
    kwh_per_hour = watts / 1000.0
    cost_usd_per_hour = kwh_per_hour * electricity_usd_kwh
    return {
        "th_s": terahashes_per_second,
        "watts": watts,
        "kwh_per_hour": kwh_per_hour,
        "cost_usd_per_hour": cost_usd_per_hour,
    }


def double_spend_probability(attacker_fraction: float, confirmations: int) -> float:
    """Return Nakamoto double-spend catch-up probability.

    Formula from Bitcoin whitepaper section 11. q is the attacker fraction and
    p = 1 - q is the honest fraction. For q >= p, the attacker eventually catches
    up with probability 1.
    """
    q = float(attacker_fraction)
    z = int(confirmations)
    if q <= 0:
        return 0.0
    if z <= 0:
        return 1.0
    p = 1.0 - q
    if q >= p:
        return 1.0

    lam = z * (q / p)
    cumulative = 0.0
    poisson_term = math.exp(-lam)

    for k in range(0, z + 1):
        if k > 0:
            poisson_term *= lam / k
        cumulative += poisson_term * (1 - (q / p) ** (z - k))

    return max(0.0, min(1.0, 1.0 - cumulative))


def build_probability_curve(
    attacker_fractions: list[float],
    max_confirmations: int = 20,
) -> pd.DataFrame:
    """Build a DataFrame of double-spend probabilities by confirmations."""
    rows = []
    for q in attacker_fractions:
        for z in range(0, max_confirmations + 1):
            rows.append({
                "attacker_fraction": q,
                "attacker_percent": q * 100,
                "confirmations": z,
                "probability": double_spend_probability(q, z),
            })
    return pd.DataFrame(rows)


def build_cost_curve(
    network_hashrate_hs: float,
    efficiency_j_per_th: float,
    electricity_usd_kwh: float,
    min_share: float = 0.05,
    max_share: float = 0.51,
    points: int = 30,
) -> pd.DataFrame:
    """Build cost/hour estimates over Nakamoto attacker fractions q."""
    if points < 2:
        raise ValueError("points must be at least 2.")

    rows = []
    step = (max_share - min_share) / (points - 1)
    for i in range(points):
        share = min_share + i * step
        attack_hashrate = estimate_attack_hashrate(network_hashrate_hs, share)
        energy = estimate_energy_cost_per_hour(
            attack_hashrate,
            efficiency_j_per_th,
            electricity_usd_kwh,
        )
        rows.append({
            "attacker_fraction": share,
            "attacker_percent": share * 100,
            "attack_hashrate_hs": attack_hashrate,
            "cost_usd_per_hour": energy["cost_usd_per_hour"],
        })
    return pd.DataFrame(rows)


def classify_security(probability: float) -> str:
    """Classify confirmation security based on attack success probability."""
    if probability < 0.001:
        return "Very high"
    if probability < 0.01:
        return "High"
    if probability < 0.05:
        return "Moderate"
    return "Low"


def render() -> None:
    import streamlit as st
    st.header("M6 - Security Score")
    st.info("UI is implemented in app.py.")
