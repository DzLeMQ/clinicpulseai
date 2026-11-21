import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from data_utils import apply_custom_css, compute_kpis, get_top_filtered_data

st.set_page_config(
    page_title="Clinical Consultation Pulse & Patient Experience",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_custom_css()

# Header
st.title("🏥 Clinical Consultation Pulse & Patient Experience")

# Top Filter Bar (No Sidebar)
df_raw, df = get_top_filtered_data()
kpis = compute_kpis(df)

st.caption(
    f"Showing **{len(df)}** of **{len(df_raw)}** surveys across **{df['Clinic Location'].nunique()}** Melbourne clinics."
)

# Executive Takeaway Banner
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

# Top KPI Cards
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Surveys", f"{kpis['total_surveys']:,}")
k2.metric("Avg Sentiment (-1 to 1)", f"{kpis['avg_sentiment']:+.2f}")
k3.metric("Net Promoter Score", f"{kpis['nps_score']:+.0f}")
k4.metric("Avg Satisfaction (1–5)", f"{kpis['avg_sat']:.2f} / 5")
k5.metric("Operational Friction", f"{kpis['friction_rate']:.1f}%", delta=f"{kpis['avg_wait']:.1f}m avg wait", delta_color="inverse")

st.markdown("")

# Top Navigation Tabs (Replaces Sidebar Pages)
tab_exec, tab_ops, tab_themes, tab_before, tab_after = st.tabs(
    [
        "📊 Executive Overview",
        "⏱️ Operations & Bottlenecks",
        "💬 Themes & Feedback",
        "📄 Before AI: Source Data",
        "✨ After AI: Enriched Data",
    ]
)

# =============================================================================
# TAB 1: EXECUTIVE OVERVIEW
# =============================================================================
with tab_exec:
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
        fig_clinic.update_layout(
            xaxis_range=[0, 1.08],
            yaxis_title="",
            legend_title="",
            height=380,
            margin=dict(l=10, r=20, t=10, b=10),
        )
        st.plotly_chart(fig_clinic, use_container_width=True)

    with c2:
        st.subheader("📈 Monthly Survey Volume vs. Sentiment")
        monthly = (
            df.groupby(["Month Name", "Month Number"], as_index=False)
            .agg(Surveys=("Survey ID", "count"), Avg_Sentiment=("Sentiment Score (-1 to 1)", "mean"))
            .sort_values("Month Number")
        )
        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Bar(x=monthly["Month Name"], y=monthly["Surveys"], name="Surveys", marker_color="#93c5fd", yaxis="y1")
        )
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
            height=380,
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

# =============================================================================
# TAB 2: OPERATIONS & BOTTLENECKS
# =============================================================================
with tab_ops:
    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.subheader("🔥 Avg Wait Time (Mins) by Specialty & Time of Day")
        heat = df.pivot_table(
            index="Consultation Type",
            columns="Time of Day Block",
            values="Wait Time (Mins)",
            aggfunc="mean",
        )
        cols = [
            c
            for c in ["Morning (08:00-11:59)", "Midday (12:00-14:59)", "Afternoon (15:00-17:30)"]
            if c in heat.columns
        ]
        fig_heat = px.imshow(
            heat[cols],
            text_auto=".1f",
            aspect="auto",
            color_continuous_scale="YlOrRd",
            labels=dict(x="Time of Day", y="Consultation Type", color="Wait (m)"),
        )
        fig_heat.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10))
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
            fig_fric.update_layout(
                yaxis_title="",
                xaxis_range=[0, max(f_counts["Count"].max() * 1.25, 4)],
                height=400,
                margin=dict(l=10, r=20, t=10, b=10),
            )
            st.plotly_chart(fig_fric, use_container_width=True)

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
    fig_scatter.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_scatter, use_container_width=True)

# =============================================================================
# TAB 3: THEMES & FEEDBACK
# =============================================================================
with tab_themes:
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
        fig_themes.update_layout(
            coloraxis_showscale=False,
            yaxis_title="",
            xaxis_range=[0, max(theme_df["Mentions"].max() * 1.25, 10)],
            height=380,
            margin=dict(l=10, r=20, t=10, b=10),
        )
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
        fig_drivers.update_layout(
            yaxis_title="",
            xaxis_range=[0, max(drivers["Count"].max() * 1.25, 5)],
            height=380,
            margin=dict(l=10, r=20, t=10, b=10),
        )
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

# =============================================================================
# TAB 4: BEFORE AI - SOURCE DATA
# =============================================================================
with tab_before:
    st.subheader("📄 Raw Source Data (Before AI Analysis)")
    st.markdown(
        """
        <div class="insight-box">
            <strong>Before AI Enrichment:</strong> Raw survey exports contain only unstructured free-text
            <code>Patient Comments</code> alongside basic visit metadata—requiring manual reading to spot trends,
            sentiment shifts, or operational bottlenecks.
        </div>
        """,
        unsafe_allow_html=True,
    )

    raw_source_file = "consultation_synthetic_surveys.csv"
    base_cols = [
        c
        for c in [
            "Survey ID",
            "Customer ID",
            "Record Cohort",
            "Consultation Type",
            "Visit Mode",
            "Clinic Location",
            "Clinic Region",
            "Patient Comments",
        ]
        if c in df.columns
    ]

    if os.path.exists(raw_source_file):
        df_source = pd.read_csv(raw_source_file)
        if "Survey ID" in df_source.columns:
            df_source = df_source[df_source["Survey ID"].isin(df["Survey ID"])]
    else:
        df_source = df[base_cols].copy()

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Records", f"{len(df_source):,}")
    m2.metric("Total Columns", f"{len(df_source.columns)}")
    m3.metric("Structured AI Insights", "0 (Unstructured Text Only)")

    st.dataframe(
        df_source.sort_values("Survey ID") if "Survey ID" in df_source.columns else df_source,
        use_container_width=True,
        hide_index=True,
        height=480,
    )

# =============================================================================
# TAB 5: AFTER AI - ENRICHED BI DATA
# =============================================================================
with tab_after:
    st.subheader("✨ AI-Enriched BI Dataset (After AI Analysis)")
    st.markdown(
        """
        <div class="insight-box">
            <strong>After AI Enrichment:</strong> Every unstructured comment is transformed into <strong>24+ structured analytical fields</strong>—including
            continuous sentiment polarity (<code>-1 to 1</code>), NPS segmentation, operational friction flags, satisfaction drivers,
            and the Top 5 contextualized themes.
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Records", f"{len(df):,}")
    m2.metric("Total Columns", f"{len(df.columns)}", delta=f"+{len(df.columns) - len(base_cols)} AI & BI columns")
    m3.metric("Automated Theme & Sentiment Coverage", "100%")

    st.dataframe(
        df.sort_values("Survey ID"),
        use_container_width=True,
        hide_index=True,
        height=480,
        column_config={
            "Consultation Date": st.column_config.DateColumn("Consultation Date", format="YYYY-MM-DD"),
            "Sentiment Score (-1 to 1)": st.column_config.NumberColumn("Sentiment Score (-1 to 1)", format="%+.2f"),
            "Satisfaction Score (1 to 5)": st.column_config.ProgressColumn(
                "Satisfaction (1–5)", min_value=1, max_value=5, format="%d / 5"
            ),
            "Wait Time (Mins)": st.column_config.NumberColumn("Wait Time (Mins)", format="%d min"),
        },
    )
