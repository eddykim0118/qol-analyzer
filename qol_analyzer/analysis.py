"""
Analysis helpers: summary stats and simple regression.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def generate_summary_statistics(
    df: pd.DataFrame,
    group_by: Optional[str] = "state",
    numeric_columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    if numeric_columns is None:
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

    if group_by and group_by in df.columns:
        return (
            df.groupby(group_by)[numeric_columns]
            .agg(["count", "mean", "median", "std", "min", "max"])
            .round(3)
        )
    return df[numeric_columns].agg(["count", "mean", "median", "std", "min", "max"]).round(3)


def run_regression_analysis(
    df: pd.DataFrame,
    target: str = "qol_score",
    predictors: Optional[List[str]] = None,
    drop_na: bool = True,
) -> Dict:
    predictors = predictors or ["real_income", "rent_burden_pct", "owner_burden_pct"]
    if target not in df.columns:
        raise ValueError(f"Target '{target}' not in DataFrame.")

    X = df[predictors].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df[target], errors="coerce")
    data = pd.concat([X, y], axis=1)
    if drop_na:
        data = data.dropna()
    X_clean = data[predictors]
    y_clean = data[target]
    if len(X_clean) == 0:
        raise ValueError("No data left after cleaning for regression.")

    model = LinearRegression()
    model.fit(X_clean, y_clean)
    y_pred = model.predict(X_clean)
    return {
        "r_squared": r2_score(y_clean, y_pred),
        "coefficients": dict(zip(predictors, model.coef_)),
        "intercept": model.intercept_,
        "n_samples": len(X_clean),
    }

