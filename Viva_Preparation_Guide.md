# Comprehensive Viva Voce Preparation Guide

**Project Title:** Campus Energy Consumption Monitoring and Analytics Dashboard  
**Target Evaluator:** Professor Sayed Faizan Qaser  
**Purpose:** Technical mastery, conceptual depth, and high-scoring answers for engineering viva examinations.

---

## Section 1: Domain Knowledge & Electrical Engineering Fundamentals

### Q1: What is the fundamental physical difference between Energy (kWh) and Power Demand (kW)?
**Answer:**  
Power ($kW$) represents the **instantaneous rate** at which electrical energy is being consumed at any exact moment ($kW = \frac{\text{Volts} \times \text{Amperes} \times \text{Power Factor}}{1000}$). Energy ($kWh$) represents the **cumulative work performed** over a duration of time ($\text{Energy} = \int \text{Power } dt$).  
In campus utility billing, electricity charges consist of two distinct parts:
1. **Energy Consumption Charges:** Billed per total kilowatt-hour ($kWh$) consumed.
2. **Maximum Demand Charges:** Billed per peak kilowatt ($kW$ or $kVA$) registered over a short window (e.g. 15 or 30 minutes). Even a brief 30-minute spike from uncoordinated chiller startups can drastically inflate the campus demand penalty for the entire month.

---

### Q2: What is facility "Baseload" and why is it critical in campus energy analytics?
**Answer:**  
Baseload is the minimum continuous electrical power that a facility draws 24 hours a day, 7 days a week, regardless of occupancy or human activity. It powers essential infrastructure such as server racks, safety ventilation, emergency corridor lighting, and refrigeration.  
By auditing baseload between 01:00 AM and 05:00 AM on weekends and holidays, energy analysts can identify **"vampire loads"** or **after-hours leakage**—such as air conditioning units, computer lab monitors, or auditorium lighting mistakenly left operating in unoccupied buildings.

---

### Q3: What is the significance of the 24-hour Diurnal Load Profile?
**Answer:**  
The diurnal load profile plots electrical consumption as a function of the 24 hours of the day ($00:00$ to $23:00$). In our campus analytics:
- **Academic & Teaching blocks** show a bell-shaped diurnal curve peaking between 11:00 AM and 03:00 PM when classes, projectors, and HVAC chillers run concurrently.
- **Student Hostels** exhibit a bimodal, inverted diurnal curve with two distinct peaks: an early morning peak ($06:30$–$08:30$) when students prepare for classes, and an evening/night peak ($18:00$–$23:30$) during study and leisure hours.
Understanding these opposing diurnal curves allows the campus to implement load balancing and peak shaving.

---

## Section 2: Data Engineering & Cleaning Pipeline

### Q4: Why did the team choose diurnal hourly median imputation instead of mean or forward-fill for missing consumption values?
**Answer:**  
Electricity consumption is highly non-stationary and exhibits strong diurnal periodicity. 
- Using a global mean would flatten the day/night difference, artificially elevating night-time readings and under-predicting midday peaks.
- Forward-fill ($ffill$) can propagate a night-time zero into a high-demand afternoon, or vice versa, distorting trend analyses.
- The **facility-specific hourly median** computes the central tendency across all previous occurrences of that exact hour (e.g. all 14:00 readings for the Computer Science Block). Median is chosen over mean because it is inherently robust against extreme sensor spikes or transmission dropouts.

---

### Q5: How did the pipeline identify and correct negative electricity readings?
**Answer:**  
Submeters measure current using Current Transformers (CTs) clamped around line conductors. During maintenance or physical meter rewiring, technicians occasionally clamp the CT in reverse orientation, causing the meter's internal microprocessor to register a negative current vector and invert the sign of $kWh$.  
Because submeters on university consumption circuits cannot feed power back into the grid (they are consumer loads, not generators), our pipeline detects $units\_kwh < 0$ and applies $abs(units\_kwh)$ to restore correct numerical polarity while logging the occurrence in `cleaning_report.json`.

---

