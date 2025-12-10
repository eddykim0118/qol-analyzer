from __future__ import annotations

from typing import Iterable, Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")


def _filter_states(df: pd.DataFrame, states: Optional[Iterable[str]]) -> pd.DataFrame:
    if states is None:
        return df
    states = list(states)
    return df[df["state"].isin(states)].copy()


def _filter_year(
    df: pd.DataFrame,
    year: Optional[int],
) -> pd.DataFrame:
    if "year" not in df.columns:
        return df

    if year is None:
        year = int(df["year"].max())

    return df[df["year"] == year].copy()


def _add_bar_labels(ax, fmt: str = ".1f"):
    for container in ax.containers:
        ax.bar_label(container, fmt=f"%{fmt}")


def plot_median_and_real_income_by_state(
    df: pd.DataFrame,
    year: Optional[int] = None,
    states: Optional[Iterable[str]] = None,
) -> plt.Figure:
    data = _filter_year(df, year)
    data = _filter_states(data, states)
    agg = (
        data.groupby("state", as_index=False)[["median_income", "real_income"]]
        .mean()
        .sort_values("state")
    )

    long = agg.melt(
        id_vars="state",
        value_vars=["median_income", "real_income"],
        var_name="income_type",
        value_name="income",
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(
        data=long,
        x="state",
        y="income",
        hue="income_type",
        palette="Set2",
        ax=ax,
    )

    ax.set_title(
        f"Median vs Real Income by State ({int(data['year'].iloc[0])})"
        if "year" in data.columns and not data.empty
        else "Median vs Real Income by State"
    )
    ax.set_xlabel("State")
    ax.set_ylabel("Income (USD)")
    ax.legend(title="Type", labels=["Median income", "Real income"])

    try:
        for container in ax.containers:
            ax.bar_label(container, fmt="%.0f")
    except Exception:
        pass

    fig.tight_layout()
    return fig


def plot_housing_burden_by_state(
    df: pd.DataFrame,
    year: Optional[int] = None,
    states: Optional[Iterable[str]] = None,
) -> plt.Figure:
    data = _filter_year(df, year)
    data = _filter_states(data, states)

    agg = (
        data.groupby("state", as_index=False)[["rent_burden_pct", "owner_burden_pct"]]
        .mean()
        .sort_values("state")
    )

    long = agg.melt(
        id_vars="state",
        value_vars=["rent_burden_pct", "owner_burden_pct"],
        var_name="burden_type",
        value_name="burden_pct",
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(
        data=long,
        x="state",
        y="burden_pct",
        hue="burden_type",
        palette="Set2",
        ax=ax,
    )

    year_label = (
        f" ({int(data['year'].iloc[0])})"
        if "year" in data.columns and not data.empty
        else ""
    )
    ax.set_title(
        "Housing Cost Burden (Share of Households Spending 30%+ on Housing)"
        + year_label
    )
    ax.set_xlabel("State")
    ax.set_ylabel("Percent of households (%)")
    ax.legend(
        title="Group",
        labels=["Renters (30%+)", "Owners (30%+)"],
    )

    _add_bar_labels(ax, fmt=".1f")

    fig.tight_layout()
    return fig


def plot_price_to_income_by_state(
    df: pd.DataFrame,
    year: Optional[int] = None,
    states: Optional[Iterable[str]] = None,
) -> plt.Figure:

    data = _filter_year(df, year)
    data = _filter_states(data, states)

    agg = (
        data.groupby("state", as_index=False)["price_to_income_ratio"]
        .mean()
        .sort_values("state")
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(
        data=agg,
        x="state",
        y="price_to_income_ratio",
        color="#4C72B0",
        ax=ax,
    )

    year_label = (
        f" ({int(data['year'].iloc[0])})"
        if "year" in data.columns and not data.empty
        else ""
    )
    ax.set_title("Price-to-Income Ratio by State" + year_label)
    ax.set_xlabel("State")
    ax.set_ylabel("Median home value / annual income")

    _add_bar_labels(ax, fmt=".2f")

    fig.tight_layout()
    return fig


def plot_qol_score_by_state(
    df: pd.DataFrame,
    year: Optional[int] = None,
    states: Optional[Iterable[str]] = None,
) -> plt.Figure:
    if "qol_score" not in df.columns:
        raise ValueError("DataFrame must contain 'qol_score' column.")

    data = _filter_year(df, year)
    data = _filter_states(data, states)

    agg = (
        data.groupby("state", as_index=False)["qol_score"]
        .mean()
        .sort_values("state")
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(
        data=agg,
        x="state",
        y="qol_score",
        color="#55A868",
        ax=ax,
    )

    year_label = (
        f" ({int(data['year'].iloc[0])})"
        if "year" in data.columns and not data.empty
        else ""
    )
    ax.set_title("Quality of Life Score by State" + year_label)
    ax.set_xlabel("State")
    ax.set_ylabel("QoL score (relative)")

    try:
        _add_bar_labels(ax, fmt=".2f")
    except Exception:
        pass

    fig.tight_layout()
    return fig

def plot_real_income_vs_rent_burden(
    df: pd.DataFrame,
    year: Optional[int] = None,
    states: Optional[Iterable[str]] = None,
) -> plt.Figure:
    data = _filter_states(df, states)
    if year is not None:
        data = _filter_year(data, year)

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.scatterplot(
        data=data,
        x="real_income",
        y="rent_burden_pct",
        hue="state",
        s=120,
        palette="deep",
        ax=ax,
    )

    title = "Real Income vs Rent Burden (Renters, 30%+)"
    if year is not None and "year" in data.columns and not data.empty:
        title += f" – {int(year)}"

    ax.set_title(title)
    ax.set_xlabel("Real income (CPI-adjusted)")
    ax.set_ylabel("Rent burden (% of households)")
    ax.legend(title="State")

    fig.tight_layout()
    return fig


def plot_real_income_vs_owner_burden(
    df: pd.DataFrame,
    year: Optional[int] = None,
    states: Optional[Iterable[str]] = None,
) -> plt.Figure:

    data = _filter_states(df, states)
    if year is not None:
        data = _filter_year(data, year)

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.scatterplot(
        data=data,
        x="real_income",
        y="owner_burden_pct",
        hue="state",
        s=120,
        palette="deep",
        ax=ax,
    )

    title = "Real Income vs Owner Housing Burden (30%+)"
    if year is not None and "year" in data.columns and not data.empty:
        title += f" – {int(year)}"

    ax.set_title(title)
    ax.set_xlabel("Real income (CPI-adjusted)")
    ax.set_ylabel("Owner burden (% of households)")
    ax.legend(title="State")

    fig.tight_layout()
    return fig

def plot_state_timeseries(
    df: pd.DataFrame,
    state: str,
    y: str,
    ylabel: Optional[str] = None,
    title: Optional[str] = None,
) -> plt.Figure:
    if "year" not in df.columns:
        raise ValueError("DataFrame must contain a 'year' column for time series plots.")

    data = df[df["state"] == state].copy()
    data = data.sort_values("year")

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.lineplot(
        data=data,
        x="year",
        y=y,
        marker="o",
        linewidth=2,
        ax=ax,
    )

    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel or y.replace("_", " ").title())

    if title is None:
        ax.set_title(f"{state}: {y.replace('_', ' ').title()} (Trend)")
    else:
        ax.set_title(title)


    for x_val, y_val in zip(data["year"], data[y]):
        ax.text(
            x_val,
            y_val,
            f"{y_val:.1f}",
            ha="center",
            va="bottom",
            fontsize=8,
            )
    fig.tight_layout()
    return fig


def plot_state_income_trend(df: pd.DataFrame, state: str) -> plt.Figure:
    return plot_state_timeseries(
        df,
        state=state,
        y="real_income",
        ylabel="Real income (CPI-adjusted)",
        title=f"{state}: Real Income Trend",
    )


def plot_state_rent_burden_trend(df: pd.DataFrame, state: str) -> plt.Figure:
    return plot_state_timeseries(
        df,
        state=state,
        y="rent_burden_pct",
        ylabel="Rent burden (% of households)",
        title=f"{state}: Rent Burden Trend",
    )


def plot_state_owner_burden_trend(df: pd.DataFrame, state: str) -> plt.Figure:
    return plot_state_timeseries(
        df,
        state=state,
        y="owner_burden_pct",
        ylabel="Owner burden (% of households)",
        title=f"{state}: Owner Burden Trend",
    )


def plot_state_qol_trend(df: pd.DataFrame, state: str) -> plt.Figure:
    if "qol_score" not in df.columns:
        raise ValueError("DataFrame must contain 'qol_score' column.")
    return plot_state_timeseries(
        df,
        state=state,
        y="qol_score",
        ylabel="QoL score (relative)",
        title=f"{state}: QoL Score Trend",
    )


def plot_real_income_trend_all_states(df: pd.DataFrame) -> plt.Figure:
    if "year" not in df.columns:
        raise ValueError("DataFrame must contain 'year' column for trend plots.")

    data = df.copy()
    data = data.sort_values(["state", "year"])

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.lineplot(
        data=data,
        x="year",
        y="real_income",
        hue="state",
        marker="o",
        linewidth=2,
        ax=ax,
    )

    ax.set_title("Real Income Trend by State")
    ax.set_xlabel("Year")
    ax.set_ylabel("Real income (CPI-adjusted)")
    ax.legend(title="State")

    fig.tight_layout()
    return fig


def plot_rent_burden_trend_all_states(df: pd.DataFrame) -> plt.Figure:
    if "year" not in df.columns:
        raise ValueError("DataFrame must contain 'year' column for trend plots.")

    data = df.copy()
    data = data.sort_values(["state", "year"])

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.lineplot(
        data=data,
        x="year",
        y="rent_burden_pct",
        hue="state",
        marker="o",
        linewidth=2,
        ax=ax,
    )

    ax.set_title("Rent Burden Trend by State (30%+ of Income)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Rent burden (% of households)")
    ax.legend(title="State")

    fig.tight_layout()
    return fig


def plot_owner_burden_trend_all_states(df: pd.DataFrame) -> plt.Figure:
    if "year" not in df.columns:
        raise ValueError("DataFrame must contain 'year' column for trend plots.")

    data = df.copy()
    data = data.sort_values(["state", "year"])

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.lineplot(
        data=data,
        x="year",
        y="owner_burden_pct",
        hue="state",
        marker="o",
        linewidth=2,
        ax=ax,
    )

    ax.set_title("Owner Housing Burden Trend by State (30%+ of Income)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Owner burden (% of households)")
    ax.legend(title="State")

    fig.tight_layout()
    return fig


def plot_qol_trend_all_states(df: pd.DataFrame) -> plt.Figure:
    if "year" not in df.columns:
        raise ValueError("DataFrame must contain 'year' column for trend plots.")
    if "qol_score" not in df.columns:
        raise ValueError("DataFrame must contain 'qol_score' column.")

    data = df.copy()
    data = data.sort_values(["state", "year"])

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.lineplot(
        data=data,
        x="year",
        y="qol_score",
        hue="state",
        marker="o",
        linewidth=2,
        ax=ax,
    )

    ax.set_title("QoL Score Trend by State")
    ax.set_xlabel("Year")
    ax.set_ylabel("QoL score (relative)")
    ax.legend(title="State")

    fig.tight_layout()
    return fig

# this one is just testing
if __name__ == "__main__":
    import os

    path = "qol_with_real_income_peryear.csv"

    if not os.path.exists(path):
        print(f"{path} not found; main test skipped.")
    else:
        df_test = pd.read_csv(path)
        print(f"Loaded {path}")

        fig1 = plot_median_and_real_income_by_state(df_test)          # income bar
        fig2 = plot_housing_burden_by_state(df_test)                  # burden bar
        fig3 = plot_price_to_income_by_state(df_test)                 # price/income
        fig4 = plot_real_income_vs_rent_burden(df_test)               # scatter

        fig5 = plot_real_income_trend_all_states(df_test)             # real income trend
        fig6 = plot_rent_burden_trend_all_states(df_test)             # rent burden trend
        fig7 = plot_owner_burden_trend_all_states(df_test)            # owner burden trend
        fig8 = plot_qol_trend_all_states(df_test)                     # QoL trend (all states)
        # QoL trend(split)
        for state in ["CA", "NY", "TX", "UT"]:
            fig = plot_state_qol_trend(df_test, state)

        plt.show()


