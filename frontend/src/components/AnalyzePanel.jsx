import React, { useState } from "react";
import { Upload, AlertTriangle, Clock, Users, ShieldAlert } from "lucide-react";
import { analyzeImage } from "../lib/api";

export default function AnalyzePanel() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);

  async function onFile(e) {
    const file = e.target.files[0];
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeImage(file);
      setResults(data.results || []);
    } catch (err) {
      setError("Could not reach the analysis service.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div>
        <label className="block border-2 border-dashed border-slate-700 rounded-xl p-8 text-center cursor-pointer hover:border-emerald-500 transition">
          <Upload className="mx-auto text-slate-500 mb-2" />
          <span className="text-sm text-slate-400">
            Upload a traffic camera frame
          </span>
          <input type="file" accept="image/*" className="hidden" onChange={onFile} />
        </label>

        {preview && (
          <img
            src={preview}
            alt="frame"
            className="mt-4 rounded-xl border border-slate-800 w-full"
          />
        )}
      </div>

      <div className="space-y-4">
        {loading && <p className="text-slate-400 text-sm">Analysing frame…</p>}
        {error && <p className="text-red-400 text-sm">{error}</p>}
        {!loading && results.length === 0 && (
          <p className="text-slate-500 text-sm">
            Detected violations and their forecast impact appear here.
          </p>
        )}
        {results.map((r, i) => (
          <ResultCard key={i} result={r} />
        ))}
      </div>
    </div>
  );
}

function ResultCard({ result }) {
  const { event, forecast, recommendation } = result;
  const isBlock = event.violation_type === "lane_block";

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle
            size={18}
            className={isBlock ? "text-amber-400" : "text-sky-400"}
          />
          <span className="font-medium capitalize">
            {event.violation_type.replace("_", " ")}
          </span>
        </div>
        <span className="text-xs text-slate-500">
          {(event.confidence * 100).toFixed(0)}% conf
        </span>
      </div>

      {event.plate_text && (
        <p className="text-xs text-slate-400 mt-1">
          Plate: <span className="font-mono">{event.plate_text}</span>
        </p>
      )}

      {forecast && (
        <div className="mt-3 grid grid-cols-3 gap-2 text-center">
          <Metric
            icon={<ShieldAlert size={14} />}
            label="Severity"
            value={forecast.severity}
          />
          <Metric
            icon={<AlertTriangle size={14} />}
            label="Closure"
            value={`${(forecast.closure_probability * 100).toFixed(0)}%`}
          />
          <Metric
            icon={<Clock size={14} />}
            label="Clear (min)"
            value={forecast.expected_clearance_minutes}
          />
        </div>
      )}

      {recommendation && (
        <div className="mt-3 bg-slate-800/60 rounded-lg p-3 text-sm">
          <div className="flex items-center gap-2 text-emerald-400 font-medium">
            <Users size={14} />
            Deploy {recommendation.officers} officer
            {recommendation.officers > 1 ? "s" : ""}
            {recommendation.barricade ? " · barricade" : ""}
          </div>
          <p className="text-slate-400 mt-1">{recommendation.diversion_note}</p>
        </div>
      )}
    </div>
  );
}

function Metric({ icon, label, value }) {
  return (
    <div className="bg-slate-800/40 rounded-lg py-2">
      <div className="flex items-center justify-center gap-1 text-slate-500 text-xs">
        {icon}
        {label}
      </div>
      <div className="font-semibold mt-1">{value}</div>
    </div>
  );
}
