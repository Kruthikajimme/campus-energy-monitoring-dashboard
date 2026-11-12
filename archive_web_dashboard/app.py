"""
Campus Energy Consumption Monitoring and Analytics Dashboard
============================================================
Full-Stack Flask Application providing interactive campus energy telemetry,
building-wise benchmarking, temporal trend forecasting, statistical anomaly detection,
cleaning pipelines, automated insights, Excel reporting, and live demonstration modes.
"""

import os
import json
from datetime import datetime
from flask import (
    Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
)
import pandas as pd
import numpy as np

from modules.data_generator import BUILDINGS, generate_campus_dataset
from modules.data_cleaning import clean_energy_dataset, EXPECTED_COLUMNS
from modules.analytics import (
    filter_dataset,
    calculate_kpis,
    get_building_consumption_analysis,
    get_daily_consumption_trend,
    get_monthly_consumption_trend,
    get_hourly_consumption_pattern,
    get_source_distribution,
    get_occupancy_vs_energy,
    get_day_type_analysis
)
from modules.anomaly_detection import detect_anomalies, get_anomaly_summary
from modules.insights import generate_campus_insights
from modules.report_generator import generate_excel_report, REPORTS_DIR

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "sample_raw_energy.csv")
CLEANED_DATA_PATH = os.path.join(DATA_DIR, "sample_cleaned_energy.csv")
REPORT_DATA_PATH = os.path.join(DATA_DIR, "cleaning_report.json")

app = Flask(__name__)
app.config["SECRET_KEY"] = "campus-energy-secret-key-2026-fixed"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

# Global active dataset in memory (thread-safe for local read/write)
CURRENT_DF = None
RAW_DF = None
CLEANING_REPORT = {}
DEMO_INJECTED_IDS = set()


def init_datasets():
    """Ensure baseline raw, cleaned, and audit files exist, then load into memory."""
    global CURRENT_DF, RAW_DF, CLEANING_REPORT
    
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    if not os.path.exists(CLEANED_DATA_PATH) or not os.path.exists(RAW_DATA_PATH):
        print("[App Init] Datasets missing. Generating simulated dataset now...")
        from generate_dataset import main as gen_main
        gen_main()
        
    RAW_DF = pd.read_csv(RAW_DATA_PATH)
    CURRENT_DF = pd.read_csv(CLEANED_DATA_PATH)
    
    if os.path.exists(REPORT_DATA_PATH):
        with open(REPORT_DATA_PATH, "r", encoding="utf-8") as f:
            CLEANING_REPORT = json.load(f)
            
    print(f"[App Init] Loaded {len(CURRENT_DF):,} cleaned records and {len(RAW_DF):,} raw records.")


# =============================================================================
# TEMPLATE FILTER HELPERS & CONTEXT PROCESSORS
# =============================================================================

@app.context_processor
def inject_global_metadata():
    """Inject standard options and metadata into all templates."""
    months = []
    if CURRENT_DF is not None and "timestamp" in CURRENT_DF.columns and not CURRENT_DF.empty:
        try:
            months = sorted(pd.to_datetime(CURRENT_DF["timestamp"]).dt.strftime("%Y-%m").unique().tolist())
        except Exception:
            pass
            
    return {
        "all_buildings": BUILDINGS,
        "all_sources": ["Grid", "Solar", "Generator"],
        "all_day_types": ["Weekday", "Weekend", "Holiday"],
        "available_months": months,
        "current_year": datetime.now().year,
        "is_simulated_data": True
    }


# =============================================================================
# WEB PAGES & VIEW ROUTES
# =============================================================================

@app.route("/")
@app.route("/dashboard")
def dashboard():
    """Overview Dashboard: High-level KPIs and multi-faceted energy visualizations."""
    return render_template("index.html", active_page="dashboard")


@app.route("/buildings")
def buildings_view():
    """Building Analysis: Comparative performance, peak demand, and intensity ratings."""
    b_analysis = get_building_consumption_analysis(CURRENT_DF)
    return render_template("buildings.html", active_page="buildings", building_data=b_analysis)


@app.route("/trends")
def trends_view():
    """Consumption Trends: Daily timeline, monthly aggregates, and diurnal hourly profiles."""
    return render_template("trends.html", active_page="trends")


@app.route("/anomalies")
def anomalies_view():
    """Anomaly Detection: Statistical outlier log, severity tags, and technician alerts."""
    anomalies = detect_anomalies(CURRENT_DF)
    summary = get_anomaly_summary(anomalies)
    return render_template("anomalies.html", active_page="anomalies", anomalies=anomalies, summary=summary)


