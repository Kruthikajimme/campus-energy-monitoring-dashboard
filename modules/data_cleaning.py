"""
Data Cleaning and Preprocessing Pipeline
-----------------------------------------
Automated quality inspection, audit reporting, and cleaning for campus energy datasets.
Detects missing values, duplicates, invalid timestamps, negative power values,
abnormal voltage readings, non-standard building names, and IQR-based statistical outliers.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime

VALID_BUILDINGS = {
    "academic block": "Academic Block",
    "library": "Library",
    "computer science block": "Computer Science Block",
    "laboratory block": "Laboratory Block",
    "boys hostel": "Boys Hostel",
    "girls hostel": "Girls Hostel",
    "canteen": "Canteen"
}

EXPECTED_COLUMNS = [
    "timestamp",
    "building",
    "meter_id",
    "units_kwh",
    "peak_kw",
    "voltage",
    "occupancy",
    "source",
    "temperature",
    "day_type"
]


def clean_energy_dataset(df_raw, iqr_multiplier=2.5):
    """
    Execute full data cleaning workflow on raw energy records.
    
    Parameters:
        df_raw (pd.DataFrame): Raw dataframe to clean.
        iqr_multiplier (float): IQR threshold multiplier for extreme outlier detection (default 2.5).
        
    Returns:
        tuple: (df_cleaned, cleaning_report_dict)
    """
    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "original_record_count": int(len(df_raw)),
        "missing_values_detected": {},
        "duplicate_records_removed": 0,
        "invalid_timestamps_removed": 0,
        "negative_readings_corrected_or_removed": 0,
        "voltage_anomalies_flagged": 0,
        "standardized_building_names": 0,
        "outliers_detected": 0,
        "outliers_by_building": {},
        "records_removed_total": 0,
        "records_corrected_total": 0,
        "final_cleaned_record_count": 0,
        "cleaning_decisions": []
    }
    
    df = df_raw.copy()
    
    # 1. Audit missing values before transformation
    missing_counts = df.isnull().sum().to_dict()
    report["missing_values_detected"] = {k: int(v) for k, v in missing_counts.items() if v > 0}
    
    # 2. Duplicate Detection and Removal
    init_len = len(df)
    # Check duplicates based on building and timestamp
    df = df.drop_duplicates(subset=["timestamp", "building"], keep="first")
    duplicates_removed = init_len - len(df)
    report["duplicate_records_removed"] = int(duplicates_removed)
    if duplicates_removed > 0:
        report["cleaning_decisions"].append({
            "step": "Duplicate Removal",
            "action": f"Removed {duplicates_removed} duplicate records matching identical (building, timestamp) tuples.",
            "rationale": "Energy meters emit exactly one cumulative interval reading per hour. Redundant rows skew sum KPIs."
        })
        
    # 3. Invalid Timestamp Detection
    ts_before = len(df)
    # Coerce errors to NaT
    df["parsed_timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    invalid_ts_count = int(df["parsed_timestamp"].isna().sum())
    report["invalid_timestamps_removed"] = invalid_ts_count
    if invalid_ts_count > 0:
        df = df.dropna(subset=["parsed_timestamp"]).copy()
        report["cleaning_decisions"].append({
            "step": "Timestamp Validation",
            "action": f"Dropped {invalid_ts_count} records containing unparseable or corrupted timestamp strings.",
            "rationale": "Chronological integrity is mandatory for temporal trend analysis and peak hour detection."
        })
    df["timestamp"] = df["parsed_timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.drop(columns=["parsed_timestamp"])
    
    # 4. Standardize Building Names
    standardized_count = 0
    def fix_building_name(val):
        nonlocal standardized_count
        if pd.isna(val):
            return "Unknown"
        clean_str = " ".join(str(val).strip().split()).lower()
        if clean_str in VALID_BUILDINGS:
            standard_name = VALID_BUILDINGS[clean_str]
            if str(val) != standard_name:
                standardized_count += 1
            return standard_name
        return str(val).strip().title()
        
    df["building"] = df["building"].apply(fix_building_name)
    report["standardized_building_names"] = int(standardized_count)
    if standardized_count > 0:
        report["cleaning_decisions"].append({
            "step": "Building Name Standardization",
            "action": f"Normalized {standardized_count} building names with inconsistent casing or extra whitespace.",
            "rationale": "Ensures clean group-by aggregations and prevents fragmented building cards."
        })
        
    # 5. Type Conversions & Handling Numeric Values
    numeric_cols = ["units_kwh", "peak_kw", "voltage", "occupancy", "temperature"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
    # 6. Negative Electricity Reading Detection
    neg_mask = df["units_kwh"] < 0
    neg_count = int(neg_mask.sum())
    report["negative_readings_corrected_or_removed"] = neg_count
    if neg_count > 0:
        # Campus electricity consumption cannot be negative unless net-metered feed-in,
        # which our campus submeters do not perform. We rectify inverted sensor signs or drop if corrupted.
        df.loc[neg_mask, "units_kwh"] = df.loc[neg_mask, "units_kwh"].abs()
        report["cleaning_decisions"].append({
            "step": "Negative Reading Correction",
            "action": f"Inverted signs for {neg_count} negative consumption values (sensor polarity errors).",
            "rationale": "Submeters occasionally invert current transformer (CT) polarity during maintenance."
        })
        
    # 7. Imputation for Missing Values
    # Impute missing units_kwh using building median for that specific hour
    records_imputed = 0
    if df["units_kwh"].isna().sum() > 0:
        kwh_na = int(df["units_kwh"].isna().sum())
        records_imputed += kwh_na
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        building_hour_medians = df.groupby(["building", "hour"])["units_kwh"].transform("median")
        df["units_kwh"] = df["units_kwh"].fillna(building_hour_medians).fillna(df["units_kwh"].median())
        df = df.drop(columns=["hour"])
        report["cleaning_decisions"].append({
            "step": "Missing Consumption Imputation",
            "action": f"Imputed {kwh_na} missing units_kwh values using building-specific hourly median.",
            "rationale": "Median preserves diurnal patterns without introducing artificial spikes."
        })
        
    if df["peak_kw"].isna().sum() > 0:
        df["peak_kw"] = df["peak_kw"].fillna(df["units_kwh"] * 1.25)
        
    if df["occupancy"].isna().sum() > 0:
        df["occupancy"] = df["occupancy"].fillna(df.groupby("building")["occupancy"].transform("median")).fillna(0).round().astype(int)
        
    if df["voltage"].isna().sum() > 0:
        df["voltage"] = df["voltage"].fillna(230.0)
        
    if df["temperature"].isna().sum() > 0:
        df["temperature"] = df["temperature"].fillna(df["temperature"].median())
        
    # 8. Voltage Anomalies Flagging / Correction (nominal is 230V, acceptable range 180V - 270V)
    bad_voltage_mask = (df["voltage"] < 180.0) | (df["voltage"] > 270.0)
    bad_voltage_count = int(bad_voltage_mask.sum())
    report["voltage_anomalies_flagged"] = bad_voltage_count
    if bad_voltage_count > 0:
        # Cap/smooth extreme voltage sensor dropouts to nominal
        df.loc[bad_voltage_mask, "voltage"] = 230.0
        report["cleaning_decisions"].append({
            "step": "Voltage Correction",
            "action": f"Reset {bad_voltage_count} anomalous voltage readings (<180V or >270V) to nominal 230V.",
            "rationale": "Campus line frequency and voltage regulators maintain 230V ± 10% under standard operation."
        })
        
    # 9. Outlier Detection using Interquartile Range (IQR) method per building
    total_outliers = 0
    outliers_dict = {}
    
    # Calculate IQR per building
    for b_name in df["building"].unique():
        b_mask = df["building"] == b_name
        b_kwh = df.loc[b_mask, "units_kwh"]
        q25 = b_kwh.quantile(0.25)
        q75 = b_kwh.quantile(0.75)
        iqr = q75 - q25
        upper_limit = q75 + (iqr_multiplier * iqr)
        
        # Severe outliers that indicate sensor malfunction (e.g. 99999.0 or multi-fold spikes)
        outlier_mask = b_mask & (df["units_kwh"] > upper_limit)
        b_outliers = int(outlier_mask.sum())
        outliers_dict[b_name] = b_outliers
        total_outliers += b_outliers
        
        if b_outliers > 0:
            # For data cleaning, we cap extreme sensor glitches to the 99th percentile of that building
            cap_val = float(b_kwh.quantile(0.99))
            df.loc[outlier_mask, "units_kwh"] = round(cap_val, 2)
            df.loc[outlier_mask, "peak_kw"] = round(cap_val * 1.25, 2)
            
    report["outliers_detected"] = total_outliers
    report["outliers_by_building"] = outliers_dict
    if total_outliers > 0:
        report["cleaning_decisions"].append({
            "step": "IQR Outlier Treatment",
            "action": f"Identified {total_outliers} extreme statistical outliers (>{iqr_multiplier}x IQR) and capped them to the 99th percentile.",
            "rationale": "Prevents telemetry dropouts/overflows (e.g., 99999 kWh) from distorting university budget projections."
        })
        
    # 10. Ensure Final Cleaned Data Formatting
    df["units_kwh"] = df["units_kwh"].round(2)
    df["peak_kw"] = df["peak_kw"].round(2)
    df["voltage"] = df["voltage"].round(1)
    df["occupancy"] = df["occupancy"].astype(int)
    df["temperature"] = df["temperature"].round(1)
    df["source"] = df["source"].fillna("Grid").astype(str)
    df["day_type"] = df["day_type"].fillna("Weekday").astype(str)
    
    # Sort chronologically
    df = df.sort_values(by=["timestamp", "building"]).reset_index(drop=True)
    
    report["records_removed_total"] = int(report["original_record_count"] - len(df))
    report["records_corrected_total"] = int(
        neg_count + standardized_count + bad_voltage_count + total_outliers + records_imputed
    )
    report["final_cleaned_record_count"] = int(len(df))
    
    return df, report

