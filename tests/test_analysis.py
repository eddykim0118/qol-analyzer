"""
Tests for analysis module.
"""

import pandas as pd
import pytest
from qol_analyzer.analysis import generate_summary_statistics, run_regression_analysis


def test_generate_summary_statistics_with_groupby():
    """Test summary statistics generation grouped by state."""
    df = pd.DataFrame({
        "state": ["CA", "CA", "TX", "TX"],
        "income": [80000, 85000, 70000, 75000],
        "rent": [2000, 2100, 1500, 1600]
    })
    result = generate_summary_statistics(df, group_by="state")
    assert "CA" in result.index
    assert "TX" in result.index
    assert ("income", "mean") in result.columns


def test_generate_summary_statistics_without_groupby():
    """Test summary statistics without grouping."""
    df = pd.DataFrame({
        "income": [80000, 85000, 70000],
        "rent": [2000, 2100, 1500]
    })
    result = generate_summary_statistics(df, group_by=None)
    assert "mean" in result.index
    assert "median" in result.index
    assert "std" in result.index
    assert "income" in result.columns


def test_generate_summary_statistics_specific_columns():
    """Test summary statistics with specific numeric columns."""
    df = pd.DataFrame({
        "state": ["CA", "TX"],
        "income": [80000, 70000],
        "rent": [2000, 1500],
        "name": ["Alice", "Bob"]
    })
    result = generate_summary_statistics(df, group_by="state", numeric_columns=["income"])
    assert "income" in str(result.columns)
    assert "rent" not in str(result.columns)


def test_generate_summary_statistics_handles_missing():
    """Test summary statistics handles NaN values."""
    df = pd.DataFrame({
        "state": ["CA", "CA", "TX"],
        "income": [80000, None, 70000]
    })
    result = generate_summary_statistics(df, group_by="state")
    # Should compute stats despite NaN
    assert result is not None


def test_run_regression_analysis_basic():
    """Test basic regression analysis."""
    df = pd.DataFrame({
        "qol_score": [1.5, 0.5, -0.5, -1.5],
        "real_income": [80000, 70000, 60000, 50000],
        "rent_burden_pct": [25, 30, 35, 40],
        "owner_burden_pct": [30, 35, 40, 45]
    })
    result = run_regression_analysis(df)
    assert "r_squared" in result
    assert "coefficients" in result
    assert "intercept" in result
    assert "n_samples" in result
    assert result["n_samples"] == 4


def test_run_regression_analysis_r_squared_range():
    """Test that R-squared is in valid range [0, 1]."""
    df = pd.DataFrame({
        "qol_score": [1.0, 2.0, 3.0, 4.0],
        "real_income": [50000, 60000, 70000, 80000],
        "rent_burden_pct": [40, 35, 30, 25],
        "owner_burden_pct": [45, 40, 35, 30]
    })
    result = run_regression_analysis(df)
    assert 0 <= result["r_squared"] <= 1


def test_run_regression_analysis_coefficients():
    """Test that coefficients are returned for all predictors."""
    df = pd.DataFrame({
        "qol_score": [1.0, 2.0, 3.0, 4.0],
        "real_income": [50000, 60000, 70000, 80000],
        "rent_burden_pct": [40, 35, 30, 25],
        "owner_burden_pct": [45, 40, 35, 30]
    })
    result = run_regression_analysis(df)
    assert "real_income" in result["coefficients"]
    assert "rent_burden_pct" in result["coefficients"]
    assert "owner_burden_pct" in result["coefficients"]


def test_run_regression_analysis_custom_predictors():
    """Test regression with custom predictor variables."""
    df = pd.DataFrame({
        "qol_score": [1.0, 2.0, 3.0],
        "income": [50000, 60000, 70000],
        "rent": [1500, 1600, 1700]
    })
    result = run_regression_analysis(df, predictors=["income", "rent"])
    assert "income" in result["coefficients"]
    assert "rent" in result["coefficients"]


def test_run_regression_analysis_custom_target():
    """Test regression with custom target variable."""
    df = pd.DataFrame({
        "happiness": [1.0, 2.0, 3.0],
        "real_income": [50000, 60000, 70000],
        "rent_burden_pct": [40, 35, 30],
        "owner_burden_pct": [45, 40, 35]
    })
    result = run_regression_analysis(df, target="happiness")
    assert result["n_samples"] == 3


def test_run_regression_analysis_drops_na():
    """Test that regression drops NaN values when drop_na=True."""
    df = pd.DataFrame({
        "qol_score": [1.0, 2.0, None, 4.0],
        "real_income": [50000, 60000, 70000, 80000],
        "rent_burden_pct": [40, 35, 30, 25],
        "owner_burden_pct": [45, None, 35, 30]
    })
    result = run_regression_analysis(df, drop_na=True)
    assert result["n_samples"] == 2  # Only 2 complete rows


def test_run_regression_analysis_missing_target_raises():
    """Test that missing target column raises ValueError."""
    df = pd.DataFrame({
        "income": [50000, 60000, 70000]
    })
    with pytest.raises(ValueError, match="Target"):
        run_regression_analysis(df, target="nonexistent")


def test_run_regression_analysis_no_data_raises():
    """Test that empty DataFrame after cleaning raises ValueError."""
    df = pd.DataFrame({
        "qol_score": [None, None],
        "real_income": [None, None],
        "rent_burden_pct": [None, None],
        "owner_burden_pct": [None, None]
    })
    with pytest.raises(ValueError, match="No data left"):
        run_regression_analysis(df, drop_na=True)


def test_run_regression_analysis_perfect_fit():
    """Test regression with perfect linear relationship."""
    # Perfect linear relationship: qol = 0.001 * income - 50
    df = pd.DataFrame({
        "qol_score": [0.0, 10.0, 20.0, 30.0],
        "real_income": [50000, 60000, 70000, 80000],
        "rent_burden_pct": [0, 0, 0, 0],
        "owner_burden_pct": [0, 0, 0, 0]
    })
    result = run_regression_analysis(df)
    # R-squared should be very close to 1 for perfect fit
    assert result["r_squared"] > 0.99
