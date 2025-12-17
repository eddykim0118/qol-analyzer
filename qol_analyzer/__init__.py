"""
Quality of Life Analyzer
========================

A comprehensive Python package for analyzing Quality of Life (QoL) across U.S. states
using data from the U.S. Census Bureau (American Community Survey), Bureau of Labor Statistics
(Consumer Price Index), and Tax Foundation (state/local tax burdens).

This package provides end-to-end functionality for:
- Fetching and cleaning multi-source datasets
- Engineering features like real purchasing power and housing burden indices
- Computing composite QoL scores using standardized z-scores
- Running regression analysis to identify QoL drivers
- Visualizing comparative state-level metrics

Quick Start
-----------
>>> from qol_analyzer import fetch_acs_data, fetch_bls_cpi, merge_datasets
>>> from qol_analyzer import add_cpi_adjustments, compute_qol_score
>>>
>>> # Fetch data for 2023
>>> acs = fetch_acs_data(year=2023, states=["CA", "TX", "NY", "UT"])
>>> cpi = fetch_bls_cpi()
>>>
>>> # Merge and compute QoL
>>> merged = merge_datasets(acs, cpi)
>>> with_real_income = add_cpi_adjustments(merged)
>>> qol_data = compute_qol_score(with_real_income)

Target States
------------
- California (CA)
- Texas (TX)
- New York (NY)
- Utah (UT)

Modules
-------
data_fetch : Data retrieval from Census ACS, BLS CPI, and Tax Foundation
data_clean : Data standardization, cleaning, and merging utilities
feature_eng : Feature engineering for CPI-adjusted income and QoL scoring
analysis : Statistical analysis and regression modeling
visualize : Plotting functions for comparative visualizations
"""

from qol_analyzer.data_fetch import (
    fetch_acs_data,
    fetch_bls_cpi,
    fetch_tax_data,
    add_derived_metrics,
)
from qol_analyzer.data_clean import (
    standardize_state_codes,
    handle_missing_values,
    merge_datasets,
)
from qol_analyzer.feature_eng import (
    add_cpi_adjustments,
    compute_qol_score,
    apply_tax_and_disposable_income,
)
from qol_analyzer.analysis import (
    generate_summary_statistics,
    run_regression_analysis,
)
from qol_analyzer.visualize import (
    plot_median_and_real_income_by_state,
    plot_housing_burden_by_state,
    plot_price_to_income_by_state,
    plot_qol_score_by_state,
    plot_real_income_vs_rent_burden,
    plot_real_income_vs_owner_burden,
    plot_state_income_trend,
    plot_state_rent_burden_trend,
    plot_state_owner_burden_trend,
    plot_state_qol_trend,
    plot_real_income_trend_all_states,
    plot_rent_burden_trend_all_states,
    plot_owner_burden_trend_all_states,
    plot_qol_trend_all_states,
)

__all__ = [
    # fetch/clean
    "fetch_acs_data",
    "fetch_bls_cpi",
    "fetch_tax_data",
    "add_derived_metrics",
    "standardize_state_codes",
    "handle_missing_values",
    "merge_datasets",
    # features
    "add_cpi_adjustments",
    "compute_qol_score",
    "apply_tax_and_disposable_income",
    # analysis
    "generate_summary_statistics",
    "run_regression_analysis",
    # viz
    "plot_median_and_real_income_by_state",
    "plot_housing_burden_by_state",
    "plot_price_to_income_by_state",
    "plot_qol_score_by_state",
    "plot_real_income_vs_rent_burden",
    "plot_real_income_vs_owner_burden",
    "plot_state_income_trend",
    "plot_state_rent_burden_trend",
    "plot_state_owner_burden_trend",
    "plot_state_qol_trend",
    "plot_real_income_trend_all_states",
    "plot_rent_burden_trend_all_states",
    "plot_owner_burden_trend_all_states",
    "plot_qol_trend_all_states",
]

