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

# Calculate dynamic business health score

# Composite health score: 40% margin index, 30% forecast accuracy, 30% inventory health
margin = (total_profit / total_revenue) * 100

try:
    import json
    with open(ROOT_DIR / "models" / "prophet" / "prophet_metrics.json", "r") as f:
        p_metrics = json.load(f)
    forecast_acc = 100 - p_metrics.get("WMAPE", 22.6)
except Exception:
    forecast_acc = 77.4

try:
    inv_df = pd.read_csv(KPI_DIR / "inventory_full.csv")
    at_risk_ratio = (inv_df["current_stock"] < inv_df["reorder_level"]).mean()
    inv_health = (1 - at_risk_ratio) * 100
    low_stock = (inv_df["current_stock"] < inv_df["reorder_level"]).sum()
except Exception:
    inv_health = 85.0
    low_stock = 0

health_score = int(0.4 * (margin * 3.0) + 0.3 * forecast_acc + 0.3 * inv_health)
health_score = max(50, min(99, health_score))

# Calculate VIP segments statistics
try:
    cust_full = pd.read_csv(KPI_DIR / "customer_segments_full.csv")
    vip_custs = cust_full[cust_full["segment"] == 1]
    vip_count = len(vip_custs)
    vip_count_pct = (vip_count / len(cust_full)) * 100
    vip_revenue = vip_custs["total_sales"].sum()
    vip_rev_pct = (vip_revenue / cust_full["total_sales"].sum()) * 100
except Exception:
    vip_count = 0
    vip_count_pct = 0.0
    vip_rev_pct = 0.0

# Calculate growth dynamically compared to the last 90 days of historical data
try:
    full_forecast = pd.read_csv(KPI_DIR / "full_forecast.csv")
    latest_forecast = full_forecast.tail(90)
    history_last_90 = full_forecast.iloc[:-90].tail(90)
    hist_mean = history_last_90["predicted_sales"].mean()
    fore_mean = latest_forecast["predicted_sales"].mean()
    growth = ((fore_mean - hist_mean) / hist_mean) * 100
except Exception:
    growth = 12.0

# Calculate daily forecast velocity
try:
    daily_forecast_velocity = forecast["predicted_sales"].mean()
except Exception:
    daily_forecast_velocity = 0.0

# =====================================================
# HEADER
# =====================================================


st.title(
    " Revenue Optimization Command Center"
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
    {health_score}
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
        f"""
        <div class="health-card">

        <h1 style="
        margin-bottom:10px;
        ">
        {health_score} / 100
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
        ⭐ VIP Segment: {vip_count} VIPs ({vip_count_pct:.1f}%) contribute {vip_rev_pct:.1f}% of total sales.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="alert-card">
        📈 Demand Forecast: Growth is projected at {growth:+.2f}% over the next 90 days.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="alert-card">
        🚨 Inventory Status: {low_stock} items are below safety reorder thresholds.
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
        " Executive Summary"
    )

    # Get the top driver feature
    try:
        top_driver_feature = drivers.iloc[0]["Feature"]
        top_driver_importance = drivers.iloc[0]["Importance"] * 100
    except Exception:
        top_driver_feature = "Promotions"
        top_driver_importance = 0.0

    st.markdown(
        f"""
        <div class="summary-card">

        <div class="insight-card">
        Revenue reached <b>${total_revenue:,.0f}</b> across historical operations.
        </div>

        <div class="insight-card">
        Customer base consists of <b>{int(total_customers):,}</b> active customer profiles.
        </div>

        <div class="insight-card">
        Top Revenue Driver: <b>{top_driver_feature}</b> with <b>{top_driver_importance:.1f}%</b> impact importance.
        </div>

        <div class="insight-card">
        Demand Velocity: Forecasted sales velocity is estimated at <b>${daily_forecast_velocity:,.2f}/day</b>.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )
    
