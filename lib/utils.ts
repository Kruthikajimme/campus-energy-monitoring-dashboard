import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatKwh(value: number): string {
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(2)} GWh`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toLocaleString("en-US", { maximumFractionDigits: 1 })} MWh`;
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 1 })} kWh`;
}

export function formatRawKwh(value: number): string {
  return `${Math.round(value).toLocaleString("en-US")} kWh`;
}

export function formatKw(value: number): string {
  return `${value.toFixed(1)} kW`;
}

export function formatCurrency(value: number): string {
  if (value >= 100000) {
    return `₹${(value / 100000).toFixed(2)} Lakhs`;
  }
  return `₹${Math.round(value).toLocaleString("en-IN")}`;
}

export function formatCarbon(tonnes: number): string {
  return `${tonnes.toFixed(1)} tCO₂e`;
}

export function formatPercent(value: number): string {
  return `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
}

export function downloadCsv(data: Record<string, any>[], filename: string) {
  if (!data || data.length === 0) return;
  const headers = Object.keys(data[0]);
  const rows = data.map((obj) =>
    headers
      .map((header) => {
        const val = obj[header];
        if (typeof val === "string" && val.includes(",")) {
          return `"${val.replace(/"/g, '""')}"`;
        }
        return val ?? "";
      })
      .join(",")
  );
  const csvContent = [headers.join(","), ...rows].join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

