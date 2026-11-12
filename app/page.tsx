"use client";

import React, { useMemo } from "react";
import {
  Zap,
  TrendingUp,
  Activity,
  Flame,
  Users,
  Building2,
  Calendar,
  AlertTriangle,
  Leaf,
  Sun,
  ShieldAlert,
  ArrowUpRight,
  ArrowDownRight,
  BarChart3
} from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";
import { useSimulation } from "@/context/SimulationContext";
import { formatKwh, formatKw, formatCurrency, formatCarbon, cn } from "@/lib/utils";
import dailyTrendsData from "@/lib/data/daily_trends.json";
import hourlyPatternsData from "@/lib/data/hourly_patterns.json";
import sourcesData from "@/lib/data/sources.json";

export default function ExecutiveOverviewPage() {
  const {
    liveSummary,
    buildings,
    selectedBuilding,
    selectedSource,
    selectedDayType,
    recentStream,
    anomalies
  } = useSimulation();

  // Filtered daily trends based on selectedDayType
  const filteredDaily = useMemo(() => {
    let data = dailyTrendsData;
    if (selectedDayType === "Weekday") {
      data = data.filter((d) => d.isWeekend === "No");
    } else if (selectedDayType === "Weekend") {
      data = data.filter((d) => d.isWeekend === "Yes");
    }
    return data;
  }, [selectedDayType]);

  // Filtered buildings
  const displayBuildings = useMemo(() => {
    if (selectedBuilding !== "ALL") {
      return buildings.filter((b) => b.id === selectedBuilding);
    }
    return buildings;
  }, [buildings, selectedBuilding]);

  // Top 3 facilities
  const topThreeBuildings = useMemo(() => {
    return [...buildings].sort((a, b) => b.totalKwh - a.totalKwh).slice(0, 3);
  }, [buildings]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Page Title & Status Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-campus-emerald/10 text-campus-emerald border border-campus-emerald/20">
              SMART CAMPUS INTELLIGENCE
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Telemetry Window: {liveSummary.startDate} to {liveSummary.endDate}
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-campus-navy mt-1">
            Executive Campus Energy Overview
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time aggregate consumption, demand peaks, decarbonization indicators, and automated diagnostics across 7 campus facilities.
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <div className="px-3 py-2 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-slate-400 block text-[10px] uppercase font-semibold">Facilities Active</span>
            <span className="text-sm font-bold text-campus-darkBlue">{buildings.length} Monitored</span>
          </div>
          <div className="px-3 py-2 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-slate-400 block text-[10px] uppercase font-semibold">Submeter Records</span>
            <span className="text-sm font-bold text-campus-emerald font-mono">
              {liveSummary.totalRecords.toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {/* 6 Top Executive KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {/* KPI 1: Total Consumption */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/90 shadow-card hover:shadow-cardHover transition-all border-t-4 border-t-campus-emerald">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>TOTAL ENERGY</span>
            <Zap className="w-4 h-4 text-campus-emerald" />
          </div>
          <div className="mt-2">
            <span className="text-lg font-black text-campus-navy tracking-tight">
              {formatKwh(liveSummary.totalKwh)}
            </span>
            <span className="text-[11px] text-slate-400 block font-mono">
              {liveSummary.totalMwh.toLocaleString()} MWh cumulative
            </span>
          </div>
        </div>

        {/* KPI 2: Daily Average */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/90 shadow-card hover:shadow-cardHover transition-all border-t-4 border-t-campus-teal">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>AVG DAILY LOAD</span>
            <Activity className="w-4 h-4 text-campus-teal" />
          </div>
          <div className="mt-2">
            <span className="text-lg font-black text-campus-navy tracking-tight">
              {Math.round(liveSummary.averageDailyKwh).toLocaleString()}
            </span>
            <span className="text-[11px] text-slate-400 block font-mono">kWh/day baseline</span>
          </div>
        </div>

        {/* KPI 3: Peak Demand */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/90 shadow-card hover:shadow-cardHover transition-all border-t-4 border-t-campus-amber">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>PEAK DEMAND</span>
            <Flame className="w-4 h-4 text-campus-amber" />
          </div>
          <div className="mt-2">
            <span className="text-lg font-black text-campus-navy tracking-tight">
              {formatKw(liveSummary.peakDemandKw)}
            </span>
            <span className="text-[11px] text-slate-400 block font-mono">Contract max draw</span>
          </div>
        </div>

        {/* KPI 4: Carbon Emissions */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/90 shadow-card hover:shadow-cardHover transition-all border-t-4 border-t-indigo-500">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>CARBON FOOTPRINT</span>
            <Leaf className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="mt-2">
            <span className="text-lg font-black text-campus-navy tracking-tight">
              {formatCarbon(liveSummary.carbonEmissionsTonnes)}
            </span>
            <span className="text-[11px] text-slate-400 block font-mono">0.82 kg CO₂/kWh grid</span>
          </div>
        </div>

        {/* KPI 5: Active Anomalies */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/90 shadow-card hover:shadow-cardHover transition-all border-t-4 border-t-campus-red">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>DETECTED ALERTS</span>
            <AlertTriangle className="w-4 h-4 text-campus-red" />
          </div>
          <div className="mt-2">
            <span className="text-lg font-black text-campus-red tracking-tight font-mono">
              {liveSummary.activeAnomalies}
            </span>
            <span className="text-[11px] text-slate-400 block font-mono">Outlier surge events</span>
          </div>
        </div>

        {/* KPI 6: Energy per Occupant */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/90 shadow-card hover:shadow-cardHover transition-all border-t-4 border-t-purple-500">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>PER OCCUPANT</span>
            <Users className="w-4 h-4 text-purple-500" />
          </div>
          <div className="mt-2">
            <span className="text-lg font-black text-campus-navy tracking-tight font-mono">
              {liveSummary.kwhPerOccupant.toFixed(2)}
            </span>
            <span className="text-[11px] text-slate-400 block font-mono">kWh/person avg</span>
          </div>
        </div>
      </div>

      {/* Main Charts Row 1: Daily Trend & Building Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Visual 1: Daily Consumption Trend (7 cols) */}
        <div className="lg:col-span-7 bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-campus-navy">
                90-Day Campus Electricity Consumption & 7-Day Moving Baseline
              </h2>
              <p className="text-xs text-slate-400">
                Daily cumulative kilowatt-hours tracked against trailing moving average
              </p>
            </div>
            <div className="flex items-center space-x-3 text-xs font-medium">
              <span className="flex items-center gap-1.5 text-campus-emerald">
                <span className="w-2.5 h-2.5 rounded-full bg-campus-emerald inline-block" /> Daily Load
              </span>
              <span className="flex items-center gap-1.5 text-campus-teal">
                <span className="w-2.5 h-2.5 rounded-full bg-campus-teal inline-block" /> 7D Moving Avg
              </span>
            </div>
          </div>

          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={filteredDaily}>
                <defs>
                  <linearGradient id="emeraldGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10, fill: "#64748B" }}
                  tickLine={false}
                  axisLine={{ stroke: "#E2E8F0" }}
                  interval={12}
                />
                <YAxis
                  tick={{ fontSize: 10, fill: "#64748B" }}
                  tickLine={false}
                  axisLine={{ stroke: "#E2E8F0" }}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#101B35",
                    borderColor: "#182B4D",
                    borderRadius: "10px",
                    color: "#FFFFFF",
                    fontSize: "12px",
                  }}
                  formatter={(value: any, name: any) => [
                    `${Number(value).toLocaleString()} kWh`,
                    name === "totalKwh" ? "Daily Total" : "7D Average",
                  ]}
                />
                <Area
                  type="monotone"
                  dataKey="totalKwh"
                  stroke="#10B981"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#emeraldGrad)"
                  name="totalKwh"
                />
                <Line
                  type="monotone"
                  dataKey="rolling7d"
                  stroke="#14B8A6"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={false}
                  name="rolling7d"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Visual 2: Facility Consumption Breakdown (5 cols) */}
        <div className="lg:col-span-5 bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-campus-navy">
                Cumulative Energy by Facility (kWh)
              </h2>
              <p className="text-xs text-slate-400">
                Ranked consumption across 7 campus buildings (Top consumer in Amber)
              </p>
            </div>
            <span className="text-[11px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              7 Facilities
            </span>
          </div>

          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={displayBuildings}
                layout="vertical"
                margin={{ top: 5, right: 20, left: 25, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                <XAxis
                  type="number"
                  tick={{ fontSize: 10, fill: "#64748B" }}
                  tickLine={false}
                  axisLine={{ stroke: "#E2E8F0" }}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                />
                <YAxis
                  dataKey="name"
                  type="category"
                  tick={{ fontSize: 11, fill: "#1E293B", fontWeight: 500 }}
                  tickLine={false}
                  axisLine={{ stroke: "#E2E8F0" }}
                  width={110}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#101B35",
                    borderColor: "#182B4D",
                    borderRadius: "10px",
                    color: "#FFFFFF",
                    fontSize: "12px",
                  }}
                  formatter={(val: any) => [`${Number(val).toLocaleString()} kWh`, "Total Consumption"]}
                />
                <Bar dataKey="totalKwh" radius={[0, 6, 6, 0]}>
                  {displayBuildings.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={index === 0 ? "#F59E0B" : entry.color || "#10B981"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 2: Source Distribution, Hourly Pattern & Top 3 Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-6">
        {/* Visual 3: Generation Source Donut (4 cols) */}
        <div className="lg:col-span-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
          <h2 className="text-sm font-bold text-campus-navy">
            Generation Source Breakdown
          </h2>
          <p className="text-xs text-slate-400 mb-2">
            Utility Grid vs. Solar vs. Backup Generator
          </p>

          <div className="h-[210px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sourcesData}
                  dataKey="totalKwh"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                >
                  {sourcesData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#101B35",
                    borderColor: "#182B4D",
                    borderRadius: "10px",
                    color: "#FFFFFF",
                    fontSize: "12px",
                  }}
                  formatter={(val: any) => [`${Number(val).toLocaleString()} kWh`, "Energy"]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-3 gap-2 mt-2 pt-3 border-t border-slate-100 text-center">
            {sourcesData.map((s) => (
              <div key={s.name} className="p-1.5 rounded-lg bg-slate-50">
                <span className="block text-[10px] font-semibold text-slate-400">{s.name}</span>
                <span className="text-xs font-bold text-campus-navy">{s.sharePct}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Visual 4: 24-Hour Diurnal Hourly Pattern (5 cols) */}
        <div className="lg:col-span-5 bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h2 className="text-sm font-bold text-campus-navy">
                24-Hour Diurnal Hourly Profile (kWh)
              </h2>
              <p className="text-xs text-slate-400">
                Weekday vs. Weekend average hourly demand curves
              </p>
            </div>
          </div>

          <div className="h-[230px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={hourlyPatternsData} margin={{ top: 10, right: 15, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="label" tick={{ fontSize: 9, fill: "#64748B" }} tickLine={false} interval={3} />
                <YAxis tick={{ fontSize: 9, fill: "#64748B" }} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#101B35",
                    borderColor: "#182B4D",
                    borderRadius: "10px",
                    color: "#FFFFFF",
                    fontSize: "12px",
                  }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: "11px", paddingTop: "6px" }} />
                <Line
                  type="monotone"
                  dataKey="weekdayKwh"
                  stroke="#10B981"
                  strokeWidth={2.5}
                  name="Weekday Load"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="weekendKwh"
                  stroke="#F59E0B"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  name="Weekend Load"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Visual 5: Top 3 Highest Consumers (3 cols) */}
        <div className="lg:col-span-3 bg-white p-5 rounded-2xl border border-slate-200 shadow-card flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-campus-navy">
              Top 3 Energy Drivers
            </h2>
            <p className="text-xs text-slate-400 mb-3">
              Facilities requiring prioritized energy management
            </p>

            <div className="space-y-3">
              {topThreeBuildings.map((b, i) => (
                <div key={b.id} className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <span className="w-6 h-6 rounded-lg bg-campus-navy text-white text-xs font-bold flex items-center justify-center">
                      #{i + 1}
                    </span>
                    <div>
                      <h4 className="text-xs font-bold text-campus-navy leading-tight">{b.name}</h4>
                      <span className="text-[10px] text-slate-400">{b.type}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-campus-emerald">{b.sharePct}%</span>
                    <span className="text-[10px] text-slate-400 block">{formatKwh(b.totalKwh)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100">
            <span className="text-[11px] font-semibold text-slate-600 block">Weekend Load Drop:</span>
            <div className="flex items-center space-x-1 text-campus-emerald font-bold text-sm">
              <ArrowDownRight className="w-4 h-4" />
              <span>{liveSummary.weekendLoadDropPct}% reduction on weekends</span>
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: Automated Executive Insights Callout */}
      <div className="bg-gradient-to-r from-campus-darkBlue to-campus-navy text-white p-6 rounded-2xl shadow-lg border border-slate-700">
        <div className="flex items-center space-x-2 text-campus-emerald text-xs font-bold uppercase tracking-wider mb-2">
          <Zap className="w-4 h-4 fill-current" />
          <span>Automated Facility Intelligence & Executive Recommendations</span>
        </div>
        <h3 className="text-lg font-bold tracking-tight text-white mb-3">
          Key Campus Operational Observations
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-white/5 border border-white/10">
            <span className="text-campus-amber font-bold block mb-1">#1 High Baseload Driver</span>
            <p className="text-slate-300 leading-relaxed">
              <strong className="text-white">{liveSummary.topConsumer}</strong> accounts for{" "}
              <strong className="text-campus-amber">{liveSummary.topConsumerShare}%</strong> of total electricity, driven by 24/7 server racks and precision cooling.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-white/5 border border-white/10">
            <span className="text-campus-emerald font-bold block mb-1">Diurnal Peak Shifting</span>
            <p className="text-slate-300 leading-relaxed">
              Campus peak power occurs between <strong className="text-white">13:00 and 16:00</strong>. Staggering laboratory autoclaves into morning windows would save ~₹3.36L annually.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-white/5 border border-white/10">
            <span className="text-campus-teal font-bold block mb-1">Solar PV Offset</span>
            <p className="text-slate-300 leading-relaxed">
              Rooftop solar currently generates <strong className="text-white">16.4%</strong> of daytime load. Expanding capacity by 120 kWp could displace additional utility tariffs.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-white/5 border border-white/10">
            <span className="text-rose-400 font-bold block mb-1">Night Baseload Leakage</span>
            <p className="text-slate-300 leading-relaxed">
              Night-time baseline (01:00-05:00) averages <strong className="text-white">~310 kWh/hr</strong>. Implementing automated night thermostat setbacks would conserve ~68,000 kWh annually.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

