import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Customer Insights",

    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.block-container{
    padding-top:2rem;
}

.metric-card{
    background:#08152f;
    border:1px solid #243b63;
    border-radius:18px;
    padding:20px;
    text-align:center;
    height:120px;
}

.metric-title{
    color:#9ca3af;
    font-size:15px;
    font-weight:600;
}

.metric-value{
    color:white;
    font-size:24px;
    font-weight:700;
    margin-top:10px;
}

.main-card{
    background:linear-gradient(
        135deg,
        #08152f,
        #0f4c4c
    );
    border-radius:14px;
    padding:16px;
    border:1px solid rgba(255,255,255,0.08);
}

.alert-card{
    background:#08152f;
    border-radius:16px;
    padding:18px;
    border:1px solid #243b63;
    margin-bottom:12px;
}

.summary-card{
    background:#08152f;
    border-radius:16px;
    padding:18px;
    border-left:4px solid #10b981;
    margin-bottom:12px;
}

.customer-card{

    background:#08152f;

    border-radius:14px;

    padding:14px;

    border:1px solid #243b63;

    text-align:center;

    min-height:120px;
}

</style>
""", unsafe_allow_html=True)

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

segments = pd.read_csv(
    KPI_DIR /
    "customer_segments_full.csv"
)

top_customers = pd.read_csv(
    KPI_DIR /
    "top_customers.csv"
)

# =====================================================
# SEGMENT MAP
# =====================================================

segment_map = {
    0: "Regular",
    1: "VIP",
    2: "Frequent",
    3: "Low Value"
}

segments["segment_name"] = (
    segments["segment"]
    .map(segment_map)
)

# =====================================================
# KPI VALUES
# =====================================================

total_customers = len(segments)

vip_customers = (
    segments["segment"] == 1
).sum()

avg_sales = (
    segments["total_sales"]
    .mean()
)

avg_orders = (
    segments["total_orders"]
    .mean()
)

# =====================================================
# HEADER
# =====================================================

st.title(
    " Customer Insights"
)

st.caption(
    "Customer Analytics, Segmentation & Growth Intelligence"
)

# =====================================================
# KPI ROW
# =====================================================

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">
    Total Customers
    </div>
    <div class="metric-value">
    {total_customers}
    </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">
    VIP Customers
    </div>
    <div class="metric-value">
    {vip_customers}
    </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">
    Avg Revenue / Customer
    </div>
    <div class="metric-value">
    ${avg_sales:,.0f}
    </div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">
    Avg Orders
    </div>
    <div class="metric-value">
    {avg_orders:.1f}
    </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# CUSTOMER HEALTH + OPPORTUNITIES
# =====================================================

left,right = st.columns([1,1])

with left:

    st.subheader(
        " Customer Health"
    )

    st.markdown("""
    <div class="main-card">

    <h2 style="margin:0;">
    88 / 100
    </h2>

    <br>

    Loyalty ............. Strong ✅

    <br>

    Frequency ........ Healthy 📈

    <br>

    Revenue ............ High 💰

    <br>

    Risk .................... Low 🟢

    </div>
    """,
    unsafe_allow_html=True)

with right:

    st.subheader(
        " Opportunity Center"
    )

    frequent_count = (
        segments["segment"] == 2
    ).sum()

    low_value_count = (
        segments["segment"] == 3
    ).sum()

    st.markdown(f"""
    <div class="alert-card">

    ⭐ {vip_customers} VIP customers generate the highest business value

    </div>

    <div class="alert-card">

    📈 {frequent_count} frequent buyers available for upsell campaigns

    </div>

    <div class="alert-card">

    🎯 {low_value_count} customers can be targeted with promotions

    </div>

    <div class="alert-card">

    💎 Retention opportunities detected in high-value segments

    </div>
    """,
    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# SEGMENT PERFORMANCE
# =====================================================

st.subheader(
    " Segment Performance"
)

segment_sales = (
    segments
    .groupby("segment_name")["total_sales"]
    .sum()
    .reset_index()
    .sort_values(
        "total_sales",
        ascending=True
    )
)

fig = px.bar(
    segment_sales,
    x="total_sales",
    y="segment_name",
    orientation="h",
    text_auto=".2s"
)

fig.update_layout(
    height=350,
    margin=dict(
        l=10,
        r=10,
        t=20,
        b=10
    ),
    xaxis_title="Revenue",
    yaxis_title=""
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# TOP CUSTOMER CHAMPIONS
# =====================================================

st.subheader(
    " Revenue Champions"
)

top5 = top_customers.head(5)

cols = st.columns(5)

for idx, (_, row) in enumerate(
    top5.iterrows()
):

    with cols[idx]:

        st.markdown(f"""
        <div class="customer-card">

        <h4>#{idx+1}</h4>

        <b>{row['Customer Name']}</b>

        <br><br>

        Revenue

        <br>

        <b>${row['Sales']:,.0f}</b>

        </div>
        """,
        unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# CUSTOMER OPPORTUNITY MATRIX
# =====================================================

st.subheader(
    " Customer Opportunity Matrix"
)

fig2 = px.scatter(
    segments,
    x="total_orders",
    y="total_sales",
    size="total_sales",
    color="segment_name",
    hover_data=[
        "customer_id"
    ]
)

fig2.update_layout(
    height=500,
    margin=dict(
        l=10,
        r=10,
        t=20,
        b=10
    ),
    xaxis_title="Total Orders",
    yaxis_title="Total Revenue"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.caption(
"""
Top Right = High Value Customers

Bottom Right = Frequent Buyers

Bottom Left = Low Value Customers

Bubble Size = Revenue Contribution
"""
)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# CUSTOMER STRATEGY SCORECARD
# =====================================================

st.subheader(
    " Customer Action Priorities"
)

vip_sales = (
    segments[
        segments["segment"] == 1
    ]["total_sales"]
    .sum()
)

frequent_sales = (
    segments[
        segments["segment"] == 2
    ]["total_sales"]
    .sum()
)

low_sales = (
    segments[
        segments["segment"] == 3
    ]["total_sales"]
    .sum()
)

c1,c2,c3 = st.columns(3)

with c1:

    st.markdown(f"""
    <div class="customer-card">

    <h4>⭐ VIP</h4>

    <b>${vip_sales:,.0f}</b>

    <br>

    Retain & Protect

    </div>
    """,
    unsafe_allow_html=True)

with c2:

    st.markdown(f"""
    <div class="customer-card">

    <h4>📈 Frequent</h4>

    <b>${frequent_sales:,.0f}</b>

    <br>

    Upsell Target

    </div>
    """,
    unsafe_allow_html=True)

with c3:

    st.markdown(f"""
    <div class="customer-card">

    <h4>🎯 Low Value</h4>

    <b>${low_sales:,.0f}</b>

    <br>

    Promotion Target

    </div>
    """,
    unsafe_allow_html=True)
    
# =====================================================
# AI CUSTOMER STRATEGY
# =====================================================

st.subheader(
    " AI Customer Strategy"
)

left,right = st.columns(2)

with left:

    st.markdown("""
    <div class="summary-card">

     VIP customers remain the
    primary revenue contributors.

    </div>

    <div class="summary-card">

     Frequent buyers offer the
    strongest upsell opportunity.

    </div>
    """,
    unsafe_allow_html=True)

with right:

    st.markdown("""
    <div class="summary-card">

     Low-value customers should
    receive targeted promotions.

    </div>

    <div class="summary-card">

     Customer portfolio remains
    healthy with positive growth outlook.

    </div>
    """,
    unsafe_allow_html=True)