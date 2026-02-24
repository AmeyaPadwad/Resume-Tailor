import streamlit as st

from config import config
from tabs import (
    master_resume_tab,
    resume_tailor_tab,
    job_tracking_tab,
    referral_database_tab,
)

# ── App config ────────────────────────────────────────────────────────────────
config()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Resume Tailor", layout="wide")
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
""",
    unsafe_allow_html=True,
)
st.title("Resume Tailor")

# Adding keys for field clearing
if "ref_form_key" not in st.session_state:
    st.session_state.ref_form_key = 0

if "job_form_key" not in st.session_state:
    st.session_state.job_form_key = 0

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🗂 Master Resume",
        "➕ Resume Tailoring",
        "📊 Job Tracking",
        "🤝 Referral Database",
    ]
)

# ── Tab 1 — Master Resume ────────────────────────────────────────────────────────────────
with tab1:
    master_resume_tab.render()

# ── Tab 2 — Resume Tailoring ────────────────────────────────────────────────────────────────
with tab2:
    resume_tailor_tab.render()


# ── Tab 3 — Jobs Tracking ────────────────────────────────────────────────────────────────
with tab3:
    job_tracking_tab.render()

# ── Tab 4 — Referral Database ────────────────────────────────────────────────────────────────
with tab4:
    referral_database_tab.render()
