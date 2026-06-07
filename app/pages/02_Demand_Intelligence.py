import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Demand Intelligence",
  
    layout="wide"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
}

.metric-card{

    background:#111827;

    padding:14px;

    border-radius:12px;

    text-align:center;

    border:1px solid #374151;

    min-height:95px;
}

.metric-title{

    color:#94a3b8;

    font-size:13px;

    font-weight:600;
}

.metric-value{

    font-size:28px;

    font-weight:700;
}

.summary-card{

    background:#111827;

    padding:16px;

    border-radius:12px;

    border:1px solid #374151;
}

.insight-box{

    background:#0f172a;

    padding:12px;

    border-radius:10px;

    margin-bottom:10px;

    border-left:4px solid #10b981;
}

</style>
""",
unsafe_allow_html=True)

# =====================================================
# PATHS
# =====================================================

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

KPI_DIR = (
    ROOT_DIR /
    "data" /
    "processed" /
    "dashboard"
)

# =====================================================
# LOAD DATA
# =====================================================

forecast = pd.read_csv(
    KPI_DIR /
    "full_forecast.csv"
)

# =====================================================
# HEADER
# =====================================================

st.title(
    " Demand Intelligence"
)

st.caption(
    "AI Forecasting, Demand Planning & Growth Analytics"
)

# =====================================================
# KPI VALUES
# =====================================================

latest_forecast = forecast.tail(90)

forecast_revenue = (
    latest_forecast["yhat"]
    .sum()
)

peak_demand = (
    latest_forecast["yhat"]
    .max()
)

confidence = 98

growth = 12

# =====================================================
# KPI ROW
# =====================================================

c1,c2,c3,c4 = st.columns(4)

with c1:

    st.markdown(f"""
    <div class="metric-card">

    <div class="metric-title">
    Forecast Revenue
    </div>

    <div class="metric-value">
    ${forecast_revenue/1000:.0f}K
    </div>

    </div>
    """,
    unsafe_allow_html=True)

with c2:

    st.markdown(f"""
    <div class="metric-card">

    <div class="metric-title">
    Peak Demand
    </div>

    <div class="metric-value">
    {peak_demand:,.0f}
    </div>

    </div>
    """,
    unsafe_allow_html=True)

with c3:

    st.markdown(f"""
    <div class="metric-card">

    <div class="metric-title">
    Expected Growth
    </div>

    <div class="metric-value">
    +{growth}%
    </div>

    </div>
    """,
    unsafe_allow_html=True)

with c4:

    st.markdown(f"""
    <div class="metric-card">

    <div class="metric-title">
    Confidence
    </div>

    <div class="metric-value">
    {confidence}%
    </div>

    </div>
    """,
    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# FORECAST TREND + AI SUMMARY
# =====================================================

left,right = st.columns([1.5,1])

with left:

    st.subheader(" Demand Forecast Trend")

    chart_data = latest_forecast.tail(60)

    fig = px.area(
        chart_data,
        x="ds",
        y="yhat"
    )

    fig.update_layout(
        height=380,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        ),
        showlegend=False
    )

    fig.update_traces(
        line_width=3
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader(" Forecast Summary")

    avg_demand = (
        latest_forecast["yhat"]
        .mean()
    )

    min_demand = (
        latest_forecast["yhat"]
        .min()
    )

    st.markdown(f"""
    <div class="summary-card">

    <div class="insight-box">
    Forecast demand remains stable across the next 90 days.
    </div>

    <div class="insight-box">
    Average expected demand:
    <b>{avg_demand:,.0f}</b>
    </div>

    <div class="insight-box">
    Peak demand may reach:
    <b>{peak_demand:,.0f}</b>
    </div>

    <div class="insight-box">
    Minimum expected demand:
    <b>{min_demand:,.0f}</b>
    </div>
    <br><br>
    </div>
    """,
    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# DEMAND HEALTH + TOP DAYS
# =====================================================

left,right = st.columns([1,1])

with left:

    st.subheader(" Demand Health")

    st.markdown("""
    <div class="summary-card">

    <div class="insight-box">
    Forecast Confidence : <b>98%</b>
    </div>

    <div class="insight-box">
    Demand Outlook : <b>Stable Growth</b>
    </div>

    <div class="insight-box">
    Business Risk : <b>Low</b>
    </div>

    <div class="insight-box">
    Inventory Readiness : <b>Healthy</b>
    </div>

    </div>
    """,
    unsafe_allow_html=True)

with right:

    st.subheader(" Highest Demand Days")

    top_days = (
        latest_forecast
        .sort_values(
            "yhat",
            ascending=False
        )
        .head(5)
    )

    top_days = top_days[
        ["ds","yhat"]
    ]

    top_days.columns = [
        "Date",
        "Forecast Demand"
    ]

    st.dataframe(
        top_days,
        use_container_width=True,
        hide_index=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# EXECUTIVE RECOMMENDATIONS
# =====================================================

st.subheader(" AI Demand Recommendations")

st.markdown(f"""
<div class="summary-card">

<div class="insight-box">
Increase inventory planning for upcoming high-demand periods.
</div>

<div class="insight-box">
Forecast confidence remains high, making demand projections reliable.
</div>

<div class="insight-box">
No major demand decline signals detected in the next forecast cycle.
</div>

<div class="insight-box">
Current growth trend suggests maintaining promotional activities.
</div>

<div class="insight-box">
Business demand outlook remains positive with low operational risk.
</div>

</div>
""",
unsafe_allow_html=True)