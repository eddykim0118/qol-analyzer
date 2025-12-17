"""
Regression analysis script to validate R² > 0.7 requirement from proposal.

This script runs comprehensive regression analysis on the processed QoL data
and generates a report documenting whether the proposal's technical evaluation
metric (R² > 0.7) is achieved.
"""

import pandas as pd
from qol_analyzer.analysis import run_regression_analysis, generate_summary_statistics


def main():
    print("=" * 80)
    print("QoL Analyzer - Regression Analysis Report")
    print("=" * 80)
    print("\nProposal Requirement: R² > 0.7 for regression model")
    print("Target: Determine if housing burden or CPI contributes more to QoL\n")

    # Load processed data
    data_path = "data/processed/qol_with_real_income_peryear.csv"
    print(f"Loading data from: {data_path}")

    try:
        df = pd.read_csv(data_path)
        print(f"✓ Data loaded successfully")
        print(f"  - Total observations: {len(df)}")
        print(f"  - Years covered: {sorted(df['year'].unique())}")
        print(f"  - States covered: {sorted(df['state'].unique())}")
    except FileNotFoundError:
        print(f"✗ Error: File not found at {data_path}")
        print("  Please run the pipeline first: python3 -m scripts.run_pipeline")
        return

    # Summary statistics
    print("\n" + "-" * 80)
    print("SUMMARY STATISTICS BY STATE")
    print("-" * 80)

    summary_cols = ["real_income", "rent_burden_pct", "owner_burden_pct", "qol_score"]
    summary = generate_summary_statistics(df, group_by="state", numeric_columns=summary_cols)
    print(summary)

    # Overall statistics
    print("\n" + "-" * 80)
    print("OVERALL STATISTICS (All States, All Years)")
    print("-" * 80)

    overall_summary = generate_summary_statistics(df, group_by=None, numeric_columns=summary_cols)
    print(overall_summary)

    # Primary regression: Default predictors
    print("\n" + "=" * 80)
    print("REGRESSION ANALYSIS #1: Default Predictors")
    print("=" * 80)
    print("Target: qol_score")
    print("Predictors: real_income, rent_burden_pct, owner_burden_pct\n")

    try:
        results1 = run_regression_analysis(df)

        print(f"R² (Coefficient of Determination): {results1['r_squared']:.6f}")
        print(f"Sample Size: {results1['n_samples']} observations")
        print(f"Intercept: {results1['intercept']:.6f}")
        print(f"\nCoefficients:")
        for var, coef in results1['coefficients'].items():
            print(f"  {var:25s}: {coef:12.6f}")

        # Evaluation
        print("\n" + "-" * 80)
        if results1['r_squared'] > 0.7:
            print(f"✓ PASS: R² = {results1['r_squared']:.4f} > 0.7 (Proposal requirement MET)")
        else:
            print(f"✗ FAIL: R² = {results1['r_squared']:.4f} ≤ 0.7 (Proposal requirement NOT met)")
            print("  Note: With only 4 states and limited observations, achieving R² > 0.7")
            print("  is challenging. Consider this in context of small sample size.")
        print("-" * 80)

        # Interpretation
        print("\nINTERPRETATION:")
        print(f"- The model explains {results1['r_squared']*100:.2f}% of variance in QoL scores")

        # Determine dominant factor
        coefs = results1['coefficients']
        abs_coefs = {k: abs(v) for k, v in coefs.items()}
        dominant = max(abs_coefs, key=abs_coefs.get)
        print(f"- Dominant predictor: {dominant} (|coef| = {abs_coefs[dominant]:.4f})")

        if abs_coefs['real_income'] > max(abs_coefs['rent_burden_pct'], abs_coefs['owner_burden_pct']):
            print("  → CPI-adjusted income is the primary driver of QoL differences")
        elif abs_coefs['rent_burden_pct'] > abs_coefs['owner_burden_pct']:
            print("  → Rent burden is the primary driver of QoL differences")
        else:
            print("  → Owner cost burden is the primary driver of QoL differences")

    except Exception as e:
        print(f"✗ Error running regression: {e}")
        return

    # Alternative regression: Include disposable income
    print("\n" + "=" * 80)
    print("REGRESSION ANALYSIS #2: Alternative Predictors")
    print("=" * 80)
    print("Target: qol_score")
    print("Predictors: disposable_income, rent_burden_pct, owner_burden_pct\n")

    try:
        results2 = run_regression_analysis(
            df,
            predictors=["disposable_income", "rent_burden_pct", "owner_burden_pct"]
        )

        print(f"R² (Coefficient of Determination): {results2['r_squared']:.6f}")
        print(f"Sample Size: {results2['n_samples']} observations")
        print(f"Intercept: {results2['intercept']:.6f}")
        print(f"\nCoefficients:")
        for var, coef in results2['coefficients'].items():
            print(f"  {var:25s}: {coef:12.6f}")

        if results2['r_squared'] > 0.7:
            print(f"\n✓ Alternative model: R² = {results2['r_squared']:.4f} > 0.7")
        else:
            print(f"\n✗ Alternative model: R² = {results2['r_squared']:.4f} ≤ 0.7")

    except Exception as e:
        print(f"Note: Could not run alternative regression: {e}")

    # By-year analysis
    print("\n" + "=" * 80)
    print("REGRESSION ANALYSIS #3: By Year")
    print("=" * 80)

    for year in sorted(df['year'].unique()):
        year_data = df[df['year'] == year]
        try:
            year_results = run_regression_analysis(year_data)
            print(f"\nYear {year}:")
            print(f"  R² = {year_results['r_squared']:.4f}, n = {year_results['n_samples']}")
            if year_results['r_squared'] > 0.7:
                print(f"  ✓ Meets threshold")
            else:
                print(f"  ✗ Below threshold")
        except Exception as e:
            print(f"\nYear {year}: Could not compute (likely insufficient data)")

    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"\nPrimary Model R²: {results1['r_squared']:.4f}")
    print(f"Proposal Target: 0.7000")
    print(f"Status: {'✓ ACHIEVED' if results1['r_squared'] > 0.7 else '✗ NOT ACHIEVED'}")

    if results1['r_squared'] <= 0.7:
        print("\nCONTEXT:")
        print("- The proposal targets 4 states, which provides limited observations")
        print("- QoL is inherently multidimensional (not fully captured by 3 predictors)")
        print("- State-level aggregation masks within-state variation")
        print("- R² between 0.5-0.7 is reasonable for cross-sectional social science data")
        print(f"- Current R² of {results1['r_squared']:.4f} indicates a moderate relationship")

    print("\nRECOMMENDATIONS:")
    if results1['r_squared'] > 0.7:
        print("- Model performs well and meets proposal requirements")
        print("- Document this result in project deliverables")
    else:
        print("- Consider multi-year pooled analysis for more observations")
        print("- Explore additional predictors (e.g., median home value, CPI index)")
        print("- Use adjusted R² for small sample sizes")
        print("- Document the context of limited sample size in findings")

    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
