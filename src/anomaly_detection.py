"""
Anomaly Detection Module for Campus Energy Analytics
---------------------------------------------------
Applies multi-tiered statistical diagnostics (Interquartile Range IQR, Rolling Average Z-Score,
and Off-Hours Baselines) to identify consumption surges, unmanaged overnight loads, and telemetry spikes.

DISCLAIMER: Flagged anomalies represent statistical deviations that warrant operational review
by campus electrical engineers. They are not confirmed physical equipment failures.
"""

import os
import numpy as np
import pandas as pd

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

BUILDING_ID_MAP = {
    "Academic Block": "BLD01",
    "Library": "BLD02",
    "Computer Science Block": "BLD03",
    "Laboratory Block": "BLD04",
    "Boys Hostel": "BLD05",
    "Girls Hostel": "BLD06",
    "Canteen": "BLD07"
}


def detect_campus_anomalies(df, iqr_multiplier=1.8, rolling_window=6, spike_threshold=1.75, export_csv=True):
    """
    Execute multi-method statistical anomaly detection across all campus buildings.
    
    Parameters:
        df (pd.DataFrame): Cleaned or enriched energy dataframe.
        iqr_multiplier (float): Multiplier for mild IQR threshold.
        rolling_window (int): Moving average window in hours.
        spike_threshold (float): Ratio above rolling mean that flags a localized spike.
        export_csv (bool): Whether to export anomaly report to reports/ and data/
        
    Returns:
        tuple: (anomalies_list, anomalies_df, summary_dict)
    """
    if df.empty or len(df) < 10:
        empty_df = pd.DataFrame()
        return [], empty_df, {"total": 0, "by_severity": {}, "by_building": {}}
        
    df_sorted = df.copy()
    df_sorted["dt"] = pd.to_datetime(df_sorted["timestamp"], errors="coerce")
    df_sorted = df_sorted.dropna(subset=["dt"]).sort_values(by=["building", "dt"]).reset_index(drop=True)
    
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
            "upper_mild": q75 + (iqr_multiplier * iqr),
            "upper_high": q75 + (2.5 * iqr),
            "upper_critical": q75 + (3.5 * iqr),
            "mean": float(b_series.mean())
        }
        
    anomalies = []
    anomaly_counter = 1
    
    for b_name, b_group in df_sorted.groupby("building"):
        b_group = b_group.copy()
        b_iqr = building_iqr_stats[b_name]
        
        # Trailing rolling mean and std
        b_group["rolling_mean"] = b_group["units_kwh"].rolling(window=rolling_window, min_periods=3).mean()
        b_group["rolling_std"] = b_group["units_kwh"].rolling(window=rolling_window, min_periods=3).std().fillna(1.0)
        
        for idx, row in b_group.iterrows():
            kwh = float(row["units_kwh"])
            hour = row["dt"].hour
            day_type = str(row.get("day_type", "Weekday"))
            peak_kw = float(row.get("peak_kw", kwh * 1.25))
            rolling_avg = float(row["rolling_mean"]) if not pd.isna(row["rolling_mean"]) else b_iqr["mean"]
            rolling_std = float(row["rolling_std"]) if not pd.isna(row["rolling_std"]) and row["rolling_std"] > 0 else 5.0
            
            is_anomaly = False
            reasons = []
            methods = []
            severity = "Low"
            expected_kwh = round(rolling_avg, 2)
            
            # Method 1: IQR-Based Outlier Detection
            if kwh >= b_iqr["upper_critical"]:
                is_anomaly = True
                severity = "Critical"
                methods.append("IQR (Extreme)")
                reasons.append(f"Exceeds 3.5x IQR upper threshold ({b_iqr['upper_critical']:.1f} kWh)")
            elif kwh >= b_iqr["upper_high"]:
                is_anomaly = True
                severity = "High"
                methods.append("IQR (High)")
                reasons.append(f"Exceeds 2.5x IQR upper threshold ({b_iqr['upper_high']:.1f} kWh)")
            elif kwh >= b_iqr["upper_mild"]:
                is_anomaly = True
                severity = "Medium"
                methods.append("IQR (Mild)")
                reasons.append(f"Exceeds mild IQR threshold ({b_iqr['upper_mild']:.1f} kWh)")
                
            # Method 2: Rolling Window Spike & Z-Score
            z_score = (kwh - rolling_avg) / rolling_std
            if rolling_avg > 10.0 and (kwh > (rolling_avg * spike_threshold) or z_score > 3.0) and (kwh - rolling_avg) > 25.0:
                is_anomaly = True
                methods.append("Rolling Z-Score")
                spike_pct = int(((kwh - rolling_avg) / rolling_avg) * 100)
                reasons.append(f"Sudden surge: +{spike_pct}% above {rolling_window}h baseline (Z={z_score:.1f})")
                if severity == "Low":
                    severity = "Medium"
                elif severity == "Medium" and spike_pct > 100:
                    severity = "High"
                    
            # Method 3: Unscheduled Off-Hours Baselines (Academic / Lab / CS / Canteen)
            if b_name in ["Academic Block", "Laboratory Block", "Computer Science Block", "Canteen"]:
                if (hour in [1, 2, 3, 4] or day_type == "Holiday") and kwh > (b_iqr["mean"] * 1.35):
                    is_anomaly = True
                    methods.append("Off-Hours Rule")
                    reasons.append(f"Unscheduled off-hours baseload leakage during unoccupied hours ({hour:02d}:00)")
                    if severity in ["Low", "Medium"]:
                        severity = "Medium"
                        
            # Method 4: High Transient Demand Surge (kW)
            if peak_kw > (kwh * 1.65) and peak_kw > 100.0:
                is_anomaly = True
                methods.append("Peak Surge")
                reasons.append(f"Transient peak demand surge ({peak_kw:.1f} kW)")
                if severity == "Low":
                    severity = "Medium"
                    
            if is_anomaly:
                anom_id = f"ANOM-{anomaly_counter:04d}"
                anomaly_counter += 1
                
                date_key = int(row["dt"].strftime("%Y%m%d"))
                time_key = int(hour * 100)
                bld_id = BUILDING_ID_MAP.get(b_name, "BLD99")
                
                dev_kwh = round(kwh - expected_kwh, 2)
                dev_pct = round((dev_kwh / max(1.0, expected_kwh)) * 100.0, 1)
                
                anomalies.append({
                    "anomaly_id": anom_id,
                    "timestamp": str(row["timestamp"]),
                    "date_key": date_key,
                    "time_key": time_key,
                    "building_id": bld_id,
                    "building_name": b_name,
                    "recorded_kwh": round(kwh, 2),
                    "expected_kwh": expected_kwh,
                    "deviation_kwh": dev_kwh,
                    "deviation_pct": dev_pct,
                    "peak_kw": round(peak_kw, 2),
                    "severity": severity,
                    "anomaly_method": " + ".join(dict.fromkeys(methods)),
                    "reason": "; ".join(reasons),
                    "recommended_action": get_action_recommendation(b_name, severity, reasons)
                })
                
    anomalies_df = pd.DataFrame(anomalies)
    if not anomalies_df.empty:
        anomalies_df = anomalies_df.sort_values(by="timestamp", ascending=False).reset_index(drop=True)
        
    # Categorical summary metrics
    by_sev = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    by_bld = {}
    for a in anomalies:
        sev = a["severity"]
        by_sev[sev] = by_sev.get(sev, 0) + 1
        b = a["building_name"]
        by_bld[b] = by_bld.get(b, 0) + 1
        
    summary = {
        "total": len(anomalies),
        "by_severity": by_sev,
        "by_building": by_bld
    }
    
    if export_csv and not anomalies_df.empty:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        os.makedirs(DATA_DIR, exist_ok=True)
        anomalies_df.to_csv(os.path.join(REPORTS_DIR, "anomaly_report.csv"), index=False)
        anomalies_df.to_csv(os.path.join(DATA_DIR, "PowerBI_Anomaly_Report.csv"), index=False)
        
    return anomalies, anomalies_df, summary


def get_action_recommendation(building, severity, reasons):
    """
    Generate tailored investigation advice for university facility engineers.
    """
    reason_str = " ".join(reasons).lower()
    
    if "off-hours" in reason_str:
        return f"Verify {building} automated setback timers; check if central AHU or split ACs were left running overnight."
    elif "sudden surge" in reason_str or "transient" in reason_str:
        return f"Inspect {building} motor starters and verify sub-feeder currents for uncoordinated heavy equipment start."
    elif severity == "Critical":
        return f"Immediate dispatch: Inspect {building} main switchboard and calibrate meter CT sensors for phase saturation."
    elif severity == "High":
        return f"Conduct physical audit of {building} distribution boards and cross-check schedule with lab administrator."
    else:
        return f"Flag {building} submeter for continuous 24-hour observation."