@app.route("/data-management")
def data_management():
    """Data Management: File uploads, manual reading entry, previews, and CSV downloads."""
    sample_rows = CURRENT_DF.head(10).to_dict(orient="records") if CURRENT_DF is not None else []
    return render_template(
        "data_management.html",
        active_page="data_management",
        sample_rows=sample_rows,
        total_records=len(CURRENT_DF) if CURRENT_DF is not None else 0
    )


@app.route("/data-cleaning")
def data_cleaning_lab():
    """Data Cleaning Lab: Transparent inspection of cleaning pipeline and audit report."""
    return render_template(
        "data_cleaning.html",
        active_page="data_cleaning",
        report=CLEANING_REPORT,
        raw_count=len(RAW_DF) if RAW_DF is not None else 0,
        cleaned_count=len(CURRENT_DF) if CURRENT_DF is not None else 0
    )


@app.route("/insights")
def insights_view():
    """Automated Insights & Recommendations: Calculated findings and energy-saving measures."""
    anomalies = detect_anomalies(CURRENT_DF)
    insights_data = generate_campus_insights(CURRENT_DF, anomalies)
    return render_template("insights.html", active_page="insights", insights=insights_data)


@app.route("/reports")
def reports_view():
    """Reports & Downloads: Generate and download formatted multi-sheet Excel workbooks."""
    anomalies = detect_anomalies(CURRENT_DF)
    kpis = calculate_kpis(CURRENT_DF, len(anomalies))
    return render_template("reports.html", active_page="reports", kpis=kpis)


@app.route("/about")
def about_view():
    """About Project: Architecture, methodology, team credentials, and acknowledgements."""
    return render_template("about.html", active_page="about")


# =============================================================================
# REST API ENDPOINTS FOR DYNAMIC DASHBOARD & CHARTS
# =============================================================================

def get_filtered_df_from_request():
    """Extract query parameters and return appropriately filtered dataframe slice."""
    b = request.args.get("building", "All")
    s_date = request.args.get("start_date", None)
    e_date = request.args.get("end_date", None)
    m = request.args.get("month", "All")
    src = request.args.get("source", "All")
    dt = request.args.get("day_type", "All")
    
    return filter_dataset(CURRENT_DF, building=b, start_date=s_date, end_date=e_date, month=m, source=src, day_type=dt)


@app.route("/api/kpis")
def api_kpis():
    """Returns dynamic KPI metrics based on current filter selection."""
    df_f = get_filtered_df_from_request()
    anomalies = detect_anomalies(df_f)
    kpis = calculate_kpis(df_f, len(anomalies))
    return jsonify(kpis)


@app.route("/api/charts/building-consumption")
def api_chart_building():
    """Building-wise total energy consumption (kWh) for bar chart comparison."""
    df_f = get_filtered_df_from_request()
    data = get_building_consumption_analysis(df_f)
    return jsonify({
        "labels": [d["building"] for d in data],
        "values": [d["total_kwh"] for d in data],
        "percentages": [d["percentage"] for d in data],
        "is_highest": [d["is_highest"] for d in data]
    })


@app.route("/api/charts/daily-trend")
def api_chart_daily():
    """Daily total energy consumption and peak kW across the timeline."""
    df_f = get_filtered_df_from_request()
    daily = get_daily_consumption_trend(df_f)
    return jsonify(daily)


@app.route("/api/charts/monthly-trend")
def api_chart_monthly():
    """Monthly energy consumption breakdown."""
    df_f = get_filtered_df_from_request()
    monthly = get_monthly_consumption_trend(df_f)
    return jsonify(monthly)


@app.route("/api/charts/hourly-pattern")
def api_chart_hourly():
    """Average consumption by hour of day (00:00 to 23:00) to pinpoint peak hours."""
    df_f = get_filtered_df_from_request()
    hourly = get_hourly_consumption_pattern(df_f)
    return jsonify(hourly)


@app.route("/api/charts/source-distribution")
def api_chart_source():
    """Pie/Doughnut energy source distribution (Grid, Solar, Generator)."""
    df_f = get_filtered_df_from_request()
    src_data = get_source_distribution(df_f)
    return jsonify(src_data)


@app.route("/api/charts/building-peaks")
def api_chart_peaks():
    """Building-wise peak electricity demand (kW)."""
    df_f = get_filtered_df_from_request()
    data = get_building_consumption_analysis(df_f)
    return jsonify({
        "labels": [d["building"] for d in data],
        "peak_kw": [d["peak_demand_kw"] for d in data]
    })


