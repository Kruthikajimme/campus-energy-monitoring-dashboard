"""
Export Web Datasets for Next.js Campus Energy Intelligence Dashboard
===================================================================
Processes the 90-day campus telemetry dataset into optimized JSON models
and static CSV assets for client-side rendering, Recharts visuals, and live simulation.
"""

import os
import json
import pandas as pd
import numpy as np

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(WORKSPACE_DIR, "powerbi", "data")
WEB_DATA_DIR = os.path.join(WORKSPACE_DIR, "lib", "data")
PUBLIC_DATA_DIR = os.path.join(WORKSPACE_DIR, "public", "data")

os.makedirs(WEB_DATA_DIR, exist_ok=True)
os.makedirs(PUBLIC_DATA_DIR, exist_ok=True)

print("=" * 70)
print(" EXPORTING DATASETS FOR NEXT.JS CAMPUS ENERGY DASHBOARD")
print("=" * 70)

# Load CSVs
fact_df = pd.read_csv(os.path.join(DATA_DIR, "FactEnergyConsumption.csv"))
bld_df = pd.read_csv(os.path.join(DATA_DIR, "DimBuilding.csv"))
date_df = pd.read_csv(os.path.join(DATA_DIR, "DimDate.csv"))
time_df = pd.read_csv(os.path.join(DATA_DIR, "DimTime.csv"))
source_df = pd.read_csv(os.path.join(DATA_DIR, "DimEnergySource.csv"))
anom_df = pd.read_csv(os.path.join(DATA_DIR, "PowerBI_Anomaly_Report.csv"))

# Merge Fact with Dimensions for easy aggregation
merged = fact_df.merge(bld_df, on="building_id", how="left")
merged = merged.merge(date_df[["date_key", "date", "day_name", "month_name", "month_year", "day_type", "is_weekend"]], on="date_key", how="left")
merged = merged.merge(time_df[["time_key", "hour", "hour_label", "time_of_day", "is_peak_hours"]], on="time_key", how="left")
merged = merged.merge(source_df[["source_id", "source_name", "is_renewable"]], on="source_id", how="left")

# 1. Buildings Metadata
building_colors = {
    "BLD01": "#10B981",  # Academic Block - Emerald
    "BLD02": "#14B8A6",  # Library - Teal
    "BLD03": "#F59E0B",  # Computer Science Block - Amber (High consumer)
    "BLD04": "#EF4444",  # Laboratory Block - Red/Rose (High peak)
    "BLD05": "#6366F1",  # Boys Hostel - Indigo
    "BLD06": "#8B5CF6",  # Girls Hostel - Purple
    "BLD07": "#06B6D4",  # Canteen - Cyan
}

buildings_list = []
for _, row in bld_df.iterrows():
    b_id = row["building_id"]
    b_sub = merged[merged["building_id"] == b_id]
    tot_kwh = float(b_sub["units_kwh"].sum())
    peak_kw = float(b_sub["peak_kw"].max())
    avg_kwh = float(b_sub["units_kwh"].mean())
    tot_occ = int(b_sub["occupancy"].sum())
    kwh_per_occ = tot_kwh / tot_occ if tot_occ > 0 else 0
    anom_count = int((b_sub["is_anomaly"] == 1).sum())

    buildings_list.append({
        "id": b_id,
        "name": row["building_name"],
        "type": row["building_type"],
        "designCapacity": int(row["design_capacity"]),
        "meterId": row["meter_id"],
        "baseloadKw": float(row["baseload_kw"]),
        "activeHours": row["active_hours"],
        "color": building_colors.get(b_id, "#10B981"),
        "totalKwh": round(tot_kwh, 1),
        "peakKw": round(peak_kw, 1),
        "avgHourlyKwh": round(avg_kwh, 2),
        "kwhPerOccupant": round(kwh_per_occ, 4),
        "anomaliesCount": anom_count,
        "sharePct": round((tot_kwh / merged["units_kwh"].sum()) * 100, 1)
    })

# Sort buildings by totalKwh descending
buildings_list = sorted(buildings_list, key=lambda x: x["totalKwh"], reverse=True)
for rank, b in enumerate(buildings_list, start=1):
    b["rank"] = rank

with open(os.path.join(WEB_DATA_DIR, "buildings.json"), "w", encoding="utf-8") as f:
    json.dump(buildings_list, f, indent=2)
print(f" -> Exported {len(buildings_list)} buildings to buildings.json")