### Q6: How does the pipeline distinguish between a severe sensor outlier and an operational equipment surge during cleaning?
**Answer:**  
We apply the Interquartile Range (IQR) method with a high threshold multiplier ($2.5\times\text{IQR}$):
$$\text{Upper Limit} = Q_3 + (2.5 \times \text{IQR})$$
- Readings exceeding this threshold are flagged as extreme statistical outliers (often caused by sensor register overflows, such as $99,999\text{ kWh}$).
- Rather than blindly deleting these records (which would create chronological gaps in the time series), the cleaning pipeline caps them to the facility's **99th percentile** value.
- Simultaneously, our separate **Anomaly Detection Engine** preserves the original event details in `PowerBI_Anomaly_Report.csv` so facility engineers can audit the physical cause.

---

## Section 3: Microsoft Power BI Star Schema & Dimensional Modeling

### Q7: Why is a Star Schema superior to a single flat denormalized table in Microsoft Power BI?
**Answer:**  
1. **VertiPaq Storage & Compression:** Power BI's in-memory columnar engine compresses data by storing distinct column values in dictionaries and bit-packing column vectors. In a flat table, text strings like building names and dates repeat millions of times, inflating memory. In a Star Schema, repeated strings are isolated to tiny dimension tables, while the fact table stores narrow integer keys.
2. **Simplified, Unambiguous DAX:** In a Star Schema, filtering flows unidirectionally from dimension tables (1) to the fact table ($*$). Measures like `[Building Consumption Percentage]` can safely use `ALL(DimBuilding)` without unexpected filter context side-effects.
3. **Report Usability:** End-users can easily navigate dimension attributes organized logically rather than scrolling through a 30-column flat table.

---

### Q8: What are Surrogate Keys and why did we use integer keys like `20261015` and `1400`?
**Answer:**  
A surrogate key is an artificial, system-assigned identifier that has no business meaning but uniquely identifies an entity. 
We engineered:
- `date_key` as an integer (`YYYYMMDD`, e.g. `20261015` for October 15, 2026).
- `time_key` as an integer (`HH00`, e.g. `1400` for 14:00).
Integer keys take significantly less storage and allow the VertiPaq engine to perform blazing-fast integer comparisons and bit-shift hash joins rather than expensive string or floating-point datetime parsing.

---

### Q9: Why is single-directional cross-filtering strictly enforced in our data model?
**Answer:**  
Single-directional filtering means dimension tables filter the fact table, but the fact table does not filter the dimension tables. 
If bi-directional cross-filtering were enabled in a multi-table model:
- Ambiguous filter paths can arise where a filter on `DimDate` flows into `FactEnergyConsumption` and unexpectedly back-filters `DimBuilding`, leading to non-deterministic DAX results.
- Bi-directional relationships degrade query performance by forcing Power BI to scan relationship tables in both directions during visual rendering.

---

## Section 4: Advanced DAX Calculations

### Q10: Explain the DAX formula for `[Building Consumption Percentage]`.
```dax
Building Consumption Percentage = 
VAR CurrentBuildingLoad = [Total Energy Consumption (kWh)]
VAR TotalCampusLoad = 
    CALCULATE (
        [Total Energy Consumption (kWh)],
        ALL ( DimBuilding )
    )
RETURN
    DIVIDE ( CurrentBuildingLoad, TotalCampusLoad, 0 )
```
**Explanation:**  
- `CurrentBuildingLoad` evaluates `[Total Energy Consumption (kWh)]` in the active visual context (e.g. for a specific building row in a matrix or bar in a chart).
- `TotalCampusLoad` uses `CALCULATE` and the `ALL(DimBuilding)` filter modifier. `ALL(DimBuilding)` instructs the DAX engine to ignore any filter applied to the `DimBuilding` table, effectively calculating the sum across all 7 facilities.
- Crucially, any active temporal filters (e.g. selecting `Month = October 2026`) are preserved because `ALL` only removes the filter on `DimBuilding`, not on `DimDate`.
- `DIVIDE` safely handles division by zero, returning 0 if total load is empty.

---

### Q11: Explain the difference between Row Context and Filter Context in DAX.
**Answer:**  
- **Row Context:** The concept of "the current row". It exists automatically in calculated columns and inside iterator functions like `SUMX`, `AVERAGEX`, or `FILTER`. It allows DAX to inspect values across different columns in the same row.
- **Filter Context:** The set of active filters applied to the data model by visuals, slicers, report pages, and `CALCULATE` statements. It determines which rows of the underlying tables are visible to an aggregation.
- **Context Transition:** Occurs when a measure is evaluated inside a row context (or when `CALCULATE` is wrapped around an expression). `CALCULATE` automatically transitions the current row context into an equivalent filter context.

