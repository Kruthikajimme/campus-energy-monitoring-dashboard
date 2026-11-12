"""
Feature Engineering Module for Campus Energy Analytics
------------------------------------------------------
Enriches cleaned energy records with dimensional foreign keys, temporal hierarchies,
per-capita metrics, carbon footprint estimates, and rolling statistical indicators.
"""

import pandas as pd
import numpy as np

BUILDING_ID_MAP = {
    "Academic Block": "BLD01",
    "Library": "BLD02",
    "Computer Science Block": "BLD03",
    "Laboratory Block": "BLD04",
    "Boys Hostel": "BLD05",
    "Girls Hostel": "BLD06",
    "Canteen": "BLD07"
}

SOURCE_ID_MAP = {
    "Grid": "SRC01",
    "Solar": "SRC02",
    "Generator": "SRC03"
}

CARBON_FACTORS = {
    "Grid": 0.82,       # kg CO2 per kWh (standard regional grid mix)
    "Solar": 0.00,      # Clean renewable
    "Generator": 0.95   # Diesel generator emissions
}


def engineer_energy_features(df):
    """
    Generate derived analytical attributes and Star Schema keys.
    
    Parameters:
        df (pd.DataFrame): Cleaned energy consumption dataframe.
        
    Returns:
        pd.DataFrame: Enriched dataframe ready for Power BI star schema modeling.
    """
    enriched = df.copy()
    
    # Ensure datetime parse
    dt = pd.to_datetime(enriched["timestamp"])
    
    # 1. Primary and Foreign Surrogate Keys for Star Schema
    enriched["reading_id"] = np.arange(1, len(enriched) + 1)
    enriched["date_key"] = dt.dt.strftime("%Y%m%d").astype(int)
    enriched["time_key"] = (dt.dt.hour * 100).astype(int)  # e.g., 900 for 09:00, 1400 for 14:00
    enriched["building_id"] = enriched["building"].map(BUILDING_ID_MAP).fillna("BLD99")
    enriched["source_id"] = enriched["source"].map(SOURCE_ID_MAP).fillna("SRC01")
    
    # 2. Temporal Hierarchies
    enriched["date"] = dt.dt.date
    enriched["year"] = dt.dt.year
    enriched["quarter"] = "Q" + dt.dt.quarter.astype(str)
    enriched["quarter_name"] = dt.dt.year.astype(str) + " Q" + dt.dt.quarter.astype(str)
    enriched["month"] = dt.dt.month
    enriched["month_name"] = dt.dt.strftime("%B")
    enriched["month_year"] = dt.dt.strftime("%b %Y")
    enriched["week_number"] = dt.dt.isocalendar().week.astype(int)
    enriched["day"] = dt.dt.day
    enriched["day_name"] = dt.dt.strftime("%A")
    enriched["day_of_week"] = dt.dt.day_of_week + 1  # 1 = Monday, 7 = Sunday
    enriched["hour"] = dt.dt.hour
    enriched["time_label"] = dt.dt.strftime("%H:00")
    enriched["is_weekend"] = dt.dt.day_of_week >= 5
    
    # Time of Day Classification
    def categorize_time_of_day(h):
        if 0 <= h < 6:
            return "Early Morning / Night"
        elif 6 <= h < 12:
            return "Morning"
        elif 12 <= h < 17:
            return "Afternoon"
        elif 17 <= h < 21:
            return "Evening"
        else:
            return "Late Night"
            
    enriched["time_of_day"] = enriched["hour"].apply(categorize_time_of_day)
    
    # Peak Operational Hours (10:00 to 16:00 on Weekdays)
    enriched["is_peak_hours"] = ((enriched["hour"] >= 10) & (enriched["hour"] <= 16) & (~enriched["is_weekend"])).astype(int)
    
    # 3. Energy Intensity and Per-Capita Features
    # Energy consumed per occupant (avoid divide-by-zero with floor of 1)
    enriched["occupancy_safe"] = enriched["occupancy"].clip(lower=1)
    enriched["kwh_per_occupant"] = (enriched["units_kwh"] / enriched["occupancy_safe"]).round(4)
    enriched = enriched.drop(columns=["occupancy_safe"])
    
    # Carbon footprint (kg CO2)
    enriched["carbon_factor"] = enriched["source"].map(CARBON_FACTORS).fillna(0.82)
    enriched["carbon_kg"] = (enriched["units_kwh"] * enriched["carbon_factor"]).round(2)
    enriched = enriched.drop(columns=["carbon_factor"])
    
    # 4. Rolling 7-Day Moving Average per Building
    # Sort chronologically by building
    enriched = enriched.sort_values(by=["building", "timestamp"]).reset_index(drop=True)
    
    # Rolling 168 hours = 7 days
    enriched["rolling_7d_kwh"] = enriched.groupby("building")["units_kwh"].transform(
        lambda s: s.rolling(window=168, min_periods=24).mean()
    ).round(2)
    
    # Fill initial periods where rolling is NaN with building mean
    b_means = enriched.groupby("building")["units_kwh"].transform("mean")
    enriched["rolling_7d_kwh"] = enriched["rolling_7d_kwh"].fillna(b_means).round(2)
    
    # Energy Intensity Ratio (relative to rolling mean)
    enriched["energy_intensity_index"] = (enriched["units_kwh"] / enriched["rolling_7d_kwh"].clip(lower=1.0)).round(3)
    
    # Sort back to standard chronological order
    enriched = enriched.sort_values(by=["timestamp", "building"]).reset_index(drop=True)
    
    return enriched
