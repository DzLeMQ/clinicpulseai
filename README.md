# 🏥 Clinical Consultation Pulse & Patient Experience

An interactive [AI-driven Business Intelligence (BI) analytics dashboard](https://clinicpulselocalai.streamlit.app/) built with **local LLMs**, **Streamlit**, **Pandas**, and **Plotly**. This application transforms unstructured patient consultation comments into structured sentiment polarity scores, Net Promoter Score (NPS) classifications, operational wait-time bottleneck heatmaps, and thematic satisfaction drivers across Melbourne clinic locations.

----

## ⚠️ Disclaimer & Code Disclosure Notice

> **SYNTHETIC DATA NOTICE — USE WITH CAUTION:**  
> All consultation records, patient identifiers (`Customer ID`), clinician names, clinic metrics, wait times, and patient comments included in this repository (`consultation_synthetic_surveys.csv` and `consultation_synthetic_surveys_enriched.csv`) are **100% synthetically generated** for demonstration, prototyping, and analytics testing purposes only.  
>
> * These datasets **do not** represent real patients, actual clinical encounters, or genuine medical facility performance.  
> * Outputs, sentiment scores, and operational insights derived from this data **must not** be used for real-world clinical decision-making, medical staffing, patient care, or regulatory reporting.  
> * **Use with caution** and validate all analytical pipelines against verified, de-identified production data before any operational deployment.

> **AI DATA ENRICHMENT CODE DISCLOSURE (WORK IN PROGRESS):**  
> Please note that the underlying scripts and local LLM pipeline codes used to generate the AI-enriched dataset (`consultation_synthetic_surveys_enriched.csv`) are **currently undisclosed in this repository as they remain a work in progress**. Only the baseline synthetic input (`consultation_synthetic_surveys.csv`), enriched output dataset, and interactive visualization application (`app.py` and `data_utils.py`) are shared for community review and testing at this stage.

---

## ✨ Key Features

* **Top Filter Bar (Sidebar-Free Layout):** Filter dynamically by **Record Cohort**, **Clinic Location**, **Consultation Type**, and **Visit Mode**, with a one-click **Reset** button.
* **Executive KPI Scorecard:** Tracks **Total Surveys**, **Average Sentiment (-1 to +1)**, **Net Promoter Score (NPS)**, **Average Satisfaction (1–5)**, and **Operational Friction Rate %**.
* **Dynamic Tab-Specific Commentaries:** Automatically recalculates narrative executive takeaways inside every tab based on active filter selections:
  * **📊 Executive Overview:** Red/Amber/Green (RAG) clinic sentiment rankings, monthly volume vs. sentiment trajectories, and clinic-level NPS loyalty breakdowns.
  * **⏱️ Operations & Bottlenecks:** Specialty × Time-of-Day wait-time heatmaps, operational friction root-cause analysis, and clinician wait-vs.-sentiment scatter benchmarks.
  * **💬 Themes & Feedback:** Top 5 patient experience themes, primary satisfaction drivers, and a searchable patient comment & theme explorer.
  * **📄 Before AI: Source Data:** Displays the raw, unstructured baseline CSV prior to NLP enrichment.
  * **✨ After AI: Enriched Data:** Showcases the AI-enriched dataset alongside an interactive **Before vs. After AI Spotlight** comparison card for individual surveys.

---

## 📁 Project Structure

```text
clinical-consultation-pulse/
├── app.py                                      # Main Streamlit UI, tabs, charts, and dynamic commentaries
├── data_utils.py                               # Custom CSS styling, data loader, top filter bar, and KPI engine
├── consultation_synthetic_surveys.csv          # Raw baseline synthetic survey dataset (Before AI)
├── consultation_synthetic_surveys_enriched.csv # AI-enriched BI dataset (After AI)
├── requirements.txt                            # Python dependencies
└── README.md                                   # Project documentation, synthetic data & code disclosure notices
```

---

## 🚀 Getting Started

### 1. Prerequisites
* **Python 3.9+** installed on your system.

### 2. Create & Activate a Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Dashboard
Ensure `app.py`, `data_utils.py`, and your CSV file(s) are in the same directory, then run:
```bash
streamlit run app.py
```

The dashboard will open automatically in your default browser at `http://localhost:8501`.

---

## 📊 Dataset Schema Overview

| Category | Key Columns | Description |
| :--- | :--- | :--- |
| **Identifiers & Cohort** | `Survey ID`, `Customer ID`, `Record Cohort` | Unique survey/patient keys and cohort flag (`Original Survey` vs. `Benchmark Edge Case`) |
| **Clinical & Location** | `Consultation Type`, `Visit Mode`, `Clinic Location`, `Clinic Region`, `Clinician Name` | Specialty, In-Clinic/Telehealth mode, and Melbourne clinic metadata |
| **Scheduling & Wait** | `Consultation Date`, `Month Name`, `Day of Week`, `Time of Day Block`, `Wait Time (Mins)` | Temporal dimensions and patient wait duration in minutes |
| **AI Sentiment & NPS** | `Sentiment`, `Sentiment Tier`, `Sentiment Score (-1 to 1)`, `Satisfaction Score (1 to 5)`, `NPS Category` | Polarity scoring (`-1` to `+1`), 1–5 rating, and Promoter/Passive/Detractor segmentation |
| **Friction & Themes** | `Operational Friction Flag`, `Friction Type`, `Primary Satisfaction Driver`, `Top 5 Themes`, `Top 5 Themes with Context` | Extracted operational bottlenecks and primary patient experience themes |
