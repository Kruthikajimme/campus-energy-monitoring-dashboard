"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Building2,
  Clock,
  AlertTriangle,
  Leaf,
  FileSpreadsheet,
  Download,
  Zap,
  Activity,
  ShieldCheck,
  ChevronRight
} from "lucide-react";
import { useSimulation } from "@/context/SimulationContext";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Executive Overview", href: "/", icon: LayoutDashboard },
  { name: "Building Performance", href: "/buildings", icon: Building2 },
  { name: "Time-Based Analytics", href: "/time-analytics", icon: Clock },
  { name: "Anomaly Detection", href: "/anomalies", icon: AlertTriangle, badge: true },
  { name: "Energy Efficiency", href: "/sustainability", icon: Leaf },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { isLive, liveSummary } = useSimulation();

  return (
    <aside className="w-64 bg-campus-navy text-white flex flex-col flex-shrink-0 border-r border-slate-800 select-none z-30">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-campus-emerald to-campus-teal flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-1.5">
              CAMPUS ENERGY <span className="text-campus-emerald font-black">IQ</span>
            </h1>
            <p className="text-[11px] font-medium text-slate-400">Smart Energy Analytics</p>
          </div>
        </div>

        {/* Live Stream Status Pill */}
        <div className="mt-4 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="relative flex h-2.5 w-2.5">
              {isLive && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-campus-emerald opacity-75"></span>
              )}
              <span
                className={cn(
                  "relative inline-flex rounded-full h-2.5 w-2.5",
                  isLive ? "bg-campus-emerald" : "bg-amber-400"
                )}
              ></span>
            </span>
            <span className="text-[11px] font-semibold tracking-wider text-slate-300">
              {isLive ? "LIVE TELEMETRY" : "STREAM PAUSED"}
            </span>
          </div>
          <span className="text-[10px] text-campus-emerald font-mono bg-emerald-500/10 px-1.5 py-0.5 rounded">
            90-DAY SYNC
          </span>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-bold tracking-wider uppercase text-slate-400">
          Analytics Dashboards
        </div>

        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group flex items-center justify-between px-3.5 py-2.5 text-sm font-medium rounded-xl transition-all duration-150",
                isActive
                  ? "bg-gradient-to-r from-campus-emerald/20 to-campus-teal/10 text-white border-l-4 border-campus-emerald shadow-sm"
                  : "text-slate-300 hover:text-white hover:bg-slate-800/60"
              )}
            >
              <div className="flex items-center space-x-3">
                <Icon
                  className={cn(
                    "w-4 h-4 transition-colors",
                    isActive ? "text-campus-emerald" : "text-slate-400 group-hover:text-slate-200"
                  )}
                />
                <span>{item.name}</span>
              </div>

              {item.badge && (
                <span className="px-2 py-0.5 text-[11px] font-bold rounded-full bg-red-500/20 text-red-400 border border-red-500/30">
                  {liveSummary.activeAnomalies}
                </span>
              )}
            </Link>
          );
        })}

        {/* Exports & Reports Section */}
        <div className="pt-6 px-3 pb-2 text-[10px] font-bold tracking-wider uppercase text-slate-400">
          Raw Data & Dictionaries
        </div>

        <a
          href="/data/campus_energy_telemetry_90d.csv"
          download="campus_energy_telemetry_90d.csv"
          className="group flex items-center justify-between px-3.5 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 rounded-xl transition-colors"
        >
          <div className="flex items-center space-x-3">
            <Download className="w-4 h-4 text-slate-400 group-hover:text-campus-emerald" />
            <span>Telemetry CSV (90D)</span>
          </div>
          <span className="text-[10px] text-slate-500">15K rows</span>
        </a>

        <a
          href="/data/campus_energy_anomalies.csv"
          download="campus_energy_anomalies.csv"
          className="group flex items-center justify-between px-3.5 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 rounded-xl transition-colors"
        >
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Anomaly Report CSV</span>
          </div>
          <span className="text-[10px] text-slate-500">418 events</span>
        </a>

        <a
          href="/data/campus_energy_data_dictionary.csv"
          download="campus_energy_data_dictionary.csv"
          className="group flex items-center justify-between px-3.5 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 rounded-xl transition-colors"
        >
          <div className="flex items-center space-x-3">
            <FileSpreadsheet className="w-4 h-4 text-teal-400" />
            <span>Data Dictionary</span>
          </div>
          <span className="text-[10px] text-slate-500">Schema</span>
        </a>
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-900/50">
        <div className="flex items-center space-x-2 text-[11px] text-slate-400">
          <ShieldCheck className="w-4 h-4 text-campus-emerald" />
          <span className="font-semibold text-slate-300">Simulated Telemetry</span>
        </div>
        <p className="text-[10px] text-slate-500 mt-1 leading-relaxed">
          Physics-based campus simulation across 7 buildings for academic evaluation.
        </p>
      </div>
    </aside>
  );
}

