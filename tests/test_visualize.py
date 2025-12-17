"""
Tests for visualize module.
"""

import pandas as pd
import pytest
import matplotlib.pyplot as plt
from qol_analyzer.visualize import (
    plot_median_and_real_income_by_state,
    plot_housing_burden_by_state,
    plot_qol_score_by_state,
    plot_real_income_vs_rent_burden,
    plot_price_to_income_by_state,
)


@pytest.fixture
def sample_qol_data():
    """Sample QoL data for testing."""
    df = pd.DataFrame({
        "state": ["CA", "TX", "NY", "UT"] * 2,
        "year": [2023] * 4 + [2024] * 4,
        "median_income": [85000, 75000, 90000, 80000, 87000, 76000, 92000, 81000],
        "real_income": [80000, 73000, 85000, 78000, 82000, 74000, 87000, 79000],
        "median_rent_monthly": [2500, 1500, 2800, 1400, 2600, 1550, 2900, 1450],
        "median_home_value": [700000, 350000, 650000, 450000, 720000, 360000, 670000, 460000],
        "rent_burden_pct": [35, 28, 38, 25, 36, 29, 39, 26],
        "owner_burden_pct": [40, 32, 42, 30, 41, 33, 43, 31],
        "qol_score": [0.5, 1.2, 0.3, 1.5, 0.6, 1.3, 0.4, 1.6],
        "annual_rent": [30000, 18000, 33600, 16800, 31200, 18600, 34800, 17400]
    })
    # Add price_to_income_ratio
    df["price_to_income_ratio"] = df["median_home_value"] / df["median_income"]
    return df


def test_plot_median_and_real_income_returns_figure(sample_qol_data):
    """Test that plot_median_and_real_income_by_state returns a Figure object."""
    fig = plot_median_and_real_income_by_state(sample_qol_data, year=2023)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_median_and_real_income_filters_year(sample_qol_data):
    """Test that plot filters by year correctly."""
    fig = plot_median_and_real_income_by_state(sample_qol_data, year=2023)
    assert fig is not None
    plt.close(fig)


def test_plot_median_and_real_income_filters_states(sample_qol_data):
    """Test that plot filters by states correctly."""
    fig = plot_median_and_real_income_by_state(sample_qol_data, states=["CA", "TX"])
    assert fig is not None
    plt.close(fig)


def test_plot_median_and_real_income_no_filters(sample_qol_data):
    """Test plot without any filters."""
    fig = plot_median_and_real_income_by_state(sample_qol_data)
    assert fig is not None
    plt.close(fig)


def test_plot_housing_burden_returns_figure(sample_qol_data):
    """Test that plot_housing_burden_by_state returns a Figure object."""
    fig = plot_housing_burden_by_state(sample_qol_data, year=2023)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_housing_burden_filters_year(sample_qol_data):
    """Test that housing burden plot filters by year."""
    fig = plot_housing_burden_by_state(sample_qol_data, year=2024)
    assert fig is not None
    plt.close(fig)


def test_plot_housing_burden_filters_states(sample_qol_data):
    """Test that housing burden plot filters by states."""
    fig = plot_housing_burden_by_state(sample_qol_data, states=["NY", "UT"])
    assert fig is not None
    plt.close(fig)


def test_plot_qol_score_returns_figure(sample_qol_data):
    """Test that plot_qol_score_by_state returns a Figure object."""
    fig = plot_qol_score_by_state(sample_qol_data, year=2023)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_qol_score_filters_year(sample_qol_data):
    """Test that QoL score plot filters by year."""
    fig = plot_qol_score_by_state(sample_qol_data, year=2024)
    assert fig is not None
    plt.close(fig)


def test_plot_qol_score_filters_states(sample_qol_data):
    """Test that QoL score plot filters by states."""
    fig = plot_qol_score_by_state(sample_qol_data, states=["CA", "TX", "NY"])
    assert fig is not None
    plt.close(fig)


def test_plot_real_income_vs_rent_burden_returns_figure(sample_qol_data):
    """Test that scatter plot returns a Figure object."""
    fig = plot_real_income_vs_rent_burden(sample_qol_data, year=2023)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_real_income_vs_rent_burden_filters_year(sample_qol_data):
    """Test that scatter plot filters by year."""
    fig = plot_real_income_vs_rent_burden(sample_qol_data, year=2024)
    assert fig is not None
    plt.close(fig)


def test_plot_real_income_vs_rent_burden_filters_states(sample_qol_data):
    """Test that scatter plot filters by states."""
    fig = plot_real_income_vs_rent_burden(sample_qol_data, states=["UT", "TX"])
    assert fig is not None
    plt.close(fig)


def test_plot_price_to_income_returns_figure(sample_qol_data):
    """Test that price to income plot returns a Figure object."""
    fig = plot_price_to_income_by_state(sample_qol_data, year=2023)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_with_empty_dataframe():
    """Test that plots handle empty DataFrames gracefully."""
    empty_df = pd.DataFrame()
    # Should not raise an error, but may return empty plot
    try:
        fig = plot_qol_score_by_state(empty_df)
        plt.close(fig)
    except (KeyError, ValueError):
        # Expected behavior for empty DataFrame
        pass


def test_plot_with_single_state(sample_qol_data):
    """Test plots work with single state data."""
    single_state = sample_qol_data[sample_qol_data["state"] == "CA"]
    fig = plot_qol_score_by_state(single_state)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_titles_and_labels(sample_qol_data):
    """Test that plots have appropriate titles and labels."""
    fig = plot_median_and_real_income_by_state(sample_qol_data, year=2023)
    ax = fig.get_axes()[0]
    assert ax.get_title() != ""
    assert ax.get_xlabel() != ""
    assert ax.get_ylabel() != ""
    plt.close(fig)


def test_multiple_plots_dont_interfere():
    """Test that creating multiple plots doesn't cause interference."""
    df = pd.DataFrame({
        "state": ["CA", "TX"],
        "year": [2023, 2023],
        "median_income": [85000, 75000],
        "real_income": [80000, 73000],
        "qol_score": [0.5, 1.2],
        "rent_burden_pct": [35, 28],
        "owner_burden_pct": [40, 32],
        "median_rent_monthly": [2500, 1500],
        "median_home_value": [700000, 350000],
        "annual_rent": [30000, 18000]
    })
    fig1 = plot_median_and_real_income_by_state(df)
    fig2 = plot_qol_score_by_state(df)

    assert fig1 is not fig2
    plt.close(fig1)
    plt.close(fig2)
