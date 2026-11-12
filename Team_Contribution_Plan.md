# Academic Team Contribution & Individual Evaluation Plan

**Project Title:** Campus Energy Consumption Monitoring and Analytics Dashboard  
**Evaluator:** Professor Sayed Faizan Qaser  
**Team Structure:** Collaborative Engineering Team of Three Members

---

## 1. Executive Team Workload Allocation

To ensure academic fairness, technical depth, and clear individual accountability, project responsibilities were distributed across three specialized engineering domains:

```
+-----------------------------------------------------------------------------------------+
|                                    PROJECT LEADERSHIP                                   |
|                CAMPUS ENERGY CONSUMPTION MONITORING & ANALYTICS DASHBOARD               |
+----------------------------+----------------------------+-------------------------------+
|          MEMBER 1          |          MEMBER 2          |            MEMBER 3           |
|      DATA ENGINEERING      |      POWER BI & DAX        |     DIAGNOSTICS & INSIGHTS    |
+----------------------------+----------------------------+-------------------------------+
| • Telemetry Simulation     | • Star Schema Data Model   | • Dual Anomaly Detection      |
| • Pre-Cleaning Validation  | • 21+ DAX Measures         | • 5-Page Dashboard Layout     |
| • 10-Stage Pandas Pipeline | • Time-Intelligence DAX    | • Empirical Q&A Insights      |
| • Missing Value Imputation | • Executive Overview Page  | • 5 Conservation Proposals    |
| • Quality Audit Report     | • Building Analytics Page  | • Live Demo Script & Tests    |
+----------------------------+----------------------------+-------------------------------+
```

---

## 2. Detailed Member Ownership Breakdown

### MEMBER 1: Data Engineering & Quality Pipeline Lead
- **Primary Modules Owned:**
  - `src/data_generator.py` (Physics-based hourly simulation across 7 campus buildings over 90 days).
  - `src/data_validation.py` (Pre-cleaning schema, type, and boundary validation).
  - `src/data_cleaning.py` (10-stage Pandas cleaning and imputation pipeline).
  - `generate_dataset.py` (Deterministic dataset generator with fixed seed `42`).
  - `tests/test_data_cleaning.py` and `tests/test_data_generation.py`.
- **Key Deliverables Produced:**
  - `data/sample_raw_energy.csv` (15,180 noisy records with controlled anomalies).
  - `data/sample_cleaned_energy.csv` (15,112 normalized records).
  - `data/cleaning_report.json` (Exhaustive JSON audit report documenting all 10 cleaning steps).
  - Data cleaning rationale and methodology documentation.

#### Member 1 Individual Viva & Defense Guide:
- **Core Pitch:** *"My primary responsibility was ensuring data correctness and chronological integrity. I engineered a realistic 90-day simulation of 7 facilities and built a 10-stage Pandas cleaning pipeline. Rather than naively deleting missing values or negative readings, I implemented domain-aware fixes: reversing inverted current-transformer (CT) sensor polarity signs, imputing missing consumption using facility-specific diurnal hourly medians, and capping sensor telemetry overflows using $2.5\times\text{IQR}$ to the 99th percentile."*
- **Key Concepts to Explain:**
  1. *Why hourly median imputation?* Preserves the characteristic diurnal day/night load curve without introducing artificial mean spikes.
  2. *How were duplicates identified?* By checking composite keys of `[timestamp, building]`.
  3. *Why preserve raw data?* To ensure full auditability for facility management without destructive in-place modification.

---

### MEMBER 2: Power BI Data Modeling & DAX Specialist
- **Primary Modules Owned:**
  - `src/feature_engineering.py` (Surrogate keys: `date_key`, `time_key`, `building_id`, `source_id`).
  - `src/export_powerbi.py` (Star Schema extraction and Excel data dictionary generation).
  - `powerbi/Data_Model.md` (Star Schema ER architecture and relationship cardinality).
  - `powerbi/DAX_Measures.md` (Authoring, testing, and documenting all 21+ DAX measures).
  - `powerbi/PowerBI_Import_Instructions.md` (Step-by-step 5-minute setup checklist).
