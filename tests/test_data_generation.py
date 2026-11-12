"""
Unit Tests for Dataset Generation Module
----------------------------------------
Tests deterministic reproducibility, record counts, schema integrity,
and building representation.
"""

import unittest
import pandas as pd
from src.data_generator import generate_campus_dataset, BUILDINGS


class TestDataGeneration(unittest.TestCase):
    
    def test_record_count_and_columns(self):
        # Generate small 7-day dataset for rapid testing
        df = generate_campus_dataset(days=7, seed=42, inject_noise=False)
        expected_rows = 7 * 24 * len(BUILDINGS)
        self.assertEqual(len(df), expected_rows)
        
        expected_cols = [
            "timestamp", "building", "meter_id", "units_kwh", "peak_kw",
            "voltage", "occupancy", "source", "temperature", "day_type"
        ]
        for col in expected_cols:
            self.assertIn(col, df.columns)

    def test_all_seven_buildings_present(self):
        df = generate_campus_dataset(days=3, seed=42, inject_noise=False)
        unique_buildings = set(df["building"].unique())
        for b in BUILDINGS:
            self.assertIn(b, unique_buildings)

    def test_reproducibility_with_seed(self):
        df1 = generate_campus_dataset(days=2, seed=42, inject_noise=False)
        df2 = generate_campus_dataset(days=2, seed=42, inject_noise=False)
        pd.testing.assert_frame_equal(df1, df2)

    def test_noise_injection_adds_dirty_data(self):
        df_clean = generate_campus_dataset(days=5, seed=42, inject_noise=False)
        df_noisy = generate_campus_dataset(days=5, seed=42, inject_noise=True)
        # Noisy dataset must have duplicates or nulls
        has_nulls = df_noisy.isna().sum().sum() > 0
        has_dups = df_noisy.duplicated(subset=["timestamp", "building"]).sum() > 0
        self.assertTrue(has_nulls or has_dups)


if __name__ == "__main__":
    unittest.main()

