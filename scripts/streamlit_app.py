import pandas as pd
import streamlit as st

@st.cache_data
def load():
    return pd.read_csv("data/processed/qol_with_real_income_peryear.csv")

df = load()

st.title("Quality of Life Explorer (CA, NY, TX, UT)")
year = st.sidebar.selectbox("Year", sorted(df["year"].unique()))
states = st.sidebar.multiselect("States", sorted(df["state"].unique()), default=sorted(df["state"].unique()))
f = df[(df["year"] == year) & (df["state"].isin(states))]

# KPIs
cols = st.columns(4)
kpis = [
    ("Median income", f["median_income"].mean()),
    ("Real income", f["real_income"].mean()),
    ("Disposable income", f["disposable_income"].mean() if "disposable_income" in f else None),
    ("QoL score", f["qol_score"].mean()),
]
for c,(label,val) in zip(cols,kpis):
    if val is not None: c.metric(label, f"{val:,.0f}")

st.subheader("QoL score by state")
st.bar_chart(f.set_index("state")["qol_score"])

st.subheader("Disposable income vs Tax burden")
if "disposable_income" in f and "tax_burden_pct" in f:
    st.scatter_chart(f.set_index("state")[["disposable_income","tax_burden_pct"]])

st.subheader("Real income trend")
f_trend = df[df["state"].isin(states)].pivot_table(index="year", columns="state", values="real_income")
st.line_chart(f_trend)

st.subheader("Data")
st.dataframe(f)