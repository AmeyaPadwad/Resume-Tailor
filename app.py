import streamlit as st
import pandas as pd
import os
from datetime import date
import base64
from resume_tools import tailor_resume


# ── Constants ──────────────────────────────────────────────────────────────────
DATA_DIR = "data"
RESUME_DIR = os.path.join(DATA_DIR, "resumes")
MASTER_PDF_PATH = os.path.join(RESUME_DIR, "master_resume.pdf")
JOBS_CSV = os.path.join(DATA_DIR, "jobs.csv")
REFERRALS_CSV = os.path.join(DATA_DIR, "referrals.csv")

JOB_STATUSES = [
    "Applied",
    "Referred",
    "Referral Pending",
    "Interview",
    "Offer",
    "Rejected",
]

JOB_DATA_COLUMNS = [
    "id",
    "company",
    "title",
    "description",
    "status",
    "date_added",
    "resume_path",
    "url",
]

# ── Bootstrap file system ──────────────────────────────────────────────────────
os.makedirs(RESUME_DIR, exist_ok=True)


def load_jobs() -> pd.DataFrame:
    if os.path.exists(JOBS_CSV):
        df = pd.read_csv(JOBS_CSV)
        df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
        df["date_added"] = df["date_added"].apply(lambda x: x.date())

    else:
        df = pd.DataFrame(columns=JOB_DATA_COLUMNS)
    return df.fillna("")


def save_jobs(df: pd.DataFrame):
    df.to_csv(JOBS_CSV, index=False)


def next_job_id(df: pd.DataFrame) -> int:
    return int(df["id"].max()) + 1 if not df.empty else 1


def load_referrals() -> pd.DataFrame:
    if os.path.exists(REFERRALS_CSV):
        df = pd.read_csv(REFERRALS_CSV)
    else:
        df = pd.DataFrame(columns=["company", "referral_name", "contact at", "notes"])
    return df.fillna("")


def save_referrals(df: pd.DataFrame):
    df.to_csv(REFERRALS_CSV, index=False)


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Resume Tailor", layout="wide")
st.title("Resume Tailor")
if "ref_form_key" not in st.session_state:
    st.session_state.ref_form_key = 0

