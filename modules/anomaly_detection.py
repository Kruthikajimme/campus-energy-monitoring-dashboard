"""
Anomaly Detection Module for Campus Energy Analytics
---------------------------------------------------
Applies statistical methods (Interquartile Range IQR and Rolling Average Z-Score)
to identify anomalous energy readings, unusual off-hours baseloads, and sudden spikes.

DISCLAIMER: Identified anomalies represent statistical deviations that warrant operational
review by campus energy managers. They are not confirmed electrical or physical hardware faults.
"""

import numpy as np
import pandas as pd


def detect_anomalies(df, iqr_multiplier=1.8, rolling_window=6, spike_threshold=1.75):
    """
    Detect statistical anomalies in electricity consumption across campus buildings.
    
    Parameters:
        df (pd.DataFrame): Cleaned energy consumption dataframe.
        iqr_multiplier (float): Multiplier for IQR threshold (default 1.8).
        rolling_window (int): Rolling window in hours for sudden spike detection.
        spike_threshold (float): Ratio above rolling mean that triggers a sudden spike alert.
        
    Returns:
        list of dict: Detected anomaly records sorted by timestamp descending.
    """
    if df.empty or len(df) < 10:
        return []
        
    anomalies = []
    df_sorted = df.copy()
    df_sorted["dt"] = pd.to_datetime(df_sorted["timestamp"], errors="coerce")
    df_sorted = df_sorted.dropna(subset=["dt"]).sort_values(by=["building", "dt"]).reset_index(drop=True)
    
    # Calculate baseline statistics per building and hour-of-day
    building_hour_stats = df_sorted.groupby(["building", df_sorted["dt"].dt.hour])["units_kwh"].agg(
        hourly_mean="mean",
        hourly_std="std",
        hourly_median="median"
    ).reset_index()
    
    # Calculate building-level IQR statistics
    building_iqr_stats = {}
    for b_name in df_sorted["building"].unique():
        b_series = df_sorted[df_sorted["building"] == b_name]["units_kwh"]
        q25 = float(b_series.quantile(0.25))
        q75 = float(b_series.quantile(0.75))
        iqr = max(1.0, q75 - q25)
        building_iqr_stats[b_name] = {
            "q25": q25,
            "q75": q75,
            "iqr": iqr,
            "upper_bound_mild": q75 + (iqr_multiplier * iqr),
            "upper_bound_high": q75 + (2.5 * iqr),
            "upper_bound_critical": q75 + (3.5 * iqr),
            "median": float(b_series.median()),
            "mean": float(b_series.mean())
        }
        
    # Group by building for rolling statistics
    for b_name, b_group in df_sorted.groupby("building"):
        b_group = b_group.copy()
        b_iqr = building_iqr_stats[b_name]
        
        # Compute rolling mean and std over past N hours
        b_group["rolling_mean"] = b_group["units_kwh"].rolling(window=rolling_window, min_periods=3).mean()
        b_group["rolling_std"] = b_group["units_kwh"].rolling(window=rolling_window, min_periods=3).std().fillna(1.0)
        
        for idx, row in b_group.iterrows():
            kwh = float(row["units_kwh"])
            hour = row["dt"].hour
            day_type = row.get("day_type", "Weekday")
            peak_kw = float(row.get("peak_kw", kwh * 1.25))
            rolling_avg = float(row["rolling_mean"]) if not pd.isna(row["rolling_mean"]) else b_iqr["mean"]
            
            is_anomaly = False
            reasons = []
            severity = "Low"
            expected_kwh = round(rolling_avg, 2)
            
            # 1. Extreme IQR Threshold Check
            if kwh >= b_iqr["upper_bound_critical"]:
                is_anomaly = True
                severity = "Critical"
                reasons.append(f"Consumption exceeds 3.5x IQR upper threshold ({b_iqr['upper_bound_critical']:.1f} kWh)")
            elif kwh >= b_iqr["upper_bound_high"]:
                is_anomaly = True
                severity = "High"
                reasons.append(f"Consumption exceeds 2.5x IQR upper threshold ({b_iqr['upper_bound_high']:.1f} kWh)")
            elif kwh >= b_iqr["upper_bound_mild"]:
                is_anomaly = True
                severity = "Medium"
                reasons.append(f"Consumption exceeds mild IQR threshold ({b_iqr['upper_bound_mild']:.1f} kWh)")
                
            # 2. Sudden Short-Term Spike vs Rolling Baseline
            if rolling_avg > 10.0 and kwh > (rolling_avg * spike_threshold) and (kwh - rolling_avg) > 25.0:
                is_anomaly = True
                spike_pct = int(((kwh - rolling_avg) / rolling_avg) * 100)
                reasons.append(f"Sudden surge: {spike_pct}% above {rolling_window}h rolling average")
                if severity == "Low":
                    severity = "Medium"
                elif severity == "Medium" and spike_pct > 100:
                    severity = "High"
                    
            # 3. Off-Hours High Consumption Check (e.g. Academic, Lab, Canteen at 01:00 - 05:00)
            if b_name in ["Academic Block", "Laboratory Block", "Computer Science Block", "Canteen"]:
                if (hour in [1, 2, 3, 4] or day_type == "Holiday") and kwh > (b_iqr["mean"] * 1.35):
                    is_anomaly = True
                    reasons.append(f"Unexpected high off-hours baseload during low-occupancy period ({hour:02d}:00)")
                    if severity in ["Low", "Medium"]:
                        severity = "Medium"
                        
            # 4. Disproportionate Peak Demand (kW) surge
            if peak_kw > (kwh * 1.65) and peak_kw > 100.0:
                is_anomaly = True
                reasons.append(f"High transient demand surge: Peak power {peak_kw:.1f} kW exceeds normal ratio")
                if severity == "Low":
                    severity = "Medium"
                    
            if is_anomaly:
                anomalies.append({
                    "building": b_name,
                    "timestamp": str(row["timestamp"]),
                    "recorded_kwh": round(kwh, 2),
                    "expected_kwh": expected_kwh,
                    "deviation_kwh": round(kwh - expected_kwh, 2),
                    "deviation_pct": round(((kwh - expected_kwh) / max(1.0, expected_kwh)) * 100.0, 1),
                    "peak_kw": round(peak_kw, 2),
                    "severity": severity,
                    "reason": "; ".join(reasons),
                    "day_type": str(row.get("day_type", "Weekday")),
                    "source": str(row.get("source", "Grid")),
                    "action_recommendation": get_action_recommendation(b_name, severity, reasons)
                })
                
    # Sort anomalies descending by timestamp
    anomalies.sort(key=lambda x: x["timestamp"], reverse=True)
    return anomalies


