# app.py
# EcoLens — Campus Sustainability Audit Agent
# Run: streamlit run app.py

import streamlit as st
import os
import time
from agent import run_audit
from report import generate_pdf

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcoLens — Campus Sustainability Audit",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

/* ════════════════════════════════════════════════
   PAGE BACKGROUND  — light green → black text
   ════════════════════════════════════════════════ */
.main { background: #EDF2E8; }

/* Main content area text (light green bg) */
section[data-testid="stMain"],
.main .block-container {
    color: #1f2328 !important;
}

/* ════════════════════════════════════════════════
   STREAMLIT NATIVE ELEMENTS — light bg → black
   ════════════════════════════════════════════════ */

/* Page headings (st.markdown "### …") */
h1, h2, h3, h4, h5, h6 {
    color: #1f2328 !important;
}

/* st.caption */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: #3a4a3a !important;
}

/* st.markdown / st.write output */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] ol,
[data-testid="stMarkdownContainer"] ul,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] em {
    color: #1f2328 !important;
}

/* Input / number-input / selectbox labels */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
label, label p {
    color: #1f2328 !important;
}

/* Input field text (light bg inputs) */
input[type="text"],
input[type="number"],
input[type="password"] {
    color: #1f2328 !important;
    background-color: #ffffff !important;
}

/* Selectbox displayed value */
[data-testid="stSelectbox"] div[data-baseweb="select"] span {
    color: #1f2328 !important;
}

/* Number input value */
[data-testid="stNumberInput"] input {
    color: #1f2328 !important;
}

/* st.info / st.success / st.error / st.warning banners */
[data-testid="stNotification"],
[data-testid="stAlert"],
div[data-testid="stAlert"] p {
    color: #1f2328 !important;
}

/* st.success green banner */
div[data-testid="stSuccess"],
div[data-testid="stSuccess"] p {
    color: #1f2328 !important;
}

