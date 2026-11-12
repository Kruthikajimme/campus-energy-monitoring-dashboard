"""
Analytics Module for Campus Energy Consumption Monitoring
---------------------------------------------------------
Computes high-level KPIs, building comparisons, temporal aggregations (daily, monthly, hourly),
source distributions, correlation metrics, and dynamic filter queries.
"""

import numpy as np
import pandas as pd


def filter_dataset(df, building="All", start_date=None, end_date=None, month=None, source="All", day_type="All"):
    """
    Apply multi-dimensional filters to the campus energy dataframe.
    """
    filtered = df.copy()
    
    # Building filter
    if building and building != "All":
        filtered = filtered[filtered["building"] == building]
        
    # Source filter
    if source and source != "All":
        filtered = filtered[filtered["source"] == source]
        
    # Day type filter
    if day_type and day_type != "All":
        filtered = filtered[filtered["day_type"] == day_type]
        
    # Temporal filtering
    if "timestamp" in filtered.columns and len(filtered) > 0:
        filtered["dt"] = pd.to_datetime(filtered["timestamp"], errors="coerce")
        
        if month and month != "All":
            # month format YYYY-MM
            filtered = filtered[filtered["dt"].dt.strftime("%Y-%m") == month]
            
        if start_date:
            try:
                start_dt = pd.to_datetime(start_date)
                filtered = filtered[filtered["dt"] >= start_dt]
            except Exception:
                pass
                
        if end_date:
            try:
                end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                filtered = filtered[filtered["dt"] <= end_dt]
            except Exception:
                pass
                
        filtered = filtered.drop(columns=["dt"], errors="ignore")
        
    return filtered


def calculate_kpis(df, anomalies_count=0):
    """
    Calculate executive KPI cards from current dataset.
    """
    if df.empty:
        return {
            "total_consumption_kwh": 0.0,
            "buildings_monitored": 0,
            "avg_daily_consumption_kwh": 0.0,
            "peak_demand_kw": 0.0,
            "total_records": 0,
            "anomalies_detected": anomalies_count,
            "total_consumption_mwh": 0.0,
            "estimated_co2_tonnes": 0.0
        }
        
    total_kwh = float(df["units_kwh"].sum())
    total_records = int(len(df))
    buildings_count = int(df["building"].nunique())
    peak_kw = float(df["peak_kw"].max()) if "peak_kw" in df.columns else 0.0
    
    # Calculate average daily consumption
    df_temp = df.copy()
    df_temp["date"] = pd.to_datetime(df_temp["timestamp"]).dt.date
    num_days = max(1, df_temp["date"].nunique())
    avg_daily_kwh = total_kwh / num_days
    
    # Estimated grid carbon emissions (approx 0.82 kg CO2 per kWh in standard grid mix)
    estimated_co2 = (total_kwh * 0.82) / 1000.0
    
    return {
        "total_consumption_kwh": round(total_kwh, 2),
        "total_consumption_mwh": round(total_kwh / 1000.0, 2),
        "buildings_monitored": buildings_count,
        "avg_daily_consumption_kwh": round(avg_daily_kwh, 2),
        "peak_demand_kw": round(peak_kw, 2),
        "total_records": total_records,
        "anomalies_detected": int(anomalies_count),
        "estimated_co2_tonnes": round(estimated_co2, 2)
    }


def get_building_consumption_analysis(df):
    """
    Aggregates energy consumption by building.
    Returns sorted list with total kWh, percentage, average, and peak demand.
    """
    if df.empty:
        return []
        
    total_campus_kwh = df["units_kwh"].sum()
    if total_campus_kwh == 0:
        total_campus_kwh = 1.0
        
    grouped = df.groupby("building").agg(
        total_kwh=("units_kwh", "sum"),
        avg_kwh=("units_kwh", "mean"),
        max_kwh=("units_kwh", "max"),
        peak_demand_kw=("peak_kw", "max"),
        avg_occupancy=("occupancy", "mean"),
        record_count=("units_kwh", "count")
    ).reset_index()
    
    grouped["percentage"] = (grouped["total_kwh"] / total_campus_kwh) * 100.0
    grouped = grouped.sort_values(by="total_kwh", ascending=False)
    
    # Identify top consumer
    max_kwh = grouped["total_kwh"].max()
    
    result = []
    for _, row in grouped.iterrows():
        result.append({
            "building": row["building"],
            "total_kwh": round(float(row["total_kwh"]), 2),
            "percentage": round(float(row["percentage"]), 2),
            "avg_kwh": round(float(row["avg_kwh"]), 2),
            "max_kwh": round(float(row["max_kwh"]), 2),
            "peak_demand_kw": round(float(row["peak_demand_kw"]), 2),
            "avg_occupancy": int(round(row["avg_occupancy"])),
            "record_count": int(row["record_count"]),
            "is_highest": bool(row["total_kwh"] == max_kwh)
        })
        
    return result


