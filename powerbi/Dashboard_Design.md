# Microsoft Power BI 5-Page Dashboard Visual Architecture

This document provides exact visual design specifications, component coordinates, field bindings, visual formatting, and color palettes for the **Campus Energy Consumption Monitoring and Analytics Dashboard**.

---

## 1. Visual Theme & Color Palette

The dashboard utilizes a modern **Executive Dark Navy & Clean White** theme with **Emerald Green Highlights**:

| Element | Hex Code | Purpose / Usage |
|---|---|---|
| **Canvas Background** | `#F8FAFC` | Clean, subtle off-white canvas backdrop |
| **Header Banner / Primary** | `#0F172A` | Deep Navy Blue for top header bar and page titles |
| **Card / Visual Container** | `#FFFFFF` | Crisp white cards with 1px border (`#E2E8F0`) and subtle drop shadow |
| **Emerald Accent (Primary)** | `#10B981` | Energy savings, normal status, primary data series |
| **Cyan Accent (Secondary)**| `#0EA5E9` | Peak demand, occupancy indicators, complementary trends |
| **Amber Accent (Warning)** | `#F59E0B` | Highest consuming facility callout, medium severity alerts |
| **Red Accent (Critical)** | `#EF4444` | Critical severity anomalies, extreme peak demand spikes |
| **Text Primary** | `#1E293B` | High contrast slate navy for visual titles and data values |
| **Text Muted** | `#64748B` | Secondary axis labels, subtitles, units |

* **Canvas Dimensions:** 16:9 Widescreen (1280 x 720 px or 1920 x 1080 px).
* **Grid Spacing:** 12 px margin between visual cards.

---

## 2. Common Top Navigation & Slicer Bar (Present on all pages)

Across the top of each page (Y: 0 to 90 px):
- **Title Block (Left, X: 15, Y: 15, W: 350, H: 65):**
  - Title: `CAMPUS ENERGY IQ` (Bold, 16 pt, `#0F172A`)
  - Subtitle: `University Facility Electricity Monitoring & Diagnostics` (9 pt, `#64748B`)
- **Slicers (Right, X: 380, Y: 15, W: 885, H: 65):**
  1. *Facility Slicer:* Dropdown from `DimBuilding[building_name]` (Multi-select with Select All).
  2. *Date Range Slicer:* Between-slider from `DimDate[date]`.
  3. *Month Slicer:* Dropdown from `DimDate[month_year]` (Sorted by `date_key`).
  4. *Power Source Slicer:* Dropdown from `DimEnergySource[source_name]` (Grid, Solar, Generator).
  5. *Day Type Slicer:* Tile buttons from `DimDate[day_type]` (Weekday, Weekend, Holiday).

---

## 3. Page 1: Executive Overview

**Objective:** High-level campus energy consumption, peak demand, diurnal trends, and top consumer callouts for senior university administrators.

```
+----------------------------------------------------------------------------------------------------+
| TOP SLICER BAR: Facility | Date Range Slider | Month | Power Source | Day Type                     |
+----------------------------------------------------------------------------------------------------+
| [ KPI 1 ]          [ KPI 2 ]          [ KPI 3 ]          [ KPI 4 ]          [ KPI 5 ]  [ KPI 6 ]   |
| Total Energy       Daily Average      Peak Demand        Monitored Bldgs    Total Rows Anomaly Evt |
| 1,181,593 kWh      13,128 kWh/day     490.4 kW           7 Facilities       15,112     418 Alerts  |
+----------------------------------------------------------------------------------------------------+
| [ VISUAL 1: LINE CHART ]                           | [ VISUAL 2: BAR CHART ]                       |
| Daily Campus Electricity Trend & Peak Demand       | Cumulative Energy by Facility (Top in Amber)  |
| X: DimDate[date]                                   | X: DimBuilding[building_name]                 |
| Y: [Total Energy Consumption (kWh)], [Peak Demand] | Y: [Total Energy Consumption (kWh)]           |
+----------------------------------------------------+-----------------------------------------------+
| [ VISUAL 3: DOUGHNUT CHART ]                       | [ VISUAL 4: SCATTER CHART ]                   |
| Power Source Share (Grid vs Solar vs Gen)          | Occupancy Headcount vs Electricity Load       |
| Legend: DimEnergySource[source_name]               | X: Fact[occupancy], Y: Fact[units_kwh]        |
| Values: [Total Energy Consumption (kWh)]           | Trendline enabled: r = 0.628                  |
+----------------------------------------------------------------------------------------------------+
```

