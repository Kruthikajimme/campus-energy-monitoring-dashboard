"""
Automated Energy Insights & Recommendations Module
--------------------------------------------------
Analyzes energy consumption metrics across campus facilities to derive actionable findings,
cost/carbon optimization opportunities, and operational recommendations.

DISCLAIMER: Recommendations are automated analytical suggestions based on statistical
patterns and should be reviewed alongside electrical engineering surveys before capital expenditure.
"""

import numpy as np
import pandas as pd


def generate_campus_insights(df, anomalies=None):
    """
    Generate dynamic campus insights and operational recommendations.
    
    Parameters:
        df (pd.DataFrame): Current filtered energy consumption dataset.
        anomalies (list): Detected anomalies list.
        
    Returns:
        dict: Structured insights, metrics, and actionable recommendations.
    """
    if df.empty:
        return {
            "key_metrics": {},
            "findings": [],
            "recommendations": [],
            "building_efficiency_rankings": []
        }
        
    total_kwh = float(df["units_kwh"].sum())
    total_days = max(1, pd.to_datetime(df["timestamp"]).dt.date.nunique())
    
    # 1. Building Consumption Rankings
    b_totals = df.groupby("building")["units_kwh"].sum().sort_values(ascending=False)
    b_means = df.groupby("building")["units_kwh"].mean()
    b_peaks = df.groupby("building")["peak_kw"].max()
    
    highest_building = b_totals.index[0]
    highest_kwh = float(b_totals.iloc[0])
    highest_pct = round((highest_kwh / max(1.0, total_kwh)) * 100.0, 1)
    
    lowest_building = b_totals.index[-1]
    lowest_kwh = float(b_totals.iloc[-1])
    lowest_pct = round((lowest_kwh / max(1.0, total_kwh)) * 100.0, 1)
    
    # 2. Hourly Peak Usage Analysis
    df_temp = df.copy()
    df_temp["hour"] = pd.to_datetime(df_temp["timestamp"]).dt.hour
    hourly_avg = df_temp.groupby("hour")["units_kwh"].mean()
    peak_hour = int(hourly_avg.idxmax())
    peak_hour_val = round(float(hourly_avg.max()), 2)
    lowest_hour = int(hourly_avg.idxmin())
    lowest_hour_val = round(float(hourly_avg.min()), 2)
    
    # Peak time window identification (top 4 consecutive hours)
    rolling_4h = hourly_avg.rolling(window=4).mean()
    best_4h_end = int(rolling_4h.idxmax())
    peak_window_str = f"{(best_4h_end - 3):02d}:00 to {best_4h_end:02d}:00"
    
    # 3. Day Type Variance (Weekday vs Weekend)
    day_type_means = df.groupby("day_type")["units_kwh"].mean()
    weekday_mean = float(day_type_means.get("Weekday", 0.0))
    weekend_mean = float(day_type_means.get("Weekend", 0.0))
    
    if weekday_mean > 0:
        weekend_drop_pct = round(((weekday_mean - weekend_mean) / weekday_mean) * 100.0, 1)
    else:
        weekend_drop_pct = 0.0
        
    # 4. Anomaly Counts by Building
    anomaly_counts = {}
    if anomalies:
        for a in anomalies:
            b = a["building"]
            anomaly_counts[b] = anomaly_counts.get(b, 0) + 1
            
    top_anomaly_building = None
    top_anomaly_count = 0
    if anomaly_counts:
        sorted_anom = sorted(anomaly_counts.items(), key=lambda x: x[1], reverse=True)
        top_anomaly_building = sorted_anom[0][0]
        top_anomaly_count = sorted_anom[0][1]
        
    # 5. Solar Share & Clean Energy
    source_sums = df.groupby("source")["units_kwh"].sum()
    solar_kwh = float(source_sums.get("Solar", 0.0))
    solar_pct = round((solar_kwh / max(1.0, total_kwh)) * 100.0, 1)
    grid_kwh = float(source_sums.get("Grid", 0.0))
    grid_pct = round((grid_kwh / max(1.0, total_kwh)) * 100.0, 1)
    
    # Build Findings List
    findings = [
        {
            "category": "Top Consumer",
            "title": f"Primary Campus Energy Driver: {highest_building}",
            "summary": f"{highest_building} accounts for {highest_kwh:,.1f} kWh ({highest_pct}% of total campus electricity).",
            "icon": "zap",
            "severity": "high" if highest_pct > 25 else "medium"
        },
        {
            "category": "Lowest Consumer",
            "title": f"Most Economical Facility: {lowest_building}",
            "summary": f"{lowest_building} consumed {lowest_kwh:,.1f} kWh, representing only {lowest_pct}% of total campus load.",
            "icon": "award",
            "severity": "low"
        },
        {
            "category": "Diurnal Peak Demand",
            "title": f"Peak Demand Window: {peak_window_str}",
            "summary": f"Campus electricity demand hits its peak at {peak_hour:02d}:00 with an average hourly load of {peak_hour_val} kWh, driven by simultaneous classroom, laboratory, and HVAC operation.",
            "icon": "clock",
            "severity": "medium"
        },
        {
            "category": "Weekday vs Weekend Variance",
            "title": f"Weekend Load Reduction: {weekend_drop_pct}%",
            "summary": f"Average hourly consumption decreases from {weekday_mean:.1f} kWh on weekdays to {weekend_mean:.1f} kWh on weekends.",
            "icon": "calendar",
            "severity": "low" if weekend_drop_pct > 30 else "medium"
        }
    ]
    
    if top_anomaly_building:
        findings.append({
            "category": "Anomaly Hotspot",
            "title": f"Frequent Anomaly Site: {top_anomaly_building}",
            "summary": f"{top_anomaly_building} recorded {top_anomaly_count} statistical consumption deviations, indicating potential baseload leakage or equipment cycling irregularities.",
            "icon": "alert-triangle",
            "severity": "high"
        })
        
    findings.append({
        "category": "Renewable Integration",
        "title": f"Rooftop Solar Penetration: {solar_pct}%",
        "summary": f"Solar energy provided {solar_kwh:,.1f} kWh of clean power, offsetting approx {round(solar_kwh * 0.82 / 1000.0, 2)} tonnes of CO2 emissions.",
        "icon": "sun",
        "severity": "low"
    })
    
    # Build Tailored Recommendations
    recommendations = []
    
    # Rec 1: Peak Shaving & Load Shifting
    recommendations.append({
        "id": "REC-01",
        "category": "Peak Shaving",
        "title": "Implement Staggered Laboratory & Workshop Equipment Schedules",
        "target_facility": "Laboratory Block & Computer Science Block",
        "suggested_action": f"Stagger heavy electrical machinery and large batch simulations outside the campus peak demand window ({peak_window_str}). Shift non-critical loads to off-peak morning or evening hours.",
        "expected_benefit": "Reduces maximum contract demand charges and prevents peak tariff penalties on utility billing.",
        "effort": "Low to Moderate (Operational schedule adjustment)"
    })
    
    # Rec 2: HVAC & Basal Cooling Automation
    recommendations.append({
        "id": "REC-02",
        "category": "HVAC Optimization",
        "title": f"Deploy Smart Thermostats and Night Setback Controls in {highest_building}",
        "target_facility": highest_building,
        "suggested_action": "Install programmable timer setbacks to ensure air conditioning and ventilation systems automatically power down or idle after 18:30 on weekdays and all weekends.",
        "expected_benefit": "Estimated 8% to 15% reduction in academic block baseload during unoccupied hours.",
        "effort": "Medium (IoT thermostat retrofits)"
    })
    
    # Rec 3: Hostel Water Heating and Lighting
    recommendations.append({
        "id": "REC-03",
        "category": "Residential Efficiency",
        "title": "Solar Thermal Water Heating & Corridor Occupancy Sensors",
        "target_facility": "Boys Hostel & Girls Hostel",
        "suggested_action": "Replace aging electric geysers with roof-mounted centralized solar thermal collectors. Retrofit hallway and restroom fixtures with passive infrared (PIR) motion sensors.",
        "expected_benefit": "Cuts residential morning and evening peak loads by up to 20% while extending lighting lifespans.",
        "effort": "Moderate to High (Capital retrofit with high long-term ROI)"
    })
    
    # Rec 4: Solar Expansion
    if solar_pct < 20.0:
        recommendations.append({
            "id": "REC-04",
            "category": "Renewable Energy",
            "title": "Expand Rooftop Photovoltaic Capacity across Library & Academic Blocks",
            "target_facility": "Library & Academic Block Roofs",
            "suggested_action": "Campus solar currently supplies only " + str(solar_pct) + "% of total power. Expanding rooftop solar by 100 kWp would significantly absorb midday air-conditioning spikes.",
            "expected_benefit": "Increases campus renewable share toward 25-30% and reduces reliance on diesel generators.",
            "effort": "High (Capital investment)"
        })
        
    # Rec 5: Anomaly Investigation
    if top_anomaly_building:
        recommendations.append({
            "id": "REC-05",
            "category": "Submetering & Maintenance",
            "title": f"Schedule Comprehensive Sub-circuit Energy Audit for {top_anomaly_building}",
            "target_facility": top_anomaly_building,
            "suggested_action": f"Deploy portable power quality loggers on {top_anomaly_building} sub-switchboards to isolate the root cause behind {top_anomaly_count} detected consumption spikes.",
            "expected_benefit": "Identifies deteriorating motor insulation, unbalanced phase loads, or unintended overnight equipment operation.",
            "effort": "Low (Preventative maintenance audit)"
        })
        
    # Efficiency Rankings Table
    rankings = []
    for b_name in b_totals.index:
        kwh = float(b_totals[b_name])
        pct = round((kwh / max(1.0, total_kwh)) * 100.0, 1)
        peak = round(float(b_peaks[b_name]), 1)
        mean_hr = round(float(b_means[b_name]), 1)
        
        # Energy efficiency rating based on intensity
        if pct < 10.0:
            rating = "A (Highly Efficient)"
            badge_class = "success"
        elif pct < 18.0:
            rating = "B (Moderate)"
            badge_class = "info"
        else:
            rating = "C (High Energy Intensity)"
            badge_class = "warning"
            
        rankings.append({
            "building": b_name,
            "total_kwh": round(kwh, 2),
            "percentage": pct,
            "hourly_mean_kwh": mean_hr,
            "peak_kw": peak,
            "anomalies": anomaly_counts.get(b_name, 0),
            "rating": rating,
            "badge_class": badge_class
        })
        
    return {
        "key_metrics": {
            "highest_building": highest_building,
            "highest_kwh": round(highest_kwh, 2),
            "highest_pct": highest_pct,
            "lowest_building": lowest_building,
            "lowest_kwh": round(lowest_kwh, 2),
            "lowest_pct": lowest_pct,
            "peak_window": peak_window_str,
            "peak_hour": f"{peak_hour:02d}:00",
            "peak_hour_val": peak_hour_val,
            "weekend_drop_pct": weekend_drop_pct,
            "solar_share_pct": solar_pct,
            "top_anomaly_building": top_anomaly_building or "None",
            "top_anomaly_count": top_anomaly_count
        },
        "findings": findings,
        "recommendations": recommendations,
        "building_efficiency_rankings": rankings
    }

