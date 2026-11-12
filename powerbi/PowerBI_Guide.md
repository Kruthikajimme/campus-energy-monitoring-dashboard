# Comprehensive Microsoft Power BI Developer Guide

A developer and evaluator manual for building, configuring, and verifying the **Campus Energy Consumption Monitoring and Analytics Dashboard** in Microsoft Power BI Desktop.

---

## 1. Environment & Architecture Principles

This BI project demonstrates enterprise data modeling principles:
- **Clean Star Schema:** Normalization of dimensions (`DimBuilding`, `DimDate`, `DimTime`, `DimEnergySource`) surrounding a high-performance fact table (`FactEnergyConsumption`).
- **VertiPaq Memory Efficiency:** Fact table columns use optimized integer surrogate keys (`date_key`, `time_key`) to maximize run-length encoding (RLE) and bit-packing compression.
- **Explicit DAX Measure Architecture:** All aggregations are authored as reusable explicit DAX measures housed within a dedicated `_KeyMeasures` table.
- **Dynamic Context Transition:** Calculations utilize `CALCULATE`, `FILTER`, `ALL`, and `DATESINPERIOD` to provide filter context safety.

---

## 2. Advanced Interactivity Configurations

### 2.1 Syncing Slicers Across Pages
To provide a seamless executive experience where selecting a facility or date range on Page 1 automatically filters Pages 2, 3, 4, and 5:
1. Select the **Facility Slicer** (`DimBuilding[building_name]`).
2. Go to the ribbon: **View** -> check **Sync slicers**.
3. In the **Sync slicers** pane on the right:
   - Check the **Sync** checkbox for all 5 pages.
   - Check the **Visible** checkbox for the pages where you want the dropdown displayed.
4. Repeat for the **Date Range Slicer** and **Power Source Slicer**.

---

### 2.2 Configuring Drill-Through Functionality
To allow users to right-click any building bar or table row on **Page 1 (Executive Overview)** and drill through to **Page 2 (Building Performance Analytics)**:
1. Navigate to **Page 2 (Building Performance Analytics)**.
2. In the **Visualizations** pane, scroll down to the **Drill-through** wells.
3. Drag `DimBuilding[building_name]` into the **Add drill-through fields here** well.
4. Set **Keep all filters** to **On**.
5. Power BI automatically adds a "<- Back" button in the upper left corner of Page 2.
6. Test in Page 1: Right-click the `Computer Science Block` bar -> select **Drill through** -> **Building Performance Analytics**. Page 2 opens pre-filtered to the Computer Science Block!

---

### 2.3 Dynamic Chart Titles via DAX
To ensure visual headers dynamically reflect the active user filter selection:
1. Create Measure 5.1 in `_KeyMeasures`:
   ```dax
   Dynamic Chart Title - Daily Trend = 
   VAR SelectedBuilding = SELECTEDVALUE ( DimBuilding[building_name], "All Campus Facilities" )
   RETURN
       "Daily Energy Consumption & Peak Demand: " & SelectedBuilding
   ```
2. Select Visual 1 (Daily Trend Line Chart) on Page 1.
3. In the **Format visual** pane -> **General** tab -> expand **Title**.
4. Click the **Conditional formatting** button (`fx`) next to the **Text** input box.
5. In the dialog, set:
   - **Format style:** Field value
   - **What field should we base this on?:** `_KeyMeasures[Dynamic Chart Title - Daily Trend]`
6. Click **OK**. The title now automatically adapts as users interact with slicers.

---

### 2.4 Conditional Formatting Rules

#### A. Data Bar Formatting in Summary Tables
1. Select the table visual on Page 2 or Page 4.
2. In the visual wells, right-click `Building Consumption Percentage` -> **Conditional formatting** -> **Data bars**.
3. Configure:
   - **Positive bar color:** Emerald Green (`#10B981`).
   - **Axis color:** Light Gray (`#CBD5E1`).
   - Click **OK**.

#### B. Severity Status Colors in Anomaly Tables
1. In the Anomaly Log table on Page 4, right-click the `severity` column -> **Conditional formatting** -> **Background color**.
2. Set **Format style** to **Rules**:
   - IF value is `Critical` THEN `#FEE2E2` (Soft Red).
   - IF value is `High` THEN `#FEF3C7` (Soft Amber).
   - IF value is `Medium` THEN `#E0F2FE` (Soft Blue).
   - IF value is `Low` THEN `#F1F5F9` (Light Gray).
3. Click **OK**.

---

## 3. Five-Page Visual Verification Checklist

| Page # | Page Name | Core Visuals Verified | Primary Slicers |
|---|---|---|---|
| **Page 1** | Executive Overview | 6 KPI Cards, Daily Trend Line Chart, Building Share Bar Chart, Source Doughnut, Occupancy Scatter | Facility, Date Range, Month, Source, Day Type |
| **Page 2** | Building Performance | Highest & Lowest Consumer Callout Cards, Horizontal Building Ranking Bar Chart, Peak Demand Column Chart, Benchmarking Matrix | Facility, Month, Day Type |
| **Page 3** | Time-Based Analytics | 24h Diurnal Spline Area Chart, Monthly Stacked Bar Chart, Day/Hour Heatmap Matrix, Weekend Variance Cards | Facility, Month, Date Range |
| **Page 4** | Anomaly Monitoring | Severity KPI Cards (Critical, High, Medium, Low), Anomaly Count by Building, Timeline Spike Scatter, Detailed Diagnostic Table | Facility, Severity, Date Range |
| **Page 5** | Energy Efficiency Insights | 9 Management Q&A Insight Cards, 5 Actionable Conservation Proposal Cards, Correlation Benchmark | Facility, Power Source |

---

## 4. Classroom Demonstration Scenario Walkthrough

During your evaluation with **Prof. Sayed Faizan Qaser**:

1. **Step 1: Baseline Architecture Display**
   - Open Power BI Desktop showing Page 1.
   - Point out the 6 baseline KPIs: `1,181,593 kWh Total`, `490.4 kW Peak Demand`, `418 Anomalies`.
   - Show that Computer Science Block is the top consumer (~22.4%).
2. **Step 2: Trigger Python Surge Injection**
   - Switch to PowerShell or Terminal:
     ```powershell
     python run_demo.py
     ```
   - Explain to the professor: *"We are simulating an unexpected heavy electrical surge (425.0 kWh) in the Academic Block caused by uncoordinated chiller sequencing and machinery inrush."*
   - Show the Python terminal output: Anomaly detection re-runs, and `ANOM-0020` is caught via Rolling Z-Score with high deviation.
3. **Step 3: Power BI Live Refresh**
   - Return to Power BI Desktop.
   - Click the **Refresh** button in the Home ribbon.
   - Demonstrate the live updates:
     - Total Consumption updates to `1,181,810 kWh`.
     - Page 4 (Anomaly Monitoring) displays the newly caught Academic Block surge event with its recommended engineering action.
4. **Step 4: Reset State**
   - Run `python run_demo.py --reset` in PowerShell and refresh Power BI to restore clean baseline telemetry.

