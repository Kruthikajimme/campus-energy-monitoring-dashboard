# Professor's 100-Point Evaluation & Demonstration Guide

**Project Title:** Campus Energy Consumption Monitoring and Analytics Dashboard  
**Faculty Evaluator:** Professor Sayed Faizan Qaser  
**Course:** Final-Year Engineering Capstone Project / Advanced Data Science & Visualization  
**Technology Stack:** Python 3.12 (Data Engineering & Analytics) + Microsoft Power BI Desktop (Business Intelligence & Dashboards)

---

## Executive Evaluation Summary Matrix (100 Points Total)

| Assessment Criterion | Weightage | Target Learning Outcomes Demonstrated | Evidence & Demonstration Artifacts |
|---|---|---|---|
| **A. Data Correctness & Preparation** | **25 Points** | Real-world telemetry structure, robust 10-stage Pandas cleaning pipeline, missing value imputation, negative sign correction, IQR outlier treatment, Star Schema normalization, audit reporting. | `sample_raw_energy.csv`, `sample_cleaned_energy.csv`, `cleaning_report.json`, `data_dictionary.xlsx`, `test_data_cleaning.py`. |
| **B. KPI & Chart Selection** | **25 Points** | Meaningful additive & semi-additive energy KPIs, diurnal hourly profiles, building benchmarking, time-series dual-axis curves, scatter correlations, advanced Power BI Star Schema, 21+ DAX measures, slicers, drill-through. | `FactEnergyConsumption.csv`, `DimBuilding`, `DimDate`, `DimTime`, `DimEnergySource`, `DAX_Measures.md`, `Dashboard_Design.md`. |
| **C. Interpretation & Actionable Findings** | **25 Points** | Empirical synthesis answering the 9 core management queries, statistical anomaly detection (IQR + Rolling Z-score), load-shifting & peak shaving proposals, carbon footprint calculations. | `anomaly_report.csv`, `PowerBI_Anomaly_Report.csv`, `insights_report.xlsx`, `insights.py`. |
| **D. Individual Explanation & Participation** | **25 Points** | Equitable 3-member team role division, technical viva readiness across Python and Power BI, live classroom demonstration workflow. | `Team_Contribution_Plan.md`, `Viva_Preparation_Guide.md`, `run_demo.py` live execution. |

---

## Detailed Evaluation Criteria & Evidence

### CRITERION A: Data Correctness and Preparation (25 Points)

#### 1. What Prof. Sayed Faizan Qaser Will Evaluate:
- Did the team design an authentic campus energy dataset representing real-world facility dynamics?
- Are units, timestamps, and electrical variables physically consistent?
- Did the team implement rigorous data cleaning rather than silently dropping or ignoring dirty data?
- Is there a transparent, reproducible audit trail documenting every cleaning decision?

#### 2. Evidence & Demonstration Steps to Show:
1. **Show the Raw vs Cleaned Dataset Comparison:**
   - Open `data/sample_raw_energy.csv` (15,180 records) vs `data/sample_cleaned_energy.csv` (15,112 records).
   - Point out the controlled data quality defects introduced into raw data: missing values, duplicate packets, polarity reversals (negative kWh), sensor glitches ($>2.5\times\text{IQR}$), and unstandardized names.
2. **Open the Cleaning Audit Report (`data/cleaning_report.json`):**
   - Demonstrate the exact cleaning statistics:
     - Original Records: `15,180`
     - Duplicate Records Removed: `62` (based on compound `[timestamp, building]` keys)
     - Invalid Timestamps Dropped: `8`
     - Negative Current Inversions Fixed: `30` (`abs(units_kwh)` sensor CT polarity reversal)
     - Missing Values Imputed: `75` (using facility diurnal hourly medians)
     - Extreme Sensor Dropouts Capped: `34` ($>2.5\times\text{IQR}$ capped to 99th percentile)
     - Voltage Regulated: `30` readings ($<180\text{V}$ or $>270\text{V}$ reset to 230V nominal)
     - Final Clean Record Count: `15,112`
3. **Show Automated Pipeline Execution:**
   - Execute in terminal:
     ```powershell
     python run_pipeline.py
     ```
   - Show Stages 1 to 3 executing with zero errors.
4. **Open the Excel Data Dictionary (`data/data_dictionary.xlsx`):**
   - Show the 6 sheets documenting every column, physical unit (kWh, kW, Volts, °C), constraints, and primary/foreign keys.

---

### CRITERION B: KPI and Chart Selection (25 Points)

#### 1. What Prof. Sayed Faizan Qaser Will Evaluate:
- Are the chosen KPIs mathematically sound and operationally relevant to university administrators?
- Does the Power BI dashboard follow dimensional modeling best practices (Star Schema)?
- Are charts chosen appropriately for the underlying data types (e.g. lines for continuous time series, bars for categorical benchmarking, area charts for diurnal curves)?
- Are DAX measures properly written, formatted, and optimized?

#### 2. Evidence & Demonstration Steps to Show:
1. **Explain the Star Schema Architecture (`powerbi/Data_Model.md`):**
   - Point to the ER diagram showing the centralized `FactEnergyConsumption` table surrounded by `DimBuilding`, `DimDate`, `DimTime`, and `DimEnergySource`.
   - Explain why surrogate integer keys (`date_key`, `time_key`) are superior to raw datetime strings in Power BI VertiPaq storage.
   - Show that single-directional cross-filtering is strictly enforced to prevent ambiguous filter contexts.
