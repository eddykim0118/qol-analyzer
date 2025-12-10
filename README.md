# qol-analyzer

Pipeline to measure Quality of Life across four states (CA, NY, TX, UT) using:
- ACS 1-year data (income, rent, home value, rent/owner burden slices)
- BLS regional CPI
- (Optional) Tax Foundation state/local tax burden

## Quick start
1) Create and activate a venv, install deps:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2) Export API keys (or use a `.env`):
```
export CENSUS_API_KEY=your_key
export BLS_API_KEY=your_key   # optional but recommended
```
3) Fetch data and build QoL dataset (with MOE, optional Tax if provided):
```
python - <<'PY'
from qol_analyzer.data_fetch import fetch_acs_data, add_derived_metrics, fetch_bls_cpi, fetch_tax_data
from qol_analyzer.data_clean import merge_datasets
from qol_analyzer.feature_eng import add_cpi_adjustments, compute_qol_score, apply_tax_and_disposable_income
import pandas as pd

years = [2022, 2023, 2024]
frames = []
for y in years:
    raw = fetch_acs_data(year=y)
    enriched = add_derived_metrics(raw)
    frames.append(enriched)
acs_all = pd.concat(frames, ignore_index=True)

cpi = fetch_bls_cpi()
try:
    tax = fetch_tax_data()  # expects data/raw/tax_foundation_data.xlsx
except FileNotFoundError:
    tax = None

merged = merge_datasets(acs_all, cpi, tax_df=tax)
# Choose CPI baseline: pass base_cpi (e.g., 2022 CPI=292.655) or default to mean-of-sample
merged = add_cpi_adjustments(merged, base_cpi=None, base_label="mean_of_sample")
merged = compute_qol_score(merged)
if tax is not None:
    merged = apply_tax_and_disposable_income(merged, income_col="real_income", tax_rate_col="tax_burden_rate")
merged.to_csv("data/processed/qol_with_real_income_peryear.csv", index=False)
print("Saved qol_with_real_income_peryear.csv")
PY
```
4) Visualize (example):
```
python - <<'PY'
import pandas as pd
from qol_analyzer.visualize import plot_qol_score_by_state
df = pd.read_csv("qol_with_real_income_peryear.csv")
fig = plot_qol_score_by_state(df, year=2024)
fig.savefig("qol_score_2024.png", dpi=200, bbox_inches="tight")
print("Saved qol_score_2024.png")
PY
```

## Modules
- `qol_analyzer.data_fetch`: fetch ACS (1-year) with MOE, BLS CPI (regional), Tax data loader, derived housing metrics + quality flags.
- `qol_analyzer.data_clean`: standardize state codes, handle missing, merge datasets.
- `qol_analyzer.feature_eng`: CPI adjustment (real income, CPI index, baseline note), QoL score (z-scores, weights), disposable income from tax burden.
- `qol_analyzer.analysis`: summary stats, simple regression on QoL.
- `qol_analyzer.visualize`: bar/line/scatter plots for income, burdens, QoL.

## Tests
Run `pytest` (basic smoke tests can be added under `tests/`).
# qol-analyzer