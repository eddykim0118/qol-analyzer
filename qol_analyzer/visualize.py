"""
Visualization helpers wrapping seaborn/matplotlib for QoL outputs.
"""

from __future__ import annotations

from typing import Iterable, Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")


def _filter_states(df: pd.DataFrame, states: Optional[Iterable[str]]) -> pd.DataFrame:
    if states is None:
        return df
    return df[df["state"].isin(states)].copy()


def _filter_year(df: pd.DataFrame, year: Optional[int]) -> pd.DataFrame:
    if "year" not in df.columns or year is None:
        return df
    return df[df["year"] == year].copy()


def plot_median_and_real_income_by_state(
    df: pd.DataFrame, year: Optional[int] = None, states: Optional[Iterable[str]] = None
) -> plt.Figure:
    data = _filter_year(_filter_states(df, states), year)
    agg = (
        data.groupby("state", as_index=False)[["median_income", "real_income"]]
        .mean()
        .sort_values("state")
    )
    long = agg.melt(id_vars="state", value_vars=["median_income", "real_income"], var_name="type", value_name="income")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(data=long, x="state", y="income", hue="type", palette="Set2", ax=ax)
    ax.set_title("Median vs Real Income by State")
    ax.set_xlabel("State")
    ax.set_ylabel("Income (USD)")
    fig.tight_layout()
    return fig


def plot_housing_burden_by_state(
    df: pd.DataFrame, year: Optional[int] = None, states: Optional[Iterable[str]] = None
) -> plt.Figure:
    data = _filter_year(_filter_states(df, states), year)
    agg = (
        data.groupby("state", as_index=False)[["rent_burden_pct", "owner_burden_pct"]]
        .mean()
        .sort_values("state")
    )
    long = agg.melt(
        id_vars="state",
        value_vars=["rent_burden_pct", "owner_burden_pct"],
        var_name="group",
        value_name="burden_pct",
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(data=long, x="state", y="burden_pct", hue="group", palette="Set2", ax=ax)
    ax.set_title("Housing Cost Burden (30%+)")
    ax.set_xlabel("State")
    ax.set_ylabel("Percent of households (%)")
    fig.tight_layout()
    return fig


def plot_price_to_income_by_state(
    df: pd.DataFrame, year: Optional[int] = None, states: Optional[Iterable[str]] = None
) -> plt.Figure:
    data = _filter_year(_filter_states(df, states), year)
    agg = data.groupby("state", as_index=False)["price_to_income_ratio"].mean().sort_values("state")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(data=agg, x="state", y="price_to_income_ratio", color="#4C72B0", ax=ax)
    ax.set_title("Price-to-Income Ratio by State")
    ax.set_xlabel("State")
    ax.set_ylabel("Median home value / annual income")
    fig.tight_layout()
    return fig


def plot_qol_score_by_state(
    df: pd.DataFrame, year: Optional[int] = None, states: Optional[Iterable[str]] = None
) -> plt.Figure:
    if "qol_score" not in df.columns:
        raise ValueError("DataFrame must contain 'qol_score'.")
    data = _filter_year(_filter_states(df, states), year)
    agg = data.groupby("state", as_index=False)["qol_score"].mean().sort_values("state")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(data=agg, x="state", y="qol_score", color="#55A868", ax=ax)
    ax.set_title("QoL Score by State")
    ax.set_xlabel("State")
    ax.set_ylabel("QoL score (relative)")
    fig.tight_layout()
    return fig


def plot_real_income_vs_rent_burden(
    df: pd.DataFrame, year: Optional[int] = None, states: Optional[Iterable[str]] = None
) -> plt.Figure:
    data = _filter_year(_filter_states(df, states), year)
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.scatterplot(data=data, x="real_income", y="rent_burden_pct", hue="state", s=120, palette="deep", ax=ax)
    ax.set_title("Real Income vs Rent Burden (30%+ renters)")
    ax.set_xlabel("Real income (CPI-adjusted)")
    ax.set_ylabel("Rent burden (% households)")
    fig.tight_layout()
    return fig


def plot_real_income_vs_owner_burden(
    df: pd.DataFrame, year: Optional[int] = None, states: Optional[Iterable[str]] = None
) -> plt.Figure:
    data = _filter_year(_filter_states(df, states), year)
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.scatterplot(data=data, x="real_income", y="owner_burden_pct", hue="state", s=120, palette="deep", ax=ax)
    ax.set_title("Real Income vs Owner Burden (30%+ owners)")
    ax.set_xlabel("Real income (CPI-adjusted)")
    ax.set_ylabel("Owner burden (% households)")
    fig.tight_layout()
    return fig


def plot_state_income_trend(df: pd.DataFrame, state: str) -> plt.Figure:
    return _plot_single_series(df, state, y="real_income", title="Real Income Trend", ylabel="Real income")


def plot_state_rent_burden_trend(df: pd.DataFrame, state: str) -> plt.Figure:
    return _plot_single_series(df, state, y="rent_burden_pct", title="Rent Burden Trend", ylabel="Rent burden (%)")


def plot_state_owner_burden_trend(df: pd.DataFrame, state: str) -> plt.Figure:
    return _plot_single_series(df, state, y="owner_burden_pct", title="Owner Burden Trend", ylabel="Owner burden (%)")


def plot_state_qol_trend(df: pd.DataFrame, state: str) -> plt.Figure:
    if "qol_score" not in df.columns:
        raise ValueError("DataFrame must contain 'qol_score'.")
    return _plot_single_series(df, state, y="qol_score", title="QoL Score Trend", ylabel="QoL score")


def _plot_single_series(df: pd.DataFrame, state: str, y: str, title: str, ylabel: str) -> plt.Figure:
    if "year" not in df.columns:
        raise ValueError("Need 'year' column for time series plots.")
    data = df[df["state"] == state].copy().sort_values("year")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.lineplot(data=data, x="year", y=y, marker="o", linewidth=2, ax=ax)
    ax.set_title(f"{state}: {title}")
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    return fig


def plot_real_income_trend_all_states(df: pd.DataFrame) -> plt.Figure:
    return _plot_multi_line(df, y="real_income", title="Real Income Trend by State", ylabel="Real income")


def plot_rent_burden_trend_all_states(df: pd.DataFrame) -> plt.Figure:
    return _plot_multi_line(df, y="rent_burden_pct", title="Rent Burden Trend by State", ylabel="Rent burden (%)")


def plot_owner_burden_trend_all_states(df: pd.DataFrame) -> plt.Figure:
    return _plot_multi_line(df, y="owner_burden_pct", title="Owner Burden Trend by State", ylabel="Owner burden (%)")


def plot_qol_trend_all_states(df: pd.DataFrame) -> plt.Figure:
    if "qol_score" not in df.columns:
        raise ValueError("DataFrame must contain 'qol_score'.")
    return _plot_multi_line(df, y="qol_score", title="QoL Trend by State", ylabel="QoL score")


def _plot_multi_line(df: pd.DataFrame, y: str, title: str, ylabel: str) -> plt.Figure:
    if "year" not in df.columns:
        raise ValueError("Need 'year' column for time series plots.")
    data = df.copy().sort_values(["state", "year"])
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.lineplot(data=data, x="year", y=y, hue="state", marker="o", linewidth=2, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.legend(title="State")
    fig.tight_layout()
    return fig

