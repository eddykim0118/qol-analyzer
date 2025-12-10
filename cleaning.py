# src/final_project_demo/cleaning.py
import requests
import pandas as pd

ACS_VARS = [
    "B19013_001E",  # median income
    "B25064_001E",  # median gross rent
    "B25077_001E",  # median home value
    "B25070_001E",  # renters total
    "B25070_007E", "B25070_008E", "B25070_009E", "B25070_010E",
    "B25091_001E",  # owners total
    "B25091_012E", "B25091_013E", "B25091_014E", "B25091_015E",
]

STATE_FIPS = {
    "UT": "49",
    "TX": "48",
    "CA": "06",
    "NY": "36",
}

YEARS = [2021, 2022, 2023, 2024]


def fetch_acs_data(year, api_key=None):
    """Fetch ACS 1-year data for a specific year."""
    api = f"https://api.census.gov/data/{year}/acs/acs1"
    vars_str = ",".join(ACS_VARS)
    records = []

    for state, fips in STATE_FIPS.items():
        url = f"{api}?get={vars_str}&for=state:{fips}"
        if api_key:
            url += f"&key={api_key}"

        resp = requests.get(url)
        resp.raise_for_status()
        header, values = resp.json()
        df = pd.DataFrame([values], columns=header)
        df["state"] = state
        df["year"] = year
        records.append(df)

    return pd.concat(records, ignore_index=True)


def add_derived_metrics(df):
    df = df.copy()

    # Convert numeric
    num_cols = [
        "B19013_001E", "B25064_001E", "B25077_001E",
        "B25070_001E", "B25070_007E", "B25070_008E",
        "B25070_009E", "B25070_010E",
        "B25091_001E", "B25091_012E", "B25091_013E",
        "B25091_014E", "B25091_015E",
    ]

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.rename(columns={
        "B19013_001E": "median_income",
        "B25064_001E": "median_rent_monthly",
        "B25077_001E": "median_home_value",
    })

    # derived
    df["annual_rent"] = df["median_rent_monthly"] * 12
    df["rent_burden_ratio"] = df["annual_rent"] / df["median_income"]
    df["price_to_income_ratio"] = df["median_home_value"] / df["median_income"]

    # renter burden %
    df["rent_30plus"] = (
        df["B25070_007E"] + df["B25070_008E"] +
        df["B25070_009E"] + df["B25070_010E"]
    )
    df["rent_burden_pct"] = (df["rent_30plus"] / df["B25070_001E"]) * 100

    # owner burden %
    df["owner_30plus"] = (
        df["B25091_012E"] + df["B25091_013E"] +
        df["B25091_014E"] + df["B25091_015E"]
    )
    df["owner_burden_pct"] = (df["owner_30plus"] / df["B25091_001E"]) * 100

    return df


def fetch_all_years(api_key=None):
    frames = []
    for year in YEARS:
        print(f"Fetching ACS {year}...")
        raw = fetch_acs_data(year, api_key)
        enriched = add_derived_metrics(raw)
        enriched.to_csv(f"acs_4states_{year}_full_enriched.csv", index=False)
        print(f"Saved acs_4states_{year}_full_enriched.csv")
        frames.append(enriched)
    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    print("Fetching ACS data for all years (2022–2024)...")
    df_all = fetch_all_years()
    print("Done.")
