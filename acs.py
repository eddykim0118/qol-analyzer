import requests
import pandas as pd


ACS_API = "https://api.census.gov/data/2024/acs/acs1"

ACS_VARS = [
    "B19013_001E",  # median income
    "B25064_001E",  # median gross rent (monthly)
    "B25077_001E",  # median home value

    "B25070_001E",  # total renter-occupied units
    "B25070_007E",  # 30–34.9%
    "B25070_008E",  # 35–39.9%
    "B25070_009E",  # 40–49.9%
    "B25070_010E",  # 50% or more

    # B25091: Selected monthly owner costs as a percentage of household income
    "B25091_001E",  # total owner-occupied units (with a mortgage etc.)
    "B25091_012E",  # 30–34.9%
    "B25091_013E",  # 35–39.9%
    "B25091_014E",  # 40–49.9%
    "B25091_015E",  # 50% or more
]

STATE_FIPS = {
    "UT": "49",
    "TX": "48",
    "CA": "06",
    "NY": "36",
}

def fetch_acs_data(api_key=None) -> pd.DataFrame:
    vars_str = ",".join(ACS_VARS)
    records = []

    for state, fips in STATE_FIPS.items():
        url = f"{ACS_API}?get={vars_str}&for=state:{fips}"
        if api_key:
            url += f"&key={api_key}"

        resp = requests.get(url)
        resp.raise_for_status()

        data = resp.json()
        header, values = data[0], data[1]
        df = pd.DataFrame([values], columns=header)
        df["state"] = state
        records.append(df)

    return pd.concat(records, ignore_index=True)



def add_derived_metrics(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    - 컬럼 rename
    - 숫자형 변환
    - annual rent, rent burden ratio, price-to-income
    - 공식 ACS rent burden (30%+)
    - 공식 ACS owner cost burden (30%+)
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
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.rename(
        columns={
            "B19013_001E": "median_income",
            "B25064_001E": "median_rent_monthly",
            "B25077_001E": "median_home_value",
        }
    )

    df["annual_rent"] = df["median_rent_monthly"] * 12

    df["rent_burden_ratio"] = df["annual_rent"] / df["median_income"]

    df["price_to_income_ratio"] = df["median_home_value"] / df["median_income"]

    df["rent_burden_30plus_num"] = (
        df["B25070_007E"]
        + df["B25070_008E"]
        + df["B25070_009E"]
        + df["B25070_010E"]
    )
    df["rent_burden_total"] = df["B25070_001E"]

    mask_rent = df["rent_burden_total"] > 0
    df["rent_burden_share"] = pd.NA
    df.loc[mask_rent, "rent_burden_share"] = (
        df.loc[mask_rent, "rent_burden_30plus_num"]
        / df.loc[mask_rent, "rent_burden_total"]
    )
    df["rent_burden_pct"] = df["rent_burden_share"] * 100

    df["owner_burden_30plus_num"] = (
        df["B25091_012E"]
        + df["B25091_013E"]
        + df["B25091_014E"]
        + df["B25091_015E"]
    )
    df["owner_burden_total"] = df["B25091_001E"]

    mask_owner = df["owner_burden_total"] > 0
    df["owner_burden_share"] = pd.NA
    df.loc[mask_owner, "owner_burden_share"] = (
        df.loc[mask_owner, "owner_burden_30plus_num"]
        / df.loc[mask_owner, "owner_burden_total"]
    )
    df["owner_burden_pct"] = df["owner_burden_share"] * 100

    return df

if __name__ == "__main__":
    api_key = None

    raw_df = fetch_acs_data(api_key=api_key)
    enriched_df = add_derived_metrics(raw_df)

    cols_to_show = [
        "state",
        "median_income",
        "median_rent_monthly",
        "median_home_value",
        "annual_rent",
        "rent_burden_ratio",
        "price_to_income_ratio",
        "rent_burden_pct",
        "owner_burden_pct",
    ]
    print(enriched_df[cols_to_show])

    enriched_df.to_csv("acs_4states_2024_full_enriched.csv", index=False)
    print("\nSaved to acs_4states_2024_full_enriched.csv")
