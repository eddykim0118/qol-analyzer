"""
Data retrieval helpers for ACS (1-year), BLS CPI, and Tax Foundation.

Defaults are tuned to the four target states in the proposal:
Utah (UT), Texas (TX), California (CA), New York (NY).
"""

from __future__ import annotations

import os
import json
import time
from typing import Dict, Iterable, List, Optional

import pandas as pd
import requests

# ACS 1-year variables (proposal set) including MOE (_M)
ACS_VARS: List[str] = [
    # Estimates
    "B19013_001E",  # median income
    "B25064_001E",  # median gross rent (monthly)
    "B25077_001E",  # median home value
    # Renters: burden slices (30%+)
    "B25070_001E",
    "B25070_007E",
    "B25070_008E",
    "B25070_009E",
    "B25070_010E",
    # Owners: burden slices (30%+)
    "B25091_001E",
    "B25091_012E",
    "B25091_013E",
    "B25091_014E",
    "B25091_015E",
    # Margins of Error
    "B19013_001M",
    "B25064_001M",
    "B25077_001M",
    "B25070_001M",
    "B25070_007M",
    "B25070_008M",
    "B25070_009M",
    "B25070_010M",
    "B25091_001M",
    "B25091_012M",
    "B25091_013M",
    "B25091_014M",
    "B25091_015M",
]

# State FIPS (2-letter codes to FIPS)
STATE_FIPS: Dict[str, str] = {
    "UT": "49",
    "TX": "48",
    "CA": "06",
    "NY": "36",
}

# Regional CPI series (BLS)
BLS_SERIES: Dict[str, str] = {
    "CA": "CUUR0400SA0",  # West
    "UT": "CUUR0400SA0",  # West
    "TX": "CUUR0300SA0",  # South
    "NY": "CUUR0100SA0",  # Northeast
}


def _get_env(key: str) -> Optional[str]:
    return os.getenv(key)


def fetch_acs_data(
    year: int,
    states: Optional[Iterable[str]] = None,
    api_key: Optional[str] = None,
    variables: Optional[List[str]] = None,
    rate_limit_sec: float = 0.2,
) -> pd.DataFrame:
    """
    Fetch ACS 1-year data for selected states.
    """
    states = list(states) if states is not None else list(STATE_FIPS.keys())
    api_key = api_key or _get_env("CENSUS_API_KEY")
    variables = variables or ACS_VARS

    api = f"https://api.census.gov/data/{year}/acs/acs1"
    var_str = ",".join(variables)
    records = []

    for st in states:
        fips = STATE_FIPS.get(st)
        if not fips:
            raise ValueError(f"Unsupported state code: {st}")

        url = f"{api}?get={var_str}&for=state:{fips}"
        if api_key:
            url += f"&key={api_key}"

        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        header, values = data[0], data[1]
        df = pd.DataFrame([values], columns=header)
        df["state"] = st
        df["year"] = year
        records.append(df)
        time.sleep(rate_limit_sec)

    return pd.concat(records, ignore_index=True)


