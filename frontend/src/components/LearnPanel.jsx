import React, { useEffect, useState } from "react";
import { Brain, Target, TrendingUp } from "lucide-react";
import { getFeedbackSummary } from "../lib/api";

export default function LearnPanel() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    getFeedbackSummary()
      .then(setSummary)
      .catch(() => setSummary({ count: 0 }));
  }, []);

  return (
    <div className="max-w-2xl">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="text-emerald-400" />
        <h2 className="text-lg font-medium">Learning Loop</h2>
      </div>

      <p className="text-sm text-slate-400 mb-6">
        After every incident the system compares what it predicted against what
        actually happened, then folds the result back in. This is the
        post-incident learning the brief asks for and most tools skip.
      </p>

      {!summary || summary.count === 0 ? (
        <p className="text-slate-500 text-sm">
          No outcomes logged yet. As incidents close, accuracy trends appear
          here.
        </p>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          <Stat
            icon={<Target size={16} />}
            label="Incidents learned from"
            value={summary.count}
          />
          <Stat
            icon={<TrendingUp size={16} />}
            label="Severity accuracy"
            value={`${(summary.severity_accuracy * 100).toFixed(0)}%`}
          />
          <Stat
            icon={<TrendingUp size={16} />}
            label="Clearance error (min)"
            value={summary.clearance_mae_minutes ?? "—"}
          />
        </div>
      )}
    </div>
  );
}

function Stat({ icon, label, value }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <div className="flex items-center gap-2 text-slate-500 text-xs">
        {icon}
        {label}
      </div>
      <div className="text-2xl font-semibold mt-2">{value}</div>
    </div>
  );
}
