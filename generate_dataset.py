"""
Campus Energy Dataset Generator Script
--------------------------------------
Generates realistic simulated energy consumption data for 7 university campus buildings
over a 90-day period (~15,000+ hourly readings).

Outputs:
  - data/sample_raw_energy.csv: Raw simulated telemetry with realistic anomalies & noise
  - data/sample_cleaned_energy.csv: Cleaned & normalized energy dataset
  - data/cleaning_report.json: Audit report explaining data quality and cleaning decisions

Usage:
  python generate_dataset.py
"""

import os
import json
import pandas as pd
try:
    from src.data_generator import generate_campus_dataset
    from src.data_cleaning import clean_energy_dataset
except ImportError:
    from modules.data_generator import generate_campus_dataset
    from modules.data_cleaning import clean_energy_dataset

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def main():
    print("=" * 70)
    print(" CAMPUS ENERGY DATASET GENERATION & PREPROCESSING PIPELINE")
    print("=" * 70)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    raw_path = os.path.join(DATA_DIR, "sample_raw_energy.csv")
    cleaned_path = os.path.join(DATA_DIR, "sample_cleaned_energy.csv")
    report_path = os.path.join(DATA_DIR, "cleaning_report.json")
    
    print("\n[1/3] Generating realistic simulated energy dataset (90 days, 7 buildings)...")
    df_raw = generate_campus_dataset(days=90, seed=42, inject_noise=True)
    df_raw.to_csv(raw_path, index=False)
    print(f" -> Raw dataset saved to: {raw_path}")
    print(f" -> Total raw records generated: {len(df_raw):,}")
    print(f" -> Columns: {list(df_raw.columns)}")
    print(f" -> Buildings included: {sorted(df_raw['building'].unique())}")
    
    print("\n[2/3] Executing data cleaning and preprocessing pipeline...")
    df_cleaned, report = clean_energy_dataset(df_raw)
    df_cleaned.to_csv(cleaned_path, index=False)
    print(f" -> Cleaned dataset saved to: {cleaned_path}")
    print(f" -> Final cleaned records: {len(df_cleaned):,}")
    
    print("\n[3/3] Exporting data cleaning audit report...")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    print(f" -> Audit report saved to: {report_path}")
    
    print("\n" + "-" * 70)
    print(" SUMMARY AUDIT METRICS:")
    print("-" * 70)
    print(f" * Original Records:              {report['original_record_count']:,}")
    print(f" * Duplicates Removed:            {report['duplicate_records_removed']:,}")
    print(f" * Invalid Timestamps Removed:    {report['invalid_timestamps_removed']:,}")
    print(f" * Negative Readings Corrected:   {report['negative_readings_corrected_or_removed']:,}")
    print(f" * Standardized Building Names:   {report['standardized_building_names']:,}")
    print(f" * Outliers Detected & Treated:   {report['outliers_detected']:,}")
    print(f" * Voltage Glitches Resolved:     {report['voltage_anomalies_flagged']:,}")
    print(f" * Final Clean Record Count:      {report['final_cleaned_record_count']:,}")
    print("-" * 70)
    print("Dataset generation and cleaning completed successfully!\n")


if __name__ == "__main__":
    main()

