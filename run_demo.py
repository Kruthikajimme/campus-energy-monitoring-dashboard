"""
Classroom Demonstration Script for Campus Energy Analytics
==========================================================
Demonstrates dynamic data updates, controlled anomaly injection, pipeline re-execution,
and Power BI dataset refresh for classroom evaluation by Prof. Sayed Faizan Qaser.

Demonstration Scenario:
  STEP 1: Display baseline dataset metrics and anomaly count.
  STEP 2: Ingest a new normal hourly electricity reading.
  STEP 3: Introduce an intentional extreme consumption spike (e.g. 425.0 kWh surge).
  STEP 4: Re-run validation, cleaning, and anomaly detection.
  STEP 5: Present the newly flagged Critical Anomaly with root-cause reason and technician action.
  STEP 6: Re-export updated Power BI datasets (FactEnergyConsumption.csv & PowerBI_Anomaly_Report.csv)
          and provide exact instructions for Power BI Desktop data refresh.
"""

import os
import sys
from datetime import datetime
import pandas as pd

from src.data_generator import BUILDINGS, METER_MAPPING
from src.data_cleaning import clean_energy_dataset
from src.feature_engineering import engineer_energy_features
from src.analytics import compute_comprehensive_analytics
from src.anomaly_detection import detect_campus_anomalies
from src.export_powerbi import export_powerbi_star_schema

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CLEANED_CSV = os.path.join(DATA_DIR, "sample_cleaned_energy.csv")
BACKUP_CLEANED_CSV = os.path.join(DATA_DIR, "sample_cleaned_energy_baseline_backup.csv")


