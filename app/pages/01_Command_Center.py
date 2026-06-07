import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Command Center",
    
    layout="wide"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
    padding-bottom:0rem;
}

h1{
    font-size:2rem !important;
}

.metric-card{
    background:#111827;
    padding:14px;
    border-radius:12px;
    text-align:center;
    border:1px solid #374151;
    min-height:100px;
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
.health-card{
    background: linear-gradient(
        135deg,
        #0f172a,
        #134e4a
    );

    padding:14px;

    border-radius:12px;

    border:1px solid rgba(
        255,
        255,
        255,
        0.08
    );

    min-height:140px;
}

.alert-card{

    background:#111827;

    padding:12px;

    border-radius:10px;

    margin-bottom:10px;

    border:1px solid #374151;
}

.summary-card{

    background:#111827;

    padding:18px;

    border-radius:12px;

    border:1px solid #374151;

    min-height:320px;
}

.insight-card{

    background:#0f172a;

    padding:15px;

    border-radius:10px;

    margin-bottom:10px;

    border-left:4px solid #10b981;
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

executive = pd.read_csv(
    KPI_DIR /
    "executive_kpis.csv"
)

anomaly = pd.read_csv(
    KPI_DIR /
    "anomaly_kpi.csv"
)

forecast = pd.read_csv(
    KPI_DIR /
    "forecast_90_days.csv"
)

segments = pd.read_csv(
    KPI_DIR /
    "segment_counts.csv"
)

drivers = pd.read_csv(
    KPI_DIR /
    "revenue_drivers.csv"
)

revenue = pd.read_csv(
    KPI_DIR /
    "revenue_kpis.csv"
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

total_customers = executive.loc[
    executive["Metric"]=="Total Customers",
    "Value"
].iloc[0]

total_orders = executive.loc[
    executive["Metric"]=="Total Orders",
    "Value"
].iloc[0]

total_anomalies = anomaly[
    "Total_Anomalies"
].iloc[0]
# =====================================================
# HEADER
# =====================================================

st.title(
    " AI Revenue Optimization Command Center"
)

st.caption(
    "Executive Decision Analytics Platform"
)

# =====================================================
# KPI ROW
# =====================================================

c1,c2,c3,c4 = st.columns(4)

with c1:

    st.markdown(f"""
    <div class="metric-card">

    <div class="metric-title">
    Revenue
    </div>

    <div class="metric-value">
    ${total_revenue/1000000:.2f}M
    </div>

    </div>
    """,
    unsafe_allow_html=True)

with c2:

    st.markdown(f"""
    <div class="metric-card">

    <div class="metric-title">
    Profit
    </div>

    <div class="metric-value">
    ${total_profit/1000:.0f}K
    </div>

    </div>
    """,
    unsafe_allow_html=True)

with c3:

    st.markdown(f"""
    <div class="metric-card">

    <div class="metric-title">
    Customers
    </div>

    <div class="metric-value">
    {int(total_customers)}
    </div>

    </div>
    """,
    unsafe_allow_html=True)

with c4:

    st.markdown(f"""
    <div class="metric-card">

    <div class="metric-title">
    Business Health
    </div>

    <div class="metric-value">
    92
    </div>

    </div>
    """,
    unsafe_allow_html=True)
    
# =====================================================
# HEALTH + ALERTS
# =====================================================

st.markdown("<br>", unsafe_allow_html=True)

left,right = st.columns([1,1])

with left:

    st.subheader(
        " Business Health"
    )

    st.markdown(
        """
        <div class="health-card">

        <h1 style="
        margin-bottom:10px;
        ">
        92 / 100
        </h1>

        Revenue : Strong <br>

        Forecast : Positive <br>

        Inventory : Healthy <br>

        Risk Level : Low 

        </div>
        """,
        unsafe_allow_html=True
    )

with right:

    st.subheader(
        " Alert Center"
    )

    st.markdown(
        f"""
        <div class="alert-card">

         {total_anomalies:,}
        anomalies detected

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="alert-card">

         VIP customers generate
        highest revenue

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="alert-card">

         Demand outlook remains
        positive

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="alert-card">

         Inventory health stable

        </div>
        """,
        unsafe_allow_html=True
    )
    
st.markdown("<br>", unsafe_allow_html=True)

left,right = st.columns(2)

with left:

    st.subheader(
        " Revenue Trend"
    )

    revenue["Order Date"] = pd.to_datetime(
        revenue["Order Date"]
    )

    monthly = (
        revenue
        .groupby(
            pd.Grouper(
                key="Order Date",
                freq="ME"
            )
        )["Sales"]
        .sum()
        .reset_index()
    )
    highest_month = monthly.loc[
    monthly["Sales"].idxmax()
    ]
    monthly = monthly.tail(12)

    fig = px.area(
        monthly,
        x="Order Date",
        y="Sales"
    )

    fig.update_layout(
        height=320,
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.caption(
    f"Highest Revenue Month: "
    f"{highest_month['Order Date'].strftime('%b %Y')} "
    f"(${highest_month['Sales']:,.0f})"
    )
with right:

    st.subheader(
        " AI Executive Summary"
    )

    st.markdown(
        f"""
        <div class="summary-card">

        <div class="insight-card">

        Revenue reached
        <b>${total_revenue:,.0f}</b>
        with strong business performance.

        </div>

        <div class="insight-card">

        Customer base remains stable with
        <b>{int(total_customers)}</b>
        active customers.

        </div>

        <div class="insight-card">

        Promotions continue to be a major
        revenue growth driver.

        </div>

        <div class="insight-card">

        Forecast indicates positive future
        demand with low business risk.

        </div>

        </div>
        """,
        unsafe_allow_html=True
    )
    
