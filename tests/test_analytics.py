"""
Unit Tests for Analytics, Feature Engineering & Insights
--------------------------------------------------------
Validates KPIs, temporal aggregations, Star Schema feature engineering,
and automated empirical insights calculations.
"""

import unittest
import pandas as pd
from src.analytics import compute_comprehensive_analytics
from src.feature_engineering import engineer_energy_features
from src.insights import generate_campus_insights_and_answers


class TestAnalytics(unittest.TestCase):
    
    def setUp(self):
        rows = []
        buildings = ["Academic Block", "Computer Science Block", "Library"]
        for day in ["2026-10-01", "2026-10-02"]:
            for hour in range(24):
                ts = f"{day} {hour:02d}:00:00"
                for b in buildings:
                    base = 50.0 if b == "Academic Block" else (80.0 if b == "Computer Science Block" else 40.0)
                    kwh = base + (hour * 1.5)
                    rows.append({
                        "timestamp": ts,
                        "building": b,
                        "meter_id": f"MTR-{b[:4]}",
                        "units_kwh": kwh,
                        "peak_kw": kwh * 1.25,
                        "voltage": 230.0,
                        "occupancy": 100,
                        "source": "Grid" if hour < 8 or hour > 16 else "Solar",
                        "temperature": 28.0,
                        "day_type": "Weekday"
                    })
        self.df = pd.DataFrame(rows)

    def test_feature_engineering_star_schema_keys(self):
        df_enr = engineer_energy_features(self.df)
        self.assertIn("reading_id", df_enr.columns)
        self.assertIn("date_key", df_enr.columns)
        self.assertIn("time_key", df_enr.columns)
        self.assertIn("building_id", df_enr.columns)
        self.assertIn("source_id", df_enr.columns)
        self.assertIn("kwh_per_occupant", df_enr.columns)
        self.assertIn("rolling_7d_kwh", df_enr.columns)

    def test_analytics_computations(self):
        df_enr = engineer_energy_features(self.df)
        res = compute_comprehensive_analytics(df_enr, export_reports=False)
        kpis = res["kpis"]
        self.assertGreater(kpis["total_consumption_kwh"], 0)
        self.assertEqual(kpis["monitored_buildings"], 3)
        self.assertGreater(kpis["peak_demand_kw"], 0)
        self.assertEqual(len(res["building_analysis"]), 3)
        self.assertEqual(len(res["daily_analysis"]), 2)
        self.assertEqual(len(res["hourly_analysis"]), 24)

    def test_insights_generation(self):
        df_enr = engineer_energy_features(self.df)
        insights = generate_campus_insights_and_answers(df_enr, export_excel=False)
        self.assertIn("core_questions_and_answers", insights)
        self.assertEqual(len(insights["core_questions_and_answers"]), 9)
        self.assertIn("recommendations", insights)
        self.assertEqual(len(insights["recommendations"]), 5)


if __name__ == "__main__":
    unittest.main()