def get_action_recommendation(building, severity, reasons):
    """
    Generate tailored investigation advice for facility technicians.
    """
    reason_str = " ".join(reasons).lower()
    
    if "off-hours" in reason_str:
        return f"Inspect {building} HVAC schedules, central chiller timers, and verify whether lab equipment/lights were left running overnight."
    elif "sudden surge" in reason_str or "transient" in reason_str:
        return f"Check {building} sub-feeder meters for heavy inductive motor inrush, compressor cycles, or unauthorized space heaters/heavy loads."
    elif severity == "Critical":
        return f"Immediate dispatch: Inspect {building} main switchgear, verify phase currents, and check for telemetry current-transformer saturation."
    elif severity == "High":
        return f"Conduct physical inspection of {building} distribution panel and review schedule with building supervisor."
    else:
        return f"Monitor {building} submeter over subsequent 12 hours to determine if pattern is recurring or isolated."


def get_anomaly_summary(anomalies):
    """
    Produce categorical summary counts of detected anomalies.
    """
    if not anomalies:
        return {
            "total": 0,
            "by_severity": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
            "by_building": {}
        }
        
    by_severity = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    by_building = {}
    
    for a in anomalies:
        sev = a["severity"]
        by_severity[sev] = by_severity.get(sev, 0) + 1
        
        b = a["building"]
        by_building[b] = by_building.get(b, 0) + 1
        
    return {
        "total": len(anomalies),
        "by_severity": by_severity,
        "by_building": by_building
    }

