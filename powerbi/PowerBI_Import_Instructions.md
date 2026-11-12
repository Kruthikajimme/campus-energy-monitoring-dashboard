# Power BI Desktop Quick-Start Ingestion Guide (5-Minute Setup)

Follow this step-by-step checklist to load the clean Star Schema datasets into **Microsoft Power BI Desktop**.

---

## Step 1: Open Power BI Desktop & Load CSVs

1. Launch **Microsoft Power BI Desktop**.
2. Click **Home** ribbon -> **Get Data** -> **Text/CSV**.
3. Browse to the project folder:
   `c:\Users\Kruthika\OneDrive\Desktop\Campus Energy Consumption Monitoring and Analytics Dashboard\data\`
   *(or `powerbi\data\`)*
4. Select and load each of the following files:
   - `FactEnergyConsumption.csv` -> Click **Load**
   - `DimBuilding.csv` -> Click **Load**
   - `DimDate.csv` -> Click **Load**
   - `DimTime.csv` -> Click **Load**
   - `DimEnergySource.csv` -> Click **Load**
   - `PowerBI_Anomaly_Report.csv` -> Click **Load**

---

## Step 2: Establish Model Relationships (Star Schema)

1. Click the **Model View** icon (left navigation bar, third icon down).
2. Arrange `FactEnergyConsumption` in the center and position the dimension tables around it.
3. Drag and drop the following foreign keys to create the relationships:

| From Dimension (1) | To Fact / Anomaly (*) | Key Column | Cardinality | Cross Filter Direction |
|---|---|---|---|---|
| `DimBuilding[building_id]` | `FactEnergyConsumption[building_id]` | `building_id` | 1 to Many (1:*) | Single |
| `DimDate[date_key]` | `FactEnergyConsumption[date_key]` | `date_key` | 1 to Many (1:*) | Single |
| `DimTime[time_key]` | `FactEnergyConsumption[time_key]` | `time_key` | 1 to Many (1:*) | Single |
| `DimEnergySource[source_id]` | `FactEnergyConsumption[source_id]` | `source_id` | 1 to Many (1:*) | Single |
| `DimBuilding[building_id]` | `PowerBI_Anomaly_Report[building_id]` | `building_id` | 1 to Many (1:*) | Single |
| `DimDate[date_key]` | `PowerBI_Anomaly_Report[date_key]` | `date_key` | 1 to Many (1:*) | Single |

---

## Step 3: Configure "Sort by Column" Properties

To prevent alphabetical sorting on calendar months and days:
1. Click the **Table / Data View** icon (left navigation bar, second icon down).
2. Select table `DimDate`:
   - Click column header `month_name` -> In ribbon, click **Sort by column** -> select `month`.
   - Click column header `day_name` -> In ribbon, click **Sort by column** -> select `day_of_week`.
   - Click column header `month_year` -> In ribbon, click **Sort by column** -> select `date_key`.
3. Select table `DimTime`:
   - Click column header `hour_label` -> In ribbon, click **Sort by column** -> select `hour`.
   - Click column header `time_of_day` -> In ribbon, click **Sort by column** -> select `hour`.

---

## Step 4: Add DAX Measures

1. In the **Home** tab, click **Enter Data**.
2. Name the table `_KeyMeasures` and click **Load**.
3. Right-click `_KeyMeasures` in the Data pane -> click **New Measure**.
4. Copy and paste the DAX expressions from [DAX_Measures.md](DAX_Measures.md), starting with:
   ```dax
   Total Energy Consumption (kWh) = SUM(FactEnergyConsumption[units_kwh])
   ```
   ```dax
   Peak Demand (kW) = MAX(FactEnergyConsumption[peak_kw])
   ```
   ```dax
   Average Daily Consumption = DIVIDE([Total Energy Consumption (kWh)], DISTINCTCOUNT(DimDate[date]), 0)
   ```
   ```dax
   Anomaly Count = CALCULATE(COUNTROWS(FactEnergyConsumption), FactEnergyConsumption[is_anomaly] = 1)
   ```

---

## Step 5: Build Visuals & Slicers

Refer to [Dashboard_Design.md](Dashboard_Design.md) for exact visual placement and field mappings across the 5 report pages:
1. **Executive Overview**
2. **Building Performance Analytics**
3. **Time-Based Consumption Analytics**
4. **Anomaly Detection and Monitoring**
5. **Energy Efficiency Insights**

---

## Step 6: How to Refresh During Classroom Demonstration

When new readings or simulated surges are injected via `python run_demo.py`:
1. Keep Power BI Desktop open.
2. Click **Home** ribbon -> **Refresh** button.
3. Power BI re-reads the updated CSVs, and all KPI cards, anomaly tables, and chart curves immediately update!

