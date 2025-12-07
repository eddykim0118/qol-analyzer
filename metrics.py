import pandas as pd

ACS_PATH = "acs_4states_2022_full_enriched.csv"
CPI_PATH = "bls_cpi_regions_for_4states.csv"


def load_data(acs_path=ACS_PATH, cpi_path=CPI_PATH) -> pd.DataFrame:

    acs = pd.read_csv(acs_path)
    cpi = pd.read_csv(cpi_path)

    cpi = cpi[["state", "cpi"]]

    df = acs.merge(cpi, on="state", how="left")
    return df


def add_real_income(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["median_income"] = pd.to_numeric(out["median_income"], errors="coerce")
    out["cpi"] = pd.to_numeric(out["cpi"], errors="coerce")

    base_cpi = out["cpi"].mean()

    out["real_income"] = out["median_income"] / (out["cpi"] / base_cpi)

    out["cpi_index"] = out["cpi"] / base_cpi * 100

    return out


def add_qol_stub(df: pd.DataFrame) -> pd.DataFrame:

    out = df.copy()
    qol_cols = [
        "median_income",
        "real_income",
        "rent_burden_ratio",
        "price_to_income_ratio",
        "rent_burden_pct",
        "owner_burden_pct",
    ]

    return out


if __name__ == "__main__":
    df = load_data()
    df = add_real_income(df)
    df = add_qol_stub(df)

    cols_to_show = [
        "state",
        "median_income",
        "cpi",
        "cpi_index",
        "real_income",
        "rent_burden_ratio",
        "price_to_income_ratio",
        "rent_burden_pct",
        "owner_burden_pct",
    ]
    print(df[cols_to_show])

    df.to_csv("qol_with_real_income.csv", index=False)
    print("\nSaved to qol_with_real_income.csv")
