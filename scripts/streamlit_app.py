"""
Quality of Life Analyzer - Interactive Dashboard

A comprehensive Streamlit dashboard for exploring Quality of Life metrics
across California, New York, Texas, and Utah.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="QoL Analyzer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
    }
    .insight-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 2rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and cache the QoL dataset."""
    return pd.read_csv("data/processed/qol_with_real_income_peryear.csv")


def create_kpi_card(title, value, delta=None, prefix="$", suffix=""):
    """Create a styled KPI metric card."""
    if delta:
        st.metric(
            label=title,
            value=f"{prefix}{value:,.0f}{suffix}",
            delta=f"{delta:+.1f}%"
        )
    else:
        st.metric(
            label=title,
            value=f"{prefix}{value:,.0f}{suffix}"
        )


def plot_qol_comparison(data):
    """Create an interactive bar chart comparing QoL scores."""
    fig = px.bar(
        data,
        x="state",
        y="qol_score",
        color="qol_score",
        color_continuous_scale="RdYlGn",
        title="Quality of Life Score by State",
        labels={"qol_score": "QoL Score", "state": "State"},
        text="qol_score"
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="",
        yaxis_title="QoL Score (standardized)",
        hovermode="x"
    )
    return fig


def plot_income_breakdown(data):
    """Create a grouped bar chart for income comparison."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=data["state"],
        y=data["median_income"],
        name="Median Income",
        marker_color="#636EFA"
    ))

    fig.add_trace(go.Bar(
        x=data["state"],
        y=data["real_income"],
        name="Real Income (CPI-adjusted)",
        marker_color="#EF553B"
    ))

    if "disposable_income" in data.columns:
        fig.add_trace(go.Bar(
            x=data["state"],
            y=data["disposable_income"],
            name="Disposable Income (after tax)",
            marker_color="#00CC96"
        ))

    fig.update_layout(
        title="Income Comparison Across States",
        xaxis_title="",
        yaxis_title="Income ($)",
        barmode='group',
        height=400,
        hovermode="x unified"
    )

    return fig


def plot_housing_burden(data):
    """Create a stacked bar chart for housing burdens."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=data["state"],
        y=data["rent_burden_pct"],
        name="Rent Burden",
        marker_color="#FF6692",
        text=data["rent_burden_pct"].round(1),
        textposition='inside'
    ))

    fig.add_trace(go.Bar(
        x=data["state"],
        y=data["owner_burden_pct"],
        name="Owner Burden",
        marker_color="#B6E880",
        text=data["owner_burden_pct"].round(1),
        textposition='inside'
    ))

    fig.update_layout(
        title="Housing Cost Burden (% spending ≥30% of income)",
        xaxis_title="",
        yaxis_title="Burden (%)",
        barmode='group',
        height=400,
        hovermode="x unified"
    )

    return fig


def plot_scatter_income_vs_qol(data):
    """Create scatter plot of income vs QoL."""
    fig = px.scatter(
        data,
        x="real_income",
        y="qol_score",
        color="state",
        size="median_home_value",
        hover_data=["year", "rent_burden_pct", "owner_burden_pct"],
        title="Real Income vs. Quality of Life",
        labels={
            "real_income": "Real Income ($)",
            "qol_score": "QoL Score",
            "median_home_value": "Median Home Value"
        }
    )

    fig.update_layout(height=450)

    return fig


def plot_time_series(df, states, metric, title, yaxis_title):
    """Create a time series line chart."""
    filtered_df = df[df["state"].isin(states)]
    pivot_df = filtered_df.pivot_table(
        index="year",
        columns="state",
        values=metric
    )

    fig = go.Figure()

    for state in pivot_df.columns:
        fig.add_trace(go.Scatter(
            x=pivot_df.index,
            y=pivot_df[state],
            name=state,
            mode='lines+markers',
            line=dict(width=3),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title=yaxis_title,
        height=400,
        hovermode="x unified"
    )

    return fig


def plot_correlation_heatmap(data):
    """Create a correlation heatmap."""
    corr_cols = ["real_income", "rent_burden_pct", "owner_burden_pct",
                 "qol_score", "median_home_value"]

    # Filter columns that exist
    available_cols = [col for col in corr_cols if col in data.columns]
    corr_matrix = data[available_cols].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale="RdBu",
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="Correlation")
    ))

    fig.update_layout(
        title="Correlation Matrix",
        height=450,
        xaxis={'side': 'bottom'}
    )

    return fig


