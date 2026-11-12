# Microsoft Power BI DAX Measures & Calculations Reference

This document provides fully validated, production-grade **Data Analysis Expressions (DAX)** for the **Campus Energy Consumption Monitoring and Analytics Dashboard**.

All measures are designed for the Star Schema data model (`FactEnergyConsumption`, `DimBuilding`, `DimDate`, `DimTime`, `DimEnergySource`).

---

## Measure Organization Architecture

In Power BI Desktop, create a dedicated disconnected calculation table named `_KeyMeasures` using:
```dax
_KeyMeasures = GENERATE({1}, ROW("Info", "Dedicated DAX Measure Container"))
```
Organize the measures into display folders:
1. `01. Core Consumption Metrics`
2. `02. Time Intelligence & Trends`
3. `03. Building Benchmarking & Rankings`
4. `04. Diagnostics & Anomaly Metrics`
5. `05. Dynamic Visual Titles & Formatting`

---

## 1. Core Consumption & Electrical Metrics

### Measure 1.1: Total Energy Consumption (kWh)
```dax
Total Energy Consumption (kWh) = 
SUM ( FactEnergyConsumption[units_kwh] )
```
* **Explanation:** Sums the cumulative hourly active electrical units (kWh) across all active filter contexts.
* **Format:** Whole number with thousand separator (`#,##0`).

---

### Measure 1.2: Total Energy Consumption (MWh)
```dax
Total Energy Consumption (MWh) = 
DIVIDE ( [Total Energy Consumption (kWh)], 1000, 0 )
```
* **Explanation:** Converts kilowatt-hours to megawatt-hours for executive high-level cards.
* **Format:** Decimal number (`#,##0.00 MWh`).

---

### Measure 1.3: Average Energy Consumption (kWh)
```dax
Average Energy Consumption = 
AVERAGE ( FactEnergyConsumption[units_kwh] )
```
* **Explanation:** Computes the arithmetic mean of hourly consumption within the filtered slice.
* **Format:** Decimal number with two decimal places (`#,##0.00`).

---

### Measure 1.4: Maximum Hourly Consumption (kWh)
```dax
Maximum Energy Consumption = 
MAX ( FactEnergyConsumption[units_kwh] )
```
* **Explanation:** Identifies the single highest hourly consumption point in the active selection.
* **Format:** Decimal number (`#,##0.00`).

---

### Measure 1.5: Minimum Hourly Consumption (kWh)
```dax
Minimum Energy Consumption = 
MIN ( FactEnergyConsumption[units_kwh] )
```
* **Explanation:** Identifies the minimum hourly baseload reading.
* **Format:** Decimal number (`#,##0.00`).

---

### Measure 1.6: Peak Electricity Demand (kW)
```dax
Peak Demand (kW) = 
MAX ( FactEnergyConsumption[peak_kw] )
```
* **Explanation:** Evaluates the highest instantaneous registered active power demand in kilowatts. Critical for monitoring maximum campus contract demand.
* **Format:** Decimal number with one decimal place (`#,##0.0 kW`).

---

### Measure 1.7: Average Daily Consumption (kWh/day)
```dax
Average Daily Consumption = 
DIVIDE (
    [Total Energy Consumption (kWh)],
    DISTINCTCOUNT ( DimDate[date] ),
    0
)
```
* **Explanation:** Divides total consumption by the count of distinct calendar days in the selection to yield normalized daily load.
* **Format:** Whole number (`#,##0 kWh/day`).

---

### Measure 1.8: Energy Consumption per Occupant
```dax
Energy Consumption per Occupant = 
DIVIDE (
    [Total Energy Consumption (kWh)],
    SUM ( FactEnergyConsumption[occupancy] ),
    0
)
```
* **Explanation:** Normalizes energy consumption against occupant headcounts (kWh per person) to enable fair comparisons across facilities of different capacities.
* **Format:** Decimal number (`0.0000 kWh/person`).

---

### Measure 1.9: Estimated Carbon Footprint (Tonnes CO2)
```dax
Estimated Carbon Footprint (Tonnes) = 
DIVIDE (
    SUM ( FactEnergyConsumption[carbon_emissions_kg] ),
    1000,
    0
)
```
* **Explanation:** Aggregates carbon emissions calculated from individual energy generation sources (Grid = 0.82 kg/kWh, Solar = 0.00 kg/kWh, Generator = 0.95 kg/kWh) and converts kilograms to metric tonnes.
* **Format:** Decimal number (`#,##0.00 Tonnes`).