/* Dividers / hr */
hr { border-color: #C8D8C0; }

/* ════════════════════════════════════════════════
   SIDEBAR — dark → white text
   ════════════════════════════════════════════════ */
[data-testid="stSidebar"],
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
/* Sidebar inputs are light — keep them dark */
[data-testid="stSidebar"] input {
    color: #1f2328 !important;
    background: #ffffff !important;
}

/* ════════════════════════════════════════════════
   DOWNLOAD BUTTON — dark green → white text
   ════════════════════════════════════════════════ */
[data-testid="stDownloadButton"] button {
    color: #ffffff !important;
    background: #1E5032 !important;
    border: none !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #163D26 !important;
    color: #ffffff !important;
}

/* ════════════════════════════════════════════════
   RUN AUDIT BUTTON — dark green → white text
   ════════════════════════════════════════════════ */
.stButton > button {
    background: #1E5032 !important;
    color: #ffffff !important;
    border: none !important;
    padding: 12px 32px !important;
    font-weight: 600 !important;
    border-radius: 4px !important;
    font-size: 1rem !important;
    width: 100%;
}
.stButton > button:hover { background: #163D26 !important; color: #ffffff !important; }

/* ════════════════════════════════════════════════
   CUSTOM CARDS (HTML injected via st.markdown)
   ════════════════════════════════════════════════ */

/* Dark green header banner → white text */
.brand {
    background: #1E5032 !important;
    color: #ffffff !important;
    padding: 28px 32px 20px;
    border-radius: 6px;
    margin-bottom: 24px;
}
.brand h1 {
    font-family: 'IBM Plex Serif', serif;
    font-size: 2.4rem;
    margin: 0 0 4px;
    color: #ffffff !important;
}
.brand p {
    margin: 0;
    opacity: 0.9;
    font-size: 0.95rem;
    color: #ffffff !important;
}

/* White form cards → black text */
.form-card {
    background: white;
    border: 1px solid #C8D8C0;
    border-radius: 6px;
    padding: 20px 24px;
    margin-bottom: 16px;
    color: #1f2328 !important;
}
.form-card h3 {
    color: #1E5032 !important;
    font-size: 1rem;
    margin: 0 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #E0EAD8;
}

/* Agent step progress box */
.step-box {
    background: #F4F9F1;
    border-left: 4px solid #3C8C5A;
    padding: 10px 14px;
    margin: 6px 0;
    border-radius: 0 4px 4px 0;
    font-size: 0.9rem;
    color: #1E5032 !important;
}

/* White score cards → black text */
.score-card {
    background: white;
    border: 1px solid #C8D8C0;
    border-radius: 6px;
    padding: 20px;
    text-align: center;
    margin-bottom: 16px;
    color: #1f2328 !important;
}
.score-big {
    font-family: 'IBM Plex Serif', serif;
    font-size: 3.5rem;
    font-weight: 600;
    line-height: 1;
}
.score-label { color: #1f2328 !important; font-size: 0.85rem; margin-top: 4px; }

/* White result cards → black text */
.result-card {
    background: white;
    border: 1px solid #C8D8C0;
    border-radius: 6px;
    padding: 20px 24px;
    margin-bottom: 16px;
    color: #1f2328 !important;
}
.result-card h4 {
    color: #1E5032 !important;
    font-size: 0.95rem;
    margin: 0 0 10px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* SDG rows inside white result card → black text */
.sdg-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #EEF3EB;
    font-size: 0.88rem;
    color: #1f2328 !important;
}
.sdg-row:last-child { border-bottom: none; }

/* SDG status badges — dark enough to read on white */
.compliant    { color: #1a5c36 !important; font-weight: 600; }
.warning      { color: #7a4f00 !important; font-weight: 600; }
.noncompliant { color: #8b1a1a !important; font-weight: 600; }

/* Data-source footnotes */
.data-source {
    font-size: 0.78rem;
    color: #2d4a2d !important;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand">
    <h1>🌿 EcoLens</h1>
    <p>AI-Powered Campus Sustainability Audit Agent &nbsp;·&nbsp; 
    Benchmarks: BEE · MoEFCC · CPCB · Jal Shakti &nbsp;·&nbsp; 
    Aligned with SDG 6, 7, 12, 13, 15</p>
</div>
""", unsafe_allow_html=True)


# ── API Key ───────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    GROQ_API_KEY = st.sidebar.text_input("Groq API Key", type="password",
                                          help="Get free key at console.groq.com")

if not GROQ_API_KEY:
    st.info("👈 Enter your Groq API key in the sidebar to get started.")
    st.stop()


# ── Input Form ───────────────────────────────────────────────────────────────
st.markdown("### Campus Information")
st.caption("Fill in your campus data. All benchmarks are sourced from Indian government standards.")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="form-card"><h3>🏫 Campus Identity</h3>', unsafe_allow_html=True)
    campus_name = st.text_input("Campus / Institution Name", placeholder="e.g. VIT Chennai")
    col1a, col1b = st.columns(2)
    with col1a:
        students = st.number_input("Number of Students", min_value=100, max_value=100000, value=5000, step=100)
    with col1b:
        staff = st.number_input("Number of Staff", min_value=10, max_value=10000, value=500, step=10)
    campus_sqft = st.number_input("Campus Area (sq. ft)", min_value=10000, max_value=50000000, value=500000, step=10000)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="form-card"><h3>⚡ Energy</h3>', unsafe_allow_html=True)
    electricity_kwh_month = st.number_input("Monthly Electricity Consumption (kWh)", min_value=1000, max_value=5000000, value=150000, step=1000)
    solar_kw = st.number_input("Solar Panels Installed (kW capacity, 0 if none)", min_value=0, max_value=10000, value=0, step=10)
    st.markdown('<p class="data-source">Source: BEE Energy Performance Index for Educational Buildings</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="form-card"><h3>🚗 Transport</h3>', unsafe_allow_html=True)
    vehicles = st.number_input("Campus Vehicles (buses, cars, two-wheelers)", min_value=0, max_value=5000, value=50, step=5)
    st.markdown('<p class="data-source">Source: ARAI / MoRTH vehicle emissions factors</p></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="form-card"><h3>💧 Water</h3>', unsafe_allow_html=True)
    water_litres_day = st.number_input("Daily Water Consumption (litres)", min_value=1000, max_value=10000000, value=225000, step=1000)
    st.markdown('<p class="data-source">Source: CPHEEO Manual, Ministry of Jal Shakti (45 L/person/day benchmark)</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="form-card"><h3>🗑️ Waste</h3>', unsafe_allow_html=True)
    waste_kg_day = st.number_input("Daily Waste Generated (kg)", min_value=10, max_value=100000, value=550, step=10)
    st.markdown('<p class="data-source">Source: CPCB SWM Guidelines (0.1 kg/student/day benchmark)</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="form-card"><h3>🌳 Green Cover & Canteen</h3>', unsafe_allow_html=True)
    trees = st.number_input("Number of Trees on Campus", min_value=0, max_value=100000, value=200, step=10)
    canteen_type = st.selectbox("Canteen Type", ["veg", "mixed"], format_func=lambda x: "Vegetarian Only" if x == "veg" else "Mixed (includes meat)")
    st.markdown('<p class="data-source">Source: GRIHA guidelines · ICAR lifecycle emissions</p></div>', unsafe_allow_html=True)


# ── Run Audit ─────────────────────────────────────────────────────────────────
st.markdown("---")
run_col, _ = st.columns([1, 2])
with run_col:
    run_clicked = st.button("🔍 Run Sustainability Audit")

if run_clicked:
    if not campus_name.strip():
        st.error("Please enter your campus name.")
        st.stop()

    campus_data = {
        "campus_name": campus_name,
        "students": students,
        "staff": staff,
        "campus_sqft": campus_sqft,
        "electricity_kwh_month": electricity_kwh_month,
        "solar_kw": solar_kw,
        "water_litres_day": water_litres_day,
        "waste_kg_day": waste_kg_day,
        "vehicles": vehicles,
        "trees": trees,
        "canteen_type": canteen_type,
    }

    # Agent step display
    st.markdown("### 🤖 Agent Running Audit...")
    steps_container = st.container()
    step_placeholders = []
    for i in range(6):
        step_placeholders.append(steps_container.empty())

    result_holder = {}

    def on_progress(step, message):
        idx = step - 1
        if idx < len(step_placeholders):
            step_placeholders[idx].markdown(
                f'<div class="step-box">Step {step}/6 &nbsp;·&nbsp; {message}</div>',
                unsafe_allow_html=True
            )

    with st.spinner(""):
        try:
            result = run_audit(GROQ_API_KEY, campus_data, progress_callback=on_progress)
        except Exception as e:
            st.error(f"Audit failed: {e}")
            st.stop()

    st.success("✅ Audit complete!")
    st.markdown("---")

    # ── Results ──────────────────────────────────────────────────────────────
    st.markdown("## 📊 Audit Results")

    # Overall score
    overall = result["scores"]["domain_scores"]["overall"]
    total_co2 = result["footprints"]["total_co2_tonnes_year"]

    if overall >= 75:
        grade, color = "A — Good", "#2E7D4F"
    elif overall >= 55:
        grade, color = "B — Satisfactory", "#B07820"
    elif overall >= 35:
        grade, color = "C — Needs Work", "#B07820"
    else:
        grade, color = "D — Critical", "#B03030"

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-big" style="color:{color}">{overall}</div>
            <div class="score-label">Overall Score / 100</div>
            <div style="color:{color};font-weight:600;margin-top:6px">{grade}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-big" style="color:#1E5032">{total_co2}</div>
            <div class="score-label">Tonnes CO₂/year</div>
            <div style="color:#1f2328;margin-top:6px;font-size:0.85rem">Total carbon footprint</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        fp = result["footprints"]
        compliant_count = sum(
            1 for v in result["scores"]["sdg_status"].values()
            if "Compliant" in v["status"] and "Non" not in v["status"]
        )
        st.markdown(f"""
        <div class="score-card">
            <div class="score-big" style="color:#1E5032">{compliant_count}/5</div>
            <div class="score-label">SDGs Compliant</div>
            <div style="color:#1f2328;margin-top:6px;font-size:0.85rem">Out of 5 tracked goals</div>
        </div>""", unsafe_allow_html=True)

    # Domain scores
    st.markdown("### Domain Scores")
    domain_scores = result["scores"]["domain_scores"]
    d1, d2, d3, d4, d5 = st.columns(5)
    for col, (domain, label) in zip(
        [d1, d2, d3, d4, d5],
        [("energy","Energy"),("water","Water"),("waste","Waste"),("transport","Transport"),("green","Green")]
    ):
        s = domain_scores[domain]
        c = "#2E7D4F" if s >= 70 else "#B07820" if s >= 45 else "#B03030"
        with col:
            st.markdown(f"""
            <div class="score-card">
                <div style="font-size:1.8rem;font-weight:700;color:{c}">{s}</div>
                <div class="score-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    # Detailed results
    r1, r2 = st.columns(2)
    with r1:
        st.markdown('<div class="result-card"><h4>Executive Summary</h4>', unsafe_allow_html=True)
        st.write(result["summary"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="result-card"><h4>Critical Problem Areas</h4>', unsafe_allow_html=True)
        st.write(result["problems"])
        st.markdown('</div>', unsafe_allow_html=True)

    with r2:
        st.markdown('<div class="result-card"><h4>Top 5 Recommendations</h4>', unsafe_allow_html=True)
        st.write(result["recommendations"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="result-card"><h4>SDG Compliance</h4>', unsafe_allow_html=True)
        for domain, info in result["scores"]["sdg_status"].items():
            status = info["status"]
            css_class = "compliant" if "✅" in status else "warning" if "⚠️" in status else "noncompliant"
            st.markdown(f"""
            <div class="sdg-row">
                <span>{info['sdg']}</span>
                <span class="{css_class}">{status}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # PDF Download
    st.markdown("---")
    st.markdown("### 📄 Download Report")
    try:
        pdf_bytes = generate_pdf(result)
        st.download_button(
            label="⬇️ Download PDF Sustainability Audit Report",
            data=pdf_bytes,
            file_name=f"EcoLens_{campus_name.replace(' ','_')}_Audit.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        st.warning(f"PDF generation error: {e}. Results are shown above.")
