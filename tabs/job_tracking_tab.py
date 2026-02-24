import os
import streamlit as st
from datetime import date

from config import load_jobs, save_jobs, JOB_STATUSES


def render():
    jobs_df = load_jobs()
    st.header("Job Application Tracker")

    if jobs_df.empty:
        st.info(
            "No job applications tracked yet. Add one in the 'Resume Tailoring' tab."
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
