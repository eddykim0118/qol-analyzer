import os
import pandas as pd
from dotenv import load_dotenv
from qol_analyzer.data_fetch import fetch_acs_data, add_derived_metrics, fetch_bls_cpi
from qol_analyzer.feature_eng import (
    add_cpi_adjustments,
    compute_qol_score,
    apply_tax_and_disposable_income,
)

def main():
    load_dotenv(dotenv_path=".env", override=False)

    years = [2022, 2023, 2024]
    acs_all = pd.concat([add_derived_metrics(fetch_acs_data(y)) for y in years], ignore_index=True)

    cpi = fetch_bls_cpi()

    # Load tax data from state_tax_metrics.csv (per-year burdens)
    tax = None
    tax_path = "data/raw/state_tax_metrics.csv"
    if os.path.exists(tax_path):
        tax_df = pd.read_csv(tax_path)
        if {"state", "year", "tax_burden_pct"}.issubset(tax_df.columns):
            tax_df["tax_burden_pct"] = pd.to_numeric(tax_df["tax_burden_pct"], errors="coerce")
            tax_df["tax_burden_rate"] = tax_df["tax_burden_pct"] / 100.0
            tax = tax_df[tax_df["year"].isin(years)][
                ["state", "year", "tax_burden_rate", "tax_burden_pct"]
            ]

    # Manual merges to honor state+year for tax
    merged = acs_all.merge(cpi, on="state", how="left")
    if tax is not None:
        merged = merged.merge(tax, on=["state", "year"], how="left")

    merged = add_cpi_adjustments(merged, base_cpi=None, base_label="mean_of_sample")
    merged = compute_qol_score(merged)
    if tax is not None:
        merged = apply_tax_and_disposable_income(
            merged, income_col="real_income", tax_rate_col="tax_burden_rate"
        )

    os.makedirs("data/processed", exist_ok=True)
    out_path = "data/processed/qol_with_real_income_peryear.csv"
    merged.to_csv(out_path, index=False)
    print(f"Saved {out_path}")
    print(merged.head())

if __name__ == "__main__":
    main()