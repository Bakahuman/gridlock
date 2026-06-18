const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function analyzeImage(file) {
  const form = new FormData();
  form.append("file", file);
  const r = await fetch(`${BASE}/analyze`, { method: "POST", body: form });
  if (!r.ok) throw new Error("analyze failed");
  return r.json();
}

export async function forecastScenario(ctx) {
  const r = await fetch(`${BASE}/forecast`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(ctx),
  });
  if (!r.ok) throw new Error("forecast failed");
  return r.json();
}

export async function getHotspots(limit = 1500) {
  const r = await fetch(`${BASE}/hotspots?limit=${limit}`);
  if (!r.ok) throw new Error("hotspots failed");
  return r.json();
}

export async function getFeedbackSummary() {
  const r = await fetch(`${BASE}/feedback/summary`);
  if (!r.ok) throw new Error("feedback failed");
  return r.json();
}
