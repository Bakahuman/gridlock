import React, { useState } from "react";
import { Activity, Camera, Map as MapIcon, Brain } from "lucide-react";
import AnalyzePanel from "./components/AnalyzePanel";
import HotspotMap from "./components/HotspotMap";
import LearnPanel from "./components/LearnPanel";

const TABS = [
  { id: "analyze", label: "Live Analysis", icon: Camera },
  { id: "map", label: "Risk Map", icon: MapIcon },
  { id: "learn", label: "Learning Loop", icon: Brain },
];

export default function App() {
  const [tab, setTab] = useState("analyze");

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 px-6 py-4 flex items-center gap-3">
        <Activity className="text-emerald-400" size={26} />
        <div>
          <h1 className="text-lg font-semibold tracking-tight">Gridlock</h1>
          <p className="text-xs text-slate-400">
            Detect. Forecast. Decide. Learn.
          </p>
        </div>
      </header>

      <nav className="flex gap-1 px-6 pt-4">
        {TABS.map((t) => {
          const Icon = t.icon;
          const active = tab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={
                "flex items-center gap-2 px-4 py-2 rounded-t-lg text-sm " +
                (active
                  ? "bg-slate-800 text-white"
                  : "text-slate-400 hover:text-white")
              }
            >
              <Icon size={16} />
              {t.label}
            </button>
          );
        })}
      </nav>

      <main className="p-6">
        {tab === "analyze" && <AnalyzePanel />}
        {tab === "map" && <HotspotMap />}
        {tab === "learn" && <LearnPanel />}
      </main>
    </div>
  );
}
