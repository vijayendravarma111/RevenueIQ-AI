import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="RevenueIQ AI Platform",
    layout="wide"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.block-container{
    padding-top:0.5rem;
}

.hero-card{

    background:linear-gradient(
        135deg,
        #08152f,
        #0f4c4c
    );

    padding:45px 35px 30px 35px;

    border-radius:18px;

    border:1px solid rgba(255,255,255,0.08);

    margin-bottom:20px;

    overflow:visible;
}

.hero-card h1{
    margin:0;
    padding:0;
    line-height:1.2;
    font-size:3.2rem;
}

.metric-card{

    background:#08152f;

    border:1px solid #243b63;

    border-radius:14px;

    padding:14px;

    text-align:center;
}

.metric-title{

    color:#9ca3af;

    font-size:13px;
}

.metric-value{

    font-size:28px;

    font-weight:700;
}

.summary-card{

    background:#08152f;

    border-radius:14px;

    padding:14px;

    border-left:4px solid #10b981;

    margin-bottom:10px;
}
.hero-features{
    display:flex;
    align-items:center;
    gap:20px;
    margin-top:20px;
}

</style>
""",
unsafe_allow_html=True)

# =====================================================
# PATHS
# =====================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

KPI_DIR = (
    ROOT_DIR /
    "data" /
    "processed" /
    "dashboard"
)

def format_currency(value):
    if value >= 1e9:
        return f"${value/1e9:.1f}B"
    elif value >= 1e6:
        return f"${value/1e6:.1f}M"
    elif value >= 1e3:
        return f"${value/1e3:.1f}K"
    else:
        return f"${value:,.2f}"

# =====================================================
# LOAD DATA
# =====================================================

executive_kpis = pd.read_csv(
    KPI_DIR / "executive_kpis.csv"
)

revenue_kpis = pd.read_csv(
    KPI_DIR / "revenue_kpis.csv"
)

top_products = pd.read_csv(
    KPI_DIR / "top_products.csv"
)

top_customers = pd.read_csv(
    KPI_DIR / "top_customers.csv"
)

inventory_kpis = pd.read_csv(
    KPI_DIR / "inventory_kpis.csv"
)

# Load 90-day forecast to calculate demand velocity
try:
    forecast_90 = pd.read_csv(KPI_DIR / "forecast_90_days.csv")
    daily_forecast_velocity = forecast_90["predicted_sales"].mean()
except Exception:
    daily_forecast_velocity = 0.0

# =====================================================
# KPI VALUES
# =====================================================

total_revenue = executive_kpis.loc[
    executive_kpis["Metric"]=="Total Revenue",
    "Value"
].iloc[0]

total_profit = executive_kpis.loc[
    executive_kpis["Metric"]=="Total Profit",
    "Value"
].iloc[0]

total_customers = executive_kpis.loc[
    executive_kpis["Metric"]=="Total Customers",
    "Value"
].iloc[0]

total_orders = executive_kpis.loc[
    executive_kpis["Metric"]=="Total Orders",
    "Value"
].iloc[0]

# =====================================================
# HERO SECTION
# =====================================================

st.markdown(f"""
<div class="hero-card">

<h1>RevenueIQ AI</h1>

<p>Data Science & Decision Intelligence Platform</p>

<div class="hero-features">
    <span>Revenue Analytics</span>
    <span>•</span>
    <span>Demand Forecasting</span>
    <span>•</span>
    <span>Customer Intelligence</span>
    <span>•</span>
    <span>AI Consulting</span>
</div>

</div>
""",
unsafe_allow_html=True)

# =====================================================
# EXECUTIVE SNAPSHOT
# =====================================================

c1,c2,c3,c4 = st.columns(4)

with c1:

    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Revenue</div>
    <div class="metric-value">${total_revenue/1000000:.2f}M</div>
    </div>
    """,
    unsafe_allow_html=True)

with c2:

    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Profit</div>
    <div class="metric-value">${total_profit/1000:.0f}K</div>
    </div>
    """,
    unsafe_allow_html=True)

with c3:

    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Customers</div>
    <div class="metric-value">{int(total_customers)}</div>
    </div>
    """,
    unsafe_allow_html=True)

