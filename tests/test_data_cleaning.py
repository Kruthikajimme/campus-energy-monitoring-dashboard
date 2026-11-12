"""
Unit Tests for Data Cleaning and Preprocessing Pipeline
-------------------------------------------------------
Validates duplicate detection, missing value imputation, negative sign correction,
building name standardization, timestamp validation, and IQR outlier treatment.
"""

import unittest
import numpy as np
import pandas as pd
from src.data_cleaning import clean_energy_dataset
from src.data_validation import validate_energy_dataset, inspect_dataset_structure


class TestDataCleaning(unittest.TestCase):
    
    def setUp(self):
        # Create a small controlled dirty dataset
        self.dirty_data = pd.DataFrame([
            # Valid row 1
            {"timestamp": "2026-10-01 10:00:00", "building": "Academic Block", "meter_id": "MTR-ACAD", "units_kwh": 95.0, "peak_kw": 120.0, "voltage": 230.0, "occupancy": 300, "source": "Grid", "temperature": 28.0, "day_type": "Weekday"},
            # Duplicate row 2 (identical timestamp + building)
            {"timestamp": "2026-10-01 10:00:00", "building": "Academic Block", "meter_id": "MTR-ACAD", "units_kwh": 95.0, "peak_kw": 120.0, "voltage": 230.0, "occupancy": 300, "source": "Grid", "temperature": 28.0, "day_type": "Weekday"},
            # Negative consumption reading
            {"timestamp": "2026-10-01 11:00:00", "building": "Library", "meter_id": "MTR-LIB", "units_kwh": -45.5, "peak_kw": 55.0, "voltage": 230.0, "occupancy": 150, "source": "Grid", "temperature": 29.0, "day_type": "Weekday"},
            # Inconsistent building name casing and trailing space
            {"timestamp": "2026-10-01 12:00:00", "building": "computer science block", "meter_id": "MTR-CS", "units_kwh": 140.0, "peak_kw": 175.0, "voltage": 230.0, "occupancy": 220, "source": "Grid", "temperature": 30.0, "day_type": "Weekday"},
            # Invalid timestamp
            {"timestamp": "INVALID_DATE_STRING", "building": "Laboratory Block", "meter_id": "MTR-LAB", "units_kwh": 110.0, "peak_kw": 140.0, "voltage": 230.0, "occupancy": 80, "source": "Grid", "temperature": 29.5, "day_type": "Weekday"},
            # Missing value in units_kwh
            {"timestamp": "2026-10-01 13:00:00", "building": "Canteen", "meter_id": "MTR-CANT", "units_kwh": np.nan, "peak_kw": 70.0, "voltage": 230.0, "occupancy": 120, "source": "Solar", "temperature": 32.0, "day_type": "Weekday"},
            # Extreme voltage glitch
            {"timestamp": "2026-10-01 14:00:00", "building": "Boys Hostel", "meter_id": "MTR-BHOST", "units_kwh": 65.0, "peak_kw": 80.0, "voltage": 0.0, "occupancy": 350, "source": "Grid", "temperature": 31.0, "day_type": "Weekday"}
        ])

    def test_pre_cleaning_validation_flags_issues(self):
        diag = validate_energy_dataset(self.dirty_data)
        self.assertFalse(diag["validation_passed"])
        self.assertEqual(diag["duplicate_rows_count"], 1)
        self.assertEqual(diag["invalid_timestamps_count"], 1)
        self.assertEqual(diag["negative_kwh_count"], 1)

    def test_duplicate_removal(self):
        cleaned_df, report = clean_energy_dataset(self.dirty_data)
        self.assertEqual(report["duplicate_records_removed"], 1)

    def test_invalid_timestamp_dropped(self):
        cleaned_df, report = clean_energy_dataset(self.dirty_data)
        self.assertEqual(report["invalid_timestamps_removed"], 1)
        self.assertFalse((cleaned_df["timestamp"] == "INVALID_DATE_STRING").any())

    def test_negative_reading_correction(self):
        cleaned_df, report = clean_energy_dataset(self.dirty_data)
        self.assertGreaterEqual(report["negative_readings_corrected_or_removed"], 1)
        self.assertTrue((cleaned_df["units_kwh"] >= 0).all())

    def test_building_name_standardization(self):
        cleaned_df, report = clean_energy_dataset(self.dirty_data)
        self.assertIn("Computer Science Block", cleaned_df["building"].values)
        self.assertNotIn("computer science block", cleaned_df["building"].values)

    def test_missing_value_imputed(self):
        cleaned_df, report = clean_energy_dataset(self.dirty_data)
        self.assertFalse(cleaned_df["units_kwh"].isna().any())

    def test_voltage_correction(self):
        cleaned_df, report = clean_energy_dataset(self.dirty_data)
        self.assertTrue((cleaned_df["voltage"] >= 180.0).all())


if __name__ == "__main__":
    unittest.main()
