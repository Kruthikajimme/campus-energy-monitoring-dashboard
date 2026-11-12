"""
Unit Tests for Anomaly Detection Module
---------------------------------------
Validates statistical anomaly detection, severity classification,
and spike identification.
"""

import unittest
import pandas as pd
from src.anomaly_detection import detect_campus_anomalies


class TestAnomalyDetection(unittest.TestCase):
    
    def setUp(self):
        # Baseline normal dataset for 3 days across 2 buildings
        rows = []
        for d in range(1, 4):
            for h in range(24):
                ts = f"2026-10-{d:02d} {h:02d}:00:00"
                for b in ["Academic Block", "Computer Science Block"]:
                    base = 60.0 if b == "Academic Block" else 90.0
                    rows.append({
                        "timestamp": ts,
                        "building": b,
                        "meter_id": f"MTR-{b[:4]}",
                        "units_kwh": base + (h * 1.5),
                        "peak_kw": (base + (h * 1.5)) * 1.25,
                        "voltage": 230.0,
                        "occupancy": 100,
                        "source": "Grid",
                        "temperature": 28.0,
                        "day_type": "Weekday"
                    })
        self.df = pd.DataFrame(rows)

    def test_extreme_spike_detection(self):
        # Inject an extreme anomaly into academic block
        spike_df = self.df.copy()
        spike_df.loc[len(spike_df)] = {
            "timestamp": "2026-10-03 23:00:00",
            "building": "Academic Block",
            "meter_id": "MTR-ACAD",
            "units_kwh": 480.0,
            "peak_kw": 600.0,
            "voltage": 230.0,
            "occupancy": 0,
            "source": "Grid",
            "temperature": 25.0,
            "day_type": "Weekday"
        }
        anomalies, df_anom, summary = detect_campus_anomalies(spike_df, export_csv=False)
        self.assertGreater(summary["total"], 0)
        
        # Check that the 480 kWh reading was detected
        found = any(a["recorded_kwh"] == 480.0 for a in anomalies)
        self.assertTrue(found)

    def test_severity_classification_exists(self):
        spike_df = self.df.copy()
        spike_df.loc[len(spike_df)] = {
            "timestamp": "2026-10-03 23:00:00",
            "building": "Computer Science Block",
            "meter_id": "MTR-CS",
            "units_kwh": 500.0,
            "peak_kw": 620.0,
            "voltage": 230.0,
            "occupancy": 10,
            "source": "Grid",
            "temperature": 25.0,
            "day_type": "Weekday"
        }
        anomalies, df_anom, summary = detect_campus_anomalies(spike_df, export_csv=False)
        self.assertIn("by_severity", summary)
        self.assertIn("Critical", summary["by_severity"])


if __name__ == "__main__":
    unittest.main()

