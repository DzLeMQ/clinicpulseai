import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from data_utils import apply_custom_css, compute_kpis, get_filtered_data

st.set_page_config(
    page_title="Executive Overview | Clinic BI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_css()

df_raw, df = get_filtered_data()
kpis = compute_kpis(df)

st.title("🏥 Executive Overview: Patient Experience & Sentiment")
st.caption(
    f"Showing **{len(df)}** of **{len(df_raw)}** surveys across **{df['Clinic Location'].nunique()}** Melbourne clinics. Use the left navigation to explore Operations & Feedback."
)

st.markdown(
    f"""
    <div class="insight-box">
        <strong>Executive Takeaway:</strong> Overall sentiment averages <strong>{kpis['avg_sentiment']:+.2f}</strong>
        (NPS <strong>{kpis['nps_score']:+.0f}</strong>) with an average wait of <strong>{kpis['avg_wait']:.1f} mins</strong>.
        <strong>{kpis['top_clinic']}</strong> leads clinic performance (<strong>{kpis['top_clinic_score']:+.2f}</strong>),
        while the primary bottleneck is <strong>{kpis['top_friction']}</strong> ({kpis['friction_rate']:.1f}% friction rate).
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Surveys", f"{kpis['total_surveys']:,}")
k2.metric("Avg Sentiment (-1 to 1)", f"{kpis['avg_sentiment']:+.2f}")
k3.metric("Net Promoter Score", f"{kpis['nps_score']:+.0f}")
k4.metric("Avg Satisfaction (1–5)", f"{kpis['avg_sat']:.2f} / 5")
k5.metric("Operational Friction", f"{kpis['friction_rate']:.1f}%", delta=f"{kpis['avg_wait']:.1f}m avg wait", delta_color="inverse")

st.markdown("---")

c1, c2 = st.columns([1.15, 1])

with c1:
    st.subheader("📍 Clinic Sentiment Ranking (RAG)")
    clinic_perf = (
        df.groupby("Clinic Location", as_index=False)
        .agg(
            Avg_Sentiment=("Sentiment Score (-1 to 1)", "mean"),
            Avg_Wait=("Wait Time (Mins)", "mean"),
            Surveys=("Survey ID", "count"),
        )
        .sort_values("Avg_Sentiment", ascending=True)
    )
    clinic_perf["Tier"] = clinic_perf["Avg_Sentiment"].apply(
        lambda v: "Strong (≥ 0.80)" if v >= 0.80 else ("Moderate (0.65–0.79)" if v >= 0.65 else "Needs Attention (< 0.65)")
    )
    fig_clinic = px.bar(
        clinic_perf,
        x="Avg_Sentiment",
        y="Clinic Location",
        orientation="h",
        color="Tier",
        color_discrete_map={
            "Strong (≥ 0.80)": "#10b981",
            "Moderate (0.65–0.79)": "#f59e0b",
            "Needs Attention (< 0.65)": "#ef4444",
        },
        text=clinic_perf["Avg_Sentiment"].map(lambda x: f"{x:+.2f}"),
        hover_data={"Avg_Wait": ":.1f", "Surveys": True},
    )
    fig_clinic.update_traces(textposition="outside")
    fig_clinic.update_layout(xaxis_range=[0, 1.08], yaxis_title="", legend_title="", height=390, margin=dict(l=10, r=20, t=10, b=10))
    st.plotly_chart(fig_clinic, use_container_width=True)

with c2:
    st.subheader("📈 Monthly Survey Volume vs. Sentiment")
    monthly = (
        df.groupby(["Month Name", "Month Number"], as_index=False)
        .agg(Surveys=("Survey ID", "count"), Avg_Sentiment=("Sentiment Score (-1 to 1)", "mean"))
        .sort_values("Month Number")
    )
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(x=monthly["Month Name"], y=monthly["Surveys"], name="Surveys", marker_color="#93c5fd", yaxis="y1"))
    fig_trend.add_trace(
        go.Scatter(
            x=monthly["Month Name"],
            y=monthly["Avg_Sentiment"],
            name="Avg Sentiment",
            mode="lines+markers+text",
            text=monthly["Avg_Sentiment"].map(lambda x: f"{x:+.2f}"),
            textposition="top center",
            line=dict(color="#1d4ed8", width=3),
            yaxis="y2",
        )
    )
    fig_trend.update_layout(
        yaxis=dict(title="Surveys", showgrid=False),
        yaxis2=dict(title="Avg Sentiment", side="right", overlaying="y", range=[-0.2, 1.1]),
        legend=dict(orientation="h", y=1.08, x=1, xanchor="right"),
        height=390,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.subheader("🎯 NPS Category Split by Clinic")
nps_clinic = (
    df.groupby(["Clinic Location", "NPS Category"], as_index=False)
    .size()
    .rename(columns={"size": "Count"})
)
fig_nps_bar = px.bar(
    nps_clinic,
    x="Count",
    y="Clinic Location",
    color="NPS Category",
    orientation="h",
    barmode="stack",
    color_discrete_map={"Promoter": "#10b981", "Passive": "#f59e0b", "Detractor": "#ef4444"},
    category_orders={"NPS Category": ["Promoter", "Passive", "Detractor"]},
)
fig_nps_bar.update_layout(yaxis_title="", xaxis_title="Survey Count", height=340, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_nps_bar, use_container_width=True)