2. **Present the 6 Executive KPIs:**
   - *Total Energy Consumption:* $1,181,593\text{ kWh}$ ($1,181.6\text{ MWh}$)
   - *Average Daily Consumption:* $13,128.8\text{ kWh/day}$
   - *Peak Electricity Demand:* $490.4\text{ kW}$
   - *Facilities Monitored:* $7$
   - *Total Telemetry Points:* $15,112$
   - *Anomalies Flagged:* $418$
3. **Demonstrate Advanced DAX Calculations (`powerbi/DAX_Measures.md`):**
   - Walk the professor through key DAX measures:
     - `Building Consumption Percentage` (using `ALL(DimBuilding)`)
     - `Building Consumption Ranking` (using `RANKX`)
     - `Rolling 7-Day Average` (using `DATESINPERIOD`)
     - `Year-to-Date Consumption` (using `TOTALYTD`)
     - `Month-over-Month Growth %` (using `DATEADD`)
4. **Show Visual Page Configurations (`powerbi/Dashboard_Design.md`):**
   - Show the 5 report pages: Executive Overview, Building Performance, Time-Based Trends, Anomaly Monitoring, and Energy Efficiency Insights.
   - Demonstrate interactive slicers, drill-through from building bars, and conditional formatting.

---

### CRITERION C: Interpretation and Actionable Findings (25 Points)

#### 1. What Prof. Sayed Faizan Qaser Will Evaluate:
- Did the team extract meaningful domain insights rather than just displaying raw numbers?
- Can the team answer core management questions with empirical data?
- Is anomaly detection grounded in statistical rigor rather than arbitrary rules?
- Are energy conservation proposals practical, cost-aware, and actionable?

#### 2. Evidence & Demonstration Steps to Show:
1. **Answer the 9 Core Management Questions (`src/insights.py` / `reports/insights_report.xlsx`):**
   - *Q1 (Top Consumer):* Computer Science Block consumes the most ($264,812\text{ kWh}$, 22.4% of campus total) due to continuous 24/7 server racks and lab AC.
   - *Q2 (Lowest Consumer):* Canteen consumes the least ($85,120\text{ kWh}$, 7.2%) due to concentrated meal-time usage and minimal night load.
   - *Q3 (Peak Window):* 13:00 to 16:00 is the peak operational window (afternoon class lectures + lab computers + midday chiller load).
   - *Q4 (Weekend Shift):* Hourly consumption drops by **18.3%** on weekends.
   - *Q5 (Occupancy Correlation):* Moderate positive correlation ($r = 0.628$).
   - *Q6 (Anomaly Hotspot):* Academic Block exhibits the highest anomaly frequency.
2. **Explain the Dual Anomaly Detection Algorithm (`src/anomaly_detection.py`):**
   - Explain how IQR thresholds ($Q_3 + 1.8\times\text{IQR}$, $Q_3 + 2.5\times\text{IQR}$, $Q_3 + 3.5\times\text{IQR}$) isolate facility-specific deviations.
   - Explain how the 6-hour moving Z-score isolates sudden electrical surges ($Z > 3.0$ and $>175\%$ of rolling mean).
   - Emphasize the ethical engineering disclaimer: *"Statistical anomalies indicate unusual operational patterns requiring inspection, not confirmed physical hardware faults."*
3. **Present the 5 Actionable Conservation Measures:**
   - **REC-01:** Stagger heavy laboratory machinery outside 11:00–15:00 peak tariff window (cuts peak kW by 12–18%).
   - **REC-02:** Deploy programmable BMS night setbacks after 18:30 in Academic Block and Library (saves 10–15% baseload).
   - **REC-03:** Solar thermal domestic water heating in student hostels (offsets electric geysers).
   - **REC-04:** 120 kWp rooftop solar PV expansion (absorbs midday AC demand).
   - **REC-05:** Targeted power quality audit for distribution boards with recurring spikes.

---

### CRITERION D: Individual Explanation and Participation (25 Points)

#### 1. What Prof. Sayed Faizan Qaser Will Evaluate:
- Did each team member contribute equitably to the project lifecycle?
- Can each member articulate their specific modules during individual viva questioning?
- Can the team demonstrate live data updates and Power BI refresh?

#### 2. Evidence & Demonstration Steps to Show:
1. **Present the Team Contribution Plan (`Team_Contribution_Plan.md`):**
   - **Member 1 (Data Engineering):** Owned dataset simulation, 10-stage cleaning pipeline, data quality validation, and `cleaning_report.json`.
   - **Member 2 (Power BI Architecture & DAX):** Owned Star Schema design, table relationships, sort-by configurations, and 21+ DAX measures.
   - **Member 3 (Anomaly Detection & Insights):** Owned IQR/Z-score anomaly engine, 5-page dashboard visual layout, insights Q&A synthesis, and live demo script.
2. **Execute the Live Demonstration Scenario:**
   - Run:
     ```powershell
     python run_demo.py
     ```
   - Walk through the 6 demonstration steps:
     - Step 1: Baseline metrics display (`1,181,593 kWh`, `418 Anomalies`).
     - Step 2 & 3: Inject normal reading (Library) and intentional 425.0 kWh surge (Academic Block).
     - Step 4: Pipeline re-executes automatically.
     - Step 5: Show the newly detected Critical Anomaly (`ANOM-0020`) with $+126.8\%$ deviation, root-cause reason, and recommended action.
     - Step 6: Explain that clicking **Refresh** in Power BI re-reads the updated CSVs, instantly reflecting the surge on cards and charts.
3. **Run the Automated PyTest Suite:**
   - Run:
     ```powershell
     pytest tests/ -v
     ```
   - Show all 24 unit and integration tests passing with 100% green status.
4. **Refer to the Viva Preparation Guide (`Viva_Preparation_Guide.md`):**
   - Each member demonstrates mastery over their technical domain.

