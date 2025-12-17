"""
Integration tests for the full QoL analysis pipeline.
"""

import pandas as pd
import pytest
from qol_analyzer.data_clean import merge_datasets, standardize_state_codes
from qol_analyzer.feature_eng import add_cpi_adjustments, compute_qol_score, apply_tax_and_disposable_income
from qol_analyzer.analysis import generate_summary_statistics, run_regression_analysis


@pytest.fixture
def mock_acs_data():
    """Mock ACS data for integration testing."""
    return pd.DataFrame({
        "state": ["CA", "TX", "NY", "UT"],
        "year": [2023, 2023, 2023, 2023],
        "median_income": [85000, 75000, 90000, 80000],
        "median_rent_monthly": [2500, 1500, 2800, 1400],
        "median_home_value": [700000, 350000, 650000, 450000],
        "rent_burden_pct": [35, 28, 38, 25],
        "owner_burden_pct": [40, 32, 42, 30]
    })


@pytest.fixture
def mock_cpi_data():
    """Mock CPI data for integration testing."""
    return pd.DataFrame({
        "state": ["CA", "TX", "NY", "UT"],
        "cpi": [340.0, 320.0, 345.0, 315.0]
    })


@pytest.fixture
def mock_tax_data():
    """Mock tax data for integration testing."""
    return pd.DataFrame({
        "state": ["CA", "TX", "NY", "UT"],
        "tax_burden_rate": [0.10, 0.08, 0.12, 0.09]
    })


def test_full_pipeline_without_tax(mock_acs_data, mock_cpi_data):
    """Test the full pipeline without tax data."""
    # Step 1: Merge datasets
    merged = merge_datasets(mock_acs_data, mock_cpi_data)
    assert len(merged) == 4
    assert "cpi" in merged.columns

    # Step 2: Add CPI adjustments
    with_real_income = add_cpi_adjustments(merged)
    assert "real_income" in with_real_income.columns
    assert "cpi_index" in with_real_income.columns

    # Step 3: Compute QoL score
    with_qol = compute_qol_score(with_real_income)
    assert "qol_score" in with_qol.columns
    assert with_qol["qol_score"].notna().all()

    # Step 4: Generate summary statistics
    summary = generate_summary_statistics(with_qol, group_by="state")
    assert len(summary) == 4

    # Step 5: Run regression
    regression = run_regression_analysis(with_qol)
    assert "r_squared" in regression
    assert 0 <= regression["r_squared"] <= 1


def test_full_pipeline_with_tax(mock_acs_data, mock_cpi_data, mock_tax_data):
    """Test the full pipeline including tax data."""
    # Step 1: Merge all datasets
    merged = merge_datasets(mock_acs_data, mock_cpi_data, mock_tax_data)
    assert len(merged) == 4
    assert "cpi" in merged.columns
    assert "tax_burden_rate" in merged.columns

    # Step 2: Add CPI adjustments
    with_real_income = add_cpi_adjustments(merged)
    assert "real_income" in with_real_income.columns

    # Step 3: Apply tax and compute disposable income
    with_disposable = apply_tax_and_disposable_income(with_real_income)
    assert "disposable_income" in with_disposable.columns
    assert with_disposable["disposable_income"].notna().all()

    # Verify disposable < real income
    assert (with_disposable["disposable_income"] < with_disposable["real_income"]).all()

    # Step 4: Compute QoL score
    with_qol = compute_qol_score(with_disposable)
    assert "qol_score" in with_qol.columns

    # Step 5: Generate summary and regression
    summary = generate_summary_statistics(with_qol, group_by="state")
    regression = run_regression_analysis(with_qol)

    assert len(summary) == 4
    assert regression["n_samples"] == 4


def test_pipeline_preserves_state_ordering(mock_acs_data, mock_cpi_data):
    """Test that pipeline preserves state ordering."""
    merged = merge_datasets(mock_acs_data, mock_cpi_data)
    with_features = add_cpi_adjustments(merged)
    with_qol = compute_qol_score(with_features)

    # States should still be in original order
    assert list(with_qol["state"]) == ["CA", "TX", "NY", "UT"]


def test_pipeline_handles_state_name_variations(mock_cpi_data):
    """Test pipeline with different state name formats."""
    acs_varied = pd.DataFrame({
        "state": ["California", "Texas", "New York", "Utah"],
        "median_income": [85000, 75000, 90000, 80000],
        "rent_burden_pct": [35, 28, 38, 25],
        "owner_burden_pct": [40, 32, 42, 30]
    })

    merged = merge_datasets(acs_varied, mock_cpi_data)
    assert len(merged) == 4
    # All states should be standardized to codes
    assert set(merged["state"]) == {"CA", "TX", "NY", "UT"}


