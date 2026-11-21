import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from data_utils import (
    apply_custom_css,
    compute_kpis,
    get_top_filtered_data,
    render_kpi_card,
)

st.set_page_config(
    page_title="Clinical Consultation Pulse & Patient Experience",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_custom_css()

# Top Filter Bar (No Sidebar)
df_raw, df = get_top_filtered_data()
kpis = compute_kpis(df)

# Hero Banner Header (Exact Title Preserved, No Subtitle)
st.markdown(
    f"""
    <div class="hero-header">
        <h1 class="hero-title">🏥 Clinical Consultation Pulse & Patient Experience</h1>
        <div class="hero-badge">
            Showing {len(df):,} of {len(df_raw):,} Surveys &bull; {df['Clinic Location'].nunique()} Melbourne Clinics
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Executive Takeaway Banner
st.markdown(
    f"""
    <div class="insight-box">
        💡 <strong>Executive Takeaway:</strong> Overall sentiment averages <strong>{kpis['avg_sentiment']:+.2f}</strong>
        (NPS <strong>{kpis['nps_score']:+.0f}</strong>) with an average wait of <strong>{kpis['avg_wait']:.1f} mins</strong>.
        <strong>{kpis['top_clinic']}</strong> leads clinic performance (<strong>{kpis['top_clinic_score']:+.2f}</strong>),
        while the primary bottleneck is <strong>{kpis['top_friction']}</strong> ({kpis['friction_rate']:.1f}% friction rate).
    </div>
    """,
    unsafe_allow_html=True,
)

# Elevated KPI Cards Row
k1, k2, k3, k4, k5 = st.columns(5)
render_kpi_card(
    k1,
    "Total Surveys",
    f"{kpis['total_surveys']:,}",
    f"{(len(df)/len(df_raw))*100:.0f}% of dataset active",
    "#0284c7",
    "#e0f2fe",
    "#0369a1",
)
render_kpi_card(
    k2,
    "Avg Sentiment (-1 to 1)",
    f"{kpis['avg_sentiment']:+.2f}",
    "Strong Positive Polarity" if kpis["avg_sentiment"] >= 0.7 else "Moderate Polarity",
    "#10b981",
    "#d1fae5",
    "#047857",
)
render_kpi_card(
    k3,
    "Net Promoter Score",
    f"{kpis['nps_score']:+.0f}",
    "World-Class (> +70)" if kpis["nps_score"] >= 70 else "Healthy (> +50)",
    "#6366f1",
    "#e0e7ff",
    "#4338ca",
)
render_kpi_card(
    k4,
    "Avg Satisfaction",
    f"{kpis['avg_sat']:.2f} / 5",
    f"{(df['Satisfaction Score (1 to 5)'] == 5).mean()*100:.0f}% rated 5-star",
    "#0d9488",
    "#ccfbf1",
    "#0f766e",
)
render_kpi_card(
    k5,
    "Operational Friction",
    f"{kpis['friction_rate']:.1f}%",
    f"⏱️ {kpis['avg_wait']:.1f} min avg wait",
    "#f59e0b" if kpis["friction_rate"] < 15 else "#ef4444",
    "#fef3c7" if kpis["friction_rate"] < 15 else "#fee2e2",
    "#b45309" if kpis["friction_rate"] < 15 else "#b91c1c",
)

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# Top Segmented Pill Navigation Tabs
tab_exec, tab_ops, tab_themes, tab_before, tab_after = st.tabs(
    [
        "📊 Executive Overview",
        "⏱️ Operations & Bottlenecks",
        "💬 Themes & Feedback",
        "📄 Before AI: Source Data",
        "✨ After AI: Enriched Data",
    ]
)

CHART_FONT = dict(family="Inter, sans-serif", color="#1e293b")

# =============================================================================
# TAB 1: EXECUTIVE OVERVIEW
# =============================================================================
with tab_exec:
    c1, c2 = st.columns([1.15, 1])

    with c1:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">📍 Clinic Sentiment Ranking (RAG Performance)</div>
                <div class="chart-desc">Average polarity score (-1 to +1) benchmarked across clinic locations</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
        fig_clinic.update_traces(textposition="outside", marker_line_width=0)
        fig_clinic.update_layout(
            font=CHART_FONT,
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis=dict(range=[0, 1.12], showgrid=True, gridcolor="#f1f5f9", title="Average Sentiment Score"),
            yaxis=dict(title=""),
            legend=dict(orientation="h", y=1.1, x=0, title=""),
            height=380,
            margin=dict(l=10, r=25, t=20, b=10),
        )
        st.plotly_chart(fig_clinic, use_container_width=True)

    with c2:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">📈 Monthly Survey Volume vs. Sentiment Trajectory</div>
                <div class="chart-desc">Consultation volume bars paired with monthly average polarity trend</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        monthly = (
            df.groupby(["Month Name", "Month Number"], as_index=False)
            .agg(Surveys=("Survey ID", "count"), Avg_Sentiment=("Sentiment Score (-1 to 1)", "mean"))
            .sort_values("Month Number")
        )
        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Bar(
                x=monthly["Month Name"],
                y=monthly["Surveys"],
                name="Survey Volume",
                marker_color="#bae6fd",
                yaxis="y1",
            )
        )
        fig_trend.add_trace(
            go.Scatter(
                x=monthly["Month Name"],
                y=monthly["Avg_Sentiment"],
                name="Avg Sentiment",
                mode="lines+markers+text",
                text=monthly["Avg_Sentiment"].map(lambda x: f"{x:+.2f}"),
                textposition="top center",
                line=dict(color="#0284c7", width=3.5),
                marker=dict(size=10, color="#0369a1"),
                yaxis="y2",
            )
        )
        fig_trend.update_layout(
            font=CHART_FONT,
            paper_bgcolor="white",
            plot_bgcolor="white",
            yaxis=dict(title="Surveys", showgrid=False),
            yaxis2=dict(title="Avg Sentiment", side="right", overlaying="y", range=[-0.1, 1.12], showgrid=True, gridcolor="#f1f5f9"),
            legend=dict(orientation="h", y=1.1, x=1, xanchor="right"),
            height=380,
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown(
        """
        <div class="chart-card">
            <div class="chart-title">🎯 Net Promoter Score (NPS) Loyalty Mix by Clinic</div>
            <div class="chart-desc">Distribution of Promoters (5★), Passives (4★ with minor friction), and Detractors (1–3★)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
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
        text="Count",
        color_discrete_map={"Promoter": "#10b981", "Passive": "#f59e0b", "Detractor": "#ef4444"},
        category_orders={"NPS Category": ["Promoter", "Passive", "Detractor"]},
    )
    fig_nps_bar.update_traces(textposition="inside")
    fig_nps_bar.update_layout(
        font=CHART_FONT,
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis=dict(title=""),
        xaxis=dict(title="Survey Count", showgrid=True, gridcolor="#f1f5f9"),
        legend=dict(orientation="h", y=1.12, x=0, title=""),
        height=340,
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_nps_bar, use_container_width=True)

# =============================================================================
# TAB 2: OPERATIONS & BOTTLENECKS
# =============================================================================
with tab_ops:
    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">🔥 Peak-Hour Wait Time Heatmap (Mins)</div>
                <div class="chart-desc">Average patient wait duration across clinical specialties and time blocks</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
        fig_heat.update_layout(font=CHART_FONT, paper_bgcolor="white", height=400, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_heat, use_container_width=True)

    with c2:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">⚠️ Operational Friction Root Causes</div>
                <div class="chart-desc">Specific delay, crowding, or service bottlenecks extracted from comments</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
                font=CHART_FONT,
                paper_bgcolor="white",
                plot_bgcolor="white",
                yaxis=dict(title=""),
                xaxis=dict(range=[0, max(f_counts["Count"].max() * 1.25, 4)], showgrid=True, gridcolor="#f1f5f9"),
                height=400,
                margin=dict(l=10, r=25, t=10, b=10),
            )
            st.plotly_chart(fig_fric, use_container_width=True)

    st.markdown(
        """
        <div class="chart-card">
            <div class="chart-title">🩺 Clinician Wait Time vs. Sentiment Benchmark</div>
            <div class="chart-desc">Bubble size reflects consultation volume; top-left quadrant indicates fast, high-satisfaction care</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
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
    fig_scatter.update_layout(
        font=CHART_FONT,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        height=370,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# =============================================================================
# TAB 3: THEMES & FEEDBACK
# =============================================================================
with tab_themes:
    c1, c2 = st.columns([1.15, 1])

    with c1:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">🏷️ Top 5 Patient Experience Themes</div>
                <div class="chart-desc">Multi-label AI theme frequency and share across active surveys</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
            font=CHART_FONT,
            paper_bgcolor="white",
            plot_bgcolor="white",
            coloraxis_showscale=False,
            yaxis=dict(title=""),
            xaxis=dict(range=[0, max(theme_df["Mentions"].max() * 1.28, 10)], showgrid=True, gridcolor="#f1f5f9"),
            height=380,
            margin=dict(l=10, r=25, t=10, b=10),
        )
        st.plotly_chart(fig_themes, use_container_width=True)

    with c2:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">💡 Primary Satisfaction Drivers</div>
                <div class="chart-desc">Dominant clinical or operational factor behind each patient's rating</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
            font=CHART_FONT,
            paper_bgcolor="white",
            plot_bgcolor="white",
            yaxis=dict(title=""),
            xaxis=dict(range=[0, max(drivers["Count"].max() * 1.25, 5)], showgrid=True, gridcolor="#f1f5f9"),
            height=380,
            margin=dict(l=10, r=25, t=10, b=10),
        )
        st.plotly_chart(fig_drivers, use_container_width=True)

    st.markdown(
        """
        <div class="chart-card">
            <div class="chart-title">🔎 Interactive Patient Comments & Theme Explorer</div>
            <div class="chart-desc">Filter by sentiment, isolate operational friction, or search clinical keywords</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns([1, 1, 2])
    sent_filter = f1.selectbox("Sentiment", ["All"] + sorted(df["Sentiment"].unique().tolist()))
    friction_only = f2.checkbox("Operational Friction Only")
    keyword = f3.text_input("Search Comments or Theme Context", placeholder="e.g., ECG, billing, toddler, delay...")

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
    st.dataframe(
        explorer[display_cols].sort_values("Survey ID"),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Consultation Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "Sentiment Score (-1 to 1)": st.column_config.NumberColumn("Sentiment", format="%+.2f"),
            "Wait Time (Mins)": st.column_config.NumberColumn("Wait", format="%d min"),
        },
    )