### Visual Specifications:
1. **6 KPI Metric Cards (Y: 100, H: 85):**
   - Card 1: `[Total Energy Consumption (kWh)]` (Accent top border `#10B981`)
   - Card 2: `[Average Daily Consumption]` (Accent top border `#0EA5E9`)
   - Card 3: `[Peak Demand (kW)]` (Accent top border `#F59E0B`)
   - Card 4: `[Number of Buildings]` (`DISTINCTCOUNT(DimBuilding[building_id])`)
   - Card 5: `[Total Telemetry Records]` (`COUNTROWS(FactEnergyConsumption)`)
   - Card 6: `[Anomaly Count]` (Font color dynamic via `[KPI Anomaly Color Hex]`)
2. **Visual 1 (Line Chart - Daily Trend, W: 610, H: 260):**
   - X-Axis: `DimDate[date]`
   - Y-Axis: `[Total Energy Consumption (kWh)]` (Emerald `#10B981`, area fill opacity 20%)
   - Secondary Y-Axis: `[Peak Demand (kW)]` (Dashed Cyan `#0EA5E9`)
3. **Visual 2 (Clustered Bar Chart - Building Share, W: 610, H: 260):**
   - X-Axis: `DimBuilding[building_name]`
   - Y-Axis: `[Total Energy Consumption (kWh)]`
   - Data Labels: Enabled (`Percentage of Total`)
   - Conditional Color: IF Rank = 1 THEN Amber `#F59E0B` ELSE Emerald `#10B981`.
4. **Visual 3 (Doughnut Chart - Source Split, W: 400, H: 240):**
   - Legend: `DimEnergySource[source_name]`
   - Values: `[Total Energy Consumption (kWh)]`
   - Slices: Grid (`#0EA5E9`), Solar (`#10B981`), Generator (`#F59E0B`). Cutout: 65%.
5. **Visual 4 (Scatter Plot - Occupancy vs Load, W: 820, H: 240):**
   - X-Axis: `FactEnergyConsumption[occupancy]`
   - Y-Axis: `FactEnergyConsumption[units_kwh]`
   - Details: `FactEnergyConsumption[reading_id]`
   - Legend: `DimBuilding[building_name]`
   - Analytics Pane: Add **Trend Line** (Linear, correlation $r = 0.628$).

---

## 4. Page 2: Building Performance Analytics

**Objective:** Detailed comparative benchmarking, peak demand intensity, and per-capita electrical efficiency across all seven campus facilities.

### Layout & Visuals:
1. **Highlight Banners (Top Row, H: 90):**
   - Card Left: `#1 Highest Consuming Facility: Computer Science Block (22.4% Campus Share)`
   - Card Right: `Most Economical Facility: Canteen (7.2% Campus Share)`
2. **Horizontal Bar Chart: Building Energy Ranking (W: 610, H: 290):**
   - Y-Axis: `DimBuilding[building_name]` (Sorted by `[Total Energy Consumption (kWh)]` descending)
   - X-Axis: `[Total Energy Consumption (kWh)]`
   - Tooltips: `[Building Consumption Percentage]`, `[Peak Demand (kW)]`, `[Average Energy Consumption]`.
3. **Column Chart: Peak Power Demand by Facility (kW) (W: 610, H: 290):**
   - X-Axis: `DimBuilding[building_name]`
   - Y-Axis: `[Peak Demand (kW)]`
   - Data Color: Red / Coral (`#EF4444`) to emphasize electrical capacity limits.
4. **Comprehensive Benchmarking Matrix Table (Full Width, H: 210):**
   - Columns: `DimBuilding[building_name]`, `DimBuilding[building_type]`, `[Building Consumption Ranking]`, `[Total Energy Consumption (kWh)]`, `[Building Consumption Percentage]`, `[Average Energy Consumption]`, `[Peak Demand (kW)]`, `[Energy Consumption per Occupant]`, `[Anomaly Count]`.
   - Conditional Formatting:
     - `[Building Consumption Percentage]`: Data Bars (Emerald).
     - `[Peak Demand (kW)]`: Color scale (White to Red).

---

## 5. Page 3: Time-Based Consumption Analytics

**Objective:** Unpack temporal load dynamics across hours, days, weeks, and calendar months; isolate peak tariff windows and quantify weekend baseload drops.