def get_daily_consumption_trend(df):
    """
    Computes daily aggregated consumption and peak demand across the timeline.
    """
    if df.empty:
        return {"dates": [], "consumption_kwh": [], "peak_kw": [], "temperatures": []}
        
    df_temp = df.copy()
    df_temp["date"] = pd.to_datetime(df_temp["timestamp"]).dt.strftime("%Y-%m-%d")
    
    daily = df_temp.groupby("date").agg(
        total_kwh=("units_kwh", "sum"),
        peak_demand=("peak_kw", "max"),
        avg_temp=("temperature", "mean")
    ).reset_index().sort_values(by="date")
    
    return {
        "dates": daily["date"].tolist(),
        "consumption_kwh": [round(float(v), 2) for v in daily["total_kwh"]],
        "peak_kw": [round(float(v), 2) for v in daily["peak_demand"]],
        "temperatures": [round(float(v), 1) for v in daily["avg_temp"]]
    }


def get_monthly_consumption_trend(df):
    """
    Computes monthly energy consumption totals and building breakdown.
    """
    if df.empty:
        return {"months": [], "totals": [], "by_building": {}}
        
    df_temp = df.copy()
    df_temp["month"] = pd.to_datetime(df_temp["timestamp"]).dt.strftime("%Y-%m")
    
    monthly_totals = df_temp.groupby("month")["units_kwh"].sum().reset_index().sort_values(by="month")
    months = monthly_totals["month"].tolist()
    totals = [round(float(v), 2) for v in monthly_totals["units_kwh"]]
    
    # Building breakdown by month
    pivot = df_temp.pivot_table(
        index="month",
        columns="building",
        values="units_kwh",
        aggfunc="sum",
        fill_value=0.0
    )
    
    by_building = {}
    for col in pivot.columns:
        by_building[col] = [round(float(v), 2) for v in pivot[col].tolist()]
        
    return {
        "months": months,
        "totals": totals,
        "by_building": by_building
    }


def get_hourly_consumption_pattern(df):
    """
    Calculates average energy consumption by hour of the day (0 to 23).
    """
    if df.empty:
        return {"hours": list(range(24)), "avg_kwh": [0.0]*24, "by_building": {}}
        
    df_temp = df.copy()
    df_temp["hour"] = pd.to_datetime(df_temp["timestamp"]).dt.hour
    
    hourly_overall = df_temp.groupby("hour")["units_kwh"].mean().reindex(range(24), fill_value=0.0)
    
    pivot = df_temp.pivot_table(
        index="hour",
        columns="building",
        values="units_kwh",
        aggfunc="mean",
        fill_value=0.0
    ).reindex(range(24), fill_value=0.0)
    
    by_building = {}
    for col in pivot.columns:
        by_building[col] = [round(float(v), 2) for v in pivot[col].tolist()]
        
    return {
        "hours": [f"{h:02d}:00" for h in range(24)],
        "avg_kwh": [round(float(v), 2) for v in hourly_overall.tolist()],
        "by_building": by_building
    }


def get_source_distribution(df):
    """
    Calculates total energy consumption and percentage split by source.
    """
    if df.empty:
        return {"sources": [], "consumption_kwh": [], "percentages": []}
        
    grouped = df.groupby("source")["units_kwh"].sum().reset_index()
    total = grouped["units_kwh"].sum()
    if total == 0:
        total = 1.0
        
    grouped["percentage"] = (grouped["units_kwh"] / total) * 100.0
    
    return {
        "sources": grouped["source"].tolist(),
        "consumption_kwh": [round(float(v), 2) for v in grouped["units_kwh"]],
        "percentages": [round(float(v), 2) for v in grouped["percentage"]]
    }


def get_occupancy_vs_energy(df, sample_limit=500):
    """
    Generates data pairs for scatter plot: Occupancy vs Energy Consumption.
    Calculates Pearson correlation coefficient.
    """
    if df.empty:
        return {"points": [], "correlation": 0.0}
        
    valid_df = df.dropna(subset=["occupancy", "units_kwh"]).copy()
    
    if len(valid_df) > sample_limit:
        sampled = valid_df.sample(n=sample_limit, random_state=42)
    else:
        sampled = valid_df
        
    corr = 0.0
    if len(valid_df) > 1 and valid_df["occupancy"].std() > 0 and valid_df["units_kwh"].std() > 0:
        corr = float(valid_df["occupancy"].corr(valid_df["units_kwh"]))
        if np.isnan(corr):
            corr = 0.0
            
    points = []
    for _, row in sampled.iterrows():
        points.append({
            "x": int(row["occupancy"]),
            "y": round(float(row["units_kwh"]), 2),
            "building": str(row["building"]),
            "timestamp": str(row["timestamp"])
        })
        
    return {
        "points": points,
        "correlation": round(corr, 3)
    }


def get_day_type_analysis(df):
    """
    Compares average consumption between Weekday, Weekend, and Holiday.
    """
    if df.empty:
        return {}
        
    grouped = df.groupby("day_type").agg(
        avg_kwh=("units_kwh", "mean"),
        total_kwh=("units_kwh", "sum"),
        count=("units_kwh", "count")
    ).reset_index()
    
    res = {}
    for _, row in grouped.iterrows():
        res[row["day_type"]] = {
            "avg_kwh": round(float(row["avg_kwh"]), 2),
            "total_kwh": round(float(row["total_kwh"]), 2),
            "records": int(row["count"])
        }
    return res

