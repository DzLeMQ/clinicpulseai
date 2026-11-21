import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import plotly.express as px
import streamlit as st
from data_utils import apply_custom_css, get_filtered_data

st.set_page_config(page_title="Themes & Feedback | Clinic BI", page_icon="💬", layout="wide")
apply_custom_css()

_, df = get_filtered_data()
total_surveys = len(df)

st.title("💬 Patient Themes & Qualitative Feedback Explorer")
st.caption("Analyze the Top 5 satisfaction drivers and search individual patient comments.")

c1, c2 = st.columns([1.15, 1])

with c1:
    st.subheader("🏷️ Top 5 Patient Experience Themes")
    theme_cols = [c for c in df.columns if c.startswith("Theme ")]
    theme_df = pd.DataFrame(
        [
            {
                "Theme": col.split(": ", 1)[1],
                "Mentions": (df[col] == "Yes").sum(),
                "Share": (df[col] == "Yes").mean() * 100,
            }
            for col in theme_cols
        ]
    ).sort_values("Mentions", ascending=True)

    fig_themes = px.bar(
        theme_df,
        x="Mentions",
        y="Theme",
        orientation="h",
        text=theme_df.apply(lambda r: f"{int(r['Mentions'])} ({r['Share']:.0f}%)", axis=1),
        color="Mentions",
        color_continuous_scale="Teal",
    )
    fig_themes.update_traces(textposition="outside")
    fig_themes.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_range=[0, max(theme_df["Mentions"].max() * 1.25, 10)], height=380, margin=dict(l=10, r=20, t=10, b=10))
    st.plotly_chart(fig_themes, use_container_width=True)

with c2:
    st.subheader("💡 Primary Satisfaction Drivers")
    drivers = df["Primary Satisfaction Driver"].value_counts().reset_index()
    drivers.columns = ["Driver", "Count"]
    fig_drivers = px.bar(
        drivers.sort_values("Count"),
        x="Count",
        y="Driver",
        orientation="h",
        text="Count",
        color_discrete_sequence=["#6366f1"],
    )
    fig_drivers.update_traces(textposition="outside")
    fig_drivers.update_layout(yaxis_title="", xaxis_range=[0, max(drivers["Count"].max() * 1.25, 5)], height=380, margin=dict(l=10, r=20, t=10, b=10))
    st.plotly_chart(fig_drivers, use_container_width=True)

st.markdown("---")
st.subheader("🔎 Searchable Comments & Context Table")

f1, f2, f3 = st.columns([1, 1, 2])
sent_filter = f1.selectbox("Sentiment", ["All"] + sorted(df["Sentiment"].unique().tolist()))
friction_only = f2.checkbox("Operational Friction Only")
keyword = f3.text_input("Search Comments or Theme Context")

explorer = df.copy()
if sent_filter != "All":
    explorer = explorer[explorer["Sentiment"] == sent_filter]
if friction_only:
    explorer = explorer[explorer["Operational Friction Flag"] == "Yes"]
if keyword.strip():
    kw = keyword.strip().lower()
    explorer = explorer[
        explorer["Patient Comments"].str.lower().str.contains(kw, na=False)
        | explorer["Top 5 Themes with Context"].str.lower().str.contains(kw, na=False)
    ]

display_cols = [
    "Survey ID", "Consultation Date", "Clinic Location", "Consultation Type",
    "Sentiment", "Sentiment Score (-1 to 1)", "NPS Category", "Wait Time (Mins)",
    "Patient Comments", "Top 5 Themes with Context",
]
st.dataframe(explorer[display_cols].sort_values("Survey ID"), use_container_width=True, hide_index=True)
