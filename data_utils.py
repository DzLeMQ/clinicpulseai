import os
import pandas as pd
import streamlit as st

DEFAULT_FILE = "consultation_surveys_bi_enriched_unique.csv"


def apply_custom_css():
    st.markdown(
        """
        <style>
        /* Import clean modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Hide sidebar and default Streamlit chrome */
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        /* Page canvas background */
        .stApp {
            background-color: #f1f5f9;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1420px;
        }

        /* Hero Gradient Banner */
        .hero-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #0284c7 100%);
            padding: 1.65rem 2rem;
            border-radius: 16px;
            color: #ffffff;
            margin-bottom: 1.25rem;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.18);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .hero-title {
            font-size: 1.85rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin: 0;
            line-height: 1.2;
        }
        .hero-badge {
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(8px);
            padding: 0.45rem 1rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #e0f2fe;
        }

        /* Custom Elevated KPI Cards */
        .kpi-card {
            background: #ffffff;
            border-radius: 14px;
            padding: 1.15rem 1.25rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
            position: relative;
            overflow: hidden;
            height: 100%;
        }
        .kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 24px -6px rgba(15, 23, 42, 0.1);
        }
        .kpi-accent {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
        }
        .kpi-label {
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 0.35rem;
        }
        .kpi-value {
            font-size: 1.85rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.15;
            margin-bottom: 0.3rem;
        }
        .kpi-sub {
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
            padding: 0.15rem 0.55rem;
            border-radius: 999px;
        }

        /* Executive Insight Callout */
        .insight-box {
            background: linear-gradient(90deg, #ffffff 0%, #f0f9ff 100%);
            border: 1px solid #bae6fd;
            border-left: 5px solid #0284c7;
            padding: 1rem 1.35rem;
            border-radius: 12px;
            margin-bottom: 1.25rem;
            color: #0f172a;
            font-size: 0.95rem;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.06);
        }

        /* Chart Card Container */
        .chart-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.15rem 1.25rem 0.5rem 1.25rem;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
            margin-bottom: 1rem;
        }
        .chart-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.15rem;
        }
        .chart-desc {
            font-size: 0.82rem;
            color: #64748b;
            margin-bottom: 0.65rem;
        }

        /* Filter Expander Styling */
        div[data-testid="stExpander"] {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
            margin-bottom: 1rem;
        }

        /* Segmented Pill Tabs */
        div[data-baseweb="tab-list"] {
            background-color: #e2e8f0;
            padding: 0.35rem;
            border-radius: 12px;
            gap: 0.35rem;
            margin-bottom: 1.1rem;
        }
        button[data-baseweb="tab"] {
            border-radius: 9px !important;
            padding: 0.55rem 1.15rem !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            color: #475569 !important;
            background-color: transparent !important;
            border: none !important;
            transition: all 0.15s ease;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #ffffff !important;
            color: #0f172a !important;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08) !important;
        }
        div[data-baseweb="tab-highlight"] {
            display: none !important;
        }

        /* Spotlight Comparison Cards */
        .spotlight-before {
            background: #fffbeb;
            border: 1px solid #fde68a;
            border-left: 4px solid #f59e0b;
            border-radius: 12px;
            padding: 1.1rem 1.25rem;
            height: 100%;
        }
        .spotlight-after {
            background: #ecfdf5;
            border: 1px solid #a7f3d0;
            border-left: 4px solid #10b981;
            border-radius: 12px;
            padding: 1.1rem 1.25rem;
            height: 100%;
        }
        .pill-tag {
            display: inline-block;
            background: #ffffff;
            border: 1px solid #cbd5e1;
            color: #1e293b;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            margin: 0.18rem 0.2rem 0.18rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_survey_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df["Consultation Date"] = pd.to_datetime(df["Consultation Date"])
    df["Sentiment Score (-1 to 1)"] = pd.to_numeric(df["Sentiment Score (-1 to 1)"])
    df["Satisfaction Score (1 to 5)"] = pd.to_numeric(df["Satisfaction Score (1 to 5)"])
    df["Wait Time (Mins)"] = pd.to_numeric(df["Wait Time (Mins)"])
    return df


def reset_filters(all_cohorts, all_clinics, all_consults, all_modes):
    st.session_state["top_flt_cohort"] = all_cohorts
    st.session_state["top_flt_clinic"] = all_clinics
    st.session_state["top_flt_consult"] = all_consults
    st.session_state["top_flt_mode"] = all_modes


def get_top_filtered_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not os.path.exists(DEFAULT_FILE):
        st.error(f"Could not find `{DEFAULT_FILE}` in the application folder.")
        st.stop()

    df_raw = load_survey_data(DEFAULT_FILE)

    all_cohorts = sorted(df_raw["Record Cohort"].unique())
    all_clinics = sorted(df_raw["Clinic Location"].unique())
    all_consults = sorted(df_raw["Consultation Type"].unique())
    all_modes = sorted(df_raw["Visit Mode"].unique())

    with st.expander("🎛️ Global Interactive Filters", expanded=True):
        f1, f2, f3, f4, f5 = st.columns([1.15, 1.25, 1.25, 0.95, 0.65])

        with f1:
            cohorts = st.multiselect(
                "Record Cohort",
                options=all_cohorts,
                default=all_cohorts,
                key="top_flt_cohort",
            )
        with f2:
            clinics = st.multiselect(
                "Clinic Location",
                options=all_clinics,
                default=all_clinics,
                key="top_flt_clinic",
            )
        with f3:
            consults = st.multiselect(
                "Consultation Type",
                options=all_consults,
                default=all_consults,
                key="top_flt_consult",
            )
        with f4:
            modes = st.multiselect(
                "Visit Mode",
                options=all_modes,
                default=all_modes,
                key="top_flt_mode",
            )
        with f5:
            st.markdown("<div style='height: 1.75rem;'></div>", unsafe_allow_html=True)
            st.button(
                "↺ Reset",
                use_container_width=True,
                on_click=reset_filters,
                args=(all_cohorts, all_clinics, all_consults, all_modes),
            )

    df = df_raw[
        (df_raw["Record Cohort"].isin(cohorts))
        & (df_raw["Clinic Location"].isin(clinics))
        & (df_raw["Consultation Type"].isin(consults))
        & (df_raw["Visit Mode"].isin(modes))
    ].copy()

    if df.empty:
        st.warning("No records match your current filters. Click **Reset** above to restore all data.")
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


def render_kpi_card(col, title: str, value: str, subtext: str, accent_color: str, badge_bg: str, badge_fg: str):
    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-accent" style="background: {accent_color};"></div>
            <div class="kpi-label">{title}</div>
            <div class="kpi-value">{value}</div>
            <span class="kpi-sub" style="background: {badge_bg}; color: {badge_fg};">{subtext}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
