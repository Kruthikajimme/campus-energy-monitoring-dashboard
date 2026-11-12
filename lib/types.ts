export interface Building {
  id: string;
  name: string;
  type: string;
  designCapacity: number;
  meterId: string;
  baseloadKw: number;
  activeHours: string;
  color: string;
  totalKwh: number;
  peakKw: number;
  avgHourlyKwh: number;
  kwhPerOccupant: number;
  anomaliesCount: number;
  sharePct: number;
  rank?: number;
}

export interface SummaryKPIs {
  totalKwh: number;
  totalMwh: number;
  averageDailyKwh: number;
  peakDemandKw: number;
  carbonEmissionsKg: number;
  carbonEmissionsTonnes: number;
  activeAnomalies: number;
  kwhPerOccupant: number;
  totalCostInr: number;
  totalCostLakhs: number;
  totalRecords: number;
  monitoredBuildings: number;
  startDate: string;
  endDate: string;
  weekendLoadDropPct: number;
  topConsumer: string;
  topConsumerShare: number;
  lowestConsumer: string;
  lowestConsumerShare: number;
}

export interface DailyTrend {
  date: string;
  totalKwh: number;
  peakKw: number;
  avgVoltage: number;
  totalOccupancy: number;
  avgTemp: number;
  rolling7d: number;
  dayType: string;
  isWeekend: string;
}

export interface HourlyPattern {
  hour: number;
  label: string;
  averageKwh: number;
  weekdayKwh: number;
  weekendKwh: number;
  peakKw: number;
  occupancy: number;
  temperature: number;
}

export interface EnergySource {
  id: string;
  name: string;
  isRenewable: boolean;
  totalKwh: number;
  carbonKg: number;
  sharePct: number;
  color: string;
}

export interface AnomalyRecord {
  id: string;
  timestamp: string;
  buildingId: string;
  buildingName: string;
  recordedKwh: number;
  expectedKwh: number;
  deviationKwh: number;
  deviationPct: number;
  peakKw: number;
  severity: "Critical" | "High" | "Medium" | "Low";
  method: string;
  reason: string;
  recommendedAction: string;
}

export interface TelemetryReading {
  readingId: number;
  timestamp: string;
  buildingId: string;
  buildingName: string;
  unitsKwh: number;
  peakKw: number;
  voltage: number;
  occupancy: number;
  sourceName: string;
  temperature: number;
  isAnomaly: number;
  severity: string;
}

export interface HeatmapPoint {
  day: string;
  hour: number;
  label: string;
  kwh: number;
}

