"""
Cleaning utilities: state code standardization, missing handling, merges.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

import numpy as np
import pandas as pd

STATE_CODE_MAP = {
    "UT": "UT",
    "TX": "TX",
    "CA": "CA",
    "NY": "NY",
    "Utah": "UT",
    "Texas": "TX",
    "California": "CA",
    "New York": "NY",
}


def standardize_state_codes(df: pd.DataFrame, state_col: str = "state") -> pd.DataFrame:
    out = df.copy()
    if state_col not in out.columns:
        return out
    out[state_col] = out[state_col].map(lambda x: STATE_CODE_MAP.get(x, x))
    return out


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = "drop",
    columns: Optional[Iterable[str]] = None,
    fill_value: Optional[float] = None,
) -> pd.DataFrame:
    out = df.copy()
    cols = list(columns) if columns is not None else out.columns
    for col in cols:
        if col not in out.columns:
            continue
        if strategy == "drop":
            out = out.dropna(subset=[col])
        elif strategy == "fill":
            if fill_value is not None:
                out[col] = out[col].fillna(fill_value)
            elif pd.api.types.is_numeric_dtype(out[col]):
                out[col] = out[col].fillna(out[col].median())
            else:
                mode_vals = out[col].mode()
                out[col] = out[col].fillna(mode_vals.iloc[0] if not mode_vals.empty else "")
        elif strategy == "forward_fill":
            out[col] = out[col].ffill()
        elif strategy == "backward_fill":
            out[col] = out[col].bfill()
    return out


def merge_datasets(
    acs_df: pd.DataFrame,
    cpi_df: pd.DataFrame,
    tax_df: Optional[pd.DataFrame] = None,
    on: str = "state",
) -> pd.DataFrame:
    acs_df = standardize_state_codes(acs_df, on)
    cpi_df = standardize_state_codes(cpi_df, on)
    if tax_df is not None:
        tax_df = standardize_state_codes(tax_df, on)

    merged = acs_df.merge(cpi_df, on=on, how="left", suffixes=("", "_cpi"))
    if tax_df is not None:
        merged = merged.merge(tax_df, on=on, how="left", suffixes=("", "_tax"))

    # numeric coercion
    for col in merged.columns:
        if merged[col].dtype == object:
            continue
        merged[col] = pd.to_numeric(merged[col], errors="coerce")
    return merged

