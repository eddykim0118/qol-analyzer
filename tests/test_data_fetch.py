import pandas as pd

from qol_analyzer.data_fetch import ACS_VARS, STATE_FIPS, add_derived_metrics


def test_state_fips_contains_expected():
    for st in ["UT", "TX", "CA", "NY"]:
        assert st in STATE_FIPS


def test_derived_metrics_columns():
    data = {
        "B19013_001E": [80000],
        "B25064_001E": [1500],
        "B25077_001E": [500000],
        "B25070_001E": [1000],
        "B25070_007E": [100],
        "B25070_008E": [100],
        "B25070_009E": [100],
        "B25070_010E": [100],
        "B25091_001E": [1000],
        "B25091_012E": [100],
        "B25091_013E": [100],
        "B25091_014E": [100],
        "B25091_015E": [100],
    }
    df = pd.DataFrame(data)
    out = add_derived_metrics(df)
    for col in [
        "median_income",
        "median_rent_monthly",
        "median_home_value",
        "annual_rent",
        "rent_burden_ratio",
        "price_to_income_ratio",
        "rent_burden_pct",
        "owner_burden_pct",
    ]:
        assert col in out.columns