- **Key Deliverables Produced:**
  - `FactEnergyConsumption.csv` (Normalized fact table).
  - Dimension tables: `DimBuilding.csv`, `DimDate.csv`, `DimTime.csv`, `DimEnergySource.csv`.
  - `data/data_dictionary.xlsx` (6-sheet corporate data dictionary).
  - 21+ explicit DAX measures across 5 calculation folders.
  - Page 1 (Executive Overview) and Page 2 (Building Performance Analytics) designs.

#### Member 2 Individual Viva & Defense Guide:
- **Core Pitch:** *"My focus was the Power BI analytical foundation. I structured the data into a pure Kimball Star Schema with a centralized fact table and four normalized dimension tables using integer surrogate keys for optimal VertiPaq compression. I authored and validated 21+ explicit DAX measures including time-intelligence calculations (`TOTALYTD`, `DATEADD`), dynamic rankings (`RANKX`), and campus percentage shares (`ALL(DimBuilding)`). Single-directional filtering was strictly enforced to guarantee unambiguous context transitions."*
- **Key Concepts to Explain:**
  1. *Why use surrogate integer keys like `20261015` instead of datetime strings?* Reduces VertiPaq dictionary size, enabling bit-packing compression and faster memory scans.
  2. *Explain `Building Consumption Percentage` DAX:* Uses `CALCULATE([Total kWh], ALL(DimBuilding))` to remove the facility filter from the denominator while keeping temporal filters active.
  3. *Why avoid bi-directional cross-filtering?* Bi-directional filtering can introduce ambiguous evaluation paths and circular relationship errors in multi-table models.

---

### MEMBER 3: Diagnostics, Visual UX & Insights Lead
- **Primary Modules Owned:**
  - `src/anomaly_detection.py` (Multi-tier IQR and rolling 6-hour moving Z-score engine).
  - `src/insights.py` (Automated empirical findings, answering the 9 core management questions).
  - `powerbi/Dashboard_Design.md` (5-page visual architecture, color palettes, and slicer syncing).
  - `powerbi/PowerBI_Guide.md` (Developer manual, drill-through, and conditional formatting rules).
  - `run_demo.py` (Classroom live demonstration workflow with surge injection).
  - `tests/test_analytics.py` and `tests/test_anomaly_detection.py`.
- **Key Deliverables Produced:**
  - `PowerBI_Anomaly_Report.csv` and `reports/anomaly_report.csv`.
  - `reports/insights_report.xlsx` (OpenPyXL multi-sheet management findings workbook).
  - Page 3 (Time-Based Analytics), Page 4 (Anomaly Monitoring), and Page 5 (Energy Efficiency Insights).
  - 5 concrete energy conservation proposals with feasibility and ROI ratings.
  - Automated test suite verification (24/24 tests passing).

#### Member 3 Individual Viva & Defense Guide:
- **Core Pitch:** *"I was responsible for turning raw telemetry into actionable engineering diagnostics. I developed a dual-method anomaly detection module combining facility-specific IQR bounds with a trailing 6-hour moving Z-score to catch sudden machinery surges and off-hours energy leakage. I synthesized empirical findings to answer the university's 9 core energy questions and formulated 5 targeted conservation proposals. I also engineered the classroom demonstration script that injects a simulated surge and proves instant detection upon Power BI refresh."*
- **Key Concepts to Explain:**
  1. *How does the dual anomaly detector work?* IQR catches static extreme outliers; the rolling Z-score catches relative localized spikes ($>175\%$ of rolling baseline), isolating sudden machine starts.
  2. *What is the engineering disclaimer?* Statistical anomalies are flags requiring technician investigation, not confirmed physical equipment failures.
  3. *How was the live demonstration designed?* Injects a 425 kWh surge into the Academic Block, proves detection via `run_demo.py`, and explains how clicking Refresh in Power BI updates cards and charts.

---

## 3. Team Collaboration Matrix

All three members collaborated closely across shared integration milestones:
- **Weekly Code Reviews:** Verifying that data formats exported by Member 1 matched the schema expectations of Member 2 and the diagnostic requirements of Member 3.
- **Cross-Testing:** Member 2 and Member 3 ran Member 1's cleaning scripts; Member 1 validated Member 2's DAX measures; Member 1 and 2 participated in testing Member 3's live demonstration script.
- **Unified Viva Readiness:** Every member is capable of walking through the entire codebase, from raw simulation to Power BI visual analytics.

