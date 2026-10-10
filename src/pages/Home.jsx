import { useEffect, useRef } from "react";
import { AlertTriangle } from "lucide-react";
import "leaflet/dist/leaflet.css";

// ── Safe places for the home map markers ─────────────────────────────────────
const SAFE_PLACES = [
  { icon: "🏫", name: "SK Serdang",       lat: 2.9982,  lon: 101.7036, color: "#1565c0" },
  { icon: "🏥", name: "Hospital Putrajaya",lat: 2.9264,  lon: 101.6964, color: "#c62828" },
  { icon: "🅿️", name: "SACC Mall Parking", lat: 3.0726,  lon: 101.5220, color: "#2e7d32" },
  { icon: "🏛️", name: "Dewan Serdang",     lat: 3.0140,  lon: 101.7010, color: "#6a1b9a" },
];

function makePinIcon(L, emoji, color) {
  return L.divIcon({
    className: "",
    html: `<div style="
        width:32px;height:32px;border-radius:50% 50% 50% 0;
        background:${color};transform:rotate(-45deg);
        border:2px solid #fff;box-shadow:0 2px 5px rgba(0,0,0,.3);
        display:flex;align-items:center;justify-content:center;">
      <span style="transform:rotate(45deg);font-size:13px;line-height:1">${emoji}</span>
    </div>`,
    iconSize: [32, 32], iconAnchor: [16, 32], popupAnchor: [0, -34],
  });
}

function makeUserPin(L) {
  return L.divIcon({
    className: "",
    html: `<div style="
        width:16px;height:16px;border-radius:50%;
        background:#1565c0;border:3px solid #fff;
        box-shadow:0 0 0 4px rgba(21,101,192,.25);"></div>`,
    iconSize: [16, 16], iconAnchor: [8, 8],
  });
}

// ── Mini-map component ────────────────────────────────────────────────────────
function HomeMap({ lat, lon, riskColor }) {
  const divRef    = useRef(null);
  const mapHandle = useRef(null);

  useEffect(() => {
    const el = divRef.current;
    if (!el) return;

    if (mapHandle.current) { mapHandle.current.remove(); mapHandle.current = null; }

    import("leaflet").then((mod) => {
      const L = mod.default ?? mod;
      if (!divRef.current) return;

      const map = L.map(divRef.current, {
        center: [lat, lon], zoom: 13,
        zoomControl: true, attributionControl: true,
      });
      mapHandle.current = map;
      setTimeout(() => map.invalidateSize(), 0);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19,
      }).addTo(map);

      // Flood risk circle
      L.circle([lat, lon], {
        radius: 1200, color: riskColor, fillColor: riskColor,
        fillOpacity: 0.1, weight: 2, dashArray: "6 4",
      }).addTo(map).bindPopup("⚠️ High flood-risk zone");

      // User marker
      L.marker([lat, lon], { icon: makeUserPin(L) })
        .addTo(map)
        .bindPopup("<b>📍 Your Location</b><br/>Serdang, Selangor")
        .openPopup();

      // Safe-place markers
      SAFE_PLACES.forEach(({ icon, name, lat: slat, lon: slon, color }) => {
        L.marker([slat, slon], { icon: makePinIcon(L, icon, color) })
          .addTo(map)
          .bindPopup(`<b>${icon} ${name}</b>`);
      });
    });

    return () => {
      if (mapHandle.current) { mapHandle.current.remove(); mapHandle.current = null; }
    };
  }, [lat, lon, riskColor]);

  return <div ref={divRef} style={{ width: "100%", height: "100%" }} />;
}

/**
 * Home — main map/overview screen.
 *
 * All modal state lives in App.jsx. This component receives callbacks
 * so it doesn't need to import or manage FloodModal / SosModal itself.
 *
 * Props:
 *   locationName       {string}
 *   locationSub        {string}
 *   riskLevel          {string}   "Low" | "Medium" | "High" | "Severe"
 *   riskColor          {string}   hex colour
 *   onOpenFloodModal   {function}  called when the risk banner is tapped
 */
export default function Home({
  locationName     = "Serdang, Selangor",
  locationSub      = "Selangor · Malaysia",
  riskLevel        = "High",
  riskColor        = "#d64045",
  onOpenFloodModal = () => {},
}) {
  const riskBg = {
    Low:    "#e8f5ee",
    Medium: "#fef3e0",
    High:   "#fdeaea",
    Severe: "#fde8e8",
  }[riskLevel] ?? "#fdeaea";

  return (
    <div style={{ padding: "10px 20px 0" }}>

      {/* Location heading */}
      <div style={{ padding: "6px 0 10px" }}>
        <div style={{ fontWeight: 700, fontSize: 17, color: "#152d4b" }}>{locationName}</div>
        <div style={{ fontSize: 11, color: "#68788b", marginTop: 2 }}>{locationSub}</div>
      </div>

      {/* Tappable risk banner → opens FloodModal */}
      <button
        onClick={onOpenFloodModal}
        style={{
          width:        "100%",
          background:   riskBg,
          border:       `1.5px solid ${riskColor}30`,
          borderRadius: 16,
          padding:      "14px 16px",
          display:      "flex",
          alignItems:   "center",
          gap:          12,
          cursor:       "pointer",
          marginBottom: 14,
          textAlign:    "left",
        }}
      >
        <AlertTriangle size={22} color={riskColor} />
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: 14, color: "#152d4b" }}>
            Current flood risk:{" "}
            <span style={{ color: riskColor }}>{riskLevel}</span>
          </div>
          <div style={{ fontSize: 12, color: "#68788b", marginTop: 2 }}>
            Tap to see details and safety tips
          </div>
        </div>
        <span
          style={{
            background:   riskColor,
            color:        "#fff",
            padding:      "3px 10px",
            borderRadius: 99,
            fontSize:     12,
            fontWeight:   700,
          }}
        >
          {riskLevel.toUpperCase()}
        </span>
      </button>

      {/* Live Leaflet map */}
      <div
        style={{
          border:       "1px solid #e4eaf0",
          borderRadius: 20,
          height:       320,
          marginBottom: 10,
          boxShadow:    "0 3px 12px rgba(21,45,75,.05)",
          overflow:     "hidden",
          background:   "#e8eef4",
        }}
      >
        <HomeMap lat={3.0738} lon={101.5183} riskColor={riskColor} />
      </div>

      {/* Risk legend */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "4px 0 6px" }}>
        <span style={{ fontSize: 11, fontWeight: 600, color: "#68788b" }}>Risk level</span>
        {[["#23875b", "LOW"], ["#b77810", "MEDIUM"], ["#d64045", "HIGH"]].map(
          ([c, l], i) => (
            <span key={l} style={{ display: "flex", alignItems: "center", gap: 4 }}>
              {i > 0 && (
                <span style={{ color: "#68788b", fontSize: 10 }}>→</span>
              )}
              <span
                style={{
                  width:        8,
                  height:       8,
                  borderRadius: "50%",
                  background:   c,
                  display:      "inline-block",
                }}
              />
              <span style={{ fontSize: 10, fontWeight: 700, color: c }}>{l}</span>
            </span>
          )
        )}
      </div>
    </div>
  );
}
