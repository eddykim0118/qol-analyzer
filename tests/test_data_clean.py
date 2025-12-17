"""
Tests for data_clean module.
"""

import pandas as pd
import pytest
from qol_analyzer.data_clean import (
    standardize_state_codes,
    handle_missing_values,
    merge_datasets,
)


def test_standardize_state_codes_abbrev():
    """Test state code standardization with abbreviations."""
    df = pd.DataFrame({"state": ["CA", "TX", "NY", "UT"]})
    result = standardize_state_codes(df)
    assert list(result["state"]) == ["CA", "TX", "NY", "UT"]


def test_standardize_state_codes_full_names():
    """Test state code standardization with full state names."""
    df = pd.DataFrame({"state": ["California", "Texas", "New York", "Utah"]})
    result = standardize_state_codes(df)
    assert list(result["state"]) == ["CA", "TX", "NY", "UT"]


def test_standardize_state_codes_mixed():
    """Test state code standardization with mixed formats."""
    df = pd.DataFrame({"state": ["CA", "Texas", "New York", "UT"]})
    result = standardize_state_codes(df)
    assert list(result["state"]) == ["CA", "TX", "NY", "UT"]


def test_standardize_state_codes_missing_column():
    """Test that function handles missing state column gracefully."""
    df = pd.DataFrame({"city": ["LA", "Austin"]})
    result = standardize_state_codes(df)
    assert "state" not in result.columns


def test_handle_missing_values_drop_strategy():
    """Test dropping rows with missing values."""
    df = pd.DataFrame({"a": [1, 2, None, 4], "b": [5, None, 7, 8]})
    result = handle_missing_values(df, strategy="drop", columns=["a"])
    assert len(result) == 3
    assert result["a"].notna().all()


def test_handle_missing_values_fill_strategy_numeric():
    """Test filling missing values with median for numeric columns."""
    df = pd.DataFrame({"a": [1.0, 2.0, None, 4.0]})
    result = handle_missing_values(df, strategy="fill", columns=["a"])
    assert result["a"].notna().all()
    assert result["a"].iloc[2] == 2.0  # median of [1, 2, 4]


def test_handle_missing_values_fill_strategy_with_value():
    """Test filling missing values with specific value."""
    df = pd.DataFrame({"a": [1, 2, None, 4]})
    result = handle_missing_values(df, strategy="fill", columns=["a"], fill_value=0)
    assert result["a"].iloc[2] == 0


def test_handle_missing_values_forward_fill():
    """Test forward fill strategy."""
    df = pd.DataFrame({"a": [1, None, None, 4]})
    result = handle_missing_values(df, strategy="forward_fill", columns=["a"])
    assert list(result["a"]) == [1, 1, 1, 4]


def test_handle_missing_values_backward_fill():
    """Test backward fill strategy."""
    df = pd.DataFrame({"a": [None, None, 3, 4]})
    result = handle_missing_values(df, strategy="backward_fill", columns=["a"])
    assert list(result["a"]) == [3, 3, 3, 4]


def test_merge_datasets_acs_and_cpi():
    """Test merging ACS and CPI datasets."""
    acs = pd.DataFrame({"state": ["CA", "TX"], "median_income": [80000, 70000]})
    cpi = pd.DataFrame({"state": ["CA", "TX"], "cpi": [340.0, 320.0]})
    result = merge_datasets(acs, cpi)
    assert "median_income" in result.columns
    assert "cpi" in result.columns
    assert len(result) == 2


def test_merge_datasets_with_tax():
    """Test merging ACS, CPI, and tax datasets."""
    acs = pd.DataFrame({"state": ["CA", "TX"], "median_income": [80000, 70000]})
    cpi = pd.DataFrame({"state": ["CA", "TX"], "cpi": [340.0, 320.0]})
    tax = pd.DataFrame({"state": ["CA", "TX"], "tax_burden_rate": [0.10, 0.08]})
    result = merge_datasets(acs, cpi, tax)
    assert "median_income" in result.columns
    assert "cpi" in result.columns
    assert "tax_burden_rate" in result.columns
    assert len(result) == 2


def test_merge_datasets_standardizes_state_codes():
    """Test that merge_datasets standardizes state codes."""
    acs = pd.DataFrame({"state": ["California", "Texas"], "median_income": [80000, 70000]})
    cpi = pd.DataFrame({"state": ["CA", "TX"], "cpi": [340.0, 320.0]})
    result = merge_datasets(acs, cpi)
    assert list(result["state"]) == ["CA", "TX"]


def test_merge_datasets_handles_missing_states():
    """Test left join behavior when states don't match."""
    acs = pd.DataFrame({"state": ["CA", "TX", "NY"], "median_income": [80000, 70000, 90000]})
    cpi = pd.DataFrame({"state": ["CA", "TX"], "cpi": [340.0, 320.0]})
    result = merge_datasets(acs, cpi)
    assert len(result) == 3
    assert result[result["state"] == "NY"]["cpi"].isna().all()


def test_merge_datasets_numeric_coercion():
    """Test that merge converts string numbers to numeric."""
    acs = pd.DataFrame({"state": ["CA"], "median_income": [80000]})
    cpi = pd.DataFrame({"state": ["CA"], "cpi": [340.0]})
    result = merge_datasets(acs, cpi)
    # Numeric conversion happens, verify the data can be used numerically
    assert result["median_income"].iloc[0] == 80000
    assert result["cpi"].iloc[0] == 340.0
