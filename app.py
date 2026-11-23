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

# Hero Banner Header
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
tab_about, tab_exec, tab_ops, tab_themes, tab_before, tab_after = st.tabs(
    [
        "ℹ️ About & Overview",
        "📊 Executive Overview",
        "⏱️ Operations & Bottlenecks",
        "💬 Themes & Feedback",
        "📄 Before AI: Source Data",
        "✨ After AI: Enriched Data",
    ]
)

CHART_FONT = dict(family="Inter, sans-serif", color="#1e293b")  

with tab_about:
    st.markdown("### 🏥 Project Overview")
    st.write(
        "An interactive Business Intelligence (BI) dashboard demonstrating how **local Large Language Models (LLMs)** "
        "transform raw, unstructured patient consultation comments into structured operational metrics across Melbourne clinic locations."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎯 What This Project Achieves")
        st.markdown("""
        * **Quantifies Unstructured Feedback:** Converts free-text patient comments into sentiment polarity scores (`-1` to `+1`), satisfaction ratings (`1–5`), and NPS segments.
        * **Pinpoints Operational Bottlenecks:** Links patient wait times with sentiment and specialty/time-of-day blocks to isolate clinic friction.
        * **Surfaces Thematic Drivers:** Extracts the top 5 experience themes and root-cause drivers for rapid executive review.
        * **Privacy-First AI Architecture:** Designed around local LLM processing so sensitive healthcare feedback never leaves on-premise infrastructure.
        """)

    with col2:
        st.markdown("#### 🧭 Dashboard Guide")
        st.markdown("""
        * **📊 Executive Overview:** Clinic RAG rankings, monthly sentiment trajectories, and NPS loyalty breakdowns.
        * **⏱ Operations & Bottlenecks:** Wait-time heatmaps, friction root causes, and clinician wait-vs.-sentiment benchmarks.
        * **💬 Themes & Feedback:** Top experience themes, satisfaction drivers, and a searchable comment explorer.
        * **📄 Before & ✨ After AI:** Inspect the raw baseline CSV side-by-side against the AI-enriched dataset.
        """)

    st.info(
        "**⚠️ Synthetic Data & Code Disclosure:** All patient records, clinician names, clinic metrics, and comments "
        "in this dashboard are **100% synthetically generated** for demonstration and prototyping purposes only—do not use "
        "for clinical or operational decision-making. Underlying local LLM enrichment scripts remain a work in progress."
    )

# =============================================================================
# TAB 1: EXECUTIVE OVERVIEW
# =============================================================================
with tab_exec:
    clinic_means = df.groupby("Clinic Location")["Sentiment Score (-1 to 1)"].mean()
    best_clinic = clinic_means.idxmax()
    best_clinic_val = clinic_means.max()
    worst_clinic = clinic_means.idxmin()
    worst_clinic_val = clinic_means.min()

    monthly_exec = (
        df.groupby(["Month Name", "Month Number"], as_index=False)
        .agg(Surveys=("Survey ID", "count"), Avg_Sentiment=("Sentiment Score (-1 to 1)", "mean"))
        .sort_values("Month Number")
    )
    peak_month = monthly_exec.loc[monthly_exec["Surveys"].idxmax(), "Month Name"]
    peak_month_vol = int(monthly_exec["Surveys"].max())

    st.markdown(
        f"""
        <div class="insight-box">
            📊 <strong>Executive Overview Commentary:</strong> Across <strong>{len(df):,} consultations</strong>,
            patient sentiment averages <strong>{kpis['avg_sentiment']:+.2f}</strong> with a Net Promoter Score of
            <strong>{kpis['nps_score']:+.0f}</strong>. <strong>{best_clinic}</strong> leads network performance
            (<strong>{best_clinic_val:+.2f}</strong>), while <strong>{worst_clinic}</strong> records the lowest
            average polarity (<strong>{worst_clinic_val:+.2f}</strong>) and warrants targeted follow-up.
            Consultation volume peaked in <strong>{peak_month}</strong> ({peak_month_vol} surveys) while maintaining
            consistent clinical satisfaction.
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Bar(
                x=monthly_exec["Month Name"],
                y=monthly_exec["Surveys"],
                name="Survey Volume",
                marker_color="#bae6fd",
                yaxis="y1",
            )
        )
        fig_trend.add_trace(
            go.Scatter(
                x=monthly_exec["Month Name"],
                y=monthly_exec["Avg_Sentiment"],
                name="Avg Sentiment",
                mode="lines+markers+text",
                text=monthly_exec["Avg_Sentiment"].map(lambda x: f"{x:+.2f}"),
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
    spec_wait = df.groupby("Consultation Type")["Wait Time (Mins)"].mean()
    slowest_spec = spec_wait.idxmax()
    slowest_spec_wait = spec_wait.max()
    fastest_spec = spec_wait.idxmin()
    fastest_spec_wait = spec_wait.min()

    time_wait = df.groupby("Time of Day Block")["Wait Time (Mins)"].mean()
    peak_block = time_wait.idxmax()
    peak_block_wait = time_wait.max()

    friction_df = df[df["Operational Friction Flag"] == "Yes"]
    friction_count = len(friction_df)

    st.markdown(
        f"""
        <div class="insight-box">
            ⏱️ <strong>Operations & Bottlenecks Commentary:</strong> Network-wide wait time averages
            <strong>{kpis['avg_wait']:.1f} mins</strong>, with <strong>{friction_count} consultations ({kpis['friction_rate']:.1f}%)</strong>
            experiencing operational friction—led by <strong>{kpis['top_friction']}</strong>.
            <strong>{slowest_spec}</strong> has the longest average wait (<strong>{slowest_spec_wait:.1f} mins</strong>)
            compared to <strong>{fastest_spec}</strong> (<strong>{fastest_spec_wait:.1f} mins</strong>), while
            <strong>{peak_block}</strong> represents the highest-congestion window (<strong>{peak_block_wait:.1f} mins</strong> avg wait).
        </div>
        """,
        unsafe_allow_html=True,
    )

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
    theme_cols = [c for c in df.columns if c.startswith("Theme ")]
    if "Top 5 Themes" in df.columns:
        theme_counts_series = df["Top 5 Themes"].value_counts()
        theme_df = pd.DataFrame(
            {
                "Theme": theme_counts_series.index,
                "Mentions": theme_counts_series.values,
                "Share": (theme_counts_series.values / len(df)) * 100,
            }
        ).sort_values("Mentions", ascending=True)
    else:
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

    top_theme_row = theme_df.iloc[-1]
    second_theme_row = theme_df.iloc[-2] if len(theme_df) > 1 else top_theme_row
    top_driver = df["Primary Satisfaction Driver"].value_counts().idxmax()
    top_driver_pct = (df["Primary Satisfaction Driver"].value_counts().max() / len(df)) * 100

    st.markdown(
        f"""
        <div class="insight-box">
            💬 <strong>Themes & Feedback Commentary:</strong> Patient praise is anchored by
            <strong>{top_theme_row['Theme']}</strong> ({int(top_theme_row['Mentions'])} mentions,
            <strong>{top_theme_row['Share']:.0f}%</strong> of consultations) and
            <strong>{second_theme_row['Theme']}</strong> ({int(second_theme_row['Mentions'])} mentions,
            <strong>{second_theme_row['Share']:.0f}%</strong>). Across single-driver attribution,
            <strong>{top_driver}</strong> stands out as the #1 primary satisfaction catalyst
            (<strong>{top_driver_pct:.0f}%</strong> of visits), confirming that clear explanations and
            actionable take-home care plans directly sustain high patient loyalty.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.15, 1])

    with c1:
        st.markdown(
            """
            <div class="chart-card">
                <div class="chart-title">🏷️ Top 5 Patient Experience Themes</div>
                <div class="chart-desc">AI theme frequency and share across active surveys</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
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

    avg_words = df_source["Patient Comments"].astype(str).str.split().str.len().mean()

    st.markdown(
        f"""
        <div class="insight-box">
            📄 <strong>Before AI Source Data Commentary:</strong> This baseline dataset holds
            <strong>{len(df_source):,} raw survey responses</strong> across <strong>{len(df_source.columns)} basic columns</strong>,
            where all clinical praise and operational complaints are locked inside unstructured free-text comments
            (averaging <strong>{avg_words:.1f} words</strong> per response). Without NLP enrichment, leadership cannot
            filter by sentiment polarity, quantify NPS loyalty, or isolate wait-time bottlenecks without reading rows manually.
        </div>
        """,
        unsafe_allow_html=True,
    )

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
    added_cols = len(df.columns) - len(base_cols)
    st.markdown(
        f"""
        <div class="insight-box">
            ✨ <strong>After AI Enriched Data Commentary:</strong> AI text analysis expands the raw dataset by
            <strong>+{added_cols} structured BI columns</strong> (totaling <strong>{len(df.columns)} columns</strong> across
            all <strong>{len(df):,} records</strong>)—converting every free-text comment into continuous sentiment scores
            (<code>-1 to +1</code>), NPS categories, operational friction flags, satisfaction drivers, and contextualized themes
            ready for instant slicing and executive reporting.
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
        f"+{added_cols} AI & BI fields added",
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
