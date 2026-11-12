"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import summaryData from "@/lib/data/summary.json";
import buildingsData from "@/lib/data/buildings.json";
import anomaliesData from "@/lib/data/anomalies.json";
import recentTelemetryData from "@/lib/data/recent_telemetry.json";
import { Building, SummaryKPIs, AnomalyRecord, TelemetryReading } from "@/lib/types";

interface SimulationContextType {
  isLive: boolean;
  speed: number;
  toggleLive: () => void;
  setSpeed: (speed: number) => void;
  simulateSpike: (targetBuildingId?: string) => void;
  resetSimulation: () => void;
  activeAlert: string | null;
  clearAlert: () => void;

  // Live Metrics
  liveSummary: SummaryKPIs;
  latestReading: TelemetryReading;
  recentStream: TelemetryReading[];
  anomalies: AnomalyRecord[];
  buildings: Building[];

  // Global Slicers & Filters
  selectedBuilding: string;
  setSelectedBuilding: (bld: string) => void;
  selectedSource: string;
  setSelectedSource: (src: string) => void;
  selectedDayType: string;
  setSelectedDayType: (dayType: string) => void;
  resetFilters: () => void;
}

const SimulationContext = createContext<SimulationContextType | undefined>(undefined);

export function SimulationProvider({ children }: { children: React.ReactNode }) {
  const [isLive, setIsLive] = useState<boolean>(true);
  const [speed, setSpeed] = useState<number>(1);
  const [activeAlert, setActiveAlert] = useState<string | null>(null);

  // Filters
  const [selectedBuilding, setSelectedBuilding] = useState<string>("ALL");
  const [selectedSource, setSelectedSource] = useState<string>("ALL");
  const [selectedDayType, setSelectedDayType] = useState<string>("ALL");

  // State
  const [liveSummary, setLiveSummary] = useState<SummaryKPIs>(summaryData as SummaryKPIs);
  const [anomalies, setAnomalies] = useState<AnomalyRecord[]>(anomaliesData as AnomalyRecord[]);
  const [buildings, setBuildings] = useState<Building[]>(buildingsData as Building[]);
  const [recentStream, setRecentStream] = useState<TelemetryReading[]>((recentTelemetryData as TelemetryReading[]).slice(0, 15));
  const [readingIndex, setReadingIndex] = useState<number>(0);

  const latestReading = recentStream[0] || (recentTelemetryData[0] as TelemetryReading);

  // Clear alert after 6 seconds
  useEffect(() => {
    if (activeAlert) {
      const timer = setTimeout(() => setActiveAlert(null), 7000);
      return () => clearTimeout(timer);
    }
  }, [activeAlert]);

  // Live simulation tick
  useEffect(() => {
    if (!isLive) return;

    const intervalMs = speed === 3 ? 800 : speed === 2 ? 1500 : 2500;

    const interval = setInterval(() => {
      // Pick a random building for live simulated telemetry
      const bld = buildingsData[Math.floor(Math.random() * buildingsData.length)];
      const baseLoad = bld.baseloadKw || 40;
      const hour = new Date().getHours();
      const isWorkingHour = hour >= 8 && hour <= 18;
      const variation = (Math.random() - 0.45) * 15;
      const currentKwh = Math.max(12, Math.round((baseLoad * (isWorkingHour ? 1.4 : 0.7) + variation) * 10) / 10);
      const currentPeak = Math.max(currentKwh, Math.round((currentKwh * (1.1 + Math.random() * 0.25)) * 10) / 10);
      const voltage = Math.round((228 + (Math.random() - 0.5) * 6) * 10) / 10;
      const occupancy = isWorkingHour ? Math.floor(bld.designCapacity * (0.3 + Math.random() * 0.5)) : Math.floor(bld.designCapacity * 0.05);
      const sources = ["Grid", "Grid", "Solar", "Solar", "Generator"];
      const source = isWorkingHour && hour >= 9 && hour <= 16 ? "Solar" : sources[Math.floor(Math.random() * sources.length)];

      const now = new Date();
      const timestamp = now.toISOString().replace("T", " ").substring(0, 19);

      const newReading: TelemetryReading = {
        readingId: 900000 + readingIndex,
        timestamp,
        buildingId: bld.id,
        buildingName: bld.name,
        unitsKwh: currentKwh,
        peakKw: currentPeak,
        voltage,
        occupancy,
        sourceName: source,
        temperature: Math.round((24 + Math.sin((hour - 8) / 12 * Math.PI) * 7) * 10) / 10,
        isAnomaly: 0,
        severity: "Normal",
      };

      setRecentStream((prev) => [newReading, ...prev.slice(0, 24)]);
      setReadingIndex((prev) => prev + 1);

      // Increment live totals
      setLiveSummary((prev) => {
        const addedKwh = currentKwh / 10;
        const newTotal = prev.totalKwh + addedKwh;
        const newCarbon = prev.carbonEmissionsKg + addedKwh * 0.82;
        return {
          ...prev,
          totalKwh: Math.round(newTotal * 10) / 10,
          totalMwh: Math.round((newTotal / 1000) * 100) / 100,
          carbonEmissionsKg: Math.round(newCarbon * 10) / 10,
          carbonEmissionsTonnes: Math.round((newCarbon / 1000) * 100) / 100,
          totalCostInr: Math.round(newTotal * 8.0),
          totalCostLakhs: Math.round((newTotal * 8.0 / 100000) * 100) / 100,
          totalRecords: prev.totalRecords + 1,
        };
      });
    }, intervalMs);

    return () => clearInterval(interval);
  }, [isLive, speed, readingIndex]);

  // Inject a realistic surge to demonstrate live anomaly detection
  const simulateSpike = useCallback((targetBuildingId?: string) => {
    const targetBld = targetBuildingId
      ? buildingsData.find((b) => b.id === targetBuildingId) || buildingsData[0]
      : buildingsData[Math.floor(Math.random() * 2)]; // Academic Block or CS Block

    const now = new Date();
    const timestamp = now.toISOString().replace("T", " ").substring(0, 19);
    const spikeKwh = Math.round((380 + Math.random() * 85) * 10) / 10; // 380-465 kWh
    const spikePeak = Math.round((spikeKwh * 1.35) * 10) / 10; // ~520 kW
    const baseline = targetBld.avgHourlyKwh || 85.0;
    const deviationPct = Math.round(((spikeKwh - baseline) / baseline) * 1000) / 10;

    const newAnomaly: AnomalyRecord = {
      id: `ANOM-LIVE-${Math.floor(1000 + Math.random() * 9000)}`,
      timestamp,
      buildingId: targetBld.id,
      buildingName: targetBld.name,
      recordedKwh: spikeKwh,
      expectedKwh: baseline,
      deviationKwh: Math.round((spikeKwh - baseline) * 10) / 10,
      deviationPct,
      peakKw: spikePeak,
      severity: "Critical",
      method: "Rolling Z-Score (Live Algorithmic Stream)",
      reason: `Sudden operational surge: +${deviationPct}% above baseline (Z=3.8)`,
      recommendedAction: `Urgent: Inspect ${targetBld.name} motor starters, sub-feeder currents and unauthorized heavy chiller testing immediately.`,
    };

    const spikeReading: TelemetryReading = {
      readingId: 999000 + Math.floor(Math.random() * 1000),
      timestamp,
      buildingId: targetBld.id,
      buildingName: targetBld.name,
      unitsKwh: spikeKwh,
      peakKw: spikePeak,
      voltage: 216.5,
      occupancy: 240,
      sourceName: "Grid",
      temperature: 28.5,
      isAnomaly: 1,
      severity: "Critical",
    };

    // Update state
    setAnomalies((prev) => [newAnomaly, ...prev]);
    setRecentStream((prev) => [spikeReading, ...prev.slice(0, 24)]);
    setLiveSummary((prev) => ({
      ...prev,
      activeAnomalies: prev.activeAnomalies + 1,
      peakDemandKw: Math.max(prev.peakDemandKw, spikePeak),
      totalKwh: Math.round((prev.totalKwh + spikeKwh) * 10) / 10,
      totalCostInr: Math.round((prev.totalKwh + spikeKwh) * 8.0),
    }));

    setActiveAlert(`CRITICAL SURGE DETECTED in ${targetBld.name}: Recorded ${spikeKwh} kWh (+${deviationPct}% above expected baseline). Flagged for engineering dispatch.`);
  }, []);

  const resetSimulation = useCallback(() => {
    setLiveSummary(summaryData as SummaryKPIs);
    setAnomalies(anomaliesData as AnomalyRecord[]);
    setBuildings(buildingsData as Building[]);
    setRecentStream((recentTelemetryData as TelemetryReading[]).slice(0, 15));
    setActiveAlert(null);
  }, []);

  const resetFilters = useCallback(() => {
    setSelectedBuilding("ALL");
    setSelectedSource("ALL");
    setSelectedDayType("ALL");
  }, []);

  return (
    <SimulationContext.Provider
      value={{
        isLive,
        speed,
        toggleLive: () => setIsLive((prev) => !prev),
        setSpeed,
        simulateSpike,
        resetSimulation,
        activeAlert,
        clearAlert: () => setActiveAlert(null),
        liveSummary,
        latestReading,
        recentStream,
        anomalies,
        buildings,
        selectedBuilding,
        setSelectedBuilding,
        selectedSource,
        setSelectedSource,
        selectedDayType,
        setSelectedDayType,
        resetFilters,
      }}
    >
      {children}
    </SimulationContext.Provider>
  );
}

export function useSimulation() {
  const context = useContext(SimulationContext);
  if (!context) {
    throw new Error("useSimulation must be used within a SimulationProvider");
  }
  return context;
}

