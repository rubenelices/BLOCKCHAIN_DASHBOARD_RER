"""M4 - AI Component: Block Inter-Arrival Time Anomaly Detector.

Approach:
  Bitcoin block mining follows a Poisson process with target rate lambda = 1/600 s.
  Inter-arrival times should therefore follow an Exponential(lambda) distribution.
  We detect anomalous blocks using two complementary methods:

  1. Statistical (baseline): flag times outside the [2.5%, 97.5%] quantiles of
     the fitted exponential.  Simple, interpretable, directly tied to theory.

  2. ML (IsolationForest): unsupervised anomaly detection on three features --
     log(inter_arrival), hour_of_day, height mod 2016 -- to capture non-linear
     structure that the univariate threshold misses (e.g. mining-pool bursts at
     certain times of day or within a difficulty epoch).

References:
  - Nakamoto 2008, Section 11 -- Poisson arrival model for blocks.
  - Eyal & Sirer 2014, "Majority is not Enough" -- selfish mining and pool behaviour.
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.metrics import f1_score, precision_score, recall_score


def build_inter_arrival_df(blocks: list[dict]) -> pd.DataFrame:
    """Compute inter-arrival times from a list of block dicts.

    Blocks must each have keys: height, timestamp.
    Returns a DataFrame with one row per inter-arrival interval.
    Negative or zero intervals (clock artefacts) are dropped.
    """
    sorted_blocks = sorted(blocks, key=lambda b: b["height"])
    records = []
    for i in range(1, len(sorted_blocks)):
        b_curr = sorted_blocks[i]
        b_prev = sorted_blocks[i - 1]
        dt = int(b_curr["timestamp"]) - int(b_prev["timestamp"])
        if dt > 0:
            records.append({
                "height":        b_curr["height"],
                "timestamp":     b_curr["timestamp"],
                "inter_arrival": dt,
            })
    return pd.DataFrame(records)


def fit_exponential(times: np.ndarray) -> dict:
    """Fit Exp(lambda) via MLE and run a KS goodness-of-fit test.

    MLE for the exponential gives lambda_hat = 1 / mean(times).
    The KS test compares the empirical CDF to the theoretical Exp(lambda_hat).

    Returns dict with: lambda_hat, mean_s, ks_stat, ks_pvalue.
    """
    mean_t = float(np.mean(times))
    lambda_hat = 1.0 / mean_t
    ks_stat, ks_pvalue = stats.kstest(times, "expon", args=(0.0, mean_t))
    return {
        "lambda_hat": lambda_hat,
        "mean_s":     mean_t,
        "ks_stat":    float(ks_stat),
        "ks_pvalue":  float(ks_pvalue),
    }


def detect_statistical(times: np.ndarray, lambda_hat: float) -> np.ndarray:
    """Flag anomalies via exponential quantile thresholds [2.5%, 97.5%].

    Under Exp(lambda), roughly 5% of blocks naturally fall outside these bounds.
    Returns a boolean array (True = anomalous).
    """
    scale = 1.0 / lambda_hat
    low   = stats.expon.ppf(0.025, scale=scale)
    high  = stats.expon.ppf(0.975, scale=scale)
    return (times < low) | (times > high)


def detect_isolation_forest(
    df: pd.DataFrame,
    contamination: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    """IsolationForest anomaly detection on three features.

    Features:
      - log1p(inter_arrival): captures skewness of the exponential.
      - height mod 2016:      position within the difficulty epoch.
      - hour_of_day (UTC):    captures circadian patterns in mining-pool activity.

    contamination=0.05 matches the statistical detector's ~5% expectation.

    Returns:
      is_anomaly  : bool array, True where IsolationForest flags an anomaly.
      scores      : float array, raw anomaly scores (lower = more anomalous).
    """
    hours        = pd.to_datetime(df["timestamp"], unit="s", utc=True).dt.hour.values
    heights_mod  = (df["height"].values % 2016).astype(float)
    log_times    = np.log1p(df["inter_arrival"].values.astype(float))

    X = np.column_stack([log_times, heights_mod, hours])
    clf    = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
    labels = clf.fit_predict(X)   # -1 = anomaly, 1 = normal
    scores = clf.score_samples(X) # lower = more anomalous
    return labels == -1, scores


def evaluate_synthetic_anomalies(
    df: pd.DataFrame,
    anomaly_fraction: float = 0.05,
    random_state: int = 42,
) -> dict:
    """Evaluate detectors by injecting labelled synthetic anomalies.

    Real Bitcoin blocks do not come with ground-truth anomaly labels. To get
    precision/recall/F1, we keep the real block heights and timestamps but
    replace a small fraction of inter-arrival times with controlled extreme
    values. Those injected points become the positive labels.
    """
    if df.empty or "inter_arrival" not in df:
        return {}

    rng = np.random.default_rng(random_state)
    synthetic_df = df.copy()
    times = synthetic_df["inter_arrival"].values.astype(float)
    n_samples = len(times)
    n_anomalies = max(1, int(round(n_samples * anomaly_fraction)))
    n_anomalies = min(n_anomalies, n_samples)

    anomaly_idx = rng.choice(n_samples, size=n_anomalies, replace=False)
    y_true = np.zeros(n_samples, dtype=bool)
    y_true[anomaly_idx] = True

    rng.shuffle(anomaly_idx)
    split = max(1, len(anomaly_idx) // 2)
    fast_idx = anomaly_idx[:split]
    slow_idx = anomaly_idx[split:]

    times[fast_idx] = rng.uniform(5, 30, size=len(fast_idx))
    if len(slow_idx) > 0:
        times[slow_idx] = rng.uniform(2400, 7200, size=len(slow_idx))
    synthetic_df["inter_arrival"] = times

    # Fit the exponential baseline on the original clean recent data, then test
    # whether the detector recovers the injected anomalies.
    lambda_hat = 1.0 / float(df["inter_arrival"].mean())
    stat_pred = detect_statistical(times, lambda_hat)
    if_pred, _ = detect_isolation_forest(
        synthetic_df,
        contamination=max(0.01, min(0.5, anomaly_fraction)),
    )

    def metrics(y_pred: np.ndarray) -> dict:
        return {
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, zero_division=0)),
            "detected": int(np.sum(y_pred)),
        }

    return {
        "n_samples": int(n_samples),
        "n_injected": int(n_anomalies),
        "anomaly_fraction": float(anomaly_fraction),
        "statistical": metrics(stat_pred),
        "isolation_forest": metrics(if_pred),
    }


def render() -> None:
    import streamlit as st
    st.header("M4 - AI Component")
    st.info("UI coming soon.")
