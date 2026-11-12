"""
Data Validation Module for Campus Energy Datasets
-------------------------------------------------
Performs structural, categorical, chronological, and numerical range validation
on raw campus energy telemetry to identify data anomalies before preprocessing.
"""

import pandas as pd
import numpy as np

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

EXPECTED_BUILDINGS = [
    "Academic Block",
    "Library",
    "Computer Science Block",
    "Laboratory Block",
    "Boys Hostel",
    "Girls Hostel",
    "Canteen"
]


def inspect_dataset_structure(df):
    """
    Inspect dimensions, memory footprint, column names, and data types.
    """
    return {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "columns_present": list(df.columns),
        "missing_mandatory_columns": [c for c in EXPECTED_COLUMNS if c not in df.columns],
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
    }


def validate_energy_dataset(df):
    """
    Execute exhaustive validation checks on raw energy records.
    
    Returns:
        dict: Validation diagnostics metrics and flags.
    """
    diagnostics = {
        "is_valid_schema": True,
        "structural_issues": [],
        "missing_counts": {},
        "duplicate_rows_count": 0,
        "invalid_timestamps_count": 0,
        "negative_kwh_count": 0,
        "zero_or_negative_voltage_count": 0,
        "unrecognized_building_names": [],
        "extreme_kwh_outliers_count": 0,
        "validation_passed": True
    }
    
    # 1. Column Schema Verification
    missing_cols = [c for c in ["timestamp", "building", "units_kwh"] if c not in df.columns]
    if missing_cols:
        diagnostics["is_valid_schema"] = False
        diagnostics["validation_passed"] = False
        diagnostics["structural_issues"].append(f"Missing mandatory columns: {missing_cols}")
        return diagnostics
        
    # 2. Missing Value Audit
    missing = df.isnull().sum().to_dict()
    diagnostics["missing_counts"] = {k: int(v) for k, v in missing.items() if v > 0}
    if sum(diagnostics["missing_counts"].values()) > 0:
        diagnostics["validation_passed"] = False
        
    # 3. Duplicate Records Detection
    dup_mask = df.duplicated(subset=["timestamp", "building"], keep="first")
    diagnostics["duplicate_rows_count"] = int(dup_mask.sum())
    if diagnostics["duplicate_rows_count"] > 0:
        diagnostics["validation_passed"] = False
        
    # 4. Timestamp Validation
    parsed_ts = pd.to_datetime(df["timestamp"], errors="coerce")
    diagnostics["invalid_timestamps_count"] = int(parsed_ts.isna().sum())
    if diagnostics["invalid_timestamps_count"] > 0:
        diagnostics["validation_passed"] = False
        
    # 5. Negative Readings Check
    numeric_kwh = pd.to_numeric(df["units_kwh"], errors="coerce")
    neg_kwh_count = int((numeric_kwh < 0).sum())
    diagnostics["negative_kwh_count"] = neg_kwh_count
    if neg_kwh_count > 0:
        diagnostics["validation_passed"] = False
        
    # 6. Voltage Anomalies Check (nominal 230V, flagging < 180V or > 270V)
    if "voltage" in df.columns:
        numeric_volt = pd.to_numeric(df["voltage"], errors="coerce")
        volt_bad_count = int(((numeric_volt < 180.0) | (numeric_volt > 270.0)).sum())
        diagnostics["zero_or_negative_voltage_count"] = volt_bad_count
        if volt_bad_count > 0:
            diagnostics["validation_passed"] = False
            
    # 7. Building Name Standardization Check
    if "building" in df.columns:
        unique_buildings = df["building"].dropna().unique().tolist()
        unrecognized = [b for b in unique_buildings if str(b).strip() not in EXPECTED_BUILDINGS]
        diagnostics["unrecognized_building_names"] = unrecognized
        if unrecognized:
            diagnostics["validation_passed"] = False
            
    # 8. Extreme Outliers (>500 kWh in single hour, indicating sensor burst)
    outlier_count = int((numeric_kwh > 500.0).sum())
    diagnostics["extreme_kwh_outliers_count"] = outlier_count
    
    return diagnostics

