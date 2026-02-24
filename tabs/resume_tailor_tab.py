import os
import pandas as pd
import streamlit as st
from datetime import date

from config import PATHS, load_jobs, save_jobs
from styles import score_card_style, keyword_gaps_pill_style, suggestions_style
from resume_tools import tailor_resume
from pdf_tools import display_pdf

MASTER_RESUME_PDF_PATH = PATHS["MASTER_RESUME_PDF_PATH"]


def render():
    jobs_df = load_jobs()
    st.header("Add Job Description")

    if not os.path.exists(MASTER_RESUME_PDF_PATH):
        st.warning("⚠️ Please upload a master resume first (Tab 1) before adding jobs.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input(
                "Job Title",
                placeholder="e.g. Data Scientist",
                key=f"title_{st.session_state.job_form_key}",
            )

        with col2:
            company = st.text_input(
                "Company Name",
                placeholder="e.g. Apple",
                key=f"company_{st.session_state.job_form_key}",
            )

        url = st.text_input(
            "Job Description URL",
            placeholder="Paste the job url here...",
            key=f"url_{st.session_state.job_form_key}",
        )

        description = st.text_area(
            "Job Description",
            placeholder="Paste the full job description here...",
            height=300,
            key=f"description_{st.session_state.job_form_key}",
        )

        job_id = int(jobs_df["id"].max()) + 1 if not jobs_df.empty else 1

        st.divider()

        # ── Save Job ──────────────────────────────────────────────────────────
        save_col, tailor_col = st.columns([1, 1])

        with save_col:
            if st.button("💾 Save Job", width="stretch"):
                if not company or not title or not description:
                    st.error("Please fill in all fields before saving.")
                else:
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
                    st.session_state["save_success"] = (
                        f"Job #{job_id} — {title} @ {company} saved!"
                    )
                    st.session_state.job_form_key += 1
                    st.rerun()
        if "save_success" in st.session_state:
            st.success(st.session_state.pop("save_success"))

        # ── Tailor Resume ───────────────────────────────────────
        with tailor_col:
            if st.button("✨ Tailor Resume", width="stretch", type="primary"):
                if not company or not title or not description:
                    st.error("Please fill in all fields before tailoring.")
                else:
                    with st.spinner("Tailoring resume..."):
                        score_json, changes_list, tailored_resume_path = tailor_resume(
                            description, job_id, company, title
                        )
                        st.session_state["score_json"] = score_json
                        st.session_state["changes_list"] = changes_list
                        st.session_state["tailored_resume_path"] = tailored_resume_path

        if "score_json" in st.session_state and "changes_list" in st.session_state:
            st.divider()
            score_json = st.session_state["score_json"]
            changes_list = st.session_state["changes_list"]
            tailored_resume_path = st.session_state["tailored_resume_path"]

            origial_score = int(score_json["score"])
            score_rationale = score_json["scoreRationale"]
            keyword_gaps = score_json["keywordGaps"]
            visa_sponsorship = score_json["visaSponsorship"]

            # ── Check visa sponsorship ────────────────────────────────────────
            if not visa_sponsorship:
                st.error("🚫 This job does not offer visa sponsorship.")

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
            if changes_list and tailored_resume_path:
                st.markdown("#### ✏️ Rewritten Bullet Points")
                master_resume_col, edited_resume_col = st.columns([1, 1])

                with master_resume_col:
                    st.markdown("##### Original Resume")

                    pdf_display_master_resume = display_pdf(MASTER_RESUME_PDF_PATH)
                    st.markdown(pdf_display_master_resume, unsafe_allow_html=True)

                with edited_resume_col:
                    st.markdown("##### Edited Resume")

                    pdf_display_edited_resume = display_pdf(tailored_resume_path)
                    st.markdown(pdf_display_edited_resume, unsafe_allow_html=True)