@app.route("/api/charts/occupancy-scatter")
def api_chart_occupancy():
    """Scatter data: Occupancy vs Energy Consumption with Pearson correlation."""
    df_f = get_filtered_df_from_request()
    scatter_data = get_occupancy_vs_energy(df_f)
    return jsonify(scatter_data)


@app.route("/api/anomalies")
def api_anomalies():
    """Returns detected statistical anomalies based on query filters."""
    df_f = get_filtered_df_from_request()
    anomalies = detect_anomalies(df_f)
    summary = get_anomaly_summary(anomalies)
    return jsonify({
        "total": len(anomalies),
        "summary": summary,
        "anomalies": anomalies[:250]  # Return top 250 for responsive UI
    })


# =============================================================================
# LIVE DEMONSTRATION & INJECTION CONTROLS
# =============================================================================

@app.route("/api/demo/inject-spike", methods=["POST"])
def demo_inject_spike():
    """
    Live Demonstration Mode:
    Simulates a sudden, substantial electricity spike (e.g. 380 kWh surge due to
    an unmanaged HVAC chiller fault or unauthorized machinery test).
    Demonstrates instant detection in the Anomaly Alerts engine and recalculation of KPIs.
    """
    global CURRENT_DF, DEMO_INJECTED_IDS
    
    data = request.get_json() or {}
    target_building = data.get("building", "Computer Science Block")
    spike_kwh = float(data.get("spike_kwh", 395.5))
    peak_kw = float(data.get("peak_kw", spike_kwh * 1.35))
    
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_record = {
        "timestamp": timestamp_str,
        "building": target_building,
        "meter_id": f"MTR-DEMO-{target_building[:4].upper()}",
        "units_kwh": spike_kwh,
        "peak_kw": peak_kw,
        "voltage": 224.5,
        "occupancy": 120,
        "source": "Grid",
        "temperature": 34.2,
        "day_type": "Weekday"
    }
    
    # Prepend or append to CURRENT_DF
    new_df = pd.DataFrame([new_record])
    CURRENT_DF = pd.concat([CURRENT_DF, new_df], ignore_index=True)
    DEMO_INJECTED_IDS.add(timestamp_str)
    
    # Run anomaly detector on the updated dataset
    anomalies = detect_anomalies(CURRENT_DF)
    detected_event = next((a for a in anomalies if a["timestamp"] == timestamp_str and a["building"] == target_building), None)
    
    return jsonify({
        "success": True,
        "message": f"Demonstration surge injected successfully into {target_building}!",
        "injected_record": new_record,
        "is_detected": detected_event is not None,
        "detected_anomaly": detected_event,
        "updated_total_records": len(CURRENT_DF),
        "updated_anomalies_count": len(anomalies)
    })


@app.route("/api/demo/reset", methods=["POST"])
def demo_reset():
    """Reset active memory dataset back to the initial cleaned dataset."""
    global CURRENT_DF, DEMO_INJECTED_IDS
    CURRENT_DF = pd.read_csv(CLEANED_DATA_PATH)
    DEMO_INJECTED_IDS.clear()
    anomalies = detect_anomalies(CURRENT_DF)
    
    return jsonify({
        "success": True,
        "message": "Dataset reset to standard baseline cleaned state.",
        "records_count": len(CURRENT_DF),
        "anomalies_count": len(anomalies)
    })


# =============================================================================
# DATA MANAGEMENT: CSV UPLOAD, MANUAL ENTRY, DOWNLOADS
# =============================================================================

@app.route("/api/data/manual-entry", methods=["POST"])
def manual_entry():
    """Accepts and validates a manually inputted energy reading."""
    global CURRENT_DF
    
    data = request.form if request.form else (request.get_json() or {})
    
    building = data.get("building")
    timestamp = data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    units_kwh = data.get("units_kwh")
    peak_kw = data.get("peak_kw")
    voltage = data.get("voltage", 230.0)
    occupancy = data.get("occupancy", 50)
    source = data.get("source", "Grid")
    day_type = data.get("day_type", "Weekday")
    temperature = data.get("temperature", 28.0)
    
    if not building or not units_kwh:
        return jsonify({"success": False, "error": "Building and units_kwh are mandatory fields."}), 400
        
    try:
        units_kwh = float(units_kwh)
        peak_kw = float(peak_kw) if peak_kw else round(units_kwh * 1.25, 2)
        voltage = float(voltage)
        occupancy = int(occupancy)
        temperature = float(temperature)
    except ValueError:
        return jsonify({"success": False, "error": "Numeric conversion failed for energy or electrical readings."}), 400
        
    meter_id = f"MTR-{building[:4].upper()}-MANUAL"
    
    new_row = {
        "timestamp": timestamp,
        "building": building,
        "meter_id": meter_id,
        "units_kwh": round(units_kwh, 2),
        "peak_kw": round(peak_kw, 2),
        "voltage": round(voltage, 1),
        "occupancy": occupancy,
        "source": source,
        "temperature": round(temperature, 1),
        "day_type": day_type
    }
    
    new_df = pd.DataFrame([new_row])
    CURRENT_DF = pd.concat([CURRENT_DF, new_df], ignore_index=True)
    
    return jsonify({
        "success": True,
        "message": f"Successfully added new energy record for {building}.",
        "record": new_row,
        "total_records": len(CURRENT_DF)
    })