---

### Q12: How does `[Rolling 7-Day Average]` work using `DATESINPERIOD`?
```dax
Rolling 7-Day Average = 
VAR MaxSelectedDate = MAX ( DimDate[date] )
RETURN
    CALCULATE (
        [Average Daily Consumption],
        DATESINPERIOD (
            DimDate[date],
            MaxSelectedDate,
            -7,
            DAY
        )
    )
```
**Explanation:**  
- `MaxSelectedDate` retrieves the latest date currently in context on the visual's X-axis.
- `DATESINPERIOD` dynamically generates a contiguous set of dates starting from `MaxSelectedDate` and looking backward by $-7$ days.
- `CALCULATE` evaluates `[Average Daily Consumption]` across this dynamic 7-day date window, producing a moving average line that smooths out transient daily volatility.

---

## Section 5: Anomaly Detection & Operational Insights

### Q13: How does the dual-method anomaly detection engine operate?
**Answer:**  
Our engine (`src/anomaly_detection.py`) uses two complementary statistical techniques:
1. **IQR-Based Thresholding (Global Outliers):** Computes $Q_1$, $Q_3$, and $\text{IQR}$ per facility. Flags readings exceeding $Q_3 + (1.8\times\text{IQR})$ as Mild, $Q_3 + (2.5\times\text{IQR})$ as High, and $Q_3 + (3.5\times\text{IQR})$ as Critical. This identifies extreme absolute demand.
2. **Rolling Window Z-Score (Localized Surges):** Computes a moving mean $\mu_{6h}$ and standard deviation $\sigma_{6h}$ over a trailing 6-hour window. A sudden surge exceeding $175\%$ of the rolling average ($Z > 3.0$ and $>25\text{ kWh}$ delta) flags uncoordinated equipment turn-ons, even if the absolute reading is below the global daily peak.
3. **Off-Hours Rule:** Flags non-residential facilities operating at $>135\%$ of annual median load between 01:00 AM and 05:00 AM.

---

### Q14: Why must anomaly detection include an ethical engineering disclaimer?
**Answer:**  
A statistical anomaly is mathematically defined as a reading that deviates significantly from an expected statistical distribution. However, in physical facility engineering:
- An anomaly could be an intentional academic event (e.g. an overnight hackathon or an authorized 24-hour wind tunnel experiment).
- An anomaly could be a benign weather phenomenon (e.g. an extreme 42°C heatwave triggering maximum chiller cooling).
- An anomaly could be a telemetry sensor dropout rather than an electrical fault.
Therefore, presenting anomalies as "confirmed electrical faults" is technically incorrect. Our platform labels them as **"records requiring investigation"** and pairs each with a specific technician action.

---

### Q15: What are the team's top energy-saving recommendations based on the data?
**Answer:**  
1. **Load Shifting & Peak Shaving:** Stagger heavy laboratory autoclaves and batch computing outside the peak tariff window ($11:00$–$15:00$) to reduce maximum contract demand charges ($kW$).
2. **BMS Night Setbacks:** Implement automated setback timers to power down academic air handling units after 18:30 on weekdays and all weekends, reducing unoccupied baseload by $10$–$15\%$.
3. **Solar PV Expansion:** Add 120 kWp of rooftop solar collectors to directly absorb afternoon cooling peaks during high-solar hours.
4. **Hostel Solar Thermal Retrofit:** Replace residential electric resistance geysers with solar water heaters to shave morning residential surges.

---

## Section 6: Limitations and Future Roadmap

### Q16: What are the technical limitations of this project?
**Answer:**  
1. **Simulated Weather Telemetry:** Ambient temperatures are generated using diurnal trigonometric mathematical curves rather than live IoT weather station feeds.
2. **Univariate Power Metrics:** Telemetry is focused on active energy ($kWh$) and peak power ($kW$). A production-grade submeter also captures reactive power ($kVARh$), power factor ($\cos \phi$), line frequency ($Hz$), and Total Harmonic Distortion ($THD$).
3. **Batch Import vs Streaming:** In this academic architecture, Power BI operates on imported CSV datasets updated via Python batch execution rather than live DirectQuery or Azure Event Hub streaming.