def generate_insights(data, all_data):
    """Generate key insights from the data."""
    insights = []

    # Best/worst QoL
    best_state = data.loc[data["qol_score"].idxmax(), "state"]
    worst_state = data.loc[data["qol_score"].idxmin(), "state"]
    insights.append(f"🏆 <strong>{best_state}</strong> has the highest QoL score, while <strong>{worst_state}</strong> has the lowest.")

    # Income leader
    richest = data.loc[data["real_income"].idxmax(), "state"]
    insights.append(f"💰 <strong>{richest}</strong> has the highest real (CPI-adjusted) income.")

    # Housing burden
    lowest_burden = data.loc[data["rent_burden_pct"].idxmin(), "state"]
    insights.append(f"🏠 <strong>{lowest_burden}</strong> has the lowest rental housing burden.")

    # Year-over-year trend (if multiple years available)
    years = sorted(all_data["year"].unique())
    if len(years) > 1:
        latest_year = years[-1]
        prev_year = years[-2]

        latest_avg = all_data[all_data["year"] == latest_year]["qol_score"].mean()
        prev_avg = all_data[all_data["year"] == prev_year]["qol_score"].mean()

        trend = "improved" if latest_avg > prev_avg else "declined"
        insights.append(f"📈 Average QoL has <strong>{trend}</strong> from {prev_year} to {latest_year}.")

    return insights


# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Header
st.markdown('<p class="main-header">🏠 Quality of Life Analyzer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Exploring QoL across California, New York, Texas, and Utah</p>', unsafe_allow_html=True)

# Load data
try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ Data file not found. Please run the pipeline first: `python3 -m scripts.run_pipeline`")
    st.stop()

# Sidebar filters
st.sidebar.header("🎛️ Filters")

# Year selector
available_years = sorted(df["year"].unique())
selected_year = st.sidebar.selectbox(
    "Select Year",
    available_years,
    index=len(available_years) - 1  # Default to most recent
)

# State selector
all_states = sorted(df["state"].unique())
selected_states = st.sidebar.multiselect(
    "Select States",
    all_states,
    default=all_states
)