@app.route("/api/data/upload", methods=["POST"])
def upload_csv():
    """Upload CSV file, validate columns, check for duplicates, clean and append."""
    global CURRENT_DF
    
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in upload request."}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400
        
    if not file.filename.endswith(".csv"):
        return jsonify({"success": False, "error": "Invalid format. Only .csv files are supported."}), 400
        
    try:
        df_uploaded = pd.read_csv(file)
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to parse CSV: {str(e)}"}), 400
        
    # Column validation
    missing_cols = [c for c in ["timestamp", "building", "units_kwh"] if c not in df_uploaded.columns]
    if missing_cols:
        return jsonify({
            "success": False,
            "error": f"Missing mandatory columns: {', '.join(missing_cols)}. Expected columns include {', '.join(EXPECTED_COLUMNS[:5])}..."
        }), 400
        
    # Check duplicates vs current dataset
    uploaded_count = len(df_uploaded)
    df_clean_up, up_report = clean_energy_dataset(df_uploaded)
    
    mode = request.form.get("mode", "append")  # "append" or "replace"
    
    if mode == "replace":
        CURRENT_DF = df_clean_up
    else:
        # Avoid duplicating exact timestamp+building records
        combined = pd.concat([CURRENT_DF, df_clean_up], ignore_index=True)
        CURRENT_DF = combined.drop_duplicates(subset=["timestamp", "building"], keep="last").reset_index(drop=True)
        
    return jsonify({
        "success": True,
        "message": f"Successfully processed {uploaded_count:,} uploaded records ({len(df_clean_up):,} valid after cleaning).",
        "mode": mode,
        "uploaded_records": uploaded_count,
        "valid_cleaned_records": len(df_clean_up),
        "total_active_records": len(CURRENT_DF),
        "cleaning_report": up_report
    })


@app.route("/api/data/preview-table")
def api_preview_table():
    """Returns paginated rows for the interactive data table."""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 15))
    view_type = request.args.get("view", "cleaned")  # "cleaned" or "raw"
    
    target_df = CURRENT_DF if view_type == "cleaned" else RAW_DF
    
    if target_df is None or target_df.empty:
        return jsonify({"data": [], "total": 0, "page": page, "total_pages": 0})
        
    total = len(target_df)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    slice_df = target_df.iloc[start_idx:end_idx].copy()
    slice_df = slice_df.fillna("—")
    
    return jsonify({
        "data": slice_df.to_dict(orient="records"),
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": int(np.ceil(total / per_page))
    })


# =============================================================================
# FILE DOWNLOAD ROUTES
# =============================================================================

@app.route("/download/cleaned-csv")
def download_cleaned_csv():
    """Download current cleaned dataset as CSV."""
    temp_path = os.path.join(DATA_DIR, "export_cleaned_energy.csv")
    CURRENT_DF.to_csv(temp_path, index=False)
    return send_file(
        temp_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name="campus_cleaned_energy_dataset.csv"
    )


@app.route("/download/raw-csv")
def download_raw_csv():
    """Download original simulated raw dataset as CSV."""
    return send_file(
        RAW_DATA_PATH,
        mimetype="text/csv",
        as_attachment=True,
        download_name="campus_raw_energy_dataset.csv"
    )


@app.route("/download/cleaning-report")
def download_cleaning_report():
    """Download JSON cleaning audit report."""
    return send_file(
        REPORT_DATA_PATH,
        mimetype="application/json",
        as_attachment=True,
        download_name="campus_data_cleaning_report.json"
    )


@app.route("/download/excel-report")
def download_excel_report():
    """Generate and return styled multi-sheet Excel workbook."""
    report_file = generate_excel_report(CURRENT_DF)
    return send_file(
        report_file,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=os.path.basename(report_file)
    )


# =============================================================================
# APPLICATION ENTRYPOINT
# =============================================================================

init_datasets()

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" Campus Energy Consumption Monitoring & Analytics Dashboard")
    print(" Running locally at: http://127.0.0.1:5000")
    print(" Press CTRL+C to terminate.")
    print("=" * 70 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
