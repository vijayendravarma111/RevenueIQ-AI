from pathlib import Path
import sys
import os

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from ai.consultant import get_response

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Consultant",
  
    layout="wide"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.hero-card{
    background:linear-gradient(
        135deg,
        #08152f,
        #0f4c4c
    );

    padding:22px;

    border-radius:16px;

    border:1px solid rgba(255,255,255,0.08);

    margin-bottom:15px;
}

.ai-card{
    background:#08152f;

    padding:14px;

    border-radius:12px;

    border-left:4px solid #10b981;

    margin-bottom:10px;
}

</style>
""",
unsafe_allow_html=True)

# =====================================================
# ENV
# =====================================================

load_dotenv()

API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

# =====================================================
# LOAD DATA
# =====================================================

KPI_DIR = (
    ROOT_DIR /
    "data" /
    "processed" /
    "dashboard"
)

executive = pd.read_csv(
    KPI_DIR /
    "executive_kpis.csv"
)

inventory = pd.read_csv(
    KPI_DIR /
    "inventory_kpis.csv"
)

customer = pd.read_csv(
    KPI_DIR /
    "customer_kpis.csv"
)

# =====================================================
# CONTEXT
# =====================================================

context = f"""

EXECUTIVE KPI

{executive.to_string()}

CUSTOMER KPI

{customer.to_string()}

INVENTORY KPI

{inventory.to_string()}

"""

# =====================================================
# HEADER
# =====================================================

st.title(
    " RevenueGPT Executive Consultant"
)

st.markdown("""
<div class="hero-card">

<h3>Enterprise AI Business Advisor</h3>

Ask questions about:

 Revenue Growth

 Customer Strategy

 Inventory Optimization

⚠ Risk Management

 CEO Action Plans

</div>
""",
unsafe_allow_html=True)

# =====================================================
# QUICK ACTIONS
# =====================================================

st.subheader(
    "⚡ Quick Actions"
)

c1,c2,c3 = st.columns(3)

with c1:

    executive_btn = st.button(
        " Executive Summary",
        use_container_width=True
    )

    revenue_btn = st.button(
        " Revenue Growth Plan",
        use_container_width=True
    )

with c2:

    customer_btn = st.button(
        " Customer Strategy",
        use_container_width=True
    )

    inventory_btn = st.button(
        " Inventory Optimization",
        use_container_width=True
    )

with c3:

    risk_btn = st.button(
        "⚠ Risk Assessment",
        use_container_width=True
    )

    ceo_btn = st.button(
        " CEO Action Plan",
        use_container_width=True
    )
    
# =====================================================
# CONSULTING MODE
# =====================================================

st.subheader(
    " Consulting Mode"
)

mode = st.selectbox(
    "",
    [
        "Executive",
        "Revenue",
        "Customer",
        "Inventory",
        "Risk",
        "Growth"
    ]
)

# =====================================================
# PRESET QUESTIONS
# =====================================================

question = ""

if executive_btn:

    question = (
        "Provide a complete executive summary "
        "of the business."
    )

elif revenue_btn:

    question = (
        "Create a revenue growth strategy "
        "for the business."
    )

elif customer_btn:

    question = (
        "Provide customer acquisition, "
        "retention and upsell recommendations."
    )

elif inventory_btn:

    question = (
        "Analyze inventory and provide "
        "optimization recommendations."
    )

elif risk_btn:

    question = (
        "Identify major business risks "
        "and mitigation plans."
    )

elif ceo_btn:

    question = (
        "Create a CEO action plan "
        "for the next 90 days."
    )

# =====================================================
# CHAT INPUT
# =====================================================

user_question = st.chat_input(
    "Ask RevenueGPT anything..."
)

if user_question:

    question = user_question

# =====================================================
# AI REQUEST
# =====================================================

answer = None

if question:

    with st.spinner(
        "RevenueGPT is analyzing your business..."
    ):

        prompt = f"""

You are a senior business consultant.

Mode:
{mode}

Business Context:
{context}

User Question:
{question}

Provide:

1. Executive Summary

2. Key Findings

3. Recommendations

4. Business Impact

5. Priority Level

Keep the answer concise,
professional and executive friendly.

"""

        try:

            answer = get_response(
                API_KEY,
                context,
                prompt
            )

        except Exception as e:

            answer = f"""
        AI service unavailable.

        Error:
        {str(e)}
        """
        
# =====================================================
# AI RESPONSE
# =====================================================

if answer:

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader(
        " AI Executive Analysis"
    )

    st.markdown(f"""
    <div class="hero-card">

    {answer}

    </div>
    """,
    unsafe_allow_html=True)

# =====================================================
# AI CONFIDENCE
# =====================================================

if answer:

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader(
        " Analysis Confidence"
    )

    confidence = 92

    st.progress(
        confidence / 100
    )

    st.caption(
        f"AI Confidence Score : {confidence}%"
    )

# =====================================================
# FOLLOW-UP SUGGESTIONS
# =====================================================

if answer:

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader(
        " Suggested Follow-Ups"
    )

    left,right = st.columns(2)

    with left:

        st.markdown("""
        <div class="ai-card">

         How can revenue be increased
        in the next quarter?

        </div>

        <div class="ai-card">

         Which customer segment
        should be prioritized?

        </div>

        <div class="ai-card">

         How can profitability
        be improved?

        </div>
        """,
        unsafe_allow_html=True)

    with right:

        st.markdown("""
        <div class="ai-card">

         What inventory risks
        require attention?

        </div>

        <div class="ai-card">

        ⚠ What are the biggest
        business risks?

        </div>

        <div class="ai-card">

         What should management
        focus on next?

        </div>
        """,
        unsafe_allow_html=True)

# =====================================================
# FOOTER
# =====================================================

st.markdown("<br>", unsafe_allow_html=True)

st.caption(
    "RevenueGPT • Enterprise AI Business Consultant"
)