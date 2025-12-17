"""
Lightweight QA checks for processed QoL output.

Run:
    python3 scripts/validate_output.py
"""

import math
import os
import sys
import pandas as pd


def approx_equal(a, b, tol=1e-6, rel=1e-4):
    if pd.isna(a) or pd.isna(b):
        return False
    return abs(a - b) <= max(tol, rel * max(abs(a), abs(b)))


def main():
    path = "data/processed/qol_with_real_income_peryear.csv"
    if not os.path.exists(path):
        sys.exit(f"Missing {path}. Run the pipeline first.")

    df = pd.read_csv(path)

    # 1) uniqueness of keys
    dup_count = df.duplicated(subset=["state", "year"]).sum() if {"state", "year"}.issubset(df.columns) else None
    if dup_count:
        print(f"[FAIL] Duplicate (state,year) rows: {dup_count}")
    else:
        print("[OK] Unique (state,year) combinations")

    # 2) basic sanity ranges
    if "tax_burden_pct" in df:
        bad_tax = df[(df["tax_burden_pct"] < 0) | (df["tax_burden_pct"] > 30)]
        if len(bad_tax):
            print(f"[WARN] Tax burden out of expected range (0–30%): {len(bad_tax)} rows")
        else:
            print("[OK] Tax burden within 0–30%")

    # 3) recompute key ratios for a small sample
    sample = df.head(5)
    for idx, row in sample.iterrows():
        # annual rent
        if {"median_rent_monthly", "annual_rent"}.issubset(row.index):
            calc = row["median_rent_monthly"] * 12
            if not approx_equal(calc, row["annual_rent"], rel=1e-6):
                print(f"[FAIL] annual_rent mismatch at index {idx}: got {row['annual_rent']}, expected {calc}")
        # rent burden ratio
        if {"annual_rent", "median_income", "rent_burden_ratio"}.issubset(row.index):
            calc = row["annual_rent"] / row["median_income"] if row["median_income"] else math.nan
            if not approx_equal(calc, row["rent_burden_ratio"], rel=1e-6):
                print(f"[FAIL] rent_burden_ratio mismatch at index {idx}: got {row['rent_burden_ratio']}, expected {calc}")
        # price to income
        if {"median_home_value", "median_income", "price_to_income_ratio"}.issubset(row.index):
            calc = row["median_home_value"] / row["median_income"] if row["median_income"] else math.nan
            if not approx_equal(calc, row["price_to_income_ratio"], rel=1e-6):
                print(f"[FAIL] price_to_income_ratio mismatch at index {idx}: got {row['price_to_income_ratio']}, expected {calc}")
        # disposable income
        if {"real_income", "tax_burden_rate", "disposable_income"}.issubset(row.index):
            calc = row["real_income"] * (1 - row["tax_burden_rate"])
            if not approx_equal(calc, row["disposable_income"], rel=1e-6):
                print(f"[FAIL] disposable_income mismatch at index {idx}: got {row['disposable_income']}, expected {calc}")

    # 4) cpi_index sanity: around 100
    if "cpi_index" in df:
        cpi_min, cpi_max = df["cpi_index"].min(), df["cpi_index"].max()
        print(f"[INFO] cpi_index range: {cpi_min:.2f} – {cpi_max:.2f}")

    print("[DONE] QA checks complete.")


if __name__ == "__main__":
    main()

