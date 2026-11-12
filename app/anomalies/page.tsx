"use client";

import React, { useState, useMemo } from "react";
import {
  AlertTriangle,
  Flame,
  ShieldAlert,
  Search,
  Filter,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Download,
  Building2,
  Clock,
  Zap,
  Info
} from "lucide-react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";
import { useSimulation } from "@/context/SimulationContext";
import { formatKwh, downloadCsv, cn } from "@/lib/utils";
import { AnomalyRecord } from "@/lib/types";

export default function AnomalyMonitoringPage() {
  const { anomalies, buildings, simulateSpike } = useSimulation();

  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedSeverity, setSelectedSeverity] = useState<string>("ALL");
  const [selectedBuildingFilter, setSelectedBuildingFilter] = useState<string>("ALL");
  const [selectedIncident, setSelectedIncident] = useState<AnomalyRecord | null>(null);

  // Severity counts
  const counts = useMemo(() => {
    return {
      total: anomalies.length,
      critical: anomalies.filter((a) => a.severity === "Critical").length,
      high: anomalies.filter((a) => a.severity === "High").length,
      medium: anomalies.filter((a) => a.severity === "Medium").length,
    };
  }, [anomalies]);

  // Anomalies by building
  const anomaliesByBuilding = useMemo(() => {
    const map: Record<string, number> = {};
    buildings.forEach((b) => (map[b.name] = 0));
    anomalies.forEach((a) => {
      map[a.buildingName] = (map[a.buildingName] || 0) + 1;
    });
    return Object.entries(map).map(([name, count]) => ({
      name,
      count,
    }));
  }, [anomalies, buildings]);

  // Severity Pie Data
  const severityPieData = useMemo(() => {
    return [
      { name: "Critical", value: counts.critical, color: "#EF4444" },
      { name: "High", value: counts.high, color: "#F59E0B" },
      { name: "Medium", value: counts.medium, color: "#3B82F6" },
    ].filter((s) => s.value > 0);
  }, [counts]);

  // Filtered anomalies table
  const filteredAnomalies = useMemo(() => {
    return anomalies.filter((a) => {
      const matchSearch =
        a.buildingName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.reason.toLowerCase().includes(searchQuery.toLowerCase());
      const matchSeverity = selectedSeverity === "ALL" || a.severity === selectedSeverity;
      const matchBuilding =
        selectedBuildingFilter === "ALL" || a.buildingId === selectedBuildingFilter;
      return matchSearch && matchSeverity && matchBuilding;
    });
  }, [anomalies, searchQuery, selectedSeverity, selectedBuildingFilter]);

  const handleExport = () => {
    downloadCsv(anomalies, "campus_energy_anomalies_audit.csv");
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-red-500/10 text-red-600 border border-red-500/20">
              STATISTICAL ANOMALY SURVEILLANCE
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Dual Engine: Facility IQR + Rolling 6h Z-Score
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-campus-navy mt-1">
            Automated Energy Anomaly & Surge Detection
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Algorithmic monitoring of sudden consumption spikes, off-hours HVAC baseload leaks, and hardware submeter glitches.
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={() => simulateSpike()}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-600 text-white shadow-sm transition-all"
          >
            <Zap className="w-3.5 h-3.5 fill-current" />
            <span>Inject Spike Demo</span>
          </button>
          <button
            onClick={handleExport}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* 4 Diagnostic KPI Badges */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card border-l-4 border-l-slate-700">
          <span className="text-xs font-semibold text-slate-400 block">TOTAL ANOMALIES</span>
          <span className="text-2xl font-black text-campus-navy font-mono mt-1 block">
            {counts.total}
          </span>
          <span className="text-[11px] text-slate-400">Total flagged incidents</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card border-l-4 border-l-red-500">
          <span className="text-xs font-semibold text-red-500 block">CRITICAL SEVERITY</span>
          <span className="text-2xl font-black text-red-600 font-mono mt-1 block">
            {counts.critical}
          </span>
          <span className="text-[11px] text-slate-400">&gt;3.5x IQR or surge &gt;150%</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card border-l-4 border-l-amber-500">
          <span className="text-xs font-semibold text-amber-500 block">HIGH SEVERITY</span>
          <span className="text-2xl font-black text-amber-600 font-mono mt-1 block">
            {counts.high}
          </span>
          <span className="text-[11px] text-slate-400">&gt;2.5x IQR threshold</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card border-l-4 border-l-blue-500">
          <span className="text-xs font-semibold text-blue-500 block">MEDIUM SEVERITY</span>
          <span className="text-2xl font-black text-blue-600 font-mono mt-1 block">
            {counts.medium}
          </span>
          <span className="text-[11px] text-slate-400">Localized Z-score &gt; 2.0</span>
        </div>
      </div>

      {/* Row 2: Charts (Anomalies by Building & Severity Donut) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Visual 1: Anomalies by Building (8 cols) */}
        <div className="lg:col-span-8 bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-campus-navy">
                Anomalous Outlier Incidents by Campus Facility
              </h3>
              <p className="text-xs text-slate-400">
                Frequency of detected surges across monitored submeters
              </p>
            </div>
          </div>
          <div className="h-[220px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={anomaliesByBuilding} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#64748B" }} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: "#64748B" }} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#101B35", borderRadius: "8px", color: "#fff", fontSize: "11px" }}
                  formatter={(v: any) => [`${v} Anomalies`, "Count"]}
                />
                <Bar dataKey="count" fill="#F59E0B" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Visual 2: Severity Distribution Donut (4 cols) */}
        <div className="lg:col-span-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
          <h3 className="text-sm font-bold text-campus-navy">Severity Breakdown</h3>
          <p className="text-xs text-slate-400 mb-2">Distribution of alert urgency</p>
          <div className="h-[180px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityPieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={70}
                  paddingAngle={4}
                >
                  {severityPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#101B35", borderRadius: "8px", color: "#fff", fontSize: "11px" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center justify-around text-center pt-2 border-t border-slate-100 text-xs">
            {severityPieData.map((s) => (
              <div key={s.name}>
                <span className="block text-[10px] text-slate-400">{s.name}</span>
                <span className="font-bold text-campus-navy font-mono">{s.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Row 3: Filterable Incident Details Table */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
          <div>
            <h3 className="text-sm font-bold text-campus-navy">
              Detailed Anomaly Incident Audit Log ({filteredAnomalies.length} Records)
            </h3>
            <p className="text-xs text-slate-400">
              Click any row to inspect root-cause analysis and technician action guidelines
            </p>
          </div>

          {/* Table Filters */}
          <div className="flex items-center flex-wrap gap-2.5">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Search facility or ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-campus-emerald/20"
              />
            </div>

            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 font-medium text-slate-700"
            >
              <option value="ALL">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
            </select>

            <select
              value={selectedBuildingFilter}
              onChange={(e) => setSelectedBuildingFilter(e.target.value)}
              className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 font-medium text-slate-700"
            >
              <option value="ALL">All Facilities</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto max-h-[420px]">
          <table className="w-full text-left text-xs">
            <thead className="sticky top-0 bg-slate-50 border-y border-slate-200 z-10">
              <tr className="text-slate-500 font-semibold uppercase text-[10px]">
                <th className="py-2.5 px-3">Alert ID</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Facility</th>
                <th className="py-2.5 px-3">Recorded</th>
                <th className="py-2.5 px-3">Expected</th>
                <th className="py-2.5 px-3">Deviation</th>
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-3">Detection Method</th>
                <th className="py-2.5 px-3">Root Cause Diagnosis</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {filteredAnomalies.slice(0, 100).map((a) => (
                <tr
                  key={a.id}
                  onClick={() => setSelectedIncident(a)}
                  className="hover:bg-slate-50 cursor-pointer transition-colors"
                >
                  <td className="py-2.5 px-3 font-mono font-bold text-campus-navy">{a.id}</td>
                  <td className="py-2.5 px-3 text-slate-500 whitespace-nowrap">{a.timestamp}</td>
                  <td className="py-2.5 px-3 font-semibold text-campus-navy">{a.buildingName}</td>
                  <td className="py-2.5 px-3 font-mono font-bold text-campus-navy">
                    {a.recordedKwh.toFixed(1)} kWh
                  </td>
                  <td className="py-2.5 px-3 font-mono text-slate-500">
                    {a.expectedKwh.toFixed(1)} kWh
                  </td>
                  <td className="py-2.5 px-3 font-mono font-bold text-red-600">
                    +{a.deviationPct}%
                  </td>
                  <td className="py-2.5 px-3">
                    <span
                      className={cn(
                        "px-2 py-0.5 rounded-full text-[10px] font-bold",
                        a.severity === "Critical"
                          ? "bg-red-100 text-red-700"
                          : a.severity === "High"
                          ? "bg-amber-100 text-amber-800"
                          : "bg-blue-100 text-blue-700"
                      )}
                    >
                      {a.severity}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-500 text-[11px]">{a.method}</td>
                  <td className="py-2.5 px-3 text-slate-700 truncate max-w-xs">{a.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Incident Detail Modal / Card */}
      {selectedIncident && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <ShieldAlert className="w-5 h-5 text-red-600" />
                <h3 className="font-bold text-base text-campus-navy">
                  Anomaly Investigation Audit
                </h3>
              </div>
              <button
                onClick={() => setSelectedIncident(null)}
                className="text-slate-400 hover:text-slate-700 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-xl font-mono">
                <div>
                  <span className="text-slate-400 block text-[10px]">INCIDENT ID</span>
                  <span className="font-bold text-campus-navy">{selectedIncident.id}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">TIMESTAMP</span>
                  <span className="font-bold text-campus-navy">{selectedIncident.timestamp}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">RECORDED / EXPECTED</span>
                  <span className="font-bold text-red-600">
                    {selectedIncident.recordedKwh} kWh / {selectedIncident.expectedKwh} kWh
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">DEVIATION SCORE</span>
                  <span className="font-bold text-red-600">+{selectedIncident.deviationPct}%</span>
                </div>
              </div>

              <div>
                <span className="text-slate-500 font-semibold block mb-0.5">Root Cause Reason:</span>
                <p className="p-2.5 bg-red-50 text-red-800 rounded-lg font-medium">
                  {selectedIncident.reason}
                </p>
              </div>

              <div>
                <span className="text-slate-500 font-semibold block mb-0.5">
                  Actionable Engineering Recommendation:
                </span>
                <p className="p-2.5 bg-emerald-50 text-emerald-800 rounded-lg font-medium leading-relaxed">
                  {selectedIncident.recommendedAction}
                </p>
              </div>

              <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-amber-800 text-[11px] flex items-start space-x-2">
                <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <span>
                  <strong>Academic Disclaimer:</strong> This event represents an algorithmically detected statistical deviation. It highlights operational abnormalities for technician investigation rather than confirming physical equipment burnout.
                </span>
              </div>
            </div>

            <div className="mt-5 pt-3 border-t border-slate-100 text-right">
              <button
                onClick={() => setSelectedIncident(null)}
                className="px-4 py-2 bg-campus-navy text-white text-xs font-bold rounded-xl hover:bg-campus-darkBlue transition-colors"
              >
                Close Audit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

