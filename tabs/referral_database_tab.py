import pandas as pd
import streamlit as st

from config import save_referrals, load_referrals


def render():
    referrals_df = load_referrals()
    st.header("Referral Database")

    # ── Search ────────────────────────────────────────────────────────────────
    search = st.text_input(
        "🔍 Search referrals", placeholder="Filter by company, name, or contact..."
    )
    if search:
        mask = referrals_df.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1
        )
        display_df = referrals_df[mask].reset_index(drop=True)
    else:
        display_df = referrals_df.copy()

    st.divider()

    # ── Add new referral ──────────────────────────────────────────────────────
    with st.expander("➕ Add New Referral", expanded=False):
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            r_name = st.text_input(
                "Referral Name",
                placeholder="e.g. Jane Doe",
                key=f"r_name_{st.session_state.ref_form_key}",
            )

            r_company = st.text_input(
                "Company",
                placeholder="e.g. Apple",
                key=f"r_company_{st.session_state.ref_form_key}",
            )

        with r_col2:
            r_contact = st.text_input(
                "Contact At",
                placeholder="e.g. LinkedIn, Email, Phone, Whatsapp",
                key=f"r_contact_{st.session_state.ref_form_key}",
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
                referrals_df = pd.concat(
                    [referrals_df, pd.DataFrame([new_ref])], ignore_index=True
                )
                save_referrals(referrals_df)
                st.success(f"Referral added: {r_name} @ {r_company}")
                st.session_state.ref_form_key += 1
                st.rerun()

    st.divider()

    # ── Editable table ────────────────────────────────────────────────────────
    if display_df.empty:
        st.info("No referrals found. Add one using the expander above.")
    else:
        st.caption(f"Showing {len(display_df)} of {len(referrals_df)} referral(s)")

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
                referrals_df.update(edited_ref_df)
            else:
                referrals_df = edited_ref_df
            save_referrals(referrals_df)
            st.success("Referral database updated!")
