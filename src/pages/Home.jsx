import { AlertTriangle } from "lucide-react";

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

      {/* Map placeholder */}
      <div
        style={{
          background:     "#f1f3ef",
          border:         "1px solid #e4eaf0",
          borderRadius:   20,
          height:         320,
          display:        "flex",
          alignItems:     "center",
          justifyContent: "center",
          color:          "#68788b",
          fontSize:       14,
          marginBottom:   10,
          boxShadow:      "0 3px 12px rgba(21,45,75,.05)",
        }}
      >
        🗺️ Map — integrate Leaflet here
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
