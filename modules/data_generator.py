"""
Data Generator Module for Campus Energy Consumption Monitoring & Analytics Dashboard
-----------------------------------------------------------------------------------
Generates realistic, reproducible simulated hourly electricity consumption data
for seven campus buildings across a 90-day period.

NOTE: This dataset is purely SIMULATED for academic demonstration, analytics modeling,
and dashboard development. It does not represent actual physical utility readings.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

BUILDINGS = [
    "Academic Block",
    "Library",
    "Computer Science Block",
    "Laboratory Block",
    "Boys Hostel",
    "Girls Hostel",
    "Canteen"
]

METER_MAPPING = {
    "Academic Block": "MTR-ACAD-101",
    "Library": "MTR-LIB-201",
    "Computer Science Block": "MTR-CS-301",
    "Laboratory Block": "MTR-LAB-401",
    "Boys Hostel": "MTR-BHOST-501",
    "Girls Hostel": "MTR-GHOST-601",
    "Canteen": "MTR-CANT-701"
}

# Building baseload (kW) and peak multiplier parameters
BUILDING_PROFILES = {
    "Academic Block": {
        "base_kwh": 45.0,
        "peak_kwh": 140.0,
        "capacity_occ": 800,
        "active_start": 8,
        "active_end": 18,
        "noise_std": 6.0
    },
    "Library": {
        "base_kwh": 30.0,
        "peak_kwh": 95.0,
        "capacity_occ": 450,
        "active_start": 8,
        "active_end": 22,
        "noise_std": 4.5
    },
    "Computer Science Block": {
        # High baseload due to servers, cloud racks, and air conditioned labs
        "base_kwh": 70.0,
        "peak_kwh": 185.0,
        "capacity_occ": 600,
        "active_start": 8,
        "active_end": 20,
        "noise_std": 8.0
    },
    "Laboratory Block": {
        # High power equipment, autoclaves, high-voltage test rigs, compressors
        "base_kwh": 55.0,
        "peak_kwh": 175.0,
        "capacity_occ": 350,
        "active_start": 9,
        "active_end": 17,
        "noise_std": 9.0
    },
    "Boys Hostel": {
        # Residential profile: low during daytime, peaks in morning & late evening
        "base_kwh": 25.0,
        "peak_kwh": 110.0,
        "capacity_occ": 500,
        "morning_peak": (6, 9),
        "night_peak": (18, 24),
        "noise_std": 5.5
    },
    "Girls Hostel": {
        # Residential profile: low during daytime, peaks in morning & late evening
        "base_kwh": 25.0,
        "peak_kwh": 105.0,
        "capacity_occ": 450,
        "morning_peak": (6, 9),
        "night_peak": (18, 24),
        "noise_std": 5.0
    },
    "Canteen": {
        # Dining profile: peaks during breakfast, lunch, tea, dinner
        "base_kwh": 20.0,
        "peak_kwh": 90.0,
        "capacity_occ": 300,
        "meal_peaks": [(7, 9), (12, 14), (17, 18), (19, 21)],
        "noise_std": 4.0
    }
}


def generate_campus_dataset(days=90, seed=42, inject_noise=True):
    """
    Generate synthetic hourly records for all 7 campus buildings.
    
    Parameters:
        days (int): Number of days to simulate (default 90 days = ~15,120 records).
        seed (int): Fixed random seed for reproducibility.
        inject_noise (bool): Whether to inject dirty records for data-cleaning demonstrations.
        
    Returns:
        pd.DataFrame: Raw synthetic dataset.
    """
    random.seed(seed)
    np.random.seed(seed)
    
    # End date is yesterday; start date is (days) days prior
    end_date = datetime.now().replace(minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days)
    
    records = []
    
    # Predefined national / campus holiday dates in the simulated range
    holiday_days = {15, 45, 72}
    
    for day_idx in range(days):
        current_day = start_date + timedelta(days=day_idx)
        weekday = current_day.weekday() # 0 = Monday, 6 = Sunday
        is_weekend = weekday >= 5
        is_holiday = day_idx in holiday_days
        
        if is_holiday:
            day_type = "Holiday"
        elif is_weekend:
            day_type = "Weekend"
        else:
            day_type = "Weekday"
            
        # Daily ambient base temperature curve (degrees Celsius)
        # Seasonal swing + daily diurnal cycle
        seasonal_temp = 26.0 + 5.0 * np.sin(2 * np.pi * day_idx / 365.0)
        
        for hour in range(24):
            timestamp = current_day.replace(hour=hour)
            
            # Hourly temperature cycle: coolest at 5 AM, warmest at 2 PM (14:00)
            hour_temp_delta = 7.0 * np.sin((hour - 8) * np.pi / 12.0)
            ambient_temp = round(float(seasonal_temp + hour_temp_delta + np.random.normal(0, 0.6)), 1)
            ambient_temp = max(18.0, min(ambient_temp, 42.0))
            
            # Solar availability: only daytime from 7:00 to 17:00 with peak at noon
            if 7 <= hour <= 17:
                solar_factor = max(0.0, np.sin((hour - 7) * np.pi / 10.0))
            else:
                solar_factor = 0.0
                
            for building in BUILDINGS:
                meter_id = METER_MAPPING[building]
                profile = BUILDING_PROFILES[building]
                
                # Calculate occupancy and consumption multiplier based on building type
                occ = 0
                load_factor = 0.0
                
                if building in ["Academic Block", "Computer Science Block", "Laboratory Block"]:
                    if day_type == "Weekday":
                        if profile["active_start"] <= hour <= profile["active_end"]:
                            # Peak working hours
                            hour_progress = (hour - profile["active_start"]) / (profile["active_end"] - profile["active_start"])
                            activity_curve = np.sin(hour_progress * np.pi)
                            load_factor = 0.55 + 0.45 * activity_curve
                            occ_ratio = 0.60 + 0.38 * activity_curve + np.random.uniform(-0.05, 0.05)
                        elif hour in [7, 19]:
                            load_factor = 0.25
                            occ_ratio = 0.10
                        else:
                            load_factor = 0.05
                            occ_ratio = 0.02
                    elif day_type == "Weekend":
                        # Partial activity on weekends (projects, library, graduate research)
                        if 10 <= hour <= 16:
                            load_factor = 0.20
                            occ_ratio = 0.15
                        else:
                            load_factor = 0.03
                            occ_ratio = 0.01
                    else: # Holiday
                        load_factor = 0.03
                        occ_ratio = 0.01
                        
                    occ = int(profile["capacity_occ"] * max(0.0, min(1.0, occ_ratio)))
                    
                elif building == "Library":
                    if day_type == "Weekday":
                        if profile["active_start"] <= hour <= profile["active_end"]:
                            activity_curve = np.sin(((hour - 8) / 14.0) * np.pi)
                            load_factor = 0.40 + 0.60 * activity_curve
                            occ_ratio = 0.45 + 0.50 * activity_curve
                        else:
                            load_factor = 0.08
                            occ_ratio = 0.02
                    else: # Weekend / Holiday reading
                        if 9 <= hour <= 20:
                            load_factor = 0.35
                            occ_ratio = 0.30
                        else:
                            load_factor = 0.05
                            occ_ratio = 0.01
                    occ = int(profile["capacity_occ"] * max(0.0, min(1.0, occ_ratio)))
                    
                elif building in ["Boys Hostel", "Girls Hostel"]:
                    # Residential: inverted activity schedule
                    if 6 <= hour <= 8: # Morning getting ready
                        load_factor = 0.70 + 0.25 * np.random.uniform(0, 1)
                        occ_ratio = 0.90
                    elif 9 <= hour <= 16: # Classes time
                        load_factor = 0.20 if day_type == "Weekday" else 0.60
                        occ_ratio = 0.15 if day_type == "Weekday" else 0.70
                    elif 17 <= hour <= 23: # Evening studies & relaxation
                        load_factor = 0.75 + 0.25 * np.random.uniform(0, 1)
                        occ_ratio = 0.95
                    else: # Night sleeping
                        load_factor = 0.30
                        occ_ratio = 0.98
                    occ = int(profile["capacity_occ"] * max(0.0, min(1.0, occ_ratio)))
                    
                elif building == "Canteen":
                    # Canteen meal times
                    is_meal = False
                    for (start_h, end_h) in profile["meal_peaks"]:
                        if start_h <= hour <= end_h:
                            is_meal = True
                            break
                    if is_meal:
                        load_factor = 0.85 + np.random.uniform(-0.1, 0.15)
                        occ_ratio = 0.80 if day_type == "Weekday" else 0.50
                    elif 9 <= hour <= 21:
                        load_factor = 0.30
                        occ_ratio = 0.20
                    else:
                        load_factor = 0.05
                        occ_ratio = 0.0
                    occ = int(profile["capacity_occ"] * max(0.0, min(1.0, occ_ratio)))
                
                # Temperature sensitivity (HVAC load increase above 28°C)
                hvac_boost = 0.0
                if ambient_temp > 28.0 and building in ["Academic Block", "Computer Science Block", "Library", "Laboratory Block"]:
                    hvac_boost = (ambient_temp - 28.0) * 2.2
                    
                # Calculate consumption in kWh
                base = profile["base_kwh"]
                peak_range = profile["peak_kwh"] - base
                mean_kwh = base + (peak_range * load_factor) + hvac_boost
                units_kwh = float(np.random.normal(mean_kwh, profile["noise_std"]))
                units_kwh = max(profile["base_kwh"] * 0.7, units_kwh)
                
                # Peak power demand (kW) is typically 1.15x - 1.40x the average hourly kWh
                peak_kw = units_kwh * np.random.uniform(1.15, 1.38)
                
                # Supply voltage nominal 230V with normal distribution (standard deviation ~ 3V)
                voltage = round(float(np.random.normal(230.0, 3.2)), 1)
                
                # Energy source determination: Grid primary, Solar during sun hours, rare Generator
                r_src = np.random.random()
                if solar_factor > 0.35 and r_src < (solar_factor * 0.55):
                    source = "Solar"
                elif r_src > 0.985:
                    source = "Generator"
                else:
                    source = "Grid"
                    
                records.append({
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "building": building,
                    "meter_id": meter_id,
                    "units_kwh": round(units_kwh, 2),
                    "peak_kw": round(peak_kw, 2),
                    "voltage": voltage,
                    "occupancy": occ,
                    "source": source,
                    "temperature": ambient_temp,
                    "day_type": day_type
                })
                
    df = pd.DataFrame(records)
    
    # Introduce controlled realistic synthetic anomalies and noise for cleaning demonstration
    if inject_noise:
        n_rows = len(df)
        
        # 1. Missing values (NaN in units_kwh, occupancy, voltage) ~ 0.5%
        missing_idx = random.sample(range(n_rows), int(n_rows * 0.005))
        for idx in missing_idx:
            col_choice = random.choice(["units_kwh", "occupancy", "voltage"])
            df.at[idx, col_choice] = np.nan
            
        # 2. Duplicate records ~ 0.4%
        dup_indices = random.sample(range(n_rows), int(n_rows * 0.004))
        dup_rows = df.iloc[dup_indices].copy()
        df = pd.concat([df, dup_rows], ignore_index=True)
        
        # 3. Invalid/negative readings ~ 0.2%
        neg_indices = random.sample(range(len(df)), int(n_rows * 0.002))
        for idx in neg_indices:
            df.at[idx, "units_kwh"] = -abs(round(float(df.at[idx, "units_kwh"] or 25.0) * 0.5, 2))
            
        # 4. Outliers (IQR detection candidates: severe sensor spikes) ~ 0.3%
        outlier_indices = random.sample(range(len(df)), int(n_rows * 0.003))
        for idx in outlier_indices:
            df.at[idx, "units_kwh"] = round(float(df.at[idx, "units_kwh"] or 80.0) * random.uniform(3.5, 6.0), 2)
            df.at[idx, "peak_kw"] = round(float(df.at[idx, "units_kwh"]) * 1.3, 2)
            
        # 5. Building name formatting inconsistencies ~ 0.3%
        name_inconsistencies = random.sample(range(len(df)), int(n_rows * 0.003))
        for idx in name_inconsistencies:
            b_name = df.at[idx, "building"]
            if b_name == "Academic Block":
                df.at[idx, "building"] = "academic block"
            elif b_name == "Computer Science Block":
                df.at[idx, "building"] = "Computer Science  Block"
            elif b_name == "Library":
                df.at[idx, "building"] = "LIBRARY "
                
        # 6. Voltage anomalies (voltage dips or surges) ~ 0.2%
        volt_indices = random.sample(range(len(df)), int(n_rows * 0.002))
        for idx in volt_indices:
            df.at[idx, "voltage"] = random.choice([0.0, 140.0, 310.0])
            
        # 7. A couple of malformed timestamp strings ~ 0.1%
        ts_indices = random.sample(range(len(df)), min(8, int(n_rows * 0.001)))
        for idx in ts_indices:
            df.at[idx, "timestamp"] = "INVALID_TIMESTAMP"
            
    return df

