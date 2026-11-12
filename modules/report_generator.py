"""
Excel Report Generation Module using OpenPyXL
---------------------------------------------
Generates a comprehensive, professionally styled multi-sheet Microsoft Excel (.xlsx) workbook
documenting campus electricity consumption, building comparisons, monthly trends,
statistical anomaly logs, and full telemetry.
"""

import os
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference

from modules.analytics import (
    calculate_kpis,
    get_building_consumption_analysis,
    get_monthly_consumption_trend
)
from modules.anomaly_detection import detect_anomalies

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def generate_excel_report(df, filename=None):
    """
    Generate a 5-sheet styled Excel workbook from current dataset.
    
    Parameters:
        df (pd.DataFrame): Cleaned energy consumption dataframe.
        filename (str, optional): Target filename.
        
    Returns:
        str: Absolute path of generated Excel workbook.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    if not filename:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Campus_Energy_Report_{timestamp_str}.xlsx"
        
    filepath = os.path.join(REPORTS_DIR, filename)
    
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)
    
    # Define corporate styles
    font_title = Font(name="Calibri", size=16, bold=True, color="1E293B")
    font_subtitle = Font(name="Calibri", size=11, italic=True, color="64748B")
    font_section = Font(name="Calibri", size=13, bold=True, color="0F172A")
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=11, bold=True, color="0F172A")
    font_regular = Font(name="Calibri", size=11, color="1E293B")
    
    fill_navy = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    fill_green = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
    fill_light_gray = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    fill_light_green = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")
    fill_light_amber = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    fill_light_red = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    
    thin_border_side = Side(border_style="thin", color="CBD5E1")
    border_all_thin = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    
    align_left = Alignment(horizontal="left", vertical="center")
    align_center = Alignment(horizontal="center", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")
    
    # Precompute metrics
    anomalies = detect_anomalies(df)
    kpis = calculate_kpis(df, len(anomalies))
    building_analysis = get_building_consumption_analysis(df)
    monthly_trend = get_monthly_consumption_trend(df)
    
    # =========================================================================
    # SHEET 1: Executive Summary
    # =========================================================================
    ws1 = wb.create_sheet(title="Executive Summary")
    ws1.views.sheetView[0].showGridLines = True
    
    # Title Block
    ws1["B2"] = "CAMPUS ENERGY CONSUMPTION & ANALYTICS REPORT"
    ws1["B2"].font = font_title
    ws1["B3"] = f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')} | Dataset: Simulated Campus Telemetry"
    ws1["B3"].font = font_subtitle
    
    # KPI Summary Table
    ws1["B5"] = "EXECUTIVE KEY PERFORMANCE INDICATORS (KPIs)"
    ws1["B5"].font = font_section
    
    kpi_rows = [
        ("Total Campus Energy Consumption", f"{kpis['total_consumption_kwh']:,.2f} kWh ({kpis['total_consumption_mwh']:,.2f} MWh)"),
        ("Number of Monitored Facilities", f"{kpis['buildings_monitored']} Buildings"),
        ("Average Daily Consumption", f"{kpis['avg_daily_consumption_kwh']:,.2f} kWh/day"),
        ("Campus Peak Electricity Demand", f"{kpis['peak_demand_kw']:,.2f} kW"),
        ("Total Telemetry Records Analyzed", f"{kpis['total_records']:,} Hourly Readings"),
        ("Statistical Anomalies Flagged", f"{kpis['anomalies_detected']} Events Requiring Review"),
        ("Estimated Grid Carbon Footprint", f"{kpis['estimated_co2_tonnes']:,.2f} Metric Tonnes CO2e")
    ]
    
    ws1["B7"] = "Metric Indicator"
    ws1["B7"].font = font_header
    ws1["B7"].fill = fill_navy
    ws1["B7"].alignment = align_left
    ws1["B7"].border = border_all_thin
    
    ws1["C7"] = "Monitored Value"
    ws1["C7"].font = font_header
    ws1["C7"].fill = fill_navy
    ws1["C7"].alignment = align_right
    ws1["C7"].border = border_all_thin
    
    curr_row = 8
    for label, val in kpi_rows:
        ws1[f"B{curr_row}"] = label
        ws1[f"B{curr_row}"].font = font_regular
        ws1[f"B{curr_row}"].alignment = align_left
        ws1[f"B{curr_row}"].border = border_all_thin
        ws1[f"B{curr_row}"].fill = fill_light_gray if curr_row % 2 == 0 else PatternFill(fill_type=None)
        
        ws1[f"C{curr_row}"] = val
        ws1[f"C{curr_row}"].font = font_bold
        ws1[f"C{curr_row}"].alignment = align_right
        ws1[f"C{curr_row}"].border = border_all_thin
        ws1[f"C{curr_row}"].fill = fill_light_gray if curr_row % 2 == 0 else PatternFill(fill_type=None)
        curr_row += 1
        
    # Top Consuming Building Callout
    top_building = building_analysis[0]["building"] if building_analysis else "N/A"
    top_kwh = building_analysis[0]["total_kwh"] if building_analysis else 0.0
    top_pct = building_analysis[0]["percentage"] if building_analysis else 0.0
    
    ws1[f"B{curr_row + 2}"] = "PRIMARY OBSERVATIONS & RECOMMENDATIONS"
    ws1[f"B{curr_row + 2}"].font = font_section
    
    obs_lines = [
        f"1. Highest Consuming Facility: {top_building} accounts for {top_kwh:,.1f} kWh ({top_pct:.1f}% of total campus electricity).",
        f"2. Peak Electricity Demand: A campus maximum load of {kpis['peak_demand_kw']:,.1f} kW was registered during academic hours.",
        f"3. Anomaly Review: {kpis['anomalies_detected']} statistical deviations were flagged for verification by campus electrical engineers.",
        "4. Energy Conservation Recommendation: Implement night setbacks on central chillers and stagger heavy lab machinery to reduce demand charges."
    ]
    
    for i, line in enumerate(obs_lines):
        ws1[f"B{curr_row + 4 + i}"] = line
        ws1[f"B{curr_row + 4 + i}"].font = font_regular
        
    # =========================================================================
    # SHEET 2: Building Analysis
    # =========================================================================
    ws2 = wb.create_sheet(title="Building Analysis")
    ws2.views.sheetView[0].showGridLines = True
    
    ws2["A1"] = "CAMPUS BUILDING ELECTRICITY CONSUMPTION BREAKDOWN"
    ws2["A1"].font = font_title
    
    headers_b = [
        "Building Name",
        "Total Energy (kWh)",
        "% of Campus Load",
        "Average Hourly (kWh)",
        "Max Hourly (kWh)",
        "Peak Demand (kW)",
        "Avg Occupancy",
        "Total Records"
    ]
    
    for col_idx, header in enumerate(headers_b, start=1):
        cell = ws2.cell(row=3, column=col_idx, value=header)
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = align_center if col_idx > 2 else align_left
        cell.border = border_all_thin
        
    row_idx = 4
    for b in building_analysis:
        ws2.cell(row=row_idx, column=1, value=b["building"]).alignment = align_left
        
        c2 = ws2.cell(row=row_idx, column=2, value=b["total_kwh"])
        c2.number_format = "#,##0.00"
        c2.alignment = align_right
        
        c3 = ws2.cell(row=row_idx, column=3, value=b["percentage"] / 100.0)
        c3.number_format = "0.0%"
        c3.alignment = align_right
        
        c4 = ws2.cell(row=row_idx, column=4, value=b["avg_kwh"])
        c4.number_format = "#,##0.00"
        c4.alignment = align_right
        
        c5 = ws2.cell(row=row_idx, column=5, value=b["max_kwh"])
        c5.number_format = "#,##0.00"
        c5.alignment = align_right
        
        c6 = ws2.cell(row=row_idx, column=6, value=b["peak_demand_kw"])
        c6.number_format = "#,##0.00"
        c6.alignment = align_right
        
        c7 = ws2.cell(row=row_idx, column=7, value=b["avg_occupancy"])
        c7.alignment = align_center
        
        c8 = ws2.cell(row=row_idx, column=8, value=b["record_count"])
        c8.alignment = align_center
        
        for col_i in range(1, 9):
            ws2.cell(row=row_idx, column=col_i).border = border_all_thin
            ws2.cell(row=row_idx, column=col_i).font = font_regular
            if b["is_highest"]:
                ws2.cell(row=row_idx, column=col_i).fill = fill_light_amber
                
        row_idx += 1
        
    # Add Bar Chart in Sheet 2
    if len(building_analysis) > 0:
        chart = BarChart()
        chart.type = "col"
        chart.style = 10
        chart.title = "Total Consumption by Building (kWh)"
        chart.y_axis.title = "Total kWh"
        chart.x_axis.title = "Building"
        
        data_ref = Reference(ws2, min_col=2, min_row=3, max_row=row_idx - 1)
        cats_ref = Reference(ws2, min_col=1, min_row=4, max_row=row_idx - 1)
        chart.add_data(data_ref, titles_from_data=True)
        chart.set_categories(cats_ref)
        chart.height = 11
        chart.width = 18
        ws2.add_chart(chart, "A14")
        
    # =========================================================================
    # SHEET 3: Monthly Analysis
    # =========================================================================
    ws3 = wb.create_sheet(title="Monthly Analysis")
    ws3.views.sheetView[0].showGridLines = True
    
    ws3["A1"] = "MONTHLY ELECTRICITY CONSUMPTION TRENDS"
    ws3["A1"].font = font_title
    
    months = monthly_trend.get("months", [])
    by_building = monthly_trend.get("by_building", {})
    
    # Monthly Total Table
    ws3["A3"] = "Month"
    ws3["A3"].font = font_header
    ws3["A3"].fill = fill_navy
    ws3["A3"].alignment = align_center
    ws3["A3"].border = border_all_thin
    
    col_counter = 2
    for b_name in by_building.keys():
        cell = ws3.cell(row=3, column=col_counter, value=b_name)
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = align_right
        cell.border = border_all_thin
        col_counter += 1
        
    cell_tot = ws3.cell(row=3, column=col_counter, value="Total Campus (kWh)")
    cell_tot.font = font_header
    cell_tot.fill = fill_green
    cell_tot.alignment = align_right
    cell_tot.border = border_all_thin
    
    m_row = 4
    for idx_m, m_name in enumerate(months):
        ws3.cell(row=m_row, column=1, value=m_name).alignment = align_center
        ws3.cell(row=m_row, column=1).border = border_all_thin
        ws3.cell(row=m_row, column=1).font = font_bold
        
        m_sum = 0.0
        c_i = 2
        for b_name, vals in by_building.items():
            val = vals[idx_m] if idx_m < len(vals) else 0.0
            m_sum += val
            c_val = ws3.cell(row=m_row, column=c_i, value=val)
            c_val.number_format = "#,##0.00"
            c_val.alignment = align_right
            c_val.border = border_all_thin
            c_val.font = font_regular
            c_i += 1
            
        tot_c = ws3.cell(row=m_row, column=c_i, value=m_sum)
        tot_c.number_format = "#,##0.00"
        tot_c.alignment = align_right
        tot_c.border = border_all_thin
        tot_c.font = font_bold
        tot_c.fill = fill_light_green
        m_row += 1
        
    # =========================================================================
    # SHEET 4: Anomaly Report
    # =========================================================================
    ws4 = wb.create_sheet(title="Anomaly Report")
    ws4.views.sheetView[0].showGridLines = True
    
    ws4["A1"] = "CAMPUS ENERGY ANOMALY AUDIT LOG"
    ws4["A1"].font = font_title
    ws4["A2"] = "Note: Statistical deviations indicate potential operational inefficiencies or sensor glitches requiring engineering inspection."
    ws4["A2"].font = font_subtitle
    
    anom_headers = [
        "Timestamp",
        "Building",
        "Recorded (kWh)",
        "Expected Baseline (kWh)",
        "Deviation (%)",
        "Peak Demand (kW)",
        "Severity",
        "Anomaly Reason",
        "Recommended Action"
    ]
    
    for c_idx, h in enumerate(anom_headers, start=1):
        cell = ws4.cell(row=4, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = align_center if c_idx in [1, 7] else align_left
        cell.border = border_all_thin
        
    a_row = 5
    for anom in anomalies[:1000]:  # Cap at top 1000 anomalies for Excel size
        ws4.cell(row=a_row, column=1, value=anom["timestamp"]).alignment = align_center
        ws4.cell(row=a_row, column=2, value=anom["building"]).alignment = align_left
        
        c3 = ws4.cell(row=a_row, column=3, value=anom["recorded_kwh"])
        c3.number_format = "#,##0.00"
        c3.alignment = align_right
        
        c4 = ws4.cell(row=a_row, column=4, value=anom["expected_kwh"])
        c4.number_format = "#,##0.00"
        c4.alignment = align_right
        
        c5 = ws4.cell(row=a_row, column=5, value=anom["deviation_pct"] / 100.0)
        c5.number_format = "+0.0%;-0.0%"
        c5.alignment = align_right
        
        c6 = ws4.cell(row=a_row, column=6, value=anom["peak_kw"])
        c6.number_format = "#,##0.00"
        c6.alignment = align_right
        
        sev_cell = ws4.cell(row=a_row, column=7, value=anom["severity"])
        sev_cell.alignment = align_center
        sev_cell.font = font_bold
        if anom["severity"] == "Critical":
            sev_cell.fill = fill_light_red
        elif anom["severity"] == "High":
            sev_cell.fill = fill_light_amber
        else:
            sev_cell.fill = fill_light_gray
            
        ws4.cell(row=a_row, column=8, value=anom["reason"]).alignment = align_left
        ws4.cell(row=a_row, column=9, value=anom["action_recommendation"]).alignment = align_left
        
        for c_i in range(1, 10):
            ws4.cell(row=a_row, column=c_i).border = border_all_thin
            if c_i != 7:
                ws4.cell(row=a_row, column=c_i).font = font_regular
        a_row += 1
        
    # =========================================================================
    # SHEET 5: Cleaned Dataset
    # =========================================================================
    ws5 = wb.create_sheet(title="Cleaned Dataset")
    ws5.views.sheetView[0].showGridLines = True
    
    clean_cols = list(df.columns)
    for col_idx, col_name in enumerate(clean_cols, start=1):
        cell = ws5.cell(row=1, column=col_idx, value=col_name)
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = align_center
        cell.border = border_all_thin
        
    # Write sample / full dataset rows (up to 5,000 for responsive Excel size)
    export_df = df.head(5000)
    for r_idx, row in export_df.iterrows():
        excel_r = r_idx + 2
        for c_idx, col_name in enumerate(clean_cols, start=1):
            val = row[col_name]
            cell = ws5.cell(row=excel_r, column=c_idx, value=val)
            cell.font = font_regular
            cell.border = border_all_thin
            if col_name in ["units_kwh", "peak_kw", "voltage", "temperature"]:
                cell.number_format = "#,##0.00"
                cell.alignment = align_right
            elif col_name in ["occupancy"]:
                cell.number_format = "#,##0"
                cell.alignment = align_right
            else:
                cell.alignment = align_left
                
    # Auto-adjust column widths across all sheets
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            # Scan top 50 cells per column to compute width efficiently
            for cell in col[:50]:
                if cell.value:
                    val_str = str(cell.value)
                    if len(val_str) > max_len:
                        max_len = len(val_str)
            sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
    wb.save(filepath)
    return filepath