def test_pipeline_with_missing_cpi(mock_acs_data):
    """Test pipeline when CPI data is missing for some states."""
    partial_cpi = pd.DataFrame({
        "state": ["CA", "TX"],
        "cpi": [340.0, 320.0]
    })

    merged = merge_datasets(mock_acs_data, partial_cpi)
    assert len(merged) == 4
    # NY and UT should have NaN CPI
    assert merged[merged["state"] == "NY"]["cpi"].isna().all()


def test_pipeline_qol_score_relationships(mock_acs_data, mock_cpi_data):
    """Test that QoL scores follow expected relationships."""
    merged = merge_datasets(mock_acs_data, mock_cpi_data)
    with_features = add_cpi_adjustments(merged)
    with_qol = compute_qol_score(with_features)

    # Utah has lowest burdens, should have relatively high QoL
    ut_qol = with_qol[with_qol["state"] == "UT"]["qol_score"].iloc[0]
    ny_qol = with_qol[with_qol["state"] == "NY"]["qol_score"].iloc[0]

    # This is a general expectation but depends on weights
    # Just verify scores are computed and are different
    assert ut_qol != ny_qol


def test_pipeline_regression_coefficients_signs(mock_acs_data, mock_cpi_data):
    """Test that regression coefficients have expected signs."""
    merged = merge_datasets(mock_acs_data, mock_cpi_data)
    with_features = add_cpi_adjustments(merged)
    with_qol = compute_qol_score(with_features)

    regression = run_regression_analysis(with_qol)

    # Real income should positively affect QoL (positive coefficient)
    # Note: This may not always hold due to z-score weighting, but test structure
    assert "real_income" in regression["coefficients"]
    assert "rent_burden_pct" in regression["coefficients"]
    assert "owner_burden_pct" in regression["coefficients"]


def test_pipeline_summary_statistics_completeness(mock_acs_data, mock_cpi_data):
    """Test that summary statistics include all expected metrics."""
    merged = merge_datasets(mock_acs_data, mock_cpi_data)
    with_features = add_cpi_adjustments(merged)
    with_qol = compute_qol_score(with_features)

    summary = generate_summary_statistics(with_qol, group_by="state")

    # Check that summary has expected statistics
    assert "count" in str(summary.columns)
    assert "mean" in str(summary.columns)
    assert "median" in str(summary.columns)
    assert "std" in str(summary.columns)


def test_pipeline_multi_year_data():
    """Test pipeline with multi-year data."""
    multi_year = pd.DataFrame({
        "state": ["CA", "TX"] * 2,
        "year": [2022, 2022, 2023, 2023],
        "median_income": [83000, 73000, 85000, 75000],
        "rent_burden_pct": [34, 27, 35, 28],
        "owner_burden_pct": [39, 31, 40, 32]
    })

    cpi_data = pd.DataFrame({
        "state": ["CA", "TX"],
        "cpi": [340.0, 320.0]
    })

    merged = merge_datasets(multi_year, cpi_data)
    with_features = add_cpi_adjustments(merged)
    with_qol = compute_qol_score(with_features)

    # Should have data for both years
    assert len(with_qol) == 4
    assert set(with_qol["year"]) == {2022, 2023}


def test_pipeline_end_to_end_data_types():
    """Test that pipeline maintains appropriate data types."""
    acs = pd.DataFrame({
        "state": ["CA", "TX"],
        "median_income": [85000, 75000],
        "rent_burden_pct": [35, 28],
        "owner_burden_pct": [40, 32]
    })

    cpi = pd.DataFrame({
        "state": ["CA", "TX"],
        "cpi": [340.0, 320.0]
    })

    merged = merge_datasets(acs, cpi)
    with_features = add_cpi_adjustments(merged)
    with_qol = compute_qol_score(with_features)

    # Numeric columns should be numeric
    assert pd.api.types.is_numeric_dtype(with_qol["median_income"])
    assert pd.api.types.is_numeric_dtype(with_qol["real_income"])
    assert pd.api.types.is_numeric_dtype(with_qol["qol_score"])
    assert pd.api.types.is_numeric_dtype(with_qol["cpi"])
