import requests
import pandas as pd

# Actually, the BEAapi need the api_key. However, I just put this value 'None'
BEA_API_KEY = None

STATES = {
    "CA": "06000",
    "NY": "36000", 
    "TX": "48000",
    "UT": "49000",
}

def fetch_bea_personal_income(years=[2021, 2022, 2023, 2024]):
    """
    SAINC1: Personal Income Summary
    LineCode=1: Personal income
    """
    url = "https://apps.bea.gov/api/data"
    params = {
        "UserID": None,
        "method": "GetData",
        "DataSetName": "Regional",
        "TableName": "SAINC1",
        "LineCode": "1",
        "GeoFIPS": "STATE",
        "Year": ",".join(map(str, years)),
        "ResultFormat": "json",
    }

    resp = requests.get(url, params=params)
    resp.raise_for_status()

    data_json = resp.json()
    beaapi = data_json.get("BEAAPI", {})
    results = beaapi.get("Results")

    if not results or "Data" not in results:
        raise RuntimeError(f"BEA INCOME API error:\n{data_json}")

    rows = results["Data"]
    data = []
    fips_to_abbr = {v: k for k, v in STATES.items()}

    for r in rows:
        fips = r["GeoFips"]
        if fips in fips_to_abbr:
            val = float(r["DataValue"].replace(",", ""))
            unit_mult = int(r.get("UNIT_MULT", 0))
            actual_value = val * (10 ** unit_mult)

            data.append({
                "state": fips_to_abbr[fips],
                "year": int(r["TimePeriod"]),
                "personal_income": actual_value,
            })

    return pd.DataFrame(data)

def fetch_bea_personal_taxes(years=[2021, 2022, 2023, 2024]):
    """
    SAINC50: Personal Current Taxes
    LineCode=15
    """
    url = "https://apps.bea.gov/api/data"
    params = {
        "UserID": None,
        "method": "GetData",
        "DataSetName": "Regional",
        "TableName": "SAINC50",
        "LineCode": "15",
        "GeoFIPS": "STATE", 
        "Year": ",".join(map(str, years)),
        "ResultFormat": "json",
    }

    resp = requests.get(url, params=params)
    resp.raise_for_status()

    data_json = resp.json()
    beaapi = data_json.get("BEAAPI", {})
    results = beaapi.get("Results")

    if not results or "Data" not in results:
        raise RuntimeError(f"BEA TAX API error:\n{data_json}")

    rows = results["Data"]

    data = []
    fips_to_abbr = {v: k for k, v in STATES.items()}

    for r in rows:
        fips = r["GeoFips"]
        if fips in fips_to_abbr:
            val = float(r["DataValue"].replace(",", ""))
            unit_mult = int(r.get("UNIT_MULT", 0))
            actual_value = val * (10 ** unit_mult)

            data.append({
                "state": fips_to_abbr[fips],
                "year": int(r["TimePeriod"]),
                "personal_taxes": actual_value,
            })

    return pd.DataFrame(data)


def build_metrics(years=[2021, 2022, 2023, 2024]):
    print("Fetching BEA Personal Income data...")
    income_df = fetch_bea_personal_income(years)
    
    print("Fetching BEA Personal Taxes data...")
    taxes_df = fetch_bea_personal_taxes(years)
    

    df = income_df.merge(taxes_df, on=["state", "year"], how="inner")
    
    df["tax_burden_pct"] = (df["personal_taxes"] / df["personal_income"]) * 100
    
    df = df.sort_values(["state", "year"]).reset_index(drop=True)
    
    df["personal_income"] = df["personal_income"].round(2)
    df["personal_taxes"] = df["personal_taxes"].round(2)
    df["tax_burden_pct"] = df["tax_burden_pct"].round(2)
    
    output_file = "state_tax_metrics.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*60}")
    print("State Tax Metrics (2021-2024)")
    print(f"{'='*60}")
    print(df.to_string(index=False))
    print(f"\n Saved → {output_file}")
    
    return df

if __name__ == "__main__":
    try:
        build_metrics()
    except Exception as e:
        print(f" Error: {e}")