---

## 2. Time-Intelligence & Temporal Trend Measures

### Measure 2.1: Previous Month Consumption
```dax
Previous Month Consumption = 
CALCULATE (
    [Total Energy Consumption (kWh)],
    DATEADD ( DimDate[date], -1, MONTH )
)
```
* **Explanation:** Shifts the filter context backward by exactly one calendar month to evaluate historical period-over-period consumption.
* **Format:** Whole number (`#,##0 kWh`).

---

### Measure 2.2: Month-over-Month Change (kWh)
```dax
Month-over-Month Change = 
VAR CurrentMonthVal = [Total Energy Consumption (kWh)]
VAR PreviousMonthVal = [Previous Month Consumption]
RETURN
    IF (
        NOT ISBLANK ( PreviousMonthVal ),
        CurrentMonthVal - PreviousMonthVal,
        BLANK ()
    )
```
* **Explanation:** Calculates the absolute kWh difference between current and prior month. Positive values indicate load increases.
* **Format:** Currency or integer with positive/negative indicators (`+#,##0;-#,##0;0`).

---

### Measure 2.3: Month-over-Month Growth Percentage
```dax
Month-over-Month Growth Percentage = 
DIVIDE (
    [Month-over-Month Change],
    [Previous Month Consumption],
    0
)
```
* **Explanation:** Computes relative growth percentage compared to the preceding month.
* **Format:** Percentage with one decimal place (`+0.0%;-0.0%;0.0%`).

---

### Measure 2.4: Year-to-Date Consumption (kWh)
```dax
Year-to-Date Consumption = 
TOTALYTD (
    [Total Energy Consumption (kWh)],
    DimDate[date]
)
```
* **Explanation:** Accumulates total electrical units consumed from the first day of the calendar year up to the current date context.
* **Format:** Whole number (`#,##0 kWh`).

---

### Measure 2.5: Running Total Consumption
```dax
Running Total Consumption = 
VAR MaxCurrentDate = MAX ( DimDate[date] )
RETURN
    CALCULATE (
        [Total Energy Consumption (kWh)],
        FILTER (
            ALL ( DimDate[date] ),
            DimDate[date] <= MaxCurrentDate
        )
    )
```
* **Explanation:** Computes continuous cumulative electricity consumed from the inception of the monitoring period, illustrating cumulative budget exhaustion.
* **Format:** Whole number (`#,##0 kWh`).

---

### Measure 2.6: Rolling 7-Day Average (kWh)
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
* **Explanation:** Smooths daily fluctuations by averaging consumption across a continuous 7-day backward window, highlighting persistent trend directions.
* **Format:** Decimal number (`#,##0.0 kWh`).

---

### Measure 2.7: Weekday Consumption (kWh)
```dax
Weekday Consumption = 
CALCULATE (
    [Total Energy Consumption (kWh)],
    DimDate[day_type] = "Weekday"
)
```
* **Explanation:** Filters energy consumption strictly to standard working days (Monday through Friday).
* **Format:** Whole number (`#,##0 kWh`).

---

### Measure 2.8: Weekend Consumption (kWh)
```dax
Weekend Consumption = 
CALCULATE (
    [Total Energy Consumption (kWh)],
    DimDate[day_type] = "Weekend"
)
```
* **Explanation:** Isolates Saturday and Sunday energy consumption.
* **Format:** Whole number (`#,##0 kWh`).

---

### Measure 2.9: Weekend-to-Weekday Variance (%)
```dax
Weekend-to-Weekday Variance (%) = 
VAR WkdayAvg = 
    CALCULATE (
        [Average Energy Consumption],
        DimDate[day_type] = "Weekday"
    )
VAR WkndAvg = 
    CALCULATE (
        [Average Energy Consumption],
        DimDate[day_type] = "Weekend"
    )
RETURN
    DIVIDE ( WkndAvg - WkdayAvg, WkdayAvg, 0 )
```
* **Explanation:** Calculates the percentage drop or shift in average hourly load on weekends. Negative values indicate weekend load reduction.
* **Format:** Percentage (`+0.0%;-0.0%`).

---

## 3. Building Benchmarking & Ranking Measures

### Measure 3.1: Building Consumption Percentage Share
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
* **Explanation:** Removes the filter on `DimBuilding` to divide the selected facility's consumption by the aggregate campus total.
* **Format:** Percentage with one decimal place (`0.0%`).