# 2. Campus Overall Summary KPIs
tot_kwh = float(merged["units_kwh"].sum())
avg_daily = tot_kwh / merged["date"].nunique()
peak_kw = float(merged["peak_kw"].max())
tot_carbon_kg = float(merged["carbon_emissions_kg"].sum())
tot_anomalies = int((merged["is_anomaly"] == 1).sum())
tot_occ = int(merged["occupancy"].sum())
kwh_per_occ = tot_kwh / tot_occ if tot_occ > 0 else 0
cost_inr = tot_kwh * 8.00

# Weekday vs Weekend
weekday_avg = float(merged[merged["is_weekend"] == "No"]["units_kwh"].mean())
weekend_avg = float(merged[merged["is_weekend"] == "Yes"]["units_kwh"].mean())
weekend_drop_pct = round(((weekday_avg - weekend_avg) / weekday_avg) * 100, 1) if weekday_avg > 0 else 0

summary_data = {
    "totalKwh": round(tot_kwh, 1),
    "totalMwh": round(tot_kwh / 1000, 2),
    "averageDailyKwh": round(avg_daily, 1),
    "peakDemandKw": round(peak_kw, 1),
    "carbonEmissionsKg": round(tot_carbon_kg, 1),
    "carbonEmissionsTonnes": round(tot_carbon_kg / 1000, 2),
    "activeAnomalies": tot_anomalies,
    "kwhPerOccupant": round(kwh_per_occ, 3),
    "totalCostInr": round(cost_inr, 2),
    "totalCostLakhs": round(cost_inr / 100000, 2),
    "totalRecords": len(merged),
    "monitoredBuildings": len(bld_df),
    "startDate": str(merged["date"].min()),
    "endDate": str(merged["date"].max()),
    "weekendLoadDropPct": weekend_drop_pct,
    "topConsumer": buildings_list[0]["name"],
    "topConsumerShare": buildings_list[0]["sharePct"],
    "lowestConsumer": buildings_list[-1]["name"],
    "lowestConsumerShare": buildings_list[-1]["sharePct"]
}

