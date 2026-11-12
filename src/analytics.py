"""
Analytics Module for Campus Energy Monitoring
---------------------------------------------
Performs aggregations, temporal grouping (daily, weekly, monthly, hourly),
building rankings, per-capita intensity, weekday vs weekend comparisons,
and exports tabular analytical summary reports.
"""

import os
import numpy as np
import pandas as pd

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def compute_comprehensive_analytics(df, export_reports=True):
    """
    Calculate summary statistics and temporal aggregations across the energy dataset.
    
    Parameters:
        df (pd.DataFrame): Enriched or cleaned energy dataframe.
        export_reports (bool): Whether to export CSV summary tables to reports/
        
    Returns:
        dict: Full statistical aggregations and analytics tables.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_calc = df.copy()
    
    if "date" not in df_calc.columns:
        df_calc["dt"] = pd.to_datetime(df_calc["timestamp"])
        df_calc["date"] = df_calc["dt"].dt.date
        df_calc["month_year"] = df_calc["dt"].dt.strftime("%Y-%m")
        df_calc["week"] = df_calc["dt"].dt.isocalendar().week
        df_calc["hour"] = df_calc["dt"].dt.hour
        df_calc["is_weekend"] = df_calc["dt"].dt.dayofweek >= 5
        
    total_kwh = float(df_calc["units_kwh"].sum())
    total_records = len(df_calc)
    num_buildings = df_calc["building"].nunique()
    
    # 1. Overall Campus KPIs
    campus_kpis = {
        "total_consumption_kwh": round(total_kwh, 2),
        "total_consumption_mwh": round(total_kwh / 1000.0, 2),
        "average_hourly_kwh": round(float(df_calc["units_kwh"].mean()), 2),
        "max_hourly_kwh": round(float(df_calc["units_kwh"].max()), 2),
        "min_hourly_kwh": round(float(df_calc["units_kwh"].min()), 2),
        "peak_demand_kw": round(float(df_calc["peak_kw"].max()), 2),
        "total_records": total_records,
        "monitored_buildings": num_buildings,
        "total_days": int(df_calc["date"].nunique()),
        "average_daily_kwh": round(total_kwh / max(1, df_calc["date"].nunique()), 2)
    }
    
    # 2. Building-wise Performance & Ranking
    b_grouped = df_calc.groupby("building").agg(
        total_kwh=("units_kwh", "sum"),
        avg_hourly_kwh=("units_kwh", "mean"),
        max_hourly_kwh=("units_kwh", "max"),
        min_hourly_kwh=("units_kwh", "min"),
        peak_demand_kw=("peak_kw", "max"),
        avg_occupancy=("occupancy", "mean"),
        record_count=("units_kwh", "count")
    ).reset_index()
    
    b_grouped["percentage_share"] = ((b_grouped["total_kwh"] / max(1.0, total_kwh)) * 100.0).round(2)
    b_grouped["avg_occupancy"] = b_grouped["avg_occupancy"].round(1)
    b_grouped["kwh_per_occupant"] = (b_grouped["total_kwh"] / (b_grouped["avg_occupancy"] * b_grouped["record_count"]).clip(lower=1.0)).round(4)
    b_grouped = b_grouped.sort_values(by="total_kwh", ascending=False).reset_index(drop=True)
    b_grouped["rank"] = np.arange(1, len(b_grouped) + 1)
    
    # Round numerical columns
    b_grouped["total_kwh"] = b_grouped["total_kwh"].round(2)
    b_grouped["avg_hourly_kwh"] = b_grouped["avg_hourly_kwh"].round(2)
    b_grouped["max_hourly_kwh"] = b_grouped["max_hourly_kwh"].round(2)
    b_grouped["min_hourly_kwh"] = b_grouped["min_hourly_kwh"].round(2)
    b_grouped["peak_demand_kw"] = b_grouped["peak_demand_kw"].round(2)
    
    # 3. Daily Consumption Trend
    daily_grouped = df_calc.groupby("date").agg(
        total_kwh=("units_kwh", "sum"),
        avg_hourly_kwh=("units_kwh", "mean"),
        peak_demand_kw=("peak_kw", "max"),
        avg_temperature=("temperature", "mean"),
        avg_occupancy=("occupancy", "mean")
    ).reset_index().sort_values(by="date").reset_index(drop=True)
    
    daily_grouped["rolling_7d_kwh"] = daily_grouped["total_kwh"].rolling(window=7, min_periods=1).mean().round(2)
    daily_grouped["total_kwh"] = daily_grouped["total_kwh"].round(2)
    daily_grouped["avg_hourly_kwh"] = daily_grouped["avg_hourly_kwh"].round(2)
    daily_grouped["peak_demand_kw"] = daily_grouped["peak_demand_kw"].round(2)
    daily_grouped["avg_temperature"] = daily_grouped["avg_temperature"].round(1)
    daily_grouped["avg_occupancy"] = daily_grouped["avg_occupancy"].round(0).astype(int)
    
    # 4. Monthly Consumption & Matrix
    monthly_grouped = df_calc.groupby("month_year").agg(
        total_kwh=("units_kwh", "sum"),
        avg_hourly_kwh=("units_kwh", "mean"),
        peak_demand_kw=("peak_kw", "max"),
        reading_count=("units_kwh", "count")
    ).reset_index().sort_values(by="month_year").reset_index(drop=True)
    
    monthly_grouped["total_kwh"] = monthly_grouped["total_kwh"].round(2)
    monthly_grouped["avg_hourly_kwh"] = monthly_grouped["avg_hourly_kwh"].round(2)
    monthly_grouped["peak_demand_kw"] = monthly_grouped["peak_demand_kw"].round(2)
    
    # Month-over-Month calculation
    monthly_grouped["prev_month_kwh"] = monthly_grouped["total_kwh"].shift(1)
    monthly_grouped["mom_growth_kwh"] = (monthly_grouped["total_kwh"] - monthly_grouped["prev_month_kwh"]).round(2)
    monthly_grouped["mom_growth_pct"] = ((monthly_grouped["mom_growth_kwh"] / monthly_grouped["prev_month_kwh"].clip(lower=1.0)) * 100.0).round(2)
    
    # 5. Hourly Load Curve (0 to 23)
    hourly_grouped = df_calc.groupby("hour").agg(
        avg_hourly_kwh=("units_kwh", "mean"),
        total_kwh=("units_kwh", "sum"),
        peak_kw=("peak_kw", "max")
    ).reindex(range(24), fill_value=0.0).reset_index()
    
    hourly_grouped["avg_hourly_kwh"] = hourly_grouped["avg_hourly_kwh"].round(2)
    hourly_grouped["total_kwh"] = hourly_grouped["total_kwh"].round(2)
    hourly_grouped["peak_kw"] = hourly_grouped["peak_kw"].round(2)
    
    # 6. Weekday vs Weekend Comparison
    day_type_summary = df_calc.groupby("day_type").agg(
        total_kwh=("units_kwh", "sum"),
        avg_hourly_kwh=("units_kwh", "mean"),
        reading_count=("units_kwh", "count")
    ).reset_index()
    day_type_summary["total_kwh"] = day_type_summary["total_kwh"].round(2)
    day_type_summary["avg_hourly_kwh"] = day_type_summary["avg_hourly_kwh"].round(2)
    
    # 7. Occupancy Correlation
    corr = 0.0
    if len(df_calc) > 1 and df_calc["occupancy"].std() > 0 and df_calc["units_kwh"].std() > 0:
        corr = float(df_calc["occupancy"].corr(df_calc["units_kwh"]))
        if np.isnan(corr):
            corr = 0.0
            
    # Export reports if requested
    if export_reports:
        b_grouped.to_csv(os.path.join(REPORTS_DIR, "building_analysis.csv"), index=False)
        daily_grouped.to_csv(os.path.join(REPORTS_DIR, "daily_analysis.csv"), index=False)
        monthly_grouped.to_csv(os.path.join(REPORTS_DIR, "monthly_analysis.csv"), index=False)
        
    return {
        "kpis": campus_kpis,
        "building_analysis": b_grouped.to_dict(orient="records"),
        "building_analysis_df": b_grouped,
        "daily_analysis": daily_grouped.to_dict(orient="records"),
        "daily_analysis_df": daily_grouped,
        "monthly_analysis": monthly_grouped.to_dict(orient="records"),
        "monthly_analysis_df": monthly_grouped,
        "hourly_analysis": hourly_grouped.to_dict(orient="records"),
        "hourly_analysis_df": hourly_grouped,
        "day_type_analysis": day_type_summary.to_dict(orient="records"),
        "occupancy_correlation": round(corr, 3)
    }

