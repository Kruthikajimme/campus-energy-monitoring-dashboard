"use client";

import React, { useState, useMemo } from "react";
import {
  Building2,
  Zap,
  Users,
  Flame,
  Gauge,
  SlidersHorizontal,
  ChevronRight,
  TrendingUp,
  AlertTriangle,
  Award,
  Layers,
  ArrowUpRight
} from "lucide-react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from "recharts";
import { useSimulation } from "@/context/SimulationContext";
import { formatKwh, formatKw, cn } from "@/lib/utils";
import buildingDailyData from "@/lib/data/building_daily_trends.json";

export default function BuildingPerformancePage() {
  const { buildings, selectedBuilding, setSelectedBuilding } = useSimulation();
  const [activeTabBuilding, setActiveTabBuilding] = useState<string>(
    selectedBuilding !== "ALL" ? selectedBuilding : buildings[0].id
  );

  const selectedBuildingData = useMemo(() => {
    return buildings.find((b) => b.id === activeTabBuilding) || buildings[0];
  }, [buildings, activeTabBuilding]);

  // Ranked buildings
  const rankedBuildings = useMemo(() => {
    return [...buildings].sort((a, b) => b.totalKwh - a.totalKwh);
  }, [buildings]);

  // Peak demand comparison
  const peakDemandData = useMemo(() => {
    return [...buildings].sort((a, b) => b.peakKw - a.peakKw);
  }, [buildings]);

  // Per capita consumption comparison
  const perCapitaData = useMemo(() => {
    return [...buildings].sort((a, b) => b.kwhPerOccupant - a.kwhPerOccupant);
  }, [buildings]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Page Header */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-campus-emerald/10 text-campus-emerald border border-campus-emerald/20">
              FACILITY BENCHMARKING
            </span>
            <span className="text-xs text-slate-400 font-mono">7 Submetered Zones</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-campus-navy mt-1">
            Campus Building Performance & Efficiency Analytics
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Comparative energy audit, peak electrical demand intensity, occupancy correlation, and per-capita electrical efficiency.
          </p>
        </div>

        {/* Building Selector Pills */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 max-w-full">
          {buildings.map((b) => (
            <button
              key={b.id}
              onClick={() => setActiveTabBuilding(b.id)}
              className={cn(
                "px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all",
                activeTabBuilding === b.id
                  ? "bg-campus-navy text-white shadow-sm"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              )}
            >
              {b.name}
            </button>
          ))}
        </div>
      </div>

      {/* Selected Facility Spotlight Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-5 border-b border-slate-100">
          <div className="flex items-center space-x-4">
            <div
              className="w-14 h-14 rounded-2xl flex items-center justify-center text-white shadow-md"
              style={{ backgroundColor: selectedBuildingData.color }}
            >
              <Building2 className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-xl font-bold text-campus-navy">
                  {selectedBuildingData.name}
                </h2>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-600">
                  Rank #{selectedBuildingData.rank} of 7
                </span>
              </div>
              <p className="text-xs text-slate-500">
                {selectedBuildingData.type} • Meter ID:{" "}
                <span className="font-mono font-semibold">{selectedBuildingData.meterId}</span> • Active:{" "}
                {selectedBuildingData.activeHours}
              </p>
            </div>
          </div>

          {/* Quick Metrics Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div className="p-3 bg-slate-50 rounded-xl">
              <span className="text-[10px] font-semibold text-slate-400 uppercase block">Total Energy</span>
              <span className="text-sm font-bold text-campus-navy">{formatKwh(selectedBuildingData.totalKwh)}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl">
              <span className="text-[10px] font-semibold text-slate-400 uppercase block">Campus Share</span>
              <span className="text-sm font-bold text-campus-emerald">{selectedBuildingData.sharePct}%</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl">
              <span className="text-[10px] font-semibold text-slate-400 uppercase block">Peak Demand</span>
              <span className="text-sm font-bold text-campus-amber">{formatKw(selectedBuildingData.peakKw)}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl">
              <span className="text-[10px] font-semibold text-slate-400 uppercase block">Per Occupant</span>
              <span className="text-sm font-bold text-indigo-600 font-mono">
                {selectedBuildingData.kwhPerOccupant.toFixed(2)} kWh
              </span>
            </div>
          </div>
        </div>

        {/* Selected Building 90-Day Trend Chart */}
        <div className="mt-5">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              90-Day Daily Consumption Profile — {selectedBuildingData.name}
            </h3>
            <span className="text-xs text-slate-400 font-mono">Daily kWh</span>
          </div>
          <div className="h-[220px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={buildingDailyData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="date" tick={{ fontSize: 9, fill: "#64748B" }} tickLine={false} interval={14} />
                <YAxis tick={{ fontSize: 9, fill: "#64748B" }} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#101B35",
                    borderColor: "#182B4D",
                    borderRadius: "10px",
                    color: "#FFFFFF",
                    fontSize: "12px",
                  }}
                  formatter={(val: any) => [`${Number(val).toLocaleString()} kWh`, selectedBuildingData.name]}
                />
                <Line
                  type="monotone"
                  dataKey={selectedBuildingData.name}
                  stroke={selectedBuildingData.color}
                  strokeWidth={2.5}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 2: Comparative Bar Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Visual 1: Total Energy Ranking */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
          <h3 className="text-sm font-bold text-campus-navy mb-1">Total Consumption Benchmark</h3>
          <p className="text-xs text-slate-400 mb-4">Ranked cumulative kWh across all 7 buildings</p>
          <div className="h-[260px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rankedBuildings} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                <XAxis type="number" tick={{ fontSize: 9, fill: "#64748B" }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: "#1E293B" }} width={90} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#101B35", borderRadius: "8px", color: "#fff", fontSize: "11px" }}
                  formatter={(v: any) => [`${Number(v).toLocaleString()} kWh`, "Total"]}
                />
                <Bar dataKey="totalKwh" radius={[0, 4, 4, 0]}>
                  {rankedBuildings.map((entry, index) => (
                    <Cell key={`bar-${index}`} fill={index === 0 ? "#F59E0B" : entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Visual 2: Peak Demand Comparison */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
          <h3 className="text-sm font-bold text-campus-navy mb-1">Peak Demand Draw (kW)</h3>
          <p className="text-xs text-slate-400 mb-4">Highest instantaneous registered power</p>
          <div className="h-[260px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={peakDemandData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                <XAxis type="number" tick={{ fontSize: 9, fill: "#64748B" }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: "#1E293B" }} width={90} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#101B35", borderRadius: "8px", color: "#fff", fontSize: "11px" }}
                  formatter={(v: any) => [`${Number(v).toFixed(1)} kW`, "Peak Draw"]}
                />
                <Bar dataKey="peakKw" radius={[0, 4, 4, 0]}>
                  {peakDemandData.map((entry, index) => (
                    <Cell key={`peak-${index}`} fill={entry.peakKw > 100 ? "#EF4444" : "#14B8A6"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Visual 3: Per-Occupant Efficiency */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
          <h3 className="text-sm font-bold text-campus-navy mb-1">Energy Intensity per Occupant</h3>
          <p className="text-xs text-slate-400 mb-4">kWh consumed per occupant headcount</p>
          <div className="h-[260px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={perCapitaData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                <XAxis type="number" tick={{ fontSize: 9, fill: "#64748B" }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: "#1E293B" }} width={90} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#101B35", borderRadius: "8px", color: "#fff", fontSize: "11px" }}
                  formatter={(v: any) => [`${Number(v).toFixed(3)} kWh/person`, "Intensity"]}
                />
                <Bar dataKey="kwhPerOccupant" radius={[0, 4, 4, 0]} fill="#8B5CF6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 3: Comprehensive Facility Benchmarking Matrix Table */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-campus-navy">
              Facility Performance & Efficiency Audit Matrix
            </h3>
            <p className="text-xs text-slate-400">
              Complete engineering benchmarking across design capacity, baseloads, and anomaly counts
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-y border-slate-200 text-slate-500 font-semibold uppercase text-[10px]">
                <th className="py-3 px-4">Rank</th>
                <th className="py-3 px-4">Facility Name</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Design Capacity</th>
                <th className="py-3 px-4">Baseload (kW)</th>
                <th className="py-3 px-4">Total Energy (kWh)</th>
                <th className="py-3 px-4">Campus Share</th>
                <th className="py-3 px-4">Peak Draw (kW)</th>
                <th className="py-3 px-4">Per Occupant</th>
                <th className="py-3 px-4">Anomalies</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {rankedBuildings.map((b) => (
                <tr
                  key={b.id}
                  onClick={() => setActiveTabBuilding(b.id)}
                  className={cn(
                    "hover:bg-slate-50 cursor-pointer transition-colors",
                    activeTabBuilding === b.id && "bg-campus-emerald/5 font-semibold"
                  )}
                >
                  <td className="py-3 px-4 font-bold text-campus-navy">#{b.rank}</td>
                  <td className="py-3 px-4">
                    <span className="flex items-center space-x-2">
                      <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: b.color }} />
                      <span className="text-campus-navy font-bold">{b.name}</span>
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-500">{b.type}</td>
                  <td className="py-3 px-4 font-mono">{b.designCapacity.toLocaleString()} persons</td>
                  <td className="py-3 px-4 font-mono">{b.baseloadKw.toFixed(1)} kW</td>
                  <td className="py-3 px-4 font-bold text-campus-navy font-mono">{formatKwh(b.totalKwh)}</td>
                  <td className="py-3 px-4 font-bold text-campus-emerald">{b.sharePct}%</td>
                  <td className="py-3 px-4 font-mono text-campus-amber font-bold">{b.peakKw.toFixed(1)} kW</td>
                  <td className="py-3 px-4 font-mono">{b.kwhPerOccupant.toFixed(3)}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded-full bg-red-100 text-red-700 text-[10px] font-bold">
                      {b.anomaliesCount} alerts
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => setActiveTabBuilding(b.id)}
                      className="text-xs text-campus-emerald hover:underline font-bold"
                    >
                      Inspect →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