# Comparison mode
comparison_mode = st.sidebar.radio(
    "View Mode",
    ["Single Year Analysis", "Multi-Year Trends"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 About")
st.sidebar.info(
    "This dashboard analyzes Quality of Life using:\n"
    "- 💵 CPI-adjusted income\n"
    "- 🏠 Housing cost burdens\n"
    "- 💳 Tax-adjusted disposable income\n\n"
    "**QoL Score**: Composite metric (higher = better)"
)

# Filter data
if comparison_mode == "Single Year Analysis":
    filtered_df = df[(df["year"] == selected_year) & (df["state"].isin(selected_states))]
else:
    filtered_df = df[df["state"].isin(selected_states)]

# Check if data exists
if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters.")
    st.stop()

# ============================================================================
# SINGLE YEAR ANALYSIS
# ============================================================================

if comparison_mode == "Single Year Analysis":

    # Key Metrics Row
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_median_income = filtered_df["median_income"].mean()
        create_kpi_card("Avg Median Income", avg_median_income, prefix="$")
        # State breakdown
        st.markdown("<small>", unsafe_allow_html=True)
        for _, row in filtered_df.sort_values("median_income", ascending=False).iterrows():
            st.markdown(f"<small>{row['state']}: ${row['median_income']:,.0f}</small>", unsafe_allow_html=True)
        st.markdown("</small>", unsafe_allow_html=True)

    with col2:
        avg_real_income = filtered_df["real_income"].mean()
        create_kpi_card("Avg Real Income", avg_real_income, prefix="$")
        # State breakdown
        st.markdown("<small>", unsafe_allow_html=True)
        for _, row in filtered_df.sort_values("real_income", ascending=False).iterrows():
            st.markdown(f"<small>{row['state']}: ${row['real_income']:,.0f}</small>", unsafe_allow_html=True)
        st.markdown("</small>", unsafe_allow_html=True)

    with col3:
        if "disposable_income" in filtered_df.columns:
            avg_disposable = filtered_df["disposable_income"].mean()
            create_kpi_card("Avg Disposable Income", avg_disposable, prefix="$")
            # State breakdown
            st.markdown("<small>", unsafe_allow_html=True)
            for _, row in filtered_df.sort_values("disposable_income", ascending=False).iterrows():
                st.markdown(f"<small>{row['state']}: ${row['disposable_income']:,.0f}</small>", unsafe_allow_html=True)
            st.markdown("</small>", unsafe_allow_html=True)
        else:
            st.metric("Avg Disposable Income", "N/A")

    with col4:
        avg_qol = filtered_df["qol_score"].mean()
        create_kpi_card("Avg QoL Score", avg_qol, prefix="", suffix="")
        # State breakdown
        st.markdown("<small>", unsafe_allow_html=True)
        for _, row in filtered_df.sort_values("qol_score", ascending=False).iterrows():
            st.markdown(f"<small>{row['state']}: {row['qol_score']:.2f}</small>", unsafe_allow_html=True)
        st.markdown("</small>", unsafe_allow_html=True)

    st.markdown("---")

    # Insights
    st.markdown("### 💡 Key Insights")
    insights = generate_insights(filtered_df, df)

    cols = st.columns(len(insights))
    for col, insight in zip(cols, insights):
        with col:
            st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Main visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💰 Income Analysis", "🏠 Housing Burden", "🔍 Detailed Data"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(plot_qol_comparison(filtered_df), use_container_width=True)

        with col2:
            st.plotly_chart(plot_scatter_income_vs_qol(filtered_df), use_container_width=True)

        st.plotly_chart(plot_correlation_heatmap(filtered_df), use_container_width=True)

    with tab2:
        st.plotly_chart(plot_income_breakdown(filtered_df), use_container_width=True)

        # Detailed income table
        st.markdown("#### Income Breakdown by State")
        income_cols = ["state", "median_income", "real_income"]
        if "disposable_income" in filtered_df.columns:
            income_cols.append("disposable_income")
        if "tax_burden_pct" in filtered_df.columns:
            income_cols.append("tax_burden_pct")

        income_table = filtered_df[income_cols].copy()
        income_table = income_table.sort_values("real_income", ascending=False)

        # Format numbers
        for col in ["median_income", "real_income", "disposable_income"]:
            if col in income_table.columns:
                income_table[col] = income_table[col].apply(lambda x: f"${x:,.0f}")

        if "tax_burden_pct" in income_table.columns:
            income_table["tax_burden_pct"] = income_table["tax_burden_pct"].apply(lambda x: f"{x:.2f}%")

        st.dataframe(income_table, use_container_width=True, hide_index=True)

    with tab3:
        st.plotly_chart(plot_housing_burden(filtered_df), use_container_width=True)

        # Housing affordability metrics
        st.markdown("#### Housing Affordability Metrics")

        col1, col2 = st.columns(2)

        with col1:
            # Price to income ratio
            if "price_to_income_ratio" in filtered_df.columns:
                fig = px.bar(
                    filtered_df,
                    x="state",
                    y="price_to_income_ratio",
                    color="price_to_income_ratio",
                    color_continuous_scale="Reds",
                    title="Home Price to Income Ratio",
                    labels={"price_to_income_ratio": "Ratio", "state": "State"}
                )
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Median home value
            fig = px.bar(
                filtered_df,
                x="state",
                y="median_home_value",
                color="median_home_value",
                color_continuous_scale="Blues",
                title="Median Home Value",
                labels={"median_home_value": "Value ($)", "state": "State"}
            )
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.markdown("#### Complete Dataset")

        # Select relevant columns for display
        display_cols = [
            "state", "year", "median_income", "real_income",
            "median_rent_monthly", "median_home_value",
            "rent_burden_pct", "owner_burden_pct", "qol_score"
        ]

        if "disposable_income" in filtered_df.columns:
            display_cols.insert(4, "disposable_income")

        display_df = filtered_df[display_cols].copy()

        # Format numeric columns
        st.dataframe(
            display_df.style.format({
                "median_income": "${:,.0f}",
                "real_income": "${:,.0f}",
                "disposable_income": "${:,.0f}",
                "median_rent_monthly": "${:,.0f}",
                "median_home_value": "${:,.0f}",
                "rent_burden_pct": "{:.1f}%",
                "owner_burden_pct": "{:.1f}%",
                "qol_score": "{:.3f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"qol_data_{selected_year}.csv",
            mime="text/csv"
        )

# ============================================================================
# MULTI-YEAR TRENDS
# ============================================================================

else:  # Multi-Year Trends

    st.markdown("### 📅 Time Series Analysis")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        years_span = f"{filtered_df['year'].min()} - {filtered_df['year'].max()}"
        st.metric("Years Covered", years_span)

    with col2:
        total_observations = len(filtered_df)
        st.metric("Total Observations", total_observations)

    with col3:
        states_count = len(selected_states)
        st.metric("States Selected", states_count)

    with col4:
        avg_qol_trend = filtered_df.groupby("year")["qol_score"].mean().diff().mean()
        trend_label = "Improving" if avg_qol_trend > 0 else "Declining"
        st.metric("QoL Trend", trend_label, delta=f"{avg_qol_trend:.3f}")

    st.markdown("---")

    # Trend charts
    tab1, tab2, tab3, tab4 = st.tabs(["📈 QoL Trends", "💵 Income Trends", "🏠 Housing Trends", "📊 Comparative View"])

    with tab1:
        st.plotly_chart(
            plot_time_series(df, selected_states, "qol_score",
                           "Quality of Life Score Over Time", "QoL Score"),
            use_container_width=True
        )

        st.markdown("#### Year-over-Year QoL Change")

        # Calculate YoY changes
        yoy_data = []
        for state in selected_states:
            state_data = df[df["state"] == state].sort_values("year")
            state_data["qol_change"] = state_data["qol_score"].diff()
            yoy_data.append(state_data)

        yoy_df = pd.concat(yoy_data)

        fig = px.bar(
            yoy_df.dropna(subset=["qol_change"]),
            x="year",
            y="qol_change",
            color="state",
            barmode="group",
            title="Year-over-Year QoL Change",
            labels={"qol_change": "QoL Change", "year": "Year"}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                plot_time_series(df, selected_states, "median_income",
                               "Median Income Trend", "Income ($)"),
                use_container_width=True
            )

        with col2:
            st.plotly_chart(
                plot_time_series(df, selected_states, "real_income",
                               "Real Income Trend (CPI-adjusted)", "Real Income ($)"),
                use_container_width=True
            )

    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                plot_time_series(df, selected_states, "rent_burden_pct",
                               "Rent Burden Trend", "Rent Burden (%)"),
                use_container_width=True
            )

        with col2:
            st.plotly_chart(
                plot_time_series(df, selected_states, "owner_burden_pct",
                               "Owner Burden Trend", "Owner Burden (%)"),
                use_container_width=True
            )

    with tab4:
        st.markdown("#### State Comparison Across All Years")

        # Create faceted comparison
        metrics_to_plot = ["qol_score", "real_income", "rent_burden_pct", "owner_burden_pct"]
        metric_labels = ["QoL Score", "Real Income", "Rent Burden %", "Owner Burden %"]

        selected_metric = st.selectbox("Select Metric", metric_labels)
        metric_col = metrics_to_plot[metric_labels.index(selected_metric)]

        fig = px.line(
            filtered_df,
            x="year",
            y=metric_col,
            color="state",
            markers=True,
            title=f"{selected_metric} - All States Comparison",
            labels={metric_col: selected_metric, "year": "Year"}
        )
        fig.update_layout(height=500, hovermode="x unified")
        fig.update_traces(line=dict(width=3), marker=dict(size=10))

        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; padding: 2rem 0;">'
    'Data sources: U.S. Census Bureau, Bureau of Labor Statistics, Tax Foundation'
    '</div>',
    unsafe_allow_html=True
)
