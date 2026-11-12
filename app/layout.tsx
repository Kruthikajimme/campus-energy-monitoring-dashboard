import type { Metadata } from "next";
import "./globals.css";
import { SimulationProvider } from "@/context/SimulationContext";
import Sidebar from "@/components/Sidebar";
import TopHeader from "@/components/TopHeader";

export const metadata: Metadata = {
  title: "Campus Energy IQ | Smart Electricity Monitoring & Analytics",
  description:
    "An enterprise-grade campus energy monitoring, predictive analytics, and automated anomaly detection platform for university facilities administration.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-campus-bg text-campus-text min-h-screen flex antialiased">
        <SimulationProvider>
          {/* Left Navigation Sidebar */}
          <Sidebar />

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
            <TopHeader />
            <main className="flex-1 overflow-y-auto px-6 py-6 lg:px-8">
              {children}
            </main>
          </div>
        </SimulationProvider>
      </body>
    </html>
  );
}

