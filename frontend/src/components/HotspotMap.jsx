import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker } from "react-leaflet";
import { getHotspots } from "../lib/api";

export default function HotspotMap() {
  const [points, setPoints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHotspots(1500)
      .then((d) => setPoints(d.points || []))
      .catch(() => setPoints([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <p className="text-sm text-slate-400 mb-3">
        Historical illegal-parking concentration across Bengaluru
        {!loading && ` · ${points.length} points`}
      </p>
      <div className="rounded-xl overflow-hidden border border-slate-800" style={{ height: 540 }}>
        <MapContainer center={[12.97, 77.59]} zoom={12} style={{ height: "100%" }}>
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution="&copy; OpenStreetMap &copy; CARTO"
          />
          {points.map((p, i) => (
            <CircleMarker
              key={i}
              center={[p.lat, p.lng]}
              radius={4}
              pathOptions={{ color: "#f59e0b", fillOpacity: 0.5, weight: 0 }}
            />
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
