"""
Power BI Star Schema Dataset Exporter & Data Dictionary Generator
-----------------------------------------------------------------
Transforms cleansed campus energy records into normalized Star Schema dimensional tables
(FactEnergyConsumption, DimBuilding, DimDate, DimTime, DimEnergySource),
anomaly reports, and generates an exhaustive Microsoft Excel Data Dictionary (.xlsx).
"""

import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from src.data_generator import BUILDING_PROFILES
from src.feature_engineering import BUILDING_ID_MAP, SOURCE_ID_MAP, CARBON_FACTORS

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
POWERBI_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "powerbi", "data")


def export_powerbi_star_schema(df_enriched, anomalies_df=None):
    """
    Generate and export Star Schema CSV tables and the Excel Data Dictionary.
    
    Parameters:
        df_enriched (pd.DataFrame): Enriched dataset containing dimensional keys.
        anomalies_df (pd.DataFrame): Dataframe of detected anomalies.
        
    Returns:
        dict: Paths of exported datasets.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(POWERBI_DATA_DIR, exist_ok=True)
    
    # -------------------------------------------------------------------------
    # 1. DimBuilding Table
    # -------------------------------------------------------------------------
    dim_building_rows = []
    for b_name, prof in BUILDING_PROFILES.items():
        dim_building_rows.append({
            "building_id": prof["building_id"],
            "building_name": b_name,
            "building_type": prof["building_type"],
            "design_capacity": prof["capacity_occ"],
            "meter_id": f"MTR-{prof['building_id']}",
            "baseload_kw": prof["base_kwh"],
            "active_hours": f"{prof.get('active_start', 8):02d}:00 - {prof.get('active_end', 18):02d}:00"
        })
    df_dim_building = pd.DataFrame(dim_building_rows)
    
    # -------------------------------------------------------------------------
    # 2. DimDate Table
    # -------------------------------------------------------------------------
    dt_series = pd.to_datetime(df_enriched["timestamp"])
    min_date = dt_series.min().date()
    max_date = dt_series.max().date()
    
    date_range = pd.date_range(start=min_date, end=max_date, freq="D")
    dim_date_rows = []
    for single_date in date_range:
        date_key = int(single_date.strftime("%Y%m%d"))
        is_wknd = single_date.dayofweek >= 5
        day_type = "Weekend" if is_wknd else "Weekday"
        dim_date_rows.append({
            "date_key": date_key,
            "date": single_date.strftime("%Y-%m-%d"),
            "year": single_date.year,
            "quarter": f"Q{single_date.quarter}",
            "quarter_name": f"{single_date.year} Q{single_date.quarter}",
            "month": single_date.month,
            "month_name": single_date.strftime("%B"),
            "month_year": single_date.strftime("%b %Y"),
            "week_number": int(single_date.isocalendar().week),
            "day": single_date.day,
            "day_name": single_date.strftime("%A"),
            "day_of_week": single_date.dayofweek + 1,
            "is_weekend": "Yes" if is_wknd else "No",
            "is_holiday": "No",
            "day_type": day_type
        })
    df_dim_date = pd.DataFrame(dim_date_rows)
    
    # -------------------------------------------------------------------------
    # 3. DimTime Table (24 Hourly Intervals)
    # -------------------------------------------------------------------------
    dim_time_rows = []
    for h in range(24):
        time_key = h * 100
        if 0 <= h < 6:
            tod = "Early Morning / Night"
        elif 6 <= h < 12:
            tod = "Morning"
        elif 12 <= h < 17:
            tod = "Afternoon"
        elif 17 <= h < 21:
            tod = "Evening"
        else:
            tod = "Late Night"
            
        dim_time_rows.append({
            "time_key": time_key,
            "hour": h,
            "hour_label": f"{h:02d}:00",
            "time_of_day": tod,
            "is_peak_hours": "Yes" if (10 <= h <= 16) else "No"
        })
    df_dim_time = pd.DataFrame(dim_time_rows)
    
    # -------------------------------------------------------------------------
    # 4. DimEnergySource Table
    # -------------------------------------------------------------------------
    dim_source_rows = [
        {
            "source_id": "SRC01",
            "source_name": "Grid",
            "is_renewable": "No",
            "carbon_factor_kg_per_kwh": CARBON_FACTORS["Grid"],
            "description": "State utility electricity grid feed via main campus substation (primary baseload)"
        },
        {
            "source_id": "SRC02",
            "source_name": "Solar",
            "is_renewable": "Yes",
            "carbon_factor_kg_per_kwh": CARBON_FACTORS["Solar"],
            "description": "Rooftop grid-tied photovoltaic generation array during daylight sun hours"
        },
        {
            "source_id": "SRC03",
            "source_name": "Generator",
            "is_renewable": "No",
            "carbon_factor_kg_per_kwh": CARBON_FACTORS["Generator"],
            "description": "Campus emergency diesel generator backup during grid curtailment or maintenance"
        }
    ]
    df_dim_source = pd.DataFrame(dim_source_rows)
    
    # -------------------------------------------------------------------------
    # 5. FactEnergyConsumption Table
    # -------------------------------------------------------------------------
    fact_cols = [
        "reading_id",
        "timestamp",
        "date_key",
        "time_key",
        "building_id",
        "source_id",
        "meter_id",
        "units_kwh",
        "peak_kw",
        "voltage",
        "occupancy",
        "temperature",
        "kwh_per_occupant",
        "carbon_kg",
        "rolling_7d_kwh",
        "energy_intensity_index"
    ]
    df_fact = df_enriched[[c for c in fact_cols if c in df_enriched.columns]].copy()
    
    # Merge anomaly flag if anomalies_df exists
    if anomalies_df is not None and not anomalies_df.empty:
        # Create a set of (timestamp, building_id) that are anomalies
        anom_set = set(zip(anomalies_df["timestamp"], anomalies_df["building_id"]))
        anom_sev_map = dict(zip(zip(anomalies_df["timestamp"], anomalies_df["building_id"]), anomalies_df["severity"]))
        
        is_anom_list = []
        sev_list = []
        for _, row in df_fact.iterrows():
            key = (row["timestamp"], row["building_id"])
            if key in anom_set:
                is_anom_list.append(1)
                sev_list.append(anom_sev_map.get(key, "Medium"))
            else:
                is_anom_list.append(0)
                sev_list.append("None")
                
        df_fact["is_anomaly"] = is_anom_list
        df_fact["anomaly_severity"] = sev_list
    else:
        df_fact["is_anomaly"] = 0
        df_fact["anomaly_severity"] = "None"
        
    # Rename carbon_kg to carbon_emissions_kg for clarity
    if "carbon_kg" in df_fact.columns:
        df_fact.rename(columns={"carbon_kg": "carbon_emissions_kg"}, inplace=True)
        
    # Save CSVs in both data/ and powerbi/data/
    csv_destinations = [DATA_DIR, POWERBI_DATA_DIR]
    saved_paths = {}
    
    for dest in csv_destinations:
        df_fact.to_csv(os.path.join(dest, "FactEnergyConsumption.csv"), index=False)
        df_dim_building.to_csv(os.path.join(dest, "DimBuilding.csv"), index=False)
        df_dim_date.to_csv(os.path.join(dest, "DimDate.csv"), index=False)
        df_dim_time.to_csv(os.path.join(dest, "DimTime.csv"), index=False)
        df_dim_source.to_csv(os.path.join(dest, "DimEnergySource.csv"), index=False)
        
        # Denormalized single-file export for quick inspection
        df_enriched.to_csv(os.path.join(dest, "powerbi_energy_dataset.csv"), index=False)
        
    saved_paths["fact"] = os.path.join(DATA_DIR, "FactEnergyConsumption.csv")
    saved_paths["dim_building"] = os.path.join(DATA_DIR, "DimBuilding.csv")
    saved_paths["dim_date"] = os.path.join(DATA_DIR, "DimDate.csv")
    saved_paths["dim_time"] = os.path.join(DATA_DIR, "DimTime.csv")
    saved_paths["dim_source"] = os.path.join(DATA_DIR, "DimEnergySource.csv")
    
    # -------------------------------------------------------------------------
    # 6. Generate Excel Data Dictionary (data/data_dictionary.xlsx)
    # -------------------------------------------------------------------------
    dict_path = os.path.join(DATA_DIR, "data_dictionary.xlsx")
    generate_excel_data_dictionary(
        dict_path, df_fact, df_dim_building, df_dim_date, df_dim_time, df_dim_source, anomalies_df
    )
    saved_paths["data_dictionary"] = dict_path
    
    return saved_paths


def generate_excel_data_dictionary(filepath, df_fact, df_bld, df_date, df_time, df_source, df_anom):
    """
    Generate an exhaustive corporate-styled Excel Data Dictionary workbook.
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # remove default sheet
    
    font_title = Font(name="Calibri", size=15, bold=True, color="0F172A")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="64748B")
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=11, bold=True, color="0F172A")
    font_regular = Font(name="Calibri", size=10, color="1E293B")
    
    fill_navy = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    fill_green = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
    fill_light_gray = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    
    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )
    
    # Sheet 1: Model Architecture Catalog
    ws_cat = wb.create_sheet(title="Model Overview")
    ws_cat.views.sheetView[0].showGridLines = True
    ws_cat["A1"] = "CAMPUS ENERGY ANALYTICS: POWER BI STAR SCHEMA DATA DICTIONARY"
    ws_cat["A1"].font = font_title
    ws_cat["A2"] = "Relational architecture, foreign key mappings, and table specifications for Microsoft Power BI"
    ws_cat["A2"].font = font_subtitle
    
    cat_headers = ["Table Name", "Table Type", "Primary Key", "Foreign Keys", "Row Count", "Description"]
    for col_idx, h in enumerate(cat_headers, 1):
        c = ws_cat.cell(row=4, column=col_idx, value=h)
        c.font = font_header
        c.fill = fill_navy
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = thin_border
        
    catalog_rows = [
        ("FactEnergyConsumption", "Fact Table", "reading_id", "date_key, time_key, building_id, source_id", len(df_fact), "Hourly campus electricity consumption readings, demand measurements, and quality metrics."),
        ("DimBuilding", "Dimension", "building_id", "None", len(df_bld), "University facilities master table (building type, nominal baseload, active working hours)."),
        ("DimDate", "Dimension", "date_key", "None", len(df_date), "Continuous calendar date table for time-intelligence calculations (quarter, month, day name, weekend)."),
        ("DimTime", "Dimension", "time_key", "None", len(df_time), "24-hour diurnal time table (hour label, time-of-day classification, peak hour flag)."),
        ("DimEnergySource", "Dimension", "source_id", "None", len(df_source), "Power source classification table (Utility Grid, Rooftop Solar, Emergency Generator, Carbon factor)."),
        ("PowerBI_Anomaly_Report", "Diagnostic Table", "anomaly_id", "date_key, time_key, building_id", len(df_anom) if df_anom is not None else 0, "Statistical outlier events flagged via IQR and rolling Z-score with recommended engineering actions.")
    ]
    
    for r_idx, r in enumerate(catalog_rows, 5):
        for c_idx, val in enumerate(r, 1):
            cell = ws_cat.cell(row=r_idx, column=c_idx, value=val)
            cell.font = font_regular if c_idx > 1 else font_bold
            cell.border = thin_border
            if c_idx in [2, 5]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if r_idx % 2 == 0:
                cell.fill = fill_light_gray
                
    # Function to create table metadata sheet
    def create_meta_sheet(sheet_title, table_title, headers, rows):
        ws = wb.create_sheet(title=sheet_title)
        ws.views.sheetView[0].showGridLines = True
        ws["A1"] = table_title
        ws["A1"].font = font_title
        
        for c_idx, h in enumerate(headers, 1):
            cell = ws.cell(row=3, column=c_idx, value=h)
            cell.font = font_header
            cell.fill = fill_green if "Fact" not in sheet_title else fill_navy
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
            
        for r_idx, r in enumerate(rows, 4):
            for c_idx, val in enumerate(r, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=val)
                cell.font = font_regular if c_idx != 1 else font_bold
                cell.border = thin_border
                if c_idx in [2, 3, 5]:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                if r_idx % 2 == 0:
                    cell.fill = fill_light_gray
                    
    meta_headers = ["Column Name", "Data Type", "Constraint / Role", "Unit / Format", "Sample Value", "Detailed Description"]
    
    fact_meta = [
        ("reading_id", "Integer", "Primary Key", "Integer", "1", "Unique surrogate key identifying each hourly telemetry observation."),
        ("timestamp", "DateTime", "Telemetry Time", "YYYY-MM-DD HH:MM:SS", "2026-10-15 14:00:00", "Chronological timestamp of the cumulative hourly energy reading."),
        ("date_key", "Integer", "Foreign Key -> DimDate", "YYYYMMDD", "20261015", "Foreign key linking reading to calendar dimension."),
        ("time_key", "Integer", "Foreign Key -> DimTime", "HH00", "1400", "Foreign key linking reading to diurnal hour dimension."),
        ("building_id", "String", "Foreign Key -> DimBuilding", "Text", "BLD03", "Foreign key identifying facility (e.g. BLD03 = Computer Science Block)."),
        ("source_id", "String", "Foreign Key -> DimEnergySource", "Text", "SRC01", "Foreign key identifying power generation source."),
        ("meter_id", "String", "Hardware ID", "Alphanumeric", "MTR-CS-301", "Submeter physical hardware serial/tag number."),
        ("units_kwh", "Decimal", "Measure (Fact)", "Kilowatt-hours (kWh)", "145.20", "Active electricity consumption during the monitored hour."),
        ("peak_kw", "Decimal", "Measure (Fact)", "Kilowatts (kW)", "182.50", "Maximum instantaneous active power demand registered during the hour."),
        ("voltage", "Decimal", "Electrical Telemetry", "Volts (V)", "230.2", "Supply voltage (nominal 230V single phase)."),
        ("occupancy", "Integer", "Sensor Metric", "Headcount", "180", "Estimated or sensor-measured occupant count in facility."),
        ("temperature", "Decimal", "Environmental Metric", "Degrees Celsius (°C)", "31.5", "Ambient outdoor temperature influencing cooling HVAC loads."),
        ("kwh_per_occupant", "Decimal", "Derived Metric", "kWh / Person", "0.8067", "Normalized consumption intensity per occupant."),
        ("carbon_emissions_kg", "Decimal", "Environmental Metric", "kg CO2", "119.06", "Estimated carbon emissions calculated based on generation source."),
        ("rolling_7d_kwh", "Decimal", "Statistical Feature", "kWh", "125.40", "Trailing 7-day (168-hour) moving baseline average."),
        ("energy_intensity_index", "Decimal", "Statistical Feature", "Ratio", "1.158", "Ratio of current load to rolling 7-day average."),
        ("is_anomaly", "Integer", "Diagnostic Flag", "Binary (0 or 1)", "0", "Binary indicator (1 if statistical outlier/surge detected, 0 otherwise)."),
        ("anomaly_severity", "String", "Diagnostic Attribute", "Categorical", "None", "Severity level: None, Low, Medium, High, or Critical.")
    ]
    create_meta_sheet("FactEnergyConsumption", "TABLE SPECIFICATION: FACTENERGYCONSUMPTION", meta_headers, fact_meta)
    
    bld_meta = [
        ("building_id", "String", "Primary Key", "Text (PK)", "BLD01", "Unique alphanumeric identifier for the university building."),
        ("building_name", "String", "Descriptive Attribute", "Text", "Academic Block", "Full formal name of the campus facility."),
        ("building_type", "String", "Categorical Hierarchy", "Text", "Academic & Teaching", "Functional classification of the building."),
        ("design_capacity", "Integer", "Physical Attribute", "Headcount", "800", "Maximum rated occupancy design capacity."),
        ("meter_id", "String", "Hardware Reference", "Text", "MTR-ACAD-101", "Dedicated main submeter hardware identifier."),
        ("baseload_kw", "Decimal", "Electrical Attribute", "kW", "45.0", "Nominal baseload power requirement for minimum operations."),
        ("active_hours", "String", "Operational Attribute", "Time Interval", "08:00 - 18:00", "Standard scheduled active working hours on weekdays.")
    ]
    create_meta_sheet("DimBuilding", "TABLE SPECIFICATION: DIMBUILDING", meta_headers, bld_meta)
    
    date_meta = [
        ("date_key", "Integer", "Primary Key", "YYYYMMDD", "20261015", "Unique integer date key linking to Fact table."),
        ("date", "Date", "Calendar Date", "YYYY-MM-DD", "2026-10-15", "Calendar date object for standard date hierarchies."),
        ("year", "Integer", "Year Hierarchy", "YYYY", "2026", "Calendar year."),
        ("quarter", "String", "Quarter Hierarchy", "Text (Q1-Q4)", "Q4", "Calendar quarter."),
        ("quarter_name", "String", "Quarter Hierarchy", "Text", "2026 Q4", "Year and quarter concatenated."),
        ("month", "Integer", "Month Hierarchy", "Integer (1-12)", "10", "Calendar month number (used for sorting Month Name)."),
        ("month_name", "String", "Month Hierarchy", "Text", "October", "Full month name."),
        ("month_year", "String", "Temporal Slicer", "Text", "Oct 2026", "Short month and year abbreviation."),
        ("week_number", "Integer", "Week Hierarchy", "Integer (1-52)", "42", "ISO calendar week number."),
        ("day", "Integer", "Day Hierarchy", "Integer (1-31)", "15", "Day of the month."),
        ("day_name", "String", "Day Hierarchy", "Text", "Thursday", "Full day of the week name."),
        ("day_of_week", "Integer", "Sort Column", "Integer (1-7)", "4", "Day of week number (1 = Monday to 7 = Sunday)."),
        ("is_weekend", "String", "Binary Attribute", "Yes / No", "No", "Flag indicating whether date is Saturday or Sunday."),
        ("is_holiday", "String", "Binary Attribute", "Yes / No", "No", "Flag indicating scheduled campus or national holiday."),
        ("day_type", "String", "Operational Slicer", "Categorical", "Weekday", "Operational day classification: Weekday, Weekend, or Holiday.")
    ]
    create_meta_sheet("DimDate", "TABLE SPECIFICATION: DIMDATE", meta_headers, date_meta)
    
    time_meta = [
        ("time_key", "Integer", "Primary Key", "HH00", "1400", "Unique integer time key linking to Fact table."),
        ("hour", "Integer", "Diurnal Hierarchy", "Integer (0-23)", "14", "Hour of the day in 24-hour military notation."),
        ("hour_label", "String", "Axis Display", "HH:00", "14:00", "Formatted hour label for Chart.js and Power BI axes."),
        ("time_of_day", "String", "Categorical Group", "Text", "Afternoon", "Time interval: Early Morning, Morning, Afternoon, Evening, Night."),
        ("is_peak_hours", "String", "Operational Flag", "Yes / No", "Yes", "Identifies campus peak operational demand window (10:00 - 16:00).")
    ]
    create_meta_sheet("DimTime", "TABLE SPECIFICATION: DIMTIME", meta_headers, time_meta)
    
    source_meta = [
        ("source_id", "String", "Primary Key", "Text (PK)", "SRC01", "Unique alphanumeric energy source key."),
        ("source_name", "String", "Source Slicer", "Text", "Grid", "Power source: Grid, Solar, or Generator."),
        ("is_renewable", "String", "Sustainability Flag", "Yes / No", "No", "Clean renewable provenance flag."),
        ("carbon_factor_kg_per_kwh", "Decimal", "Carbon Metric", "kg CO2 / kWh", "0.82", "Emissions factor applied to compute carbon footprint."),
        ("description", "String", "Descriptive Text", "Text", "Utility Grid...", "Operational explanation of power source.")
    ]
    create_meta_sheet("DimEnergySource", "TABLE SPECIFICATION: DIMENERGYSOURCE", meta_headers, source_meta)
    
    # Auto-adjust column widths across all sheets
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 65)
            
    wb.save(filepath)
    return filepath

