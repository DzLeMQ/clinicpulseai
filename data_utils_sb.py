import os
import pandas as pd
import streamlit as st

DEFAULT_FILE = "consultation_surveys_bi_enriched_unique.csv"


def apply_custom_css():
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        div[data-testid="stMetric"] {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 14px 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .insight-box {
            background-color: #f0f9ff;
            border-left: 4px solid #0284c7;
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 1rem;
            color: #0f172a;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_survey_data(file_source) -> pd.DataFrame:
    df = pd.read_csv(file_source)
    df["Consultation Date"] = pd.to_datetime(df["Consultation Date"])
    df["Sentiment Score (-1 to 1)"] = pd.to_numeric(df["Sentiment Score (-1 to 1)"])
    df["Satisfaction Score (1 to 5)"] = pd.to_numeric(df["Satisfaction Score (1 to 5)"])
    df["Wait Time (Mins)"] = pd.to_numeric(df["Wait Time (Mins)"])
    return df


def get_filtered_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    st.sidebar.header("📂 Data & Global Filters")

    if "uploaded_bytes" not in st.session_state:
        st.session_state["uploaded_bytes"] = None

    uploaded_file = st.sidebar.file_uploader(
        "Upload Enriched Survey CSV",
        type=["csv"],
        help="Persists across all pages once uploaded.",
    )
    if uploaded_file is not None:
        st.session_state["uploaded_bytes"] = uploaded_file.getvalue()

    if st.session_state["uploaded_bytes"] is not None:
        import io
        df_raw = load_survey_data(io.BytesIO(st.session_state["uploaded_bytes"]))
    elif os.path.exists(DEFAULT_FILE):
        df_raw = load_survey_data(DEFAULT_FILE)
    else:
        st.error(f"Could not find `{DEFAULT_FILE}`. Please upload it in the sidebar.")
        st.stop()

    all_cohorts = sorted(df_raw["Record Cohort"].unique())
    all_clinics = sorted(df_raw["Clinic Location"].unique())
    all_consults = sorted(df_raw["Consultation Type"].unique())
    all_modes = sorted(df_raw["Visit Mode"].unique())

    cohorts = st.sidebar.multiselect(
        "Record Cohort", options=all_cohorts, default=all_cohorts, key="flt_cohort"
    )
    clinics = st.sidebar.multiselect(
        "Clinic Location", options=all_clinics, default=all_clinics, key="flt_clinic"
    )
    consults = st.sidebar.multiselect(
        "Consultation Type", options=all_consults, default=all_consults, key="flt_consult"
    )
    modes = st.sidebar.multiselect(
        "Visit Mode", options=all_modes, default=all_modes, key="flt_mode"
    )

    df = df_raw[
        (df_raw["Record Cohort"].isin(cohorts))
        & (df_raw["Clinic Location"].isin(clinics))
        & (df_raw["Consultation Type"].isin(consults))
        & (df_raw["Visit Mode"].isin(modes))
    ].copy()

    if df.empty:
        st.warning("No records match your current filters. Please widen your selection.")
        st.stop()

    return df_raw, df


def compute_kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    promoters = (df["NPS Category"] == "Promoter").sum()
    detractors = (df["NPS Category"] == "Detractor").sum()
    clinic_means = df.groupby("Clinic Location")["Sentiment Score (-1 to 1)"].mean()
    friction_df = df[df["Operational Friction Flag"] == "Yes"]

    return {
        "total_surveys": total,
        "avg_sentiment": df["Sentiment Score (-1 to 1)"].mean(),
        "avg_sat": df["Satisfaction Score (1 to 5)"].mean(),
        "avg_wait": df["Wait Time (Mins)"].mean(),
        "friction_rate": (df["Operational Friction Flag"] == "Yes").mean() * 100,
        "nps_score": ((promoters - detractors) / total) * 100,
        "top_clinic": clinic_means.idxmax(),
        "top_clinic_score": clinic_means.max(),
        "top_friction": (
            friction_df["Friction Type"].value_counts().idxmax()
            if not friction_df.empty
            else "None"
        ),
    }