# =============================================================================
# TAB 4: BEFORE AI - SOURCE DATA
# =============================================================================
with tab_before:
    st.markdown(
        """
        <div class="insight-box">
            📄 <strong>Before AI Enrichment:</strong> Raw survey exports contain only unstructured free-text
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
    render_kpi_card(m1, "Source Records", f"{len(df_source):,}", "Raw CSV rows", "#64748b", "#f1f5f9", "#334155")
    render_kpi_card(m2, "Source Columns", f"{len(df_source.columns)}", "Basic metadata + free text", "#f59e0b", "#fef3c7", "#b45309")
    render_kpi_card(m3, "Structured AI Insights", "0", "Manual review required", "#ef4444", "#fee2e2", "#b91c1c")

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
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
    st.markdown(
        """
        <div class="insight-box">
            ✨ <strong>After AI Enrichment:</strong> Every unstructured comment is transformed into <strong>24+ structured analytical fields</strong>—including
            continuous sentiment polarity (<code>-1 to 1</code>), NPS segmentation, operational friction flags, satisfaction drivers,
            and the Top 5 contextualized themes.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Interactive Single-Survey Before vs. After Spotlight
    with st.expander("🔬 Interactive Before vs. After AI Spotlight (Inspect Any Survey)", expanded=True):
        selected_id = st.selectbox(
            "Select a Survey ID to compare raw input vs. AI-extracted intelligence:",
            options=df["Survey ID"].sort_values().tolist(),
            index=0,
        )
        row = df[df["Survey ID"] == selected_id].iloc[0]

        sp1, sp2 = st.columns(2)
        with sp1:
            st.markdown(
                f"""
                <div class="spotlight-before">
                    <div style="font-size:0.78rem; font-weight:700; text-transform:uppercase; color:#b45309; margin-bottom:0.4rem;">
                        📄 Before AI (Raw Unstructured Input)
                    </div>
                    <div style="font-size:0.88rem; color:#475569; margin-bottom:0.5rem;">
                        <strong>{row['Survey ID']}</strong> &bull; {row['Consultation Type']} &bull; {row['Clinic Location']}
                    </div>
                    <div style="font-size:1rem; font-style:italic; color:#0f172a; background:#ffffff; padding:0.75rem; border-radius:8px; border:1px solid #fde68a;">
                        "{row['Patient Comments']}"
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sp2:
            themes_list = [t.strip() for t in str(row["Top 5 Themes with Context"]).split("|") if t.strip()]
            theme_pills = "".join([f'<span class="pill-tag">🏷️ {t}</span>' for t in themes_list])
            st.markdown(
                f"""
                <div class="spotlight-after">
                    <div style="font-size:0.78rem; font-weight:700; text-transform:uppercase; color:#047857; margin-bottom:0.4rem;">
                        ✨ After AI (Structured BI Intelligence)
                    </div>
                    <div style="margin-bottom:0.5rem;">
                        <span class="pill-tag">Sentiment: <strong>{row['Sentiment']} ({row['Sentiment Score (-1 to 1)']:+.2f})</strong></span>
                        <span class="pill-tag">NPS: <strong>{row['NPS Category']} ({row['Satisfaction Score (1 to 5)']}★)</strong></span>
                        <span class="pill-tag">Friction: <strong>{row['Friction Type']}</strong></span>
                    </div>
                    <div>{theme_pills}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    m1, m2, m3 = st.columns(3)
    render_kpi_card(m1, "Enriched Records", f"{len(df):,}", "100% unique comments", "#0284c7", "#e0f2fe", "#0369a1")
    render_kpi_card(
        m2,
        "Total BI Columns",
        f"{len(df.columns)}",
        f"+{len(df.columns) - len(base_cols)} AI & BI fields added",
        "#10b981",
        "#d1fae5",
        "#047857",
    )
    render_kpi_card(m3, "Automated Coverage", "100%", "Zero manual tagging", "#6366f1", "#e0e7ff", "#4338ca")

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
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
