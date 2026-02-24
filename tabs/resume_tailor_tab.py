import os
import pandas as pd
import streamlit as st
from datetime import date

from config import PATHS, load_jobs, save_jobs
from styles import score_card_style, keyword_gaps_pill_style, suggestions_style
from resume_tools import tailor_resume

MASTER_PDF_PATH = PATHS["MASTER_PDF_PATH"]


def render():
    jobs_df = load_jobs()
    st.header("Add Job Description")

    if not os.path.exists(MASTER_PDF_PATH):
        st.warning("⚠️ Please upload a master resume first (Tab 1) before adding jobs.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Job Title", placeholder="e.g. Data Scientist")

        with col2:
            company = st.text_input("Company Name", placeholder="e.g. Apple")

        url = st.text_input(
            "Job Description URL",
            placeholder="Paste the job url here...",
        )

        description = st.text_area(
            "Job Description",
            placeholder="Paste the full job description here...",
            height=300,
        )

        st.divider()

        # ── Save Job ──────────────────────────────────────────────────────────
        save_col, tailor_col = st.columns([1, 1])

        with save_col:
            if st.button("💾 Save Job", width="stretch"):
                if not company or not title or not description:
                    st.error("Please fill in all fields before saving.")
                else:
                    job_id = int(jobs_df["id"].max()) + 1 if not jobs_df.empty else 1
                    new_row = {
                        "id": job_id,
                        "company": company,
                        "title": title,
                        "description": description,
                        "status": "Applied",
                        "date_added": date.today(),
                        "resume_path": "",
                        "url": url,
                    }
                    jobs_df = pd.concat(
                        [jobs_df, pd.DataFrame([new_row])], ignore_index=True
                    )
                    save_jobs(jobs_df)
                    st.success(f"Job #{job_id} — {title} @ {company} saved!")

        # ── Tailor Resume ───────────────────────────────────────
        with tailor_col:
            if st.button("✨ Tailor Resume", width="stretch", type="primary"):
                if not company or not title or not description:
                    st.error("Please fill in all fields before tailoring.")
                else:
                    with st.spinner("Tailoring resume..."):
                        score_json, changes_list = tailor_resume(
                            MASTER_PDF_PATH, description
                        )
                        st.session_state["score_json"] = score_json
                        st.session_state["changes_list"] = changes_list

        if "score_json" in st.session_state and "changes_list" in st.session_state:
            st.divider()
            score_json = st.session_state["score_json"]
            changes_list = st.session_state["changes_list"]

            origial_score = int(score_json["score"])
            score_rationale = score_json["scoreRationale"]
            keyword_gaps = score_json["keywordGaps"]

            # ── Match Score Card ──────────────────────────────────────────────
            st.markdown(
                score_card_style(origial_score, score_rationale),
                unsafe_allow_html=True,
            )

            # ── Keyword Gaps ──────────────────────────────────────────────────
            if keyword_gaps:
                st.markdown("#### 🔍 Keyword Gaps")
                pills_html = " ".join(
                    keyword_gaps_pill_style(gap) for gap in keyword_gaps
                )
                st.markdown(
                    f'<div style="line-height:2.2;">{pills_html}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Rewritten Bullet Points ───────────────────────────────────────
            if changes_list:
                st.markdown("#### ✏️ Rewritten Bullet Points")
                for change in changes_list:
                    original = change.get("original", "")
                    rewritten = change.get("rewritten", "")
                    st.markdown(
                        suggestions_style(original, rewritten),
                        unsafe_allow_html=True,
                    )
