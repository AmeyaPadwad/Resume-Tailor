import os
import base64
import streamlit as st

from config import PATHS

MASTER_PDF_PATH = PATHS["MASTER_PDF_PATH"]


def render():
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