tab1, tab2, tab3, tab4 = st.tabs(
    ["🗂 Master Resume", "➕ Add Job Description", "📊 Tracking", "🤝 Referral Database"]
)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Master Resume
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Master Resume")

    # Upload section
    uploaded = st.file_uploader("Upload new master resume (PDF)", type=["pdf"])
    if uploaded:
        with open(MASTER_PDF_PATH, "wb") as f:
            f.write(uploaded.read())
        st.success("Master resume saved!")

    st.divider()

    # Preview section
    if os.path.exists(MASTER_PDF_PATH):
        st.subheader("Current Master Resume")
        with open(MASTER_PDF_PATH, "rb") as f:
            pdf_bytes = f.read()

        # Embed PDF in an iframe via base64
        b64 = base64.b64encode(pdf_bytes).decode()
        pdf_display = f"""
            <iframe
                src="data:application/pdf;base64,{b64}"
                width="100%" height="800px"
                style="border: 1px solid #ccc; border-radius: 6px;">
            </iframe>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)

    else:
        st.info("No master resume uploaded yet. Use the uploader above to add one.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Add Job Description
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
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
                    jobs_df = load_jobs()
                    job_id = next_job_id(jobs_df)
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
                        original_resume_score, resume_change_suggestions = (
                            tailor_resume(MASTER_PDF_PATH, description)
                        )
                        st.caption(original_resume_score)
                        st.caption(resume_change_suggestions)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Tracking
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("Job Application Tracker")

    jobs_df = load_jobs()

    if jobs_df.empty:
        st.info(
            "No job applications tracked yet. Add one in the 'Add Job Description' tab."
        )
    else:
        # ── Summary metrics ───────────────────────────────────────────────────
        metrics = ["Applied today", "Referral Pending", "Applied"]
        m_cols = st.columns(len(metrics))
        for i, status in enumerate(metrics):
            if status == "Applied today":
                count = len(jobs_df[jobs_df["date_added"] == date.today()])
            else:
                count = len(jobs_df[jobs_df["status"] == status])
            m_cols[i].metric(status, count)

        st.divider()

        # ── Editable table ────────────────────────────────────────────────────
        st.subheader("Applications")

        status_filter = st.multiselect("Filter by Status", options=JOB_STATUSES)
        if status_filter:
            filtered_jobs_df = jobs_df[jobs_df["status"].isin(status_filter)]
        else:
            filtered_jobs_df = jobs_df

        st.caption(f"Showing {len(filtered_jobs_df)} of {len(jobs_df)} application(s)")

        edited_df = st.data_editor(
            filtered_jobs_df[
                ["company", "title", "status", "date_added", "resume_path", "url"]
            ],
            width="stretch",
            column_config={
                "company": st.column_config.TextColumn("Company"),
                "title": st.column_config.TextColumn("Job Title"),
                "status": st.column_config.SelectboxColumn(
                    "Status", options=JOB_STATUSES, required=True
                ),
                "date_added": st.column_config.DateColumn("Date Added", width="small"),
                "resume_path": st.column_config.TextColumn("Resume File"),
                "url": st.column_config.TextColumn("Job URL"),
            },
            num_rows="dynamic",
            key="jobs_table",
        )

        if st.button("💾 Save Changes", width="content"):
            # Merge editable columns back into full df (preserves description column)
            jobs_df.update(edited_df[["id", "status"]].set_index(edited_df.index))
            save_jobs(jobs_df)
            st.success("Changes saved!")

        st.divider()

        # ── Job description expander ──────────────────────────────────────────
        st.subheader("View Job Details")
        if not jobs_df.empty:
            job_options = {
                f"{row['title']} @ {row['company']}": idx
                for idx, row in jobs_df.iterrows()
            }
            selected_label = st.selectbox(
                "Select a job to view", list(job_options.keys())
            )
            selected_row = jobs_df.loc[job_options[selected_label]]

            with st.expander("Job Description"):
                st.write(selected_row["description"])

            if selected_row["resume_path"] and os.path.exists(
                str(selected_row["resume_path"])
            ):
                with open(selected_row["resume_path"], "rb") as f:
                    st.download_button(
                        label="⬇️ Download Tailored Resume",
                        data=f.read(),
                        file_name=os.path.basename(selected_row["resume_path"]),
                        mime="application/pdf",
                    )
            else:
                st.caption("No tailored resume saved for this application yet.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Referral Database
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("Referral Database")

    ref_df = load_referrals()

    # ── Search ────────────────────────────────────────────────────────────────
    search = st.text_input(
        "🔍 Search referrals", placeholder="Filter by company, name, or contact..."
    )
    if search:
        mask = ref_df.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1
        )
        display_df = ref_df[mask].reset_index(drop=True)
    else:
        display_df = ref_df.copy()

    st.divider()

    # ── Add new referral ──────────────────────────────────────────────────────
    with st.expander("➕ Add New Referral", expanded=False):
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            r_company = st.text_input(
                "Company",
                placeholder="e.g. Apple",
                key=f"r_company_{st.session_state.ref_form_key}",
            )
            r_contact = st.text_input(
                "Contact At",
                placeholder="e.g. LinkedIn, Email, Phone, Whatsapp",
                key=f"r_contact_{st.session_state.ref_form_key}",
            )
        with r_col2:
            r_name = st.text_input(
                "Referral Name",
                placeholder="e.g. Jane Doe",
                key=f"r_name_{st.session_state.ref_form_key}",
            )
            r_notes = st.text_input(
                "Notes",
                placeholder="",
                key=f"r_notes_{st.session_state.ref_form_key}",
            )

        if st.button("💾 Add Referral", width="content"):
            if not r_company or not r_name:
                st.error("Company and Referral Name are required.")
            else:
                new_ref = {
                    "company": r_company,
                    "referral_name": r_name,
                    "contact at": r_contact,
                    "notes": r_notes,
                }
                ref_df = pd.concat([ref_df, pd.DataFrame([new_ref])], ignore_index=True)
                save_referrals(ref_df)
                st.success(f"Referral added: {r_name} @ {r_company}")
                st.session_state.ref_form_key += 1
                st.rerun()

    st.divider()

    # ── Editable table ────────────────────────────────────────────────────────
    if display_df.empty:
        st.info("No referrals found. Add one using the expander above.")
    else:
        st.caption(f"Showing {len(display_df)} of {len(ref_df)} referral(s)")

        edited_ref_df = st.data_editor(
            display_df,
            width="stretch",
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "company": st.column_config.TextColumn("Company"),
                "referral_name": st.column_config.TextColumn("Referral Name"),
                "contact at": st.column_config.TextColumn("Contact At"),
                "notes": st.column_config.TextColumn(
                    "Notes", width="large", required=False, default=""
                ),
            },
            key="referrals_table",
        )

        if st.button("💾 Save Changes", key="save_referrals"):
            if search:
                # Merge edits back into the full dataframe by index
                ref_df.update(edited_ref_df)
            else:
                ref_df = edited_ref_df
            save_referrals(ref_df)
            st.success("Referral database updated!")
