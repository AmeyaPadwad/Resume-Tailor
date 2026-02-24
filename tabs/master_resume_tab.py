import os
import streamlit as st

from config import PATHS
from pdf_tools import display_pdf, docx_to_pdf

MASTER_RESUME_DOCX_PATH = PATHS["MASTER_RESUME_DOCX_PATH"]
MASTER_RESUME_PDF_PATH = PATHS["MASTER_RESUME_PDF_PATH"]


def render():
    st.header("Master Resume")

    # Upload section
    uploaded = st.file_uploader("Upload new master resume (.docx)", type=["docx"])
    if uploaded:
        with open(MASTER_RESUME_DOCX_PATH, "wb") as f:
            f.write(uploaded.read())
        st.success("Master resume saved!")

    st.divider()

    # Preview section
    if os.path.exists(MASTER_RESUME_DOCX_PATH):
        # Create resume pdf if it does not exist:
        if not os.path.exists(MASTER_RESUME_PDF_PATH):
            docx_to_pdf(MASTER_RESUME_DOCX_PATH, MASTER_RESUME_PDF_PATH)

        st.subheader("Current Master Resume")
        master_resume_pdf_display = display_pdf(MASTER_RESUME_PDF_PATH)
        st.markdown(master_resume_pdf_display, unsafe_allow_html=True)

    else:
        st.info("No master resume uploaded yet. Use the uploader above to add one.")
