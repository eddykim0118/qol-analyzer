import pandas as pd

YEARS = [2021, 2022, 2023, 2024]

frames = []
for year in YEARS:
    df_y = pd.read_csv(f"acs_4states_{year}_full_enriched.csv")
    df_y["year"] = year
    frames.append(df_y)

df = pd.concat(frames, ignore_index=True)


cpi = pd.read_csv("bls_cpi_regions_for_4states.csv")[["state", "cpi"]]
df = df.merge(cpi, on="state", how="left")

df["median_income"] = pd.to_numeric(df["median_income"], errors="coerce")
df["cpi"] = pd.to_numeric(df["cpi"], errors="coerce")

base_cpi = df["cpi"].mean()
df["real_income"] = df["median_income"] / (df["cpi"] / base_cpi)
df["cpi_index"] = df["cpi"] / base_cpi * 100

from scipy.stats import zscore

df["z_real_income"] = zscore(df["real_income"])
df["z_rent_burden"] = -zscore(df["rent_burden_pct"])
df["z_owner_burden"] = -zscore(df["owner_burden_pct"])

df["qol_score"] = (
    0.5 * df["z_real_income"] +
    0.25 * df["z_rent_burden"] +
    0.25 * df["z_owner_burden"]
)

df.to_csv("qol_with_real_income_peryear.csv", index=False)
print("Saved -> qol_with_real_income_peryear.csv")
