"use client";

import React from "react";
import {
  Play,
  Pause,
  RotateCcw,
  Zap,
  Filter,
  AlertCircle,
  X,
  Gauge,
  SlidersHorizontal,
  Flame
} from "lucide-react";
import { useSimulation } from "@/context/SimulationContext";
import { cn } from "@/lib/utils";

export default function TopHeader() {
  const {
    isLive,
    toggleLive,
    speed,
    setSpeed,
    simulateSpike,
    resetSimulation,
    activeAlert,
    clearAlert,
    buildings,
    selectedBuilding,
    setSelectedBuilding,
    selectedSource,
    setSelectedSource,
    selectedDayType,
    setSelectedDayType,
    resetFilters,
    latestReading
  } = useSimulation();

  return (
    <header className="sticky top-0 z-20 bg-white border-b border-slate-200 shadow-sm">
      {/* Critical Anomaly Alert Callout */}
      {activeAlert && (
        <div className="bg-gradient-to-r from-red-600 to-rose-600 text-white px-4 py-2.5 text-xs font-medium flex items-center justify-between shadow-md animate-in slide-in-from-top duration-200">
          <div className="flex items-center space-x-2">
            <span className="p-1 bg-white/20 rounded-full animate-bounce">
              <Flame className="w-3.5 h-3.5 text-amber-200" />
            </span>
            <span>{activeAlert}</span>
          </div>
          <button
            onClick={clearAlert}
            className="p-1 hover:bg-white/20 rounded transition-colors"
          >
            <X className="w-4 h-4 text-white" />
          </button>
        </div>
      )}

      {/* Main Control Strip */}
      <div className="px-6 py-3 flex flex-wrap items-center justify-between gap-4">
        {/* Left: Latest Telemetry Ticker */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200 text-slate-700">
            <Gauge className="w-3.5 h-3.5 text-campus-emerald" />
            <span className="font-semibold text-slate-800">Latest Submeter:</span>
            <span className="font-mono text-campus-darkBlue font-bold">{latestReading.buildingName}</span>
          </div>

          <div className="hidden sm:flex items-center space-x-3 text-slate-500 font-mono text-[11px]">
            <span>{latestReading.unitsKwh.toFixed(1)} kWh</span>
            <span>•</span>
            <span>{latestReading.peakKw.toFixed(1)} kW</span>
            <span>•</span>
            <span>{latestReading.voltage} V</span>
            <span>•</span>
            <span className="text-slate-400">{latestReading.timestamp}</span>
          </div>
        </div>

        {/* Right: Live Simulation & Global Filters */}
        <div className="flex items-center flex-wrap gap-2.5">
          {/* Facility Slicer */}
          <select
            value={selectedBuilding}
            onChange={(e) => setSelectedBuilding(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 font-medium text-slate-700 hover:border-slate-300 focus:outline-none focus:ring-2 focus:ring-campus-emerald/20 transition-all"
          >
            <option value="ALL">All 7 Facilities</option>
            {buildings.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>

          {/* Source Slicer */}
          <select
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 font-medium text-slate-700 hover:border-slate-300 focus:outline-none focus:ring-2 focus:ring-campus-emerald/20 transition-all"
          >
            <option value="ALL">All Sources</option>
            <option value="Grid">Utility Grid</option>
            <option value="Solar">Rooftop Solar</option>
            <option value="Generator">Backup Gen</option>
          </select>

          {/* Day Type Slicer */}
          <select
            value={selectedDayType}
            onChange={(e) => setSelectedDayType(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 font-medium text-slate-700 hover:border-slate-300 focus:outline-none focus:ring-2 focus:ring-campus-emerald/20 transition-all"
          >
            <option value="ALL">All Days</option>
            <option value="Weekday">Working Weekdays</option>
            <option value="Weekend">Weekends</option>
          </select>

          {(selectedBuilding !== "ALL" || selectedSource !== "ALL" || selectedDayType !== "ALL") && (
            <button
              onClick={resetFilters}
              title="Reset Filters"
              className="text-xs text-slate-500 hover:text-slate-800 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}

          <div className="h-4 w-px bg-slate-200 mx-1 hidden sm:block" />

          {/* Start / Pause Stream */}
          <button
            onClick={toggleLive}
            className={cn(
              "flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all shadow-sm",
              isLive
                ? "bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200"
                : "bg-campus-emerald text-white hover:bg-campus-emeraldDark shadow-emerald-500/20"
            )}
          >
            {isLive ? (
              <>
                <Pause className="w-3.5 h-3.5 text-amber-600" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Start Live</span>
              </>
            )}
          </button>

          {/* Speed Toggle */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-[11px] font-semibold text-slate-600">
            {[1, 2, 3].map((s) => (
              <button
                key={s}
                onClick={() => setSpeed(s)}
                className={cn(
                  "px-2 py-1 rounded transition-colors",
                  speed === s ? "bg-white text-campus-navy shadow-xs font-bold" : "hover:text-slate-900"
                )}
              >
                {s}x
              </button>
            ))}
          </div>

          {/* Simulate Energy Spike (Demonstration Feature) */}
          <button
            onClick={() => simulateSpike(selectedBuilding !== "ALL" ? selectedBuilding : undefined)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500 hover:bg-amber-600 text-white shadow-sm shadow-amber-500/20 transition-all active:scale-95"
            title="Inject real-time electricity spike to test algorithmic anomaly detection"
          >
            <Zap className="w-3.5 h-3.5 fill-current" />
            <span>Simulate Spike</span>
          </button>

          {/* Reset Baseline */}
          <button
            onClick={resetSimulation}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
            title="Reset Simulation to Clean Baseline"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}

