import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import plotly.express as px
import streamlit as st
from data_utils import apply_custom_css, get_filtered_data

st.set_page_config(page_title="Operations & Bottlenecks | Clinic BI", page_icon="⏱️", layout="wide")
apply_custom_css()

_, df = get_filtered_data()

st.title("⏱️ Operations & Wait Time Bottlenecks")
st.caption("Identify peak-hour congestion, specialty delays, and friction patterns across clinics.")

c1, c2 = st.columns([1.2, 1])

with c1:
    st.subheader("🔥 Avg Wait Time (Mins) by Specialty & Time of Day")
    heat = df.pivot_table(
        index="Consultation Type",
        columns="Time of Day Block",
        values="Wait Time (Mins)",
        aggfunc="mean",
    )
    cols = [c for c in ["Morning (08:00-11:59)", "Midday (12:00-14:59)", "Afternoon (15:00-17:30)"] if c in heat.columns]
    fig_heat = px.imshow(
        heat[cols],
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="YlOrRd",
        labels=dict(x="Time of Day", y="Consultation Type", color="Wait (m)"),
    )
    fig_heat.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)

with c2:
    st.subheader("⚠️ Operational Friction Breakdown")
    friction_df = df[df["Operational Friction Flag"] == "Yes"]
    if friction_df.empty:
        st.success("Zero operational friction recorded for the selected filters!")
    else:
        f_counts = friction_df["Friction Type"].value_counts().reset_index()
        f_counts.columns = ["Friction Type", "Count"]
        fig_fric = px.bar(
            f_counts.sort_values("Count"),
            x="Count",
            y="Friction Type",
            orientation="h",
            text="Count",
            color_discrete_sequence=["#ef4444"],
        )
        fig_fric.update_traces(textposition="outside")
        fig_fric.update_layout(yaxis_title="", xaxis_range=[0, max(f_counts["Count"].max() * 1.25, 4)], height=420, margin=dict(l=10, r=20, t=10, b=10))
        st.plotly_chart(fig_fric, use_container_width=True)

st.markdown("---")
st.subheader("🩺 Clinician Wait Time vs. Sentiment Benchmark")
clinician_perf = (
    df.groupby(["Clinician Name", "Consultation Type"], as_index=False)
    .agg(
        Surveys=("Survey ID", "count"),
        Avg_Wait=("Wait Time (Mins)", "mean"),
        Avg_Sentiment=("Sentiment Score (-1 to 1)", "mean"),
    )
)
fig_scatter = px.scatter(
    clinician_perf,
    x="Avg_Wait",
    y="Avg_Sentiment",
    size="Surveys",
    color="Consultation Type",
    hover_name="Clinician Name",
    labels={"Avg_Wait": "Average Wait Time (Mins)", "Avg_Sentiment": "Average Sentiment (-1 to 1)"},
)
fig_scatter.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_scatter, use_container_width=True)
