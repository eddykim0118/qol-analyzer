"""
Tests for feature_eng module.
"""

import pandas as pd
import pytest
from qol_analyzer.feature_eng import (
    add_cpi_adjustments,
    compute_qol_score,
    apply_tax_and_disposable_income,
)


def test_add_cpi_adjustments():
    """Test basic CPI adjustment calculation."""
    df = pd.DataFrame({"median_income": [80000, 70000], "cpi": [340.0, 320.0]})
    out = add_cpi_adjustments(df)
    assert "real_income" in out.columns
    assert "cpi_index" in out.columns
    assert out["real_income"].notna().all()


def test_add_cpi_adjustments_with_base_cpi():
    """Test CPI adjustment with custom base CPI."""
    df = pd.DataFrame({"median_income": [80000], "cpi": [340.0]})
    out = add_cpi_adjustments(df, base_cpi=320.0)
    expected_index = (340.0 / 320.0) * 100
    assert abs(out["cpi_index"].iloc[0] - expected_index) < 0.01


def test_add_cpi_adjustments_custom_columns():
    """Test CPI adjustment with custom column names."""
    df = pd.DataFrame({"income": [80000], "consumer_price_index": [340.0]})
    out = add_cpi_adjustments(df, income_col="income", cpi_col="consumer_price_index")
    assert "real_income" in out.columns
    assert "cpi_index" in out.columns


def test_add_cpi_adjustments_with_base_label():
    """Test that base label is recorded."""
    df = pd.DataFrame({"median_income": [80000], "cpi": [340.0]})
    out = add_cpi_adjustments(df, base_cpi=320.0, base_label="2020_baseline")
    assert out["cpi_base_note"].iloc[0] == "2020_baseline"


def test_add_cpi_adjustments_mean_baseline():
    """Test CPI adjustment uses mean as baseline when not specified."""
    df = pd.DataFrame({"median_income": [80000, 70000], "cpi": [340.0, 320.0]})
    out = add_cpi_adjustments(df)
    # Mean CPI is 330, so index should be relative to 330
    expected_index_1 = (340.0 / 330.0) * 100
    expected_index_2 = (320.0 / 330.0) * 100
    assert abs(out["cpi_index"].iloc[0] - expected_index_1) < 0.01
    assert abs(out["cpi_index"].iloc[1] - expected_index_2) < 0.01


def test_add_cpi_adjustments_handles_missing():
    """Test CPI adjustment handles missing values."""
    df = pd.DataFrame({"median_income": [80000, None], "cpi": [340.0, 320.0]})
    out = add_cpi_adjustments(df)
    assert out["real_income"].iloc[0] > 0
    assert pd.isna(out["real_income"].iloc[1])


def test_compute_qol_score():
    """Test basic QoL score computation."""
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


def test_compute_qol_score_custom_weights():
    """Test QoL score with custom weights."""
    df = pd.DataFrame(
        {
            "real_income": [50000, 60000],
            "rent_burden_pct": [30, 25],
            "owner_burden_pct": [40, 35],
        }
    )
    out = compute_qol_score(df, weight_real_income=0.6, weight_rent_burden=0.2, weight_owner_burden=0.2)
    assert "qol_score" in out.columns


def test_compute_qol_score_higher_income_better():
    """Test that higher income yields better QoL score."""
    df = pd.DataFrame(
        {
            "real_income": [50000, 80000],
            "rent_burden_pct": [30, 30],
            "owner_burden_pct": [40, 40],
        }
    )
    out = compute_qol_score(df)
    assert out["qol_score"].iloc[1] > out["qol_score"].iloc[0]


def test_compute_qol_score_lower_burden_better():
    """Test that lower housing burden yields better QoL score."""
    df = pd.DataFrame(
        {
            "real_income": [60000, 60000],
            "rent_burden_pct": [20, 40],
            "owner_burden_pct": [25, 45],
        }
    )
    out = compute_qol_score(df)
    assert out["qol_score"].iloc[0] > out["qol_score"].iloc[1]


def test_compute_qol_score_missing_columns():
    """Test QoL score when some columns are missing."""
    df = pd.DataFrame({"real_income": [50000, 60000]})
    out = compute_qol_score(df)
    assert "qol_score" in out.columns


def test_compute_qol_score_handles_nan():
    """Test QoL score handles NaN values."""
    df = pd.DataFrame(
        {
            "real_income": [50000, None, 70000],
            "rent_burden_pct": [30, 25, 35],
            "owner_burden_pct": [40, 35, 45],
        }
    )
    out = compute_qol_score(df)
    assert "qol_score" in out.columns


def test_compute_qol_score_zero_variance():
    """Test QoL score when all values are the same (zero variance)."""
    df = pd.DataFrame(
        {
            "real_income": [60000, 60000, 60000],
            "rent_burden_pct": [30, 30, 30],
            "owner_burden_pct": [40, 40, 40],
        }
    )
    out = compute_qol_score(df)
    # Should handle zero variance gracefully
    assert "qol_score" in out.columns


def test_apply_tax_and_disposable_income():
    """Test disposable income calculation with tax burden."""
    df = pd.DataFrame({"real_income": [100000, 80000], "tax_burden_rate": [0.10, 0.08]})
    out = apply_tax_and_disposable_income(df)
    assert "disposable_income" in out.columns
    assert out["disposable_income"].iloc[0] == 90000
    assert out["disposable_income"].iloc[1] == 73600


def test_apply_tax_and_disposable_income_custom_columns():
    """Test disposable income with custom column names."""
    df = pd.DataFrame({"income": [100000], "tax_rate": [0.10]})
    out = apply_tax_and_disposable_income(df, income_col="income", tax_rate_col="tax_rate", output_col="net_income")
    assert "net_income" in out.columns
    assert out["net_income"].iloc[0] == 90000


def test_apply_tax_and_disposable_income_missing_tax():
    """Test disposable income when tax rate is missing."""
    df = pd.DataFrame({"real_income": [100000], "tax_burden_rate": [None]})
    out = apply_tax_and_disposable_income(df)
    assert pd.isna(out["disposable_income"].iloc[0])


def test_apply_tax_and_disposable_income_zero_tax():
    """Test disposable income with zero tax."""
    df = pd.DataFrame({"real_income": [100000], "tax_burden_rate": [0.0]})
    out = apply_tax_and_disposable_income(df)
    assert out["disposable_income"].iloc[0] == 100000


def test_apply_tax_and_disposable_income_high_tax():
    """Test disposable income with high tax rate."""
    df = pd.DataFrame({"real_income": [100000], "tax_burden_rate": [0.30]})
    out = apply_tax_and_disposable_income(df)
    assert out["disposable_income"].iloc[0] == 70000

