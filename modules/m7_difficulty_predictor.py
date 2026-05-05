"""M7 - Difficulty adjustment predictor core logic."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


FEATURE_COLUMNS = [
    "prev_difficulty",
    "ratio",
    "prev_ratio",
    "prev_pct_change",
    "rolling_ratio_3",
    "rolling_pct_change_3",
]


def build_prediction_dataset(adjustment_df: pd.DataFrame) -> pd.DataFrame:
    """Build a supervised dataset from difficulty adjustment periods.

    Each row uses the completed period duration ratio plus previous adjustment
    context to predict the percentage change applied at that adjustment event.
    """
    if adjustment_df.empty:
        return pd.DataFrame()

    df = build_feature_frame(adjustment_df)
    if df.empty:
        return pd.DataFrame()
    df["target_pct_change"] = df["pct_change"]

    dataset = df.dropna(subset=FEATURE_COLUMNS + ["target_pct_change"]).copy()
    return dataset.reset_index(drop=True)


def build_feature_frame(adjustment_df: pd.DataFrame) -> pd.DataFrame:
    """Return adjustment rows with model features, including the latest row."""
    if adjustment_df.empty:
        return pd.DataFrame()

    df = adjustment_df.copy().sort_values("height").reset_index(drop=True)
    df["prev_difficulty"] = df["difficulty"].shift(1)
    df["prev_ratio"] = df["ratio"].shift(1)
    df["prev_pct_change"] = df["pct_change"].shift(1)
    df["rolling_ratio_3"] = df["ratio"].rolling(3).mean()
    df["rolling_pct_change_3"] = df["pct_change"].rolling(3).mean()
    return df.dropna(subset=FEATURE_COLUMNS).reset_index(drop=True)


def temporal_train_test_split(
    dataset: pd.DataFrame,
    test_fraction: float = 0.30,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split data chronologically to avoid training on future periods."""
    if dataset.empty:
        return dataset.copy(), dataset.copy()
    n_test = max(1, int(round(len(dataset) * test_fraction)))
    n_test = min(n_test, max(1, len(dataset) - 1))
    split_idx = len(dataset) - n_test
    return dataset.iloc[:split_idx].copy(), dataset.iloc[split_idx:].copy()


def train_models(train_df: pd.DataFrame) -> dict:
    """Train baseline and RandomForest regressors."""
    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["target_pct_change"]
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=200,
            max_depth=4,
            min_samples_leaf=2,
            random_state=42,
        ),
    }
    for model in models.values():
        model.fit(X_train, y_train)
    return models


def evaluate_model(model, test_df: pd.DataFrame) -> dict:
    """Evaluate a model on chronological holdout data."""
    X_test = test_df[FEATURE_COLUMNS]
    y_true = test_df["target_pct_change"].values
    y_pred = model.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": rmse,
        "r2": float(r2_score(y_true, y_pred)) if len(y_true) > 1 else float("nan"),
        "predictions": y_pred,
    }


def train_and_evaluate(
    adjustment_df: pd.DataFrame,
    test_fraction: float = 0.30,
) -> dict:
    """Train difficulty predictors and return metrics plus next forecast."""
    dataset = build_prediction_dataset(adjustment_df)
    if len(dataset) < 8:
        raise ValueError("Need at least 8 usable adjustment periods for M7.")
    feature_df = build_feature_frame(adjustment_df)

    train_df, test_df = temporal_train_test_split(dataset, test_fraction)
    models = train_models(train_df)
    evaluations = {
        name: evaluate_model(model, test_df)
        for name, model in models.items()
    }

    best_name = min(evaluations, key=lambda name: evaluations[name]["mae"])
    best_model = models[best_name]
    latest_row = feature_df.iloc[[-1]]
    latest_pct_change = float(best_model.predict(latest_row[FEATURE_COLUMNS])[0])
    previous_difficulty = float(latest_row["prev_difficulty"].iloc[0])
    actual_difficulty = float(latest_row["difficulty"].iloc[0])
    predicted_adjusted_difficulty = previous_difficulty * (1 + latest_pct_change / 100.0)

    result_rows = test_df[["date", "height", "target_pct_change"]].copy()
    for name, evaluation in evaluations.items():
        result_rows[f"{name} prediction"] = evaluation["predictions"]

    return {
        "dataset": dataset,
        "train_df": train_df,
        "test_df": test_df,
        "models": models,
        "evaluations": evaluations,
        "best_model_name": best_name,
        "latest_pct_change": latest_pct_change,
        "previous_difficulty": previous_difficulty,
        "actual_difficulty": actual_difficulty,
        "predicted_adjusted_difficulty": predicted_adjusted_difficulty,
        "holdout_predictions": result_rows,
    }


def render() -> None:
    import streamlit as st
    st.header("M7 - Difficulty Predictor")
    st.info("UI is implemented in app.py.")
