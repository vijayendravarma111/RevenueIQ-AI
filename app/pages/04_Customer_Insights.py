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
        " Customer Segment Distribution"
    )

    # Calculate dynamic customer segment distribution
    segment_distribution = segments["segment_name"].value_counts().reset_index()
    segment_distribution.columns = ["Segment", "Count"]

    fig_dist = px.pie(
        segment_distribution,
        names="Segment",
        values="Count",
        hole=0.4,
        color="Segment",
        color_discrete_map={
            "VIP": "#10b981",       # Green
            "Frequent": "#3b82f6",   # Blue
            "Regular": "#f59e0b",    # Amber
            "Low Value": "#ef4444"   # Red
        }
    )
    fig_dist.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True
    )
    st.plotly_chart(fig_dist, use_container_width=True)



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
# SEGMENT COMPOSITION
# =====================================================
st.subheader(" Segment Composition & RFM Metrics")

try:
    segment_stats = segments.groupby("segment_name").agg(
        customer_count=("customer_id", "count"),
        avg_sales=("total_sales", "mean"),
        avg_orders=("total_orders", "mean"),
        avg_profit=("total_profit", "mean")
    ).reset_index()

    segment_stats.columns = [
        "Segment",
        "Customer Count",
        "Average Spend ($)",
        "Average Orders",
        "Average Profit ($)"
    ]

    st.dataframe(
        segment_stats.style.format({
            "Customer Count": "{:,}",
            "Average Spend ($)": "${:,.2f}",
            "Average Orders": "{:.1f}",
            "Average Profit ($)": "${:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )
except Exception as e:
    st.error(f"Error loading segment composition: {str(e)}")

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# SEGMENT REVENUE CONTRIBUTION
# =====================================================

st.subheader(
    " Segment Revenue Contribution"
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
# CUSTOMER STRATEGY RECOMMENDATIONS
# =====================================================

st.subheader(
    " Customer Segment Contributions"
)

# Calculate dynamic stats
try:
    total_sales_sum = segments["total_sales"].sum()
    
    vip_c = (segments["segment"] == 1).sum()
    vip_c_pct = (vip_c / len(segments)) * 100
    vip_sales = segments[segments["segment"] == 1]["total_sales"].sum()
    vip_sales_pct = (vip_sales / total_sales_sum) * 100
    
    freq_c = (segments["segment"] == 2).sum()
    freq_c_pct = (freq_c / len(segments)) * 100
    freq_sales = segments[segments["segment"] == 2]["total_sales"].sum()
    freq_sales_pct = (freq_sales / total_sales_sum) * 100
    
    low_c = (segments["segment"] == 3).sum()
    low_c_pct = (low_c / len(segments)) * 100
    low_sales = segments[segments["segment"] == 3]["total_sales"].sum()
    low_sales_pct = (low_sales / total_sales_sum) * 100
    
    reg_c = (segments["segment"] == 0).sum()
    reg_c_pct = (reg_c / len(segments)) * 100
    reg_sales = segments[segments["segment"] == 0]["total_sales"].sum()
    reg_sales_pct = (reg_sales / total_sales_sum) * 100
except Exception:
    vip_c, vip_c_pct, vip_sales, vip_sales_pct = 0, 0.0, 0.0, 0.0
    freq_c, freq_c_pct, freq_sales, freq_sales_pct = 0, 0.0, 0.0, 0.0
    low_c, low_c_pct, low_sales, low_sales_pct = 0, 0.0, 0.0, 0.0
    reg_c, reg_c_pct, reg_sales, reg_sales_pct = 0, 0.0, 0.0, 0.0

left,right = st.columns(2)

with left:

    st.markdown(f"""
    <div class="summary-card">
    💎 <b>VIP Champions</b>: {vip_c} customers ({vip_c_pct:.1f}%) generate <b>${vip_sales:,.2f}</b> ({vip_sales_pct:.1f}% of total sales).
    </div>

    <div class="summary-card">
    ⚡ <b>Frequent Buyers</b>: {freq_c} customers ({freq_c_pct:.1f}%) generate <b>${freq_sales:,.2f}</b> ({freq_sales_pct:.1f}% of total sales).
    </div>
    """,
    unsafe_allow_html=True)

with right:

    st.markdown(f"""
    <div class="summary-card">
    📊 <b>Regular Cohort</b>: {reg_c} customers ({reg_c_pct:.1f}%) generate <b>${reg_sales:,.2f}</b> ({reg_sales_pct:.1f}% of total sales).
    </div>

    <div class="summary-card">
    🎯 <b>Low-Value Cohort</b>: {low_c} customers ({low_c_pct:.1f}%) generate <b>${low_sales:,.2f}</b> ({low_sales_pct:.1f}% of total sales).
    </div>
    """,
    unsafe_allow_html=True)

# =====================================================
# ML DIAGNOSTICS & MODEL CARD
# =====================================================
st.markdown("<br>", unsafe_allow_html=True)

with st.expander("📊 Machine Learning Diagnostics & Model Card", expanded=False):
    st.markdown("### K-Means Customer Segmentation Model")
    st.markdown("""
    This segmentation module groups the customer base into distinct, actionable cohorts using unsupervised K-Means clustering.
    
    #### Model Configurations
    * **Features Used (RFM Model)**: `total_sales` (Monetary), `total_profit` (Monetary), `total_quantity` (Volume), `total_orders` (Frequency).
    * **Data Scaling**: `StandardScaler` applied to prevent larger magnitude features (e.g., total sales) from dominating the distance calculations.
    * **Optimal Clusters ($K$)**: 4 clusters.
    """)
    
    # Load KMeans metrics from JSON
    kmeans_metrics_path = ROOT_DIR / "models" / "kmeans" / "kmeans_metrics.json"
    k_metrics = {}
    if kmeans_metrics_path.exists():
        try:
            import json
            with open(kmeans_metrics_path, "r") as f:
                k_metrics = json.load(f)
        except Exception:
            pass
            
    c1, c2 = st.columns(2)
    if k_metrics:
        c1.metric("Silhouette Score (Cohesion & Separation)", f"{k_metrics.get('SilhouetteScore', 0.0):.4f}")
        c2.metric("Inertia (Within-Cluster Sum of Squares)", f"{k_metrics.get('Inertia', 0.0):,.2f}")
    else:
        c1.metric("Silhouette Score", "N/A")
        c2.metric("Inertia (WCSS)", "N/A")
        
    st.markdown("""
    #### Business Strategy Matrix & Interpretation
    * **VIP Customers (Cluster 1 / Segment 1)**: High purchase frequency, highest revenue contribution, and high profitability. Strategy: **Retain & Protect** (loyalty program access, dedicated support).
    * **Frequent Buyers (Cluster 2 / Segment 2)**: Very high order count and volume, but moderate profitability. Strategy: **Upsell Target** (bundle offers, cross-sell high-margin products).
    * **Regular Customers (Cluster 0 / Segment 0)**: Moderate spend and frequency. Strategy: **Nurture** (targeted emails, re-engagement offers).
    * **Low-Value Customers (Cluster 3 / Segment 3)**: Lowest purchase frequency, sales, and profit. Strategy: **Promotion Target** (low-cost reactive couponing, minimal customer acquisition spend).
    """)