### Layout & Visuals:
1. **24-Hour Diurnal Profile Area Chart (W: 610, H: 280):**
   - X-Axis: `DimTime[hour_label]` (Sorted by `DimTime[hour]`)
   - Y-Axis: `[Average Energy Consumption]`
   - Visual Type: Spline Area Chart (Purple `#8B5CF6`)
   - Reference Line: Vertical band highlighting Peak Tariff Window (**11:00 to 15:00**).
2. **Monthly Stacked Column Chart (W: 610, H: 280):**
   - X-Axis: `DimDate[month_year]` (Sorted by `date_key`)
   - Y-Axis: `[Total Energy Consumption (kWh)]`
   - Legend: `DimBuilding[building_name]`
   - Data Labels: Total label enabled on top of stack.
3. **Diurnal Hourly Matrix / Heatmap (W: 800, H: 230):**
   - Rows: `DimDate[day_name]` (Sorted by `day_of_week`: Monday through Sunday)
   - Columns: `DimTime[hour_label]` (00:00 to 23:00)
   - Values: `[Average Energy Consumption]`
   - Conditional Formatting: Background color scale (Light Blue to Dark Navy to Amber). Clearly isolates working hours from idle weekend nights.
4. **Weekday vs Weekend Comparative Metric Cards (W: 420, H: 230):**
   - Card 1: `Weekday Average: 63.8 kWh/h`
   - Card 2: `Weekend Average: 45.6 kWh/h`
   - Card 3: `Weekend Load Reduction: -18.3%` (Green badge)

---

## 6. Page 4: Anomaly Detection and Monitoring

**Objective:** Audit statistical deviations, detect unexpected spikes, and guide facility technicians with prioritized action recommendations.

### Layout & Visuals:
1. **Severity Status Metric Cards (Top Row, H: 85):**
   - Card 1: `Total Anomalies: 418 Events` (Gray `#64748B`)
   - Card 2: `Critical Severity: 0 Events` (Normal) (Red `#EF4444`)
   - Card 3: `High Severity: 4 Events` (Amber `#F59E0B`)
   - Card 4: `Medium Severity: 414 Events` (Cyan `#0EA5E9`)
2. **Clustered Bar Chart: Anomaly Count by Facility (W: 550, H: 270):**
   - Y-Axis: `DimBuilding[building_name]`
   - X-Axis: `[Anomaly Count]`
   - Color: Dynamic by severity proportion.
3. **Scatter / Timeline Spike Analysis (W: 670, H: 270):**
   - X-Axis: `PowerBI_Anomaly_Report[timestamp]`
   - Y-Axis: `PowerBI_Anomaly_Report[recorded_kwh]`
   - Legend / Color: `PowerBI_Anomaly_Report[severity]`
4. **Detailed Anomaly Investigation Action Log Table (Full Width, H: 240):**
   - Columns: `timestamp`, `building_name`, `recorded_kwh`, `expected_kwh`, `deviation_pct` (`+0.0%`), `peak_kw`, `severity`, `anomaly_method`, `reason`, `recommended_action`.
   - Conditional Formatting:
     - `severity`: Background color (Critical = `#FEE2E2`, High = `#FEF3C7`, Medium = `#E0F2FE`).

---

## 7. Page 5: Energy Efficiency Insights

**Objective:** Present data-driven empirical findings, answer the 9 core management queries, and lay out actionable energy conservation measures.

### Layout & Visuals:
1. **Executive Answers & Empirical Findings Card Deck (Left Column, W: 600, H: 580):**
   - Scrollable or card list displaying answers to the 9 management questions:
     1. *Top Consumer:* Computer Science Block (continuous IT/cooling).
     2. *Lowest Consumer:* Canteen (periodic dining usage).
     3. *Peak Window:* 13:00 to 16:00 (midday academic & HVAC overlap).
     4. *Weekend Shift:* -18.3% overall campus load drop.
     5. *Occupancy r:* Moderate correlation ($r = 0.628$).
     6. *Spike Drivers:* Motor inrush currents and chiller sequencing.
2. **Energy Conservation Proposals Table (Right Column, W: 620, H: 580):**
   - Structured visual cards displaying the 5 concrete initiatives:
     - **REC-01:** Stagger heavy lab autoclaves & batch compute outside 11:00–15:00 peak tariff window.
     - **REC-02:** Deploy automated BMS night setbacks in Academic & Library blocks after 18:30.
     - **REC-03:** Install solar thermal water heating & PIR motion sensors in Boys & Girls Hostels.
     - **REC-04:** Expand rooftop solar PV by 120 kWp to absorb midday cooling demand.
     - **REC-05:** Targeted power quality audit on high-anomaly distribution boards.

