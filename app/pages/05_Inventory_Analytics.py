import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Inventory Analytics",

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

    background:#08152f;

    border:1px solid #243b63;

    border-radius:14px;

    padding:14px;

    text-align:center;

    min-height:95px;
}

.metric-title{

    color:#9ca3af;

    font-size:13px;

    font-weight:600;
}

.metric-value{

    font-size:28px;

    font-weight:700;
}

.summary-card{

    background:#08152f;

    border-radius:14px;

    padding:16px;

    border:1px solid #243b63;
}

.alert-card{

    background:#08152f;

    border-radius:12px;

    padding:12px;

    margin-bottom:10px;

    border-left:4px solid #f59e0b;
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

inventory = pd.read_csv(
    KPI_DIR /
    "inventory_full.csv"
)

# =====================================================
# KPI VALUES
# =====================================================

total_products = (
    inventory["product_id"]
    .nunique()
)

total_stock = (
    inventory["current_stock"]
    .sum()
)

low_stock = (
    inventory["current_stock"]
    <
    inventory["reorder_level"]
).sum()

inventory_health = (
    (
        1 -
        (low_stock / len(inventory))
    ) * 100
)

# =====================================================
# HEADER
# =====================================================

st.title(
    " Inventory Analytics"
)

st.caption(
    "Inventory Intelligence & Forecast-Driven Safety Stock Monitoring"
)

# =====================================================
# KPI ROW
# =====================================================

c1,c2,c3,c4 = st.columns(4)

with c1:

    st.markdown(f"""
    <div class="metric-card">

    <div class="metric-title">
    Products
    </div>

    <div class="metric-value">
    {total_products:,}
    </div>

    </div>
    """,
    unsafe_allow_html=True)

with c2:

    st.markdown(f"""
    <div class="metric-card">

    <div class="metric-title">
    Stock Units
    </div>

    <div class="metric-value">
    {total_stock:,}
    </div>

    </div>
    """,
    unsafe_allow_html=True)

with c3:

    st.markdown(f"""
    <div class="metric-card">

    <div class="metric-title">
    At Risk Items
    </div>

    <div class="metric-value">
    {low_stock:,}
    </div>

    </div>
    """,
    unsafe_allow_html=True)

with c4:

    st.markdown(f"""
    <div class="metric-card">

    <div class="metric-title">
    Inventory Health
    </div>

    <div class="metric-value">
    {inventory_health:.0f}%
    </div>

    </div>
    """,
    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
# =====================================================
# INVENTORY RISK MONITOR
# =====================================================

inventory["risk_status"] = "Healthy"

inventory.loc[
    inventory["current_stock"]
    <
    inventory["reorder_level"],
    "risk_status"
] = "At Risk"

inventory.loc[
    inventory["current_stock"]
    <
    (
        inventory["reorder_level"] * 0.5
    ),
    "risk_status"
] = "Critical"

risk_summary = (
    inventory["risk_status"]
    .value_counts()
    .reset_index()
)

risk_summary.columns = [
    "Status",
    "Count"
]

left,right = st.columns([1,1])

with left:

    st.subheader(
        "⚠ Inventory Risk Monitor"
    )

    fig = px.pie(
        risk_summary,
        names="Status",
        values="Count",
        hole=0.72
    )

    fig.update_layout(
        height=420,
        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0
        ),
        showlegend=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader(
        " Inventory Alerts"
    )

    critical_items = (
        inventory["risk_status"]
        ==
        "Critical"
    ).sum()

    st.markdown(f"""
    <div style="
        background:#071633;
        padding:14px;
        border-radius:12px;
        margin-bottom:10px;
        border-left:4px solid #ef4444;
    ">
    🔴 Critical Stock
    <br>
    <b style="font-size:20px;">{critical_items}</b>
    </div>

    <div style="
        background:#071633;
        padding:14px;
        border-radius:12px;
        margin-bottom:10px;
        border-left:4px solid #f59e0b;
    ">
    🟡 Reorder Required
    <br>
    <b style="font-size:20px;">{low_stock}</b>
    </div>

    <div style="
        background:#071633;
        padding:14px;
        border-radius:12px;
        margin-bottom:10px;
        border-left:4px solid #10b981;
    ">
    🟢 Inventory Health
    <br>
    <b style="font-size:20px;">{inventory_health:.1f}%</b>
    </div>

    <div style="
        background:#071633;
        padding:14px;
        border-radius:12px;
        border-left:4px solid #3b82f6;
    ">
    📦 Products Monitored
    <br>
    <b style="font-size:20px;">{total_products:,}</b>
    </div>
    """,
    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# STOCK RISK MAP
# =====================================================

st.subheader(
    " Stock Risk Map"
)

fig2 = px.scatter(
    inventory,
    x="reorder_level",
    y="current_stock",
    color="risk_status",
    hover_data=[
        "product_id"
    ]
)

fig2.update_layout(
    height=450,
    margin=dict(
        l=10,
        r=10,
        t=20,
        b=10
    ),
    xaxis_title="Reorder Level",
    yaxis_title="Current Stock"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.caption(
"""
Above diagonal = Healthy Inventory

Near diagonal = Monitor Closely

Below diagonal = Reorder Required
"""
)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# FORECAST-DRIVEN INVENTORY PLANNING
# =====================================================

st.subheader(
    " Forecast-Driven Inventory Planning"
)

# Calculate run-out stats using forecast growth factor
try:
    try:
        full_forecast = pd.read_csv(KPI_DIR / "full_forecast.csv")
        latest_forecast = full_forecast.tail(90)
        history_last_90 = full_forecast.iloc[:-90].tail(90)
        hist_mean = history_last_90["predicted_sales"].mean()
        fore_mean = latest_forecast["predicted_sales"].mean()
        growth = ((fore_mean - hist_mean) / hist_mean) * 100
        growth_factor = 1 + (growth / 100.0)
    except Exception:
        growth_factor = 1.12

    # Scale daily unit velocity by forecast growth factor
    inventory["forecasted_daily_velocity"] = inventory["daily_velocity"] * growth_factor
    inventory["days_to_stockout"] = inventory["current_stock"] / inventory["forecasted_daily_velocity"]
    
    stockout_critical = (inventory["days_to_stockout"] < 15).sum()
    stockout_warning = ((inventory["days_to_stockout"] >= 15) & (inventory["days_to_stockout"] < 30)).sum()
    avg_runout_days = inventory["days_to_stockout"].mean()
except Exception:
    stockout_critical = 0
    stockout_warning = 0
    avg_runout_days = 0.0

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card" style="background:#08152f; border:1px solid #243b63; border-radius:14px; padding:14px; text-align:center;">
    <div class="metric-title" style="color:#9ca3af; font-size:13px; font-weight:600;">Critical Run-Out (&lt; 15 Days)</div>
    <div class="metric-value" style="font-size:24px; font-weight:700; color:white; margin-top:10px;">{stockout_critical} products</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card" style="background:#08152f; border:1px solid #243b63; border-radius:14px; padding:14px; text-align:center;">
    <div class="metric-title" style="color:#9ca3af; font-size:13px; font-weight:600;">Run-Out Risk (15-30 Days)</div>
    <div class="metric-value" style="font-size:24px; font-weight:700; color:white; margin-top:10px;">{stockout_warning} products</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card" style="background:#08152f; border:1px solid #243b63; border-radius:14px; padding:14px; text-align:center;">
    <div class="metric-title" style="color:#9ca3af; font-size:13px; font-weight:600;">Average Inventory Cover</div>
    <div class="metric-value" style="font-size:24px; font-weight:700; color:white; margin-top:10px;">{avg_runout_days:.1f} days</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# INVENTORY ACTION CENTER
# =====================================================

st.subheader(
    " Inventory Action Center"
)

c1,c2 = st.columns(2)

with c1:

    st.markdown(f"""
    <div class="alert-card">
    🔴 Critical Stock
    <br>
    <b>{critical_items}</b>
    </div>
    """,
    unsafe_allow_html=True)

with c2:

    st.markdown(f"""
    <div class="alert-card">
    🟡 Reorder Soon
    <br>
    <b>{low_stock}</b>
    </div>
    """,
    unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# INVENTORY EXECUTIVE SUMMARY
# =====================================================

st.subheader(
    " Inventory Executive Summary"
)

left,right = st.columns(2)

with left:

    st.markdown(f"""
    <div class="summary-card">
    📦 Inventory health remains strong at <b>{inventory_health:.1f}%</b>.
    </div>

    <div class="summary-card">
    🚨 <b>{critical_items}</b> products require immediate replenishment.
    </div>
    """,
    unsafe_allow_html=True)

with right:

    st.markdown(f"""
    <div class="summary-card">
    ⚠️ <b>{low_stock}</b> products are below safety reorder thresholds.
    </div>

    <div class="summary-card">
    📅 Expected inventory cover is <b>{avg_runout_days:.1f}</b> days based on forecasted daily demand.
    </div>
    """,
    unsafe_allow_html=True)