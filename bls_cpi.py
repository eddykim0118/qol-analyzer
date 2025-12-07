import requests
import pandas as pd

BLS_SERIES = {
    "CA": "CUUR0400SA0",  # West
    "UT": "CUUR0400SA0",  # West
    "TX": "CUUR0300SA0",  # South
    "NY": "CUUR0100SA0",  # Northeast
}


def fetch_cpi(bls_api_key=None) -> pd.DataFrame:

    series_list = list(set(BLS_SERIES.values()))

    payload = {
        "seriesid": series_list,
        "latest": True
    }
    if bls_api_key:
        payload["registrationkey"] = bls_api_key

    resp = requests.post(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        json=payload
    )
    resp.raise_for_status()

    data = resp.json()
    if data.get("status") != "REQUEST_SUCCEEDED":
        print("BLS API error:", data)
        raise RuntimeError(f"BLS API request failed: {data.get('status')}")

    sid_to_cpi = {}
    for item in data["Results"]["series"]:
        sid = item["seriesID"]
        value = float(item["data"][0]["value"])
        sid_to_cpi[sid] = value

    rows = []
    for state, sid in BLS_SERIES.items():
        cpi_value = sid_to_cpi.get(sid)
        rows.append({
            "state": state,
            "series_id": sid,
            "cpi": cpi_value,
        })

    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    bls_api_key = None 

    cpi_df = fetch_cpi(bls_api_key=bls_api_key)
    print(cpi_df)

    cpi_df.to_csv("bls_cpi_regions_for_4states.csv", index=False)
    print("\nSaved to bls_cpi_regions_for_4states.csv")

