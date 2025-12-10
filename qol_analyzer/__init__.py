"""
Quality of Life Analyzer

Modular utilities to fetch ACS/BLS data, engineer QoL metrics,
run basic analysis, and visualize results.
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

