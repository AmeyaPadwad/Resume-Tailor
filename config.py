import os
import pandas as pd

# ── Constants ──────────────────────────────────────────────────────────────────
data_dir = "data"
resume_dir = os.path.join(data_dir, "resumes")
master_pdf_path = os.path.join(resume_dir, "master_resume.pdf")
jobs_csv = os.path.join(data_dir, "jobs.csv")
referrals_csv = os.path.join(data_dir, "referrals.csv")

# ── Exports ──────────────────────────────────────────────────────────────────

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
PATHS = {
    "DATA_DIR": data_dir,
    "RESUME_DIR": resume_dir,
    "MASTER_PDF_PATH": master_pdf_path,
    "JOBS_CSV": jobs_csv,
    "REFERRALS_CSV": referrals_csv,
}


# ── Bootstrap file system ──────────────────────────────────────────────────────
def config():
    # 1. Make data directory
    os.makedirs(data_dir, exist_ok=True)

    # 2. Make resume directory
    os.makedirs(resume_dir, exist_ok=True)


def load_jobs():
    if os.path.exists(jobs_csv):
        jobs_df = pd.read_csv(jobs_csv)
        jobs_df["date_added"] = pd.to_datetime(jobs_df["date_added"], errors="coerce")
        jobs_df["date_added"] = jobs_df["date_added"].apply(lambda x: x.date())
    else:
        jobs_df = pd.DataFrame(columns=JOB_DATA_COLUMNS)

    jobs_df = jobs_df.fillna("")
    return jobs_df


def load_referrals():
    if os.path.exists(referrals_csv):
        referrals_df = pd.read_csv(referrals_csv)
    else:
        referrals_df = pd.DataFrame(
            columns=["company", "referral_name", "contact at", "notes"]
        )
    referrals_df = referrals_df.fillna("")

    return referrals_df


def save_jobs(df: pd.DataFrame):
    df.to_csv(jobs_csv, index=False)


def save_referrals(df: pd.DataFrame):
    df.to_csv(referrals_csv, index=False)