def add_derived_metrics(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add proposal-aligned metrics:
    - annual_rent, rent_burden_ratio, price_to_income_ratio
    - rent_burden_pct (renter share 30%+), owner_burden_pct (owner share 30%+)
    """
    df = raw_df.copy()

    num_cols = [
        "B19013_001E",
        "B25064_001E",
        "B25077_001E",
        "B25070_001E",
        "B25070_007E",
        "B25070_008E",
        "B25070_009E",
        "B25070_010E",
        "B25091_001E",
        "B25091_012E",
        "B25091_013E",
        "B25091_014E",
        "B25091_015E",
        "B19013_001M",
        "B25064_001M",
        "B25077_001M",
        "B25070_001M",
        "B25070_007M",
        "B25070_008M",
        "B25070_009M",
        "B25070_010M",
        "B25091_001M",
        "B25091_012M",
        "B25091_013M",
        "B25091_014M",
        "B25091_015M",
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.rename(
        columns={
            "B19013_001E": "median_income",
            "B25064_001E": "median_rent_monthly",
            "B25077_001E": "median_home_value",
            "B19013_001M": "median_income_moe",
            "B25064_001M": "median_rent_monthly_moe",
            "B25077_001M": "median_home_value_moe",
            "B25070_001M": "rent_burden_total_moe",
            "B25070_007M": "rent_burden_30_moe",
            "B25070_008M": "rent_burden_35_moe",
            "B25070_009M": "rent_burden_40_moe",
            "B25070_010M": "rent_burden_50_moe",
            "B25091_001M": "owner_burden_total_moe",
            "B25091_012M": "owner_burden_30_moe",
            "B25091_013M": "owner_burden_35_moe",
            "B25091_014M": "owner_burden_40_moe",
            "B25091_015M": "owner_burden_50_moe",
        }
    )

    df["annual_rent"] = df["median_rent_monthly"] * 12
    df["rent_burden_ratio"] = df["annual_rent"] / df["median_income"]
    df["price_to_income_ratio"] = df["median_home_value"] / df["median_income"]

    df["rent_burden_30plus_num"] = (
        df.get("B25070_007E", 0)
        + df.get("B25070_008E", 0)
        + df.get("B25070_009E", 0)
        + df.get("B25070_010E", 0)
    )
    df["rent_burden_total"] = df.get("B25070_001E", pd.NA)
    rent_mask = df["rent_burden_total"] > 0
    df["rent_burden_share"] = pd.NA
    df.loc[rent_mask, "rent_burden_share"] = (
        df.loc[rent_mask, "rent_burden_30plus_num"]
        / df.loc[rent_mask, "rent_burden_total"]
    )
    df["rent_burden_pct"] = df["rent_burden_share"] * 100

    df["owner_burden_30plus_num"] = (
        df.get("B25091_012E", 0)
        + df.get("B25091_013E", 0)
        + df.get("B25091_014E", 0)
        + df.get("B25091_015E", 0)
    )
    df["owner_burden_total"] = df.get("B25091_001E", pd.NA)
    owner_mask = df["owner_burden_total"] > 0
    df["owner_burden_share"] = pd.NA
    df.loc[owner_mask, "owner_burden_share"] = (
        df.loc[owner_mask, "owner_burden_30plus_num"]
        / df.loc[owner_mask, "owner_burden_total"]
    )
    df["owner_burden_pct"] = df["owner_burden_share"] * 100

    # Relative MOE and quality flags (simple threshold: >30% relative MOE)
    for est_col, moe_col in [
        ("median_income", "median_income_moe"),
        ("median_rent_monthly", "median_rent_monthly_moe"),
        ("median_home_value", "median_home_value_moe"),
    ]:
        if moe_col in df.columns and est_col in df.columns:
            rel_col = f"{est_col}_rel_moe"
            flag_col = f"{est_col}_high_moe_flag"
            df[rel_col] = df[moe_col] / df[est_col]
            df[flag_col] = df[rel_col] > 0.3

    return df


def fetch_bls_cpi(bls_api_key: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch latest CPI for each regional series used by our four states.
    """
    bls_api_key = bls_api_key or _get_env("BLS_API_KEY")

    series_list = list(set(BLS_SERIES.values()))
    payload = {"seriesid": series_list, "latest": True}
    if bls_api_key:
        payload["registrationkey"] = bls_api_key

    resp = requests.post(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS API error: {data}")

    sid_to_cpi = {}
    for item in data.get("Results", {}).get("series", []):
        sid = item["seriesID"]
        value = float(item["data"][0]["value"])
        sid_to_cpi[sid] = value

    rows = []
    for state, sid in BLS_SERIES.items():
        rows.append({"state": state, "series_id": sid, "cpi": sid_to_cpi.get(sid)})

    return pd.DataFrame(rows)


def fetch_tax_data(file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Placeholder for Tax Foundation Excel loader.
    """
    file_path = file_path or "data/raw/tax_foundation_data.xlsx"
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Tax data not found at {file_path}. Download and place it under data/raw/."
        )
    df = pd.read_excel(file_path)

    # Standardize columns
    cols = {c.lower(): c for c in df.columns}
    state_col = cols.get("state") or cols.get("state_name") or cols.get("st")
    if not state_col:
        raise ValueError("Could not find state column in tax data.")

    pct_col = None
    for cand in ["tax burden", "tax burden %", "tax_burden", "tax_burden_pct", "burden_pct"]:
        if cand in cols:
            pct_col = cols[cand]
            break
    if pct_col is None:
        numeric_candidates = [
            c for c in df.columns if c != state_col and pd.api.types.is_numeric_dtype(df[c])
        ]
        if not numeric_candidates:
            raise ValueError("Could not find tax burden column in tax data.")
        pct_col = numeric_candidates[0]

    out = df[[state_col, pct_col]].copy()
    out.columns = ["state", "tax_burden_raw"]

    if out["tax_burden_raw"].max() > 1.0:
        out["tax_burden_pct"] = out["tax_burden_raw"]
        out["tax_burden_rate"] = out["tax_burden_pct"] / 100.0
    else:
        out["tax_burden_rate"] = out["tax_burden_raw"]
        out["tax_burden_pct"] = out["tax_burden_rate"] * 100.0

    return out[["state", "tax_burden_rate", "tax_burden_pct"]]

