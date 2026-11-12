"use client";

import React, { useMemo } from "react";
import {
  Leaf,
  Sun,
  Zap,
  TrendingDown,
  DollarSign,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Building2,
  Users,
  Compass,
  ArrowRight,
  FileCheck
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
  Legend,
  ResponsiveContainer
} from "recharts";
import { useSimulation } from "@/context/SimulationContext";
import { formatKwh, formatCarbon, formatCurrency, cn } from "@/lib/utils";
import sourcesData from "@/lib/data/sources.json";

export default function SustainabilityPage() {
  const { liveSummary, buildings } = useSimulation();

  // Carbon emissions by facility
  const carbonByBuilding = useMemo(() => {
    return [...buildings]
      .map((b) => ({
        name: b.name,
        carbonTonnes: Math.round(((b.totalKwh * 0.82) / 1000) * 10) / 10,
        color: b.color,
      }))
      .sort((a, b) => b.carbonTonnes - a.carbonTonnes);
  }, [buildings]);

  // Strategic Proposals list
  const proposals = [
    {
      id: "PROP-01",
      title: "HVAC Programmable Night Setbacks & Chiller Optimization",
      target: "Academic Block & Library",
      problem: "Continuous baseline chiller and AHU operation during unoccupied overnight hours (20:00 - 06:00).",
      action: "Install automated building management setback timers and occupancy-driven thermostat shutoffs.",
      annualSavingsKwh: 68000,
      costSavingsInr: 544000,
      carbonAbatedTonnes: 55.8,
      paybackMonths: 4.2,
      priority: "Urgent",
    },
    {
      id: "PROP-02",
      title: "Peak Demand Staggering in Heavy Engineering Laboratories",
      target: "Laboratory Block",
      problem: "Simultaneous operation of industrial autoclaves and wind tunnels between 13:00 and 15:00 drives contract demand surcharges.",
      action: "Reschedule heavy motor loads and testing protocols to morning slots (08:30 - 11:00) before midday peak.",
      annualSavingsKwh: 42000,
      costSavingsInr: 336000,
      carbonAbatedTonnes: 34.4,
      paybackMonths: 1.5,
      priority: "High",
    },
    {
      id: "PROP-03",
      title: "Rooftop Solar Photovoltaic (PV) Expansion (120 kWp)",
      target: "Boys & Girls Hostel Rooftops",
      problem: "High daytime utility grid reliance despite optimal unshaded residential rooftop solar irradiance.",
      action: "Commission 120 kWp monocrystalline solar arrays with grid-tied inverters across dorm roofs.",
      annualSavingsKwh: 48000,
      costSavingsInr: 384000,
      carbonAbatedTonnes: 39.4,
      paybackMonths: 36.0,
      priority: "Strategic",
    },
    {
      id: "PROP-04",
      title: "Hostel Water Geyser Automation & Power Factor Correction",
      target: "Boys & Girls Hostels",
      problem: "Uncontrolled 24/7 domestic water heating and low inductive power factor during morning student surges.",
      action: "Retrofit digital timer switches on hot-water geysers and automatic power factor capacitors (APFC).",
      annualSavingsKwh: 18000,
      costSavingsInr: 144000,
      carbonAbatedTonnes: 14.8,
      paybackMonths: 8.0,
      priority: "Medium",
    },
    {
      id: "PROP-05",
      title: "Computer Lab Power Management & Server Virtualization",
      target: "Computer Science Block",
      problem: "350+ desktop workstations left idling in sleep-disabled state across multiple departmental labs.",
      action: "Deploy active Group Policy power management and consolidate physical lab servers onto centralized virtual hosts.",
      annualSavingsKwh: 9000,
      costSavingsInr: 72000,
      carbonAbatedTonnes: 7.4,
      paybackMonths: 2.0,
      priority: "Medium",
    },
  ];

  const totalProjectedSavingsKwh = proposals.reduce((acc, p) => acc + p.annualSavingsKwh, 0);
  const totalProjectedSavingsCost = proposals.reduce((acc, p) => acc + p.costSavingsInr, 0);
  const totalProjectedCarbon = proposals.reduce((acc, p) => acc + p.carbonAbatedTonnes, 0);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-campus-emerald/10 text-campus-emerald border border-campus-emerald/20">
              CAMPUS DECARBONIZATION ROADMAP
            </span>
            <span className="text-xs text-slate-400 font-mono">Net-Zero Transition Plan</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-campus-navy mt-1">
            Energy Efficiency & Strategic Sustainability
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Decarbonization analytics, solar penetration benchmarks, carbon accounting, and data-driven conservation proposals.
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs bg-emerald-50 px-4 py-2.5 rounded-xl border border-emerald-200 text-emerald-800 font-semibold">
          <Leaf className="w-4 h-4 text-campus-emerald" />
          <span>Renewable Share: 16.4% Solar Offset</span>
        </div>
      </div>

      {/* 4 Top Sustainability Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card border-t-4 border-t-campus-emerald">
          <span className="text-xs font-semibold text-slate-400 block">ANNUAL SAVINGS POTENTIAL</span>
          <span className="text-xl font-black text-campus-navy font-mono mt-1 block">
            {totalProjectedSavingsKwh.toLocaleString()} kWh
          </span>
          <span className="text-[11px] text-campus-emerald font-semibold">~15.6% campus reduction</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card border-t-4 border-t-campus-teal">
          <span className="text-xs font-semibold text-slate-400 block">FINANCIAL SAVINGS</span>
          <span className="text-xl font-black text-campus-navy font-mono mt-1 block">
            {formatCurrency(totalProjectedSavingsCost)}
          </span>
          <span className="text-[11px] text-slate-400">At ₹8.00 / commercial kWh</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card border-t-4 border-t-indigo-500">
          <span className="text-xs font-semibold text-slate-400 block">CARBON ABATEMENT</span>
          <span className="text-xl font-black text-campus-navy font-mono mt-1 block">
            {totalProjectedCarbon.toFixed(1)} tCO₂e
          </span>
          <span className="text-[11px] text-slate-400">Avoided coal generation</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-card border-t-4 border-t-amber-500">
          <span className="text-xs font-semibold text-slate-400 block">AVG PAYBACK PERIOD</span>
          <span className="text-xl font-black text-campus-navy font-mono mt-1 block">
            9.9 Months
          </span>
          <span className="text-[11px] text-slate-400">Rapid capital ROI</span>
        </div>
      </div>

      {/* Row 2: Carbon Emissions by Building & Renewable Donut */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Visual 1: Carbon Footprint by Building (7 cols) */}
        <div className="lg:col-span-7 bg-white p-5 rounded-2xl border border-slate-200 shadow-card">
          <h3 className="text-sm font-bold text-campus-navy mb-1">
            Carbon Emissions by Campus Facility (Tonnes CO₂e)
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            Emissions calculated via official grid emission factor (0.82 kg CO₂/kWh)
          </p>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={carbonByBuilding} layout="vertical" margin={{ left: 25 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                <XAxis type="number" tick={{ fontSize: 9, fill: "#64748B" }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: "#1E293B" }} width={95} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#101B35", borderRadius: "8px", color: "#fff", fontSize: "11px" }}
                  formatter={(v: any) => [`${v} Tonnes CO₂e`, "Emissions"]}
                />
                <Bar dataKey="carbonTonnes" fill="#182B4D" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Visual 2: Renewable vs Fossil Fuel Split (5 cols) */}
        <div className="lg:col-span-5 bg-white p-5 rounded-2xl border border-slate-200 shadow-card flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-campus-navy mb-1">
              Renewable vs. Non-Renewable Fuel Split
            </h3>
            <p className="text-xs text-slate-400 mb-2">
              Clean solar displacement versus utility fossil dependence
            </p>
            <div className="h-[180px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sourcesData}
                    dataKey="totalKwh"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={3}
                  >
                    {sourcesData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: "#101B35", borderRadius: "8px", color: "#fff", fontSize: "11px" }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100 text-xs text-emerald-900 mt-3">
            <span className="font-bold flex items-center gap-1.5">
              <Sun className="w-4 h-4 text-campus-emerald" /> Solar Generation Avoidance
            </span>
            <p className="mt-1 text-[11px] text-emerald-700 leading-relaxed">
              Rooftop solar has displaced <strong>159,000+ kg of CO₂</strong> emissions and saved the university over <strong>₹15.5 Lakhs</strong> in grid utility tariffs over the 90-day monitoring window.
            </p>
          </div>
        </div>
      </div>

      {/* Row 3: 5 Actionable Strategic Conservation Proposals */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-campus-navy">
              Strategic Energy Conservation Action Plan (Empirical ROI Analysis)
            </h3>
            <p className="text-xs text-slate-400">
              5 prioritized engineering interventions derived from measured telemetry demand curves
            </p>
          </div>
          <span className="text-xs font-bold text-campus-emerald bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
            Total Projected Savings: ₹14.80 Lakhs / yr
          </span>
        </div>

        <div className="space-y-3.5">
          {proposals.map((p) => (
            <div
              key={p.id}
              className="p-4 rounded-xl border border-slate-200 hover:border-campus-emerald/60 hover:shadow-sm transition-all bg-slate-50/50"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 pb-2 border-b border-slate-100">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-campus-navy text-white font-mono">
                    {p.id}
                  </span>
                  <h4 className="text-sm font-bold text-campus-navy">{p.title}</h4>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-200 text-slate-700">
                    {p.target}
                  </span>
                </div>

                <div className="flex items-center space-x-3 text-xs font-mono">
                  <span className="text-campus-emerald font-bold">
                    {p.annualSavingsKwh.toLocaleString()} kWh/yr
                  </span>
                  <span className="text-campus-darkBlue font-bold">
                    {formatCurrency(p.costSavingsInr)}/yr
                  </span>
                  <span className="text-indigo-600 font-bold">
                    {p.carbonAbatedTonnes} tCO₂e
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3 text-xs">
                <div>
                  <span className="text-slate-400 text-[10px] uppercase font-bold block">
                    Observed Operational Inefficiency:
                  </span>
                  <p className="text-slate-700 mt-0.5">{p.problem}</p>
                </div>
                <div>
                  <span className="text-campus-emerald text-[10px] uppercase font-bold block">
                    Recommended Technical Intervention:
                  </span>
                  <p className="text-slate-700 mt-0.5 font-medium">{p.action}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
