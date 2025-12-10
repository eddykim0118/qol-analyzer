"""
Feature engineering: CPI adjustments, QoL scoring.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np
import pandas as pd
from scipy.stats import zscore


def add_cpi_adjustments(
    df: pd.DataFrame,
    income_col: str = "median_income",
    cpi_col: str = "cpi",
    base_cpi: Optional[float] = None,
    base_label: Optional[str] = None,
) -> pd.DataFrame:
    out = df.copy()
    income = pd.to_numeric(out.get(income_col, np.nan), errors="coerce")
    cpi = pd.to_numeric(out.get(cpi_col, np.nan), errors="coerce")

    effective_base = base_cpi if base_cpi is not None else cpi.mean(skipna=True)
    out["cpi_index"] = (cpi / effective_base) * 100
    out["real_income"] = income / (cpi / effective_base)
    out["cpi_base_note"] = base_label or ("mean_of_sample" if base_cpi is None else str(base_cpi))
    return out


def compute_qol_score(
    df: pd.DataFrame,
    weight_real_income: float = 0.5,
    weight_rent_burden: float = 0.25,
    weight_owner_burden: float = 0.25,
    positive_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    out = df.copy()
    positive_cols = positive_cols or ["real_income"]

    metrics = {
        "real_income": weight_real_income,
        "rent_burden_pct": weight_rent_burden,
        "owner_burden_pct": weight_owner_burden,
    }

    zcols = {}
    for col, weight in metrics.items():
        if col not in out.columns:
            continue
        values = pd.to_numeric(out[col], errors="coerce")
        if values.std(ddof=0) == 0:
            zvals = pd.Series(0, index=out.index)
        else:
            zvals = zscore(values, nan_policy="omit")
        # invert burdens (lower is better)
        if col not in positive_cols:
            zvals = -zvals
        zcols[col] = zvals * weight

    if not zcols:
        out["qol_score"] = np.nan
        return out

    total = sum(zcols.values())
    out["qol_score"] = total
    return out


def apply_tax_and_disposable_income(
    df: pd.DataFrame,
    income_col: str = "real_income",
    tax_rate_col: str = "tax_burden_rate",
    output_col: str = "disposable_income",
) -> pd.DataFrame:
    """
    Compute disposable income using a tax burden rate (fraction).
    If tax rate is missing, leaves value as NaN.
    """
    out = df.copy()
    income = pd.to_numeric(out.get(income_col, np.nan), errors="coerce")
    tax_rate = pd.to_numeric(out.get(tax_rate_col, np.nan), errors="coerce")
    out[output_col] = income * (1 - tax_rate)
    return out