with c4:

    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-title">Orders</div>
    <div class="metric-value">{int(total_orders)}</div>
    </div>
    """,
    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
# =====================================================
# EXECUTIVE PERFORMANCE
# =====================================================

revenue_kpis["Order Date"] = pd.to_datetime(
    revenue_kpis["Order Date"]
)

monthly = (
    revenue_kpis
    .groupby("Order Date")["Sales"]
    .sum()
    .reset_index()
)

left,right = st.columns([1.5,1])

with left:

    st.subheader(
        " Revenue Performance"
    )

    fig = px.area(
        monthly,
        x="Order Date",
        y="Sales"
    )

    fig.update_layout(
        height=380,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        ),
        xaxis_title="",
        yaxis_title=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader(
        " Business Health"
    )

    margin = (
        total_profit /
        total_revenue
    ) * 100

    st.markdown(f"""
    <div class="summary-card">

     Revenue Performance

    Strong

    </div>

    <div class="summary-card">

     Profit Margin

    {margin:.1f}%

    </div>

    <div class="summary-card">

     Customer Activity

    Healthy

    </div>

    <div class="summary-card">

     Growth Outlook

    Positive

    </div>
    """,
    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# PLATFORM CAPABILITIES
# =====================================================

st.subheader(
    " Platform Intelligence Modules"
)

m1,m2,m3,m4,m5,m6 = st.columns(6)

with m1:
    st.info(
        "📊 Revenue"
    )

with m2:
    st.info(
        "📈 Demand"
    )

with m3:
    st.info(
        "👥 Customers"
    )

with m4:
    st.info(
        "📦 Inventory"
    )

with m5:
    st.info(
        "🤖 AI"
    )

with m6:
    st.info(
        "⚠ Risk"
    )

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# BUSINESS CHAMPIONS
# =====================================================

left,right = st.columns(2)

with left:

    st.subheader(
        " Revenue Champions"
    )

    top5_products = (
        top_products
        .head(5)
    )

    for _,row in top5_products.iterrows():

        st.markdown(f"""
        <div class="summary-card">

        <b>{row['Product Name']}</b>

        <br>

        Revenue :
        ${row['Sales']:,.0f}

        </div>
        """,
        unsafe_allow_html=True)

with right:

    st.subheader(
        " Customer Champions"
    )

    top5_customers = (
        top_customers
        .head(5)
    )

    for _,row in top5_customers.iterrows():

        st.markdown(f"""
        <div class="summary-card">

        <b>{row['Customer Name']}</b>

        <br>

        Revenue :
        ${row['Sales']:,.0f}

        </div>
        """,
        unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# EXECUTIVE SUMMARY
# =====================================================

st.subheader(
    " Executive Summary"
)

margin = (
    total_profit /
    total_revenue
) * 100

inventory_products = int(
    inventory_kpis[
        "Total Products"
    ].iloc[0]
)

inventory_stock = int(
    inventory_kpis[
        "Total Stock"
    ].iloc[0]
)

st.markdown(f"""
<div class="hero-card">

<h3>Executive Overview</h3>

 Revenue performance remains strong with
<b>${total_revenue/1000000:.2f}M</b> generated.


 Profitability remains healthy with
<b>{margin:.1f}%</b> margin.


 Customer base consists of
<b>{int(total_customers):,}</b> active customer profiles.


 Inventory operations support
<b>{inventory_products:,}</b> products and
<b>{inventory_stock:,}</b> stock units.


 Forecast-driven daily sales velocity is estimated at
<b>{format_currency(daily_forecast_velocity)}/day</b> over the next 90 days.

</div>
""",
unsafe_allow_html=True)

# =====================================================
# PLATFORM VALUE
# =====================================================

st.markdown("<br>", unsafe_allow_html=True)

st.subheader(
    " Business Value Delivered"
)

v1,v2,v3,v4 = st.columns(4)

with v1:
    st.success(
        "Revenue Growth"
    )

with v2:
    st.success(
        "Demand Forecasting"
    )

with v3:
    st.success(
        "Customer Intelligence"
    )

with v4:
    st.success(
        "Inventory Optimization"
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown("<br>", unsafe_allow_html=True)

st.caption(
    "AI Revenue Intelligence Platform • Enterprise Decision Intelligence System"
)