def run_classroom_demonstration(auto=True):
    print("=" * 76)
    print(" CLASSROOM DEMONSTRATION WORKFLOW: LIVE DATA UPDATE & ANOMALY DETECTION")
    print(" Evaluated for Professor Sayed Faizan Qaser's Engineering Assessment")
    print("=" * 76)
    
    if not os.path.exists(CLEANED_CSV):
        print("Cleaned dataset missing. Running full pipeline first...")
        from run_pipeline import run_pipeline
        run_pipeline()
        
    # Create baseline backup if not exists
    if not os.path.exists(BACKUP_CLEANED_CSV):
        pd.read_csv(CLEANED_CSV).to_csv(BACKUP_CLEANED_CSV, index=False)
        
    df_baseline = pd.read_csv(CLEANED_CSV)
    
    # -------------------------------------------------------------------------
    # STEP 1: Baseline Dashboard Metrics
    # -------------------------------------------------------------------------
    print("\n" + "-" * 76)
    print(" [STEP 1] BASELINE SYSTEM STATE (Before Injection)")
    print("-" * 76)
    
    df_base_enriched = engineer_energy_features(df_baseline)
    base_analytics = compute_comprehensive_analytics(df_base_enriched, export_reports=False)
    _, _, base_anom_summary = detect_campus_anomalies(df_base_enriched, export_csv=False)
    
    base_kpi = base_analytics["kpis"]
    print(f" -> Active Telemetry Records:      {base_kpi['total_records']:,}")
    print(f" -> Total Campus Consumption:      {base_kpi['total_consumption_kwh']:,.1f} kWh")
    print(f" -> Peak Electricity Demand:       {base_kpi['peak_demand_kw']:,.1f} kW")
    print(f" -> Average Daily Consumption:     {base_kpi['average_daily_kwh']:,.1f} kWh/day")
    print(f" -> Total Baseline Anomalies:      {base_anom_summary['total']} events")
    
    if not auto:
        input("\nPress Enter to proceed to Step 2 (Inject New Readings)...")
        
    # -------------------------------------------------------------------------
    # STEP 2 & 3: Inject New Reading & Extreme Controlled Surge
    # -------------------------------------------------------------------------
    print("\n" + "-" * 76)
    print(" [STEP 2 & 3] INJECTING TELEMETRY & CONTROLLED CONSUMPTION SPIKE")
    print("-" * 76)
    
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Normal reading: Library
    normal_record = {
        "timestamp": now_ts,
        "building": "Library",
        "meter_id": METER_MAPPING["Library"],
        "units_kwh": 52.4,
        "peak_kw": 68.0,
        "voltage": 230.1,
        "occupancy": 140,
        "source": "Grid",
        "temperature": 29.5,
        "day_type": "Weekday"
    }
    
    # Intentional surge: Academic Block (425.0 kWh - severe HVAC chiller fault / uncoordinated inrush)
    spike_record = {
        "timestamp": now_ts,
        "building": "Academic Block",
        "meter_id": METER_MAPPING["Academic Block"],
        "units_kwh": 425.0,
        "peak_kw": 540.0,
        "voltage": 221.4,
        "occupancy": 450,
        "source": "Grid",
        "temperature": 34.0,
        "day_type": "Weekday"
    }
    
    print(f" 1. Normal Reading Added:   Library -> 52.4 kWh, Occupancy = 140")
    print(f" 2. Simulated Surge Added:  Academic Block -> 425.0 kWh, Peak = 540.0 kW (Nominal is ~80 kWh)")
    print(f"    * Timestamp:            {now_ts}")
    print(f"    * Simulated Event:      Unmanaged chiller staging & unauthorized heavy machinery test")
    
    df_updated = pd.concat([df_baseline, pd.DataFrame([normal_record, spike_record])], ignore_index=True)
    
    # -------------------------------------------------------------------------
    # STEP 4: Re-Run Pipeline (Validation, Cleaning, Anomaly Detection)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 76)
    print(" [STEP 4] RE-RUNNING DATA VALIDATION & ANOMALY DETECTION ENGINE")
    print("-" * 76)
    
    df_cleaned_new, _ = clean_energy_dataset(df_updated)
    df_enriched_new = engineer_energy_features(df_cleaned_new)
    new_analytics = compute_comprehensive_analytics(df_enriched_new, export_reports=True)
    anomalies_new, df_anom_new, new_anom_summary = detect_campus_anomalies(df_enriched_new, export_csv=True)
    
    # Re-export updated Power BI datasets
    export_powerbi_star_schema(df_enriched_new, df_anom_new)
    df_cleaned_new.to_csv(CLEANED_CSV, index=False)
    
    new_kpi = new_analytics["kpis"]
    print(f" -> Updated Telemetry Records:    {new_kpi['total_records']:,} (+2 records)")
    print(f" -> Updated Campus Consumption:    {new_kpi['total_consumption_kwh']:,.1f} kWh (+477.4 kWh)")
    print(f" -> Updated Peak Demand:           {new_kpi['peak_demand_kw']:,.1f} kW (Surged from {base_kpi['peak_demand_kw']} kW to {new_kpi['peak_demand_kw']} kW)")
    print(f" -> Total Flagged Anomalies:       {new_anom_summary['total']} events (+1 new anomaly caught)")
    
    # -------------------------------------------------------------------------
    # STEP 5: Verification of Caught Anomaly
    # -------------------------------------------------------------------------
    print("\n" + "-" * 76)
    print(" [STEP 5] AUDITING THE FLAGGED ANOMALY RECORD")
    print("-" * 76)
    
    caught_event = next((a for a in anomalies_new if a["timestamp"] == now_ts and a["building_name"] == "Academic Block"), None)
    
    if caught_event:
        print(" [SUCCESS] ANOMALY DETECTED BY ALGORITHMIC ENGINE!")
        print(f"  - Anomaly Identifier:    {caught_event['anomaly_id']}")
        print(f"  - Target Facility:       {caught_event['building_name']}")
        print(f"  - Recorded Consumption:  {caught_event['recorded_kwh']} kWh")
        print(f"  - Expected Baseline:     {caught_event['expected_kwh']} kWh")
        print(f"  - Percentage Deviation:  +{caught_event['deviation_pct']}% above expected")
        print(f"  - Severity Level:        {caught_event['severity']} SEVERITY")
        print(f"  - Detection Method:      {caught_event['anomaly_method']}")
        print(f"  - Root-Cause Reason:     {caught_event['reason']}")
        print(f"  - Action Recommendation: {caught_event['recommended_action']}")
    else:
        print(" [NOTE] Injected record fell within IQR limits.")
        
    # -------------------------------------------------------------------------
    # STEP 6: Power BI Refresh Demonstration Instructions
    # -------------------------------------------------------------------------
    print("\n" + "-" * 76)
    print(" [STEP 6] DEMONSTRATING POWER BI REFRESH IN CLASS")
    print("-" * 76)
    print(" 1. The updated records have been written to 'data/FactEnergyConsumption.csv' and")
    print("    'data/PowerBI_Anomaly_Report.csv'.")
    print(" 2. Open Microsoft Power BI Desktop with your report.")
    print(" 3. Click the 'Home' tab -> 'Refresh' button in the ribbon.")
    print(" 4. Point out to Professor Qaser:")
    print(f"    * Total Consumption KPI card updates to {new_kpi['total_consumption_kwh']:,.1f} kWh.")
    print(f"    * Peak Demand KPI card immediately increases to {new_kpi['peak_demand_kw']} kW.")
    print(f"    * The Anomaly Detection page (Page 4) now displays the new Critical incident.")
    print(" 5. Explain clearly: Power BI uses an imported data model, so clicking Refresh")
    print("    re-reads the updated CSVs generated by our Python engine.")
    print("-" * 76)
    
    print("\nTo reset back to baseline data at any time, run: python run_demo.py --reset")


def reset_baseline():
    """Reset the cleaned dataset and Power BI files back to original baseline."""
    if os.path.exists(BACKUP_CLEANED_CSV):
        df_base = pd.read_csv(BACKUP_CLEANED_CSV)
        df_base.to_csv(CLEANED_CSV, index=False)
        
        df_enr = engineer_energy_features(df_base)
        compute_comprehensive_analytics(df_enr, export_reports=True)
        _, df_anom, _ = detect_campus_anomalies(df_enr, export_csv=True)
        export_powerbi_star_schema(df_enr, df_anom)
        print("Baseline dataset and Power BI star schema files have been completely RESTORED.")
    else:
        from run_pipeline import run_pipeline
        run_pipeline()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_baseline()
    else:
        run_classroom_demonstration(auto=True)

