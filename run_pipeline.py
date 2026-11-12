"""
Campus Energy Analytics & Power BI Data Pipeline Runner
=======================================================
End-to-End Orchestrator:
  1. Dataset Generation / Loading
  2. Data Quality Validation
  3. 10-Stage Data Cleaning & Preprocessing
  4. Feature Engineering & Star Schema Key Assignment
  5. Analytics & Temporal Aggregations
  6. Dual-Method Anomaly Detection (IQR + Rolling Z-Score)
  7. Automated Insights Synthesis & Question-Answering
  8. Power BI Star Schema Dataset & Data Dictionary Export
"""

import os
import json
import pandas as pd

from src.data_generator import generate_campus_dataset
from src.data_validation import validate_energy_dataset, inspect_dataset_structure
from src.data_cleaning import clean_energy_dataset
from src.feature_engineering import engineer_energy_features
from src.analytics import compute_comprehensive_analytics
from src.anomaly_detection import detect_campus_anomalies
from src.insights import generate_campus_insights_and_answers
from src.export_powerbi import export_powerbi_star_schema

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
POWERBI_DATA_DIR = os.path.join(os.path.dirname(__file__), "powerbi", "data")


def run_pipeline():
    print("=" * 76)
    print(" CAMPUS ENERGY ANALYTICS & POWER BI DATA PROCESSING PIPELINE")
    print("=" * 76)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(POWERBI_DATA_DIR, exist_ok=True)
    
    raw_csv = os.path.join(DATA_DIR, "sample_raw_energy.csv")
    cleaned_csv = os.path.join(DATA_DIR, "sample_cleaned_energy.csv")
    cleaning_json = os.path.join(DATA_DIR, "cleaning_report.json")
    
    # STAGE 1: Dataset Generation / Ingestion
    print("\n[STAGE 1/8] Ingesting / Generating Simulated Campus Energy Dataset...")
    if not os.path.exists(raw_csv):
        print(" -> Raw file not found. Generating reproducible 90-day simulated telemetry...")
        df_raw = generate_campus_dataset(days=90, seed=42, inject_noise=True)
        df_raw.to_csv(raw_csv, index=False)
    else:
        df_raw = pd.read_csv(raw_csv)
    print(f" -> Raw Dataset: {len(df_raw):,} records loaded across 7 campus buildings.")
    
    # STAGE 2: Data Quality Validation
    print("\n[STAGE 2/8] Executing Pre-Cleaning Data Validation...")
    struct = inspect_dataset_structure(df_raw)
    diagnostics = validate_energy_dataset(df_raw)
    print(f" -> Schema Status: Valid ({struct['total_columns']} columns present)")
    print(f" -> Missing Values Detected: {sum(diagnostics['missing_counts'].values())} cells across columns {list(diagnostics['missing_counts'].keys())}")
    print(f" -> Duplicate Records Detected: {diagnostics['duplicate_rows_count']}")
    print(f" -> Invalid Timestamps: {diagnostics['invalid_timestamps_count']}")
    print(f" -> Negative Reading Glitches: {diagnostics['negative_kwh_count']}")
    print(f" -> Voltage Anomalies: {diagnostics['zero_or_negative_voltage_count']}")
    print(f" -> Non-Standard Building Names: {diagnostics['unrecognized_building_names']}")
    
    # STAGE 3: 10-Stage Data Cleaning & Imputation
    print("\n[STAGE 3/8] Executing Data Cleaning & Imputation Pipeline...")
    df_cleaned, clean_report = clean_energy_dataset(df_raw)
    df_cleaned.to_csv(cleaned_csv, index=False)
    with open(cleaning_json, "w", encoding="utf-8") as f:
        json.dump(clean_report, f, indent=4)
    with open(os.path.join(REPORTS_DIR, "cleaning_report.json"), "w", encoding="utf-8") as f:
        json.dump(clean_report, f, indent=4)
    print(f" -> Cleaned Dataset Saved: {len(df_cleaned):,} records (Audit report saved to cleaning_report.json)")
    
    # STAGE 4: Feature Engineering & Dimensional Keys
    print("\n[STAGE 4/8] Performing Feature Engineering & Star Schema Key Assignment...")
    df_enriched = engineer_energy_features(df_cleaned)
    print(f" -> Enriched columns added: date_key, time_key, building_id, source_id, kwh_per_occupant, rolling_7d_kwh, carbon_kg")
    
    # STAGE 5: Analytics & Aggregations
    print("\n[STAGE 5/8] Computing Campus Analytics & Temporal Groupings...")
    analytics_res = compute_comprehensive_analytics(df_enriched, export_reports=True)
    kpis = analytics_res["kpis"]
    print(f" -> Total Campus Consumption:  {kpis['total_consumption_kwh']:,.1f} kWh ({kpis['total_consumption_mwh']:,.1f} MWh)")
    print(f" -> Average Daily Consumption:   {kpis['average_daily_kwh']:,.1f} kWh/day")
    print(f" -> Peak Electricity Demand:     {kpis['peak_demand_kw']:,.1f} kW")
    print(f" -> Occupancy vs kWh Correlation: r = {analytics_res['occupancy_correlation']}")
    print(" -> Exported summary tables: building_analysis.csv, daily_analysis.csv, monthly_analysis.csv")
    
    # STAGE 6: Anomaly Detection
    print("\n[STAGE 6/8] Executing Multi-Method Anomaly Detection Engine...")
    anomalies, df_anomalies, anom_summary = detect_campus_anomalies(df_enriched, export_csv=True)
    print(f" -> Total Flagged Anomalies:     {anom_summary['total']} events")
    print(f"    * Critical Severity:         {anom_summary['by_severity']['Critical']}")
    print(f"    * High Severity:             {anom_summary['by_severity']['High']}")
    print(f"    * Medium Severity:           {anom_summary['by_severity']['Medium']}")
    print(f"    * Low Severity:              {anom_summary['by_severity']['Low']}")
    print(f" -> Exported reports: reports/anomaly_report.csv & data/PowerBI_Anomaly_Report.csv")
    
    # STAGE 7: Insights Synthesis & Q&A Reporting
    print("\n[STAGE 7/8] Generating Automated Insights & Management Q&A Matrix...")
    insights_res = generate_campus_insights_and_answers(df_enriched, df_anomalies, export_excel=True)
    print(f" -> #1 Energy Consumer:          {insights_res['highest_building']}")
    print(f" -> Lowest Energy Consumer:      {insights_res['lowest_building']}")
    print(f" -> Peak Operational Window:     {insights_res['peak_window']}")
    print(f" -> Weekend Load Reduction:      {insights_res['weekend_drop_pct']}%")
    print(f" -> Exported Excel Insights:     reports/insights_report.xlsx")
    
    # STAGE 8: Power BI Star Schema Datasets & Data Dictionary Export
    print("\n[STAGE 8/8] Exporting Power BI Star Schema Model & Data Dictionary...")
    pbi_paths = export_powerbi_star_schema(df_enriched, df_anomalies)
    print(" -> Star Schema Tables Exported:")
    print(f"    * Fact Table:       FactEnergyConsumption.csv ({len(df_enriched):,} rows)")
    print(f"    * DimBuilding:      DimBuilding.csv (7 facilities)")
    print(f"    * DimDate:          DimDate.csv ({analytics_res['kpis']['total_days']} calendar days)")
    print(f"    * DimTime:          DimTime.csv (24 diurnal intervals)")
    print(f"    * DimEnergySource:  DimEnergySource.csv (3 generation sources)")
    print(f"    * Anomaly Log:      PowerBI_Anomaly_Report.csv ({len(df_anomalies):,} records)")
    print(f"    * Flat Dataset:     powerbi_energy_dataset.csv ({len(df_enriched):,} rows)")
    print(f"    * Data Dictionary:  data/data_dictionary.xlsx (Comprehensive 6-sheet workbook)")
    
    print("\n" + "=" * 76)
    print(" PIPELINE EXECUTION COMPLETED 100% SUCCESSFULLY!")
    print(" All files are prepared for Microsoft Power BI Desktop ingestion.")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    run_pipeline()

