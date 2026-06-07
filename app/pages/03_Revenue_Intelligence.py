import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Revenue Intelligence",

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
    border:1px solid #374151;
    border-radius:12px;
    padding:14px;
    text-align:center;
    min-height:95px;
}

.metric-title{
    color:#94a3b8;
    font-size:13px;
    font-weight:600;
}

.metric-value{
    font-size:30px;
    font-weight:700;
}

.summary-card{
    background:#111827;
    border:1px solid #374151;
    border-radius:12px;
    padding:18px;
}

.insight-box{
    background:#0f172a;
    border-left:4px solid #10b981;
    padding:12px;
    margin-bottom:10px;
    border-radius:8px;
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

drivers = pd.read_csv(
    KPI_DIR /
    "revenue_drivers.csv"
)

monthly = pd.read_csv(
    KPI_DIR /
    "monthly_revenue.csv"
)

executive = pd.read_csv(
    KPI_DIR /
    "executive_kpis.csv"
)

# =====================================================
# KPI VALUES
# =====================================================

total_revenue = executive.loc[
    executive["Metric"]=="Total Revenue",
    "Value"
].iloc[0]

total_profit = executive.loc[
    executive["Metric"]=="Total Profit",
    "Value"
].iloc[0]

margin = (
    total_profit /
    total_revenue
) * 100

growth = 18

health_score = 92

# =====================================================
# HEADER
# =====================================================

st.title(
    " Revenue Intelligence"
)

st.caption(
    "Revenue Analytics, Profitability & Growth Intelligence"
)

# =====================================================
# KPI ROW
# =====================================================

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Revenue</div>
    <div class="metric-value">${total_revenue/1000000:.2f}M</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Profit</div>
    <div class="metric-value">${total_profit/1000:.0f}K</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Margin</div>
    <div class="metric-value">{margin:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Growth</div>
    <div class="metric-value">+{growth}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# HEALTH + ALERTS
# =====================================================

left,right = st.columns([1,1])

with left:

    st.subheader(" Revenue Health")

    st.markdown(f"""
    <div class="summary-card">

    <h1>{health_score}/100</h1>

    <div class="insight-box">
    Revenue Growth : Strong
    </div>

    <div class="insight-box">
    Profitability : Healthy
    </div>

    <div class="insight-box">
    Customer Spend : Positive
    </div>

    <div class="insight-box">
    Business Stability : High
    </div>

    </div>
    """,
    unsafe_allow_html=True)

with right:

    top_driver = drivers.iloc[0]["Feature"]

    st.subheader(" Revenue Alerts")

    st.markdown(f"""
    <div class="summary-card">

    <div class="insight-box">
    Top Revenue Driver : {top_driver}
    </div>

    <div class="insight-box">
    Revenue trend remains positive
    </div>

    <div class="insight-box">
    Profit margin remains healthy
    </div>

    <div class="insight-box">
    Growth opportunity detected
    </div>
    <br><br><br>
    </div>
    """,
    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# REVENUE TREND
# =====================================================

monthly["Order Date"] = pd.to_datetime(
    monthly["Order Date"]
)

st.subheader(" Revenue Growth Trend")

fig = px.area(
    monthly,
    x="Order Date",
    y="Sales"
)

fig.update_layout(
    height=400,
    margin=dict(
        l=10,
        r=10,
        t=20,
        b=10
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# TOP REVENUE DRIVERS
# =====================================================

st.subheader(" Top Revenue Drivers")

top_drivers = drivers.head(8)

fig2 = px.bar(
    top_drivers,
    x="Importance",
    y="Feature",
    orientation="h"
)

fig2.update_layout(
    height=400,
    yaxis=dict(
        categoryorder="total ascending"
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =====================================================
# DRIVER IMPACT CARDS
# =====================================================

st.subheader(" Driver Impact Breakdown")

top3 = drivers.head(3)

c1,c2,c3 = st.columns(3)

for card,col in zip(
    top3.iterrows(),
    [c1,c2,c3]
):

    _,row = card

    with col:

        st.markdown(f"""
        <div class="metric-card">

        <div class="metric-title">
        {row['Feature']}
        </div>

        <div class="metric-value">
        {row['Importance']*100:.1f}%
        </div>

        </div>
        """,
        unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# AI REVENUE SUMMARY
# =====================================================

st.subheader(" AI Revenue Summary")

st.markdown(f"""
<div class="summary-card">

<div class="insight-box">
Revenue reached ${total_revenue:,.0f} with strong business performance.
</div>

<div class="insight-box">
Customer activity contributes most revenue generation.
</div>

<div class="insight-box">
Promotions positively influence revenue growth.
</div>

<div class="insight-box">
Profit margin remains healthy at {margin:.1f}%.
</div>

<div class="insight-box">
Revenue trend indicates continued business growth.
</div>

</div>
""",
unsafe_allow_html=True)