---

### Measure 3.2: Building Consumption Ranking
```dax
Building Consumption Ranking = 
RANKX (
    ALL ( DimBuilding[building_name] ),
    [Total Energy Consumption (kWh)],
    ,
    DESC,
    Dense
)
```
* **Explanation:** Dynamically assigns an ordinal rank (1 to 7) to each building based on total energy consumed, with rank 1 designating the heaviest consumer.
* **Format:** Whole number (`0`).

---

### Measure 3.3: Highest Consuming Building
```dax
Highest Consuming Building = 
VAR TopBuildingTable = 
    TOPN (
        1,
        ALL ( DimBuilding[building_name] ),
        [Total Energy Consumption (kWh)],
        DESC
    )
RETURN
    CONCATENATEX ( TopBuildingTable, DimBuilding[building_name] )
```
* **Explanation:** Evaluates the single facility with the maximum total consumption and returns its name string for KPI display cards.
* **Format:** Text string.

---

### Measure 3.4: Lowest Consuming Building
```dax
Lowest Consuming Building = 
VAR LowBuildingTable = 
    TOPN (
        1,
        ALL ( DimBuilding[building_name] ),
        [Total Energy Consumption (kWh)],
        ASC
    )
RETURN
    CONCATENATEX ( LowBuildingTable, DimBuilding[building_name] )
```
* **Explanation:** Evaluates the facility with the lowest total load and returns its name string.
* **Format:** Text string.

---

### Measure 3.5: Energy Intensity Index
```dax
Energy Intensity Index = 
VAR CurrentAvg = [Average Energy Consumption]
VAR BaselineAvg = 
    CALCULATE (
        AVERAGE ( FactEnergyConsumption[rolling_7d_kwh] )
    )
RETURN
    DIVIDE ( CurrentAvg, BaselineAvg, 1.0 )
```
* **Explanation:** Evaluates the ratio between active filtered consumption and the rolling 7-day baseline. Values $> 1.25$ indicate abnormal thermal or operational intensity.
* **Format:** Decimal number (`0.00x`).

---

## 4. Diagnostics & Anomaly Metrics

### Measure 4.1: Total Anomaly Count
```dax
Anomaly Count = 
CALCULATE (
    COUNTROWS ( FactEnergyConsumption ),
    FactEnergyConsumption[is_anomaly] = 1
)
```
* **Explanation:** Counts the total number of flagged hourly anomaly events in the active filter context.
* **Format:** Whole number (`#,##0`).

---

### Measure 4.2: Critical Anomaly Count
```dax
Critical Anomaly Count = 
CALCULATE (
    COUNTROWS ( FactEnergyConsumption ),
    FactEnergyConsumption[anomaly_severity] = "Critical"
)
```
* **Explanation:** Counts extreme statistical outliers exceeding 3.5x IQR thresholds.
* **Format:** Whole number (`#,##0`).

---

### Measure 4.3: Anomaly Event Rate (%)
```dax
Anomaly Rate (%) = 
DIVIDE (
    [Anomaly Count],
    COUNTROWS ( FactEnergyConsumption ),
    0
)
```
* **Explanation:** Percentage of total telemetry readings flagged as operational anomalies.
* **Format:** Percentage (`0.0%`).

---

## 5. Dynamic Visual Titles & Conditional Formatting

### Measure 5.1: Dynamic Daily Trend Title
```dax
Dynamic Chart Title - Daily Trend = 
VAR SelectedBuilding = SELECTEDVALUE ( DimBuilding[building_name], "All Campus Facilities" )
RETURN
    "Daily Energy Consumption & Peak Demand: " & SelectedBuilding
```
* **Explanation:** Returns a dynamic text string reflecting the user's current building selection for chart headers.

---

### Measure 5.2: KPI Card Anomaly Status Color
```dax
KPI Anomaly Color Hex = 
VAR CriticalCount = [Critical Anomaly Count]
VAR TotalAnom = [Anomaly Count]
RETURN
    SWITCH (
        TRUE (),
        CriticalCount > 0, "#EF4444",   -- Vibrant Red for Critical
        TotalAnom > 15, "#F59E0B",      -- Amber for High Alert
        "#10B981"                       -- Emerald Green for Normal
    )
```
* **Explanation:** Returns hex color codes for Power BI Conditional Formatting on card text or border accents.

