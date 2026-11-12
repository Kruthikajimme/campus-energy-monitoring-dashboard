"use client";

import React, { useState, useMemo } from "react";
import {
  Clock,
  Calendar,
  Zap,
  TrendingDown,
  Sun,
  Moon,
  ArrowDownRight,
  Flame,
  Layers,
  Activity
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";
import { useSimulation } from "@/context/SimulationContext";
import { formatKwh, formatKw, cn } from "@/lib/utils";
import hourlyPatternsData from "@/lib/data/hourly_patterns.json";
import dailyTrendsData from "@/lib/data/daily_trends.json";
import heatmapData from "@/lib/data/heatmap.json";

export default function TimeAnalyticsPage() {
  const { liveSummary, selectedDayType } = useSimulation();
  const [selectedMetric, setSelectedMetric] = useState<"kwh" | "peak">("kwh");

  // Monthly aggregations from daily data
  const monthlyData = useMemo(() => {
    const monthsMap: Record<string, { totalKwh: number; count: number; maxPeak: number }> = {};
    dailyTrendsData.forEach((d) => {
      const monthKey = d.date.substring(0, 7); // YYYY-MM
      const name =
        monthKey === "2026-08"
          ? "Aug 2026"
          : monthKey === "2026-09"
          ? "Sep 2026"
          : monthKey === "2026-10"
          ? "Oct 2026"
          : "Nov 2026";
      if (!monthsMap[name]) {
        monthsMap[name] = { totalKwh: 0, count: 0, maxPeak: 0 };
      }
      monthsMap[name].totalKwh += d.totalKwh;
      monthsMap[name].count += 1;
      monthsMap[name].maxPeak = Math.max(monthsMap[name].maxPeak, d.peakKw);
    });

    return Object.entries(monthsMap).map(([month, val]) => ({
      month,
      totalKwh: Math.round(val.totalKwh),
      avgDailyKwh: Math.round(val.totalKwh / val.count),
      peakKw: Math.round(val.maxPeak),
    }));
  }, []);

  // Day of week summary
  const dayOfWeekSummary = useMemo(() => {
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    return days.map((d) => {
      const pts = heatmapData.filter((p) => p.day === d);
      const avg = pts.reduce((acc, curr) => acc + curr.kwh, 0) / pts.length;
      return {
        day: d,
        avgKwh: Math.round(avg * 10) / 10,
        isWeekend: d === "Saturday" || d === "Sunday",
      };
    });
  }, []);

  const daysList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const hoursList = Array.from({ length: 24 }, (_, i) => i);

  // Helper for heatmap cell color
  const getHeatmapColor = (val: number) => {
    if (val > 80) return "bg-red-600 text-white";
    if (val > 65) return "bg-amber-500 text-white";
    if (val > 50) return "bg-emerald-500 text-white";
    if (val > 35) return "bg-teal-400 text-slate-900";
    if (val > 20) return "bg-teal-200 text-slate-800";
    return "bg-slate-100 text-slate-600";
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Page Title */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-campus-emerald/10 text-campus-emerald border border-campus-emerald/20">
              TEMPORAL LOAD CYCLES
            </span>
            <span className="text-xs text-slate-400 font-mono">90-Day Chronological Data</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-campus-navy mt-1">
            Time-Based Consumption & Peak Demand Analytics
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Diurnal 24-hour load curves, weekday vs. weekend variances, peak tariff windows, and hour-by-day load heatmaps.
          </p>
        </div>

        {/* Quick Findings Pill */}
        <div className="flex items-center space-x-3 text-xs bg-slate-50 px-4 py-2.5 rounded-xl border border-slate-200">
          <Clock className="w-4 h-4 text-campus-amber" />
          <div>
            <span className="text-slate-400 block text-[10px] font-semibold uppercase">Peak Window</span>
            <span className="font-bold text-campus-navy">13:00 — 16:00 Daily</span>
          </div>
        </div>
      </div>

      {/* Row 1: Diurnal Profile & Monthly Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Visual 1: 24-Hour Diurnal Curve (7 cols) */}
        <div className="lg:col-span-7 bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-campus-navy">
                24-Hour Diurnal Hourly Consumption Profile (kWh)
              </h2>
              <p className="text-xs text-slate-400">
                Hourly demand comparison across typical weekdays versus weekends
              </p>
            </div>
            <div className="flex items-center space-x-3 text-xs font-semibold">
              <span className="flex items-center gap-1.5 text-campus-emerald">
                <Sun className="w-3.5 h-3.5" /> Weekday
              </span>
              <span className="flex items-center gap-1.5 text-campus-amber">
                <Moon className="w-3.5 h-3.5" /> Weekend
              </span>
            </div>
          </div>

          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={hourlyPatternsData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="label" tick={{ fontSize: 10, fill: "#64748B" }} tickLine={false} interval={2} />
                <YAxis tick={{ fontSize: 10, fill: "#64748B" }} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#101B35",
                    borderColor: "#182B4D",
                    borderRadius: "10px",
                    color: "#FFFFFF",
                    fontSize: "12px",
                  }}
                  formatter={(val: any, name: any) => [
                    `${Number(val).toLocaleString()} kWh`,
                    name === "weekdayKwh" ? "Weekday Average" : "Weekend Average",
                  ]}
                />
                <Line
                  type="monotone"
                  dataKey="weekdayKwh"
                  stroke="#10B981"
                  strokeWidth={3}
                  name="weekdayKwh"
                  dot={{ r: 3, fill: "#10B981" }}
                />
                <Line
                  type="monotone"
                  dataKey="weekendKwh"
                  stroke="#F59E0B"
                  strokeWidth={2.5}
                  strokeDasharray="4 4"
                  name="weekendKwh"
                  dot={{ r: 3, fill: "#F59E0B" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Visual 2: Monthly Consumption Waterfall/Bars (5 cols) */}
        <div className="lg:col-span-5 bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-campus-navy">
                Monthly Campus Energy & Peak Draw
              </h2>
              <p className="text-xs text-slate-400">Month-over-month energy variance (kWh)</p>
            </div>
          </div>

          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="month" tick={{ fontSize: 10, fill: "#64748B" }} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: "#64748B" }} tickLine={false} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#101B35",
                    borderColor: "#182B4D",
                    borderRadius: "10px",
                    color: "#FFFFFF",
                    fontSize: "12px",
                  }}
                  formatter={(v: any) => [`${Number(v).toLocaleString()} kWh`, "Total"]}
                />
                <Bar dataKey="totalKwh" radius={[6, 6, 0, 0]} fill="#10B981" name="Monthly Total" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 2: Hour-of-Day vs. Day-of-Week Load Heatmap */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <h3 className="text-sm font-bold text-campus-navy">
              Campus Electricity Demand Matrix (Day of Week vs. Hour of Day)
            </h3>
            <p className="text-xs text-slate-400">
              Mean hourly consumption (kWh) heat intensity. Darker red indicates peak tariff periods.
            </p>
          </div>

          {/* Color Legend */}
          <div className="flex items-center space-x-2 text-[10px] font-semibold text-slate-500">
            <span>Low (&lt;20)</span>
            <span className="w-3.5 h-3.5 rounded bg-slate-100 border border-slate-200 inline-block" />
            <span className="w-3.5 h-3.5 rounded bg-teal-300 inline-block" />
            <span className="w-3.5 h-3.5 rounded bg-emerald-500 inline-block" />
            <span className="w-3.5 h-3.5 rounded bg-amber-500 inline-block" />
            <span className="w-3.5 h-3.5 rounded bg-red-600 inline-block" />
            <span>Peak (&gt;80 kWh)</span>
          </div>
        </div>

        {/* Heatmap Grid */}
        <div className="overflow-x-auto">
          <div className="min-w-[800px]">
            {/* Header: Hours */}
            <div className="grid grid-cols-25 gap-1 text-center text-[10px] font-semibold text-slate-400 mb-1">
              <div className="text-left font-bold text-slate-600">Day / Hour</div>
              {hoursList.map((h) => (
                <div key={h} className="font-mono">
                  {h}
                </div>
              ))}
            </div>

            {/* Rows: Days */}
            <div className="space-y-1">
              {daysList.map((day) => {
                const dayPts = heatmapData.filter((p) => p.day === day);
                return (
                  <div key={day} className="grid grid-cols-25 gap-1 items-center">
                    <div className="text-xs font-semibold text-campus-navy truncate pr-2">
                      {day.substring(0, 3)}
                    </div>
                    {hoursList.map((h) => {
                      const pt = dayPts.find((p) => p.hour === h);
                      const val = pt ? pt.kwh : 0;
                      return (
                        <div
                          key={h}
                          title={`${day} ${h}:00 — ${val} kWh`}
                          className={cn(
                            "h-7 rounded flex items-center justify-center font-mono text-[9px] font-bold transition-all hover:scale-110 hover:shadow-md cursor-pointer",
                            getHeatmapColor(val)
                          )}
                        >
                          {Math.round(val)}
                        </div>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: Day-of-Week Comparison Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {dayOfWeekSummary.map((d) => (
          <div
            key={d.day}
            className={cn(
              "p-3.5 rounded-xl border text-center transition-all",
              d.isWeekend
                ? "bg-amber-50/50 border-amber-200"
                : "bg-white border-slate-200 shadow-xs"
            )}
          >
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
              {d.day}
            </span>
            <span className="text-base font-black text-campus-navy mt-1 block">
              {d.avgKwh} <span className="text-[10px] font-normal text-slate-400">kWh/h</span>
            </span>
            <span
              className={cn(
                "inline-block mt-1 text-[9px] font-semibold px-2 py-0.5 rounded-full",
                d.isWeekend ? "bg-amber-200/60 text-amber-800" : "bg-emerald-100 text-emerald-800"
              )}
            >
              {d.isWeekend ? "Weekend" : "Weekday"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