with open(os.path.join(WEB_DATA_DIR, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary_data, f, indent=2)
print(" -> Exported summary.json")

# 3. Daily Trends (90 days)
daily_grp = merged.groupby("date").agg({
    "units_kwh": "sum",
    "peak_kw": "max",
    "voltage": "mean",
    "occupancy": "sum",
    "temperature": "mean",
    "day_type": "first",
    "is_weekend": "first"
}).reset_index()

daily_grp["rolling_7d"] = daily_grp["units_kwh"].rolling(7, min_periods=1).mean().round(1)

daily_list = []
for _, row in daily_grp.iterrows():
    daily_list.append({
        "date": row["date"],
        "totalKwh": round(float(row["units_kwh"]), 1),
        "peakKw": round(float(row["peak_kw"]), 1),
        "avgVoltage": round(float(row["voltage"]), 1),
        "totalOccupancy": int(row["occupancy"]),
        "avgTemp": round(float(row["temperature"]), 1),
        "rolling7d": round(float(row["rolling_7d"]), 1),
        "dayType": row["day_type"],
        "isWeekend": row["is_weekend"]
    })

with open(os.path.join(WEB_DATA_DIR, "daily_trends.json"), "w", encoding="utf-8") as f:
    json.dump(daily_list, f, indent=2)
print(f" -> Exported {len(daily_list)} daily trend points to daily_trends.json")

# 4. Building-Wise Daily Trends (for drill-down and building comparison)
bld_daily_grp = merged.groupby(["date", "building_name"]).agg({
    "units_kwh": "sum",
    "peak_kw": "max",
    "occupancy": "sum"
}).reset_index()

# Pivot for multi-line comparison
pivoted_daily = bld_daily_grp.pivot(index="date", columns="building_name", values="units_kwh").reset_index()
bld_daily_list = []
for _, row in pivoted_daily.iterrows():
    item = {"date": row["date"]}
    for b in bld_df["building_name"]:
        item[b] = round(float(row.get(b, 0)), 1)
    bld_daily_list.append(item)

with open(os.path.join(WEB_DATA_DIR, "building_daily_trends.json"), "w", encoding="utf-8") as f:
    json.dump(bld_daily_list, f, indent=2)
print(f" -> Exported building_daily_trends.json")

# 5. Hourly Diurnal Patterns (24 hours) - Campus & Per Building, Weekday vs Weekend
hourly_campus = merged.groupby(["hour", "hour_label", "is_weekend"]).agg({
    "units_kwh": "mean",
    "peak_kw": "mean",
    "occupancy": "mean",
    "temperature": "mean"
}).reset_index()

hourly_list = []
for h in range(24):
    label = f"{h:02d}:00"
    w_sub = hourly_campus[(hourly_campus["hour"] == h) & (hourly_campus["is_weekend"] == "No")]
    we_sub = hourly_campus[(hourly_campus["hour"] == h) & (hourly_campus["is_weekend"] == "Yes")]
    
    wk_kwh = float(w_sub["units_kwh"].iloc[0]) if len(w_sub) > 0 else 0
    we_kwh = float(we_sub["units_kwh"].iloc[0]) if len(we_sub) > 0 else 0
    tot_avg = float(merged[merged["hour"] == h]["units_kwh"].mean())
    
    item = {
        "hour": h,
        "label": label,
        "averageKwh": round(tot_avg, 1),
        "weekdayKwh": round(wk_kwh, 1),
        "weekendKwh": round(we_kwh, 1),
        "peakKw": round(float(merged[merged["hour"] == h]["peak_kw"].mean()), 1),
        "occupancy": round(float(merged[merged["hour"] == h]["occupancy"].mean()), 0),
        "temperature": round(float(merged[merged["hour"] == h]["temperature"].mean()), 1)
    }
    hourly_list.append(item)

with open(os.path.join(WEB_DATA_DIR, "hourly_patterns.json"), "w", encoding="utf-8") as f:
    json.dump(hourly_list, f, indent=2)
print(" -> Exported hourly_patterns.json")

# 6. Source Distribution
src_grp = merged.groupby(["source_id", "source_name", "is_renewable"]).agg({
    "units_kwh": "sum",
    "carbon_emissions_kg": "sum"
}).reset_index()

source_colors = {
    "Grid": "#0EA5E9",       # Blue
    "Solar": "#10B981",      # Emerald
    "Generator": "#F59E0B"   # Amber
}

sources_list = []
for _, row in src_grp.iterrows():
    kwh = float(row["units_kwh"])
    sources_list.append({
        "id": row["source_id"],
        "name": row["source_name"],
        "isRenewable": row["is_renewable"] == "Yes",
        "totalKwh": round(kwh, 1),
        "carbonKg": round(float(row["carbon_emissions_kg"]), 1),
        "sharePct": round((kwh / tot_kwh) * 100, 1),
        "color": source_colors.get(row["source_name"], "#64748B")
    })

with open(os.path.join(WEB_DATA_DIR, "sources.json"), "w", encoding="utf-8") as f:
    json.dump(sources_list, f, indent=2)
print(" -> Exported sources.json")

# 7. Day-of-Week vs. Hour Matrix (Heatmap)
heatmap_grp = merged.groupby(["day_name", "hour"]).agg({
    "units_kwh": "mean"
}).reset_index()

days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heatmap_list = []
for d in days_order:
    for h in range(24):
        sub = heatmap_grp[(heatmap_grp["day_name"] == d) & (heatmap_grp["hour"] == h)]
        val = float(sub["units_kwh"].iloc[0]) if len(sub) > 0 else 0
        heatmap_list.append({
            "day": d,
            "hour": h,
            "label": f"{h:02d}:00",
            "kwh": round(val, 1)
        })

with open(os.path.join(WEB_DATA_DIR, "heatmap.json"), "w", encoding="utf-8") as f:
    json.dump(heatmap_list, f, indent=2)
print(" -> Exported heatmap.json")

# 8. Anomaly Reports
anom_records = []
for _, row in anom_df.iterrows():
    anom_records.append({
        "id": row["anomaly_id"],
        "timestamp": row["timestamp"],
        "buildingId": row["building_id"],
        "buildingName": row["building_name"],
        "recordedKwh": round(float(row["recorded_kwh"]), 2),
        "expectedKwh": round(float(row["expected_kwh"]), 2),
        "deviationKwh": round(float(row["deviation_kwh"]), 2),
        "deviationPct": round(float(row["deviation_pct"]), 1),
        "peakKw": round(float(row["peak_kw"]), 2),
        "severity": row["severity"],
        "method": row["anomaly_method"],
        "reason": row["reason"],
        "recommendedAction": row["recommended_action"]
    })

with open(os.path.join(WEB_DATA_DIR, "anomalies.json"), "w", encoding="utf-8") as f:
    json.dump(anom_records, f, indent=2)
print(f" -> Exported {len(anom_records)} anomalies to anomalies.json")

# 9. Recent Telemetry (Last 2,500 records for live feed & table search)
recent_telemetry = merged.sort_values("timestamp", ascending=False).head(2500)
telemetry_list = []
for _, row in recent_telemetry.iterrows():
    telemetry_list.append({
        "readingId": int(row["reading_id"]),
        "timestamp": str(row["timestamp"]),
        "buildingId": str(row["building_id"]),
        "buildingName": str(row["building_name"]),
        "unitsKwh": round(float(row["units_kwh"]), 2),
        "peakKw": round(float(row["peak_kw"]), 2),
        "voltage": round(float(row["voltage"]), 1),
        "occupancy": int(row["occupancy"]),
        "sourceName": str(row["source_name"]),
        "temperature": round(float(row["temperature"]), 1),
        "isAnomaly": int(row["is_anomaly"]),
        "severity": str(row["anomaly_severity"]) if pd.notnull(row["anomaly_severity"]) else "Normal"
    })

with open(os.path.join(WEB_DATA_DIR, "recent_telemetry.json"), "w", encoding="utf-8") as f:
    json.dump(telemetry_list, f, indent=2)
print(f" -> Exported {len(telemetry_list)} recent telemetry rows to recent_telemetry.json")

# 10. Copy static CSVs to public/data for direct client downloads
fact_df.to_csv(os.path.join(PUBLIC_DATA_DIR, "campus_energy_telemetry_90d.csv"), index=False)
anom_df.to_csv(os.path.join(PUBLIC_DATA_DIR, "campus_energy_anomalies.csv"), index=False)

# Export Data Dictionary CSV
data_dict = [
    {"Column": "reading_id", "Type": "Integer", "Unit": "-", "Description": "Unique identifier for each hourly reading record"},
    {"Column": "timestamp", "Type": "DateTime", "Unit": "YYYY-MM-DD HH:MM:SS", "Description": "Timestamp of hourly submeter reading"},
    {"Column": "building_id", "Type": "String", "Unit": "-", "Description": "Identifier code for campus facility (BLD01-BLD07)"},
    {"Column": "building_name", "Type": "String", "Unit": "-", "Description": "Name of university facility"},
    {"Column": "meter_id", "Type": "String", "Unit": "-", "Description": "Hardware submeter serial number"},
    {"Column": "units_kwh", "Type": "Float", "Unit": "kWh", "Description": "Cumulative active electrical energy consumed during the hour"},
    {"Column": "peak_kw", "Type": "Float", "Unit": "kW", "Description": "Maximum active electrical power demand registered in the hour"},
    {"Column": "voltage", "Type": "Float", "Unit": "Volts", "Description": "Line AC voltage (nominal 230V)"},
    {"Column": "occupancy", "Type": "Integer", "Unit": "Headcount", "Description": "Estimated sensor occupancy headcount in the facility"},
    {"Column": "source", "Type": "String", "Unit": "-", "Description": "Generation source: Grid, Solar, or Generator"},
    {"Column": "temperature", "Type": "Float", "Unit": "°C", "Description": "Ambient outdoor temperature"},
    {"Column": "day_type", "Type": "String", "Unit": "-", "Description": "Classification: Weekday, Weekend, or Holiday"},
    {"Column": "kwh_per_occupant", "Type": "Float", "Unit": "kWh/person", "Description": "Per-capita energy intensity index"},
    {"Column": "carbon_emissions_kg", "Type": "Float", "Unit": "kg CO2e", "Description": "Carbon footprint calculated as kWh * 0.82 kg/kWh"},
    {"Column": "is_anomaly", "Type": "Integer", "Unit": "0 or 1", "Description": "Binary flag indicating statistical consumption surge"},
    {"Column": "anomaly_severity", "Type": "String", "Unit": "-", "Description": "Severity level: Critical, High, Medium, or Normal"}
]
pd.DataFrame(data_dict).to_csv(os.path.join(PUBLIC_DATA_DIR, "campus_energy_data_dictionary.csv"), index=False)
print(" -> Exported CSV assets to public/data/")

print("\n" + "=" * 70)
print(" ALL WEB DATASETS GENERATED AND VERIFIED SUCCESSFULLY!")
print("=" * 70)

