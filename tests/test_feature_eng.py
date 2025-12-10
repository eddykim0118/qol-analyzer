import pandas as pd
from qol_analyzer.feature_eng import add_cpi_adjustments, compute_qol_score


def test_add_cpi_adjustments():
    df = pd.DataFrame({"median_income": [80000, 70000], "cpi": [340.0, 320.0]})
    out = add_cpi_adjustments(df)
    assert "real_income" in out.columns
    assert "cpi_index" in out.columns
    assert out["real_income"].notna().all()


def test_compute_qol_score():
    df = pd.DataFrame(
        {
            "real_income": [50000, 60000, 70000],
            "rent_burden_pct": [30, 25, 35],
            "owner_burden_pct": [40, 35, 45],
        }
    )
    out = compute_qol_score(df)
    assert "qol_score" in out.columns
    assert len(out["qol_score"]) == 3

