import { useState } from "react";
import { AlertTriangle, X, MapPin, Clock, ChevronRight, CheckCircle, Loader } from "lucide-react";

// ── API base URL — change this when deploying ─────────────────────────────────
const API_BASE = "http://localhost:8000";

/**
 * Water level options that match the backend's accepted keys.
 * key   → sent to POST /report as water_level_key
 * label → shown to the user
 * color → button accent colour
 */
const WATER_OPTIONS = [
  { key: "dry",   label: "💧 Dry / No water",     color: "#23875b" },
  { key: "ankle", label: "👟 Ankle deep",           color: "#b77810" },
  { key: "wheel", label: "🚗 At wheel height",      color: "#b77810" },
  { key: "knee",  label: "🦵 Above knee",           color: "#d64045" },
  { key: "waist", label: "🌊 Waist deep — DANGER",  color: "#c62828" },
];

/**
 * FloodModal
 *
 * Props:
 *   isOpen    {boolean}   controls visibility
 *   onClose   {function}  called when the modal is dismissed
 *   alert     {object}    flood alert data:
 *     { location, riskLevel, riskColor, message, advice,
 *       minutesUntilFlood, rainfall, waterLevel, lat, lon }
 */
export default function FloodModal({ isOpen, onClose, alert = {} }) {
  const [submitState, setSubmitState] = useState("idle"); // "idle" | "loading" | "success" | "error"
  const [errorMsg,    setErrorMsg]    = useState("");
  const [submitted,   setSubmitted]   = useState(null);  // the chosen WATER_OPTIONS entry

  if (!isOpen) return null;

  const {
    location          = "Serdang, Selangor",
    riskLevel         = "High",
    riskColor         = "#d64045",
    message           = "Upstream river rising rapidly.",
    advice            = "Avoid low-lying underpasses. Take elevated expressway.",
    minutesUntilFlood = 20,
    rainfall          = "42 mm/h",
    waterLevel        = "3.1 m",
    lat               = 3.0738,
    lon               = 101.5183,
  } = alert;

  const riskBg = {
    Low:    "#e8f5ee",
    Medium: "#fef3e0",
    High:   "#fdeaea",
    Severe: "#fde8e8",
  }[riskLevel] ?? "#fdeaea";

  // ── Submit a water-level report to the backend ────────────────────────────
  async function handleReport(option) {
    setSubmitState("loading");
    setSubmitted(option);
    setErrorMsg("");

    try {
      const res = await fetch(`${API_BASE}/report`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          location:        location,
          water_level_key: option.key,
          lat:             lat,
          lon:             lon,
        }),
      });

      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail?.detail ?? `HTTP ${res.status}`);
      }

      setSubmitState("success");
    } catch (err) {
      setSubmitState("error");
      setErrorMsg(err.message || "Could not reach the server.");
    }
  }

  function handleClose() {
    // Reset form state so the modal is clean next time it opens
    setSubmitState("idle");
    setSubmitted(null);
    setErrorMsg("");
    onClose();
  }

  return (
    <div
      onClick={handleClose}
      style={{
        position:       "fixed",
        inset:          0,
        background:     "rgba(21, 45, 75, 0.55)",
        display:        "flex",
        alignItems:     "flex-end",
        justifyContent: "center",
        zIndex:         1000,
        backdropFilter: "blur(2px)",
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width:        "100%",
          maxWidth:     390,
          background:   "#fff",
          borderRadius: "24px 24px 0 0",
          padding:      "0 0 32px",
          boxShadow:    "0 -8px 40px rgba(21,45,75,0.18)",
          animation:    "slideUp 0.22s ease-out",
          maxHeight:    "92dvh",
          overflowY:    "auto",
        }}
      >
        {/* Drag handle */}
        <div style={{ display: "flex", justifyContent: "center", padding: "12px 0 4px" }}>
          <div style={{ width: 40, height: 4, borderRadius: 99, background: "#e4eaf0" }} />
        </div>

        {/* ── Header ── */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 20px 0" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <AlertTriangle size={20} color={riskColor} strokeWidth={2.5} />
            <span style={{ fontWeight: 800, fontSize: 18, color: "#152d4b" }}>Flood Alert</span>
          </div>
          <button
            onClick={handleClose}
            aria-label="Close"
            style={{ background: "#f4f7fa", border: "none", borderRadius: 99, padding: 6, cursor: "pointer", display: "flex" }}
          >
            <X size={18} color="#68788b" />
          </button>
        </div>

        {/* Location */}
        <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "6px 20px 0" }}>
          <MapPin size={14} color="#68788b" />
          <span style={{ fontSize: 13, color: "#68788b" }}>{location}</span>
        </div>

        {/* Risk badge */}
        <div style={{ padding: "14px 20px 0" }}>
          <span style={{ background: riskColor, color: "#fff", padding: "5px 16px", borderRadius: 99, fontSize: 13, fontWeight: 700 }}>
            {riskLevel.toUpperCase()} RISK
          </span>
        </div>

        {/* Alert message */}
        <div style={{ margin: "14px 20px 0", background: riskBg, borderRadius: 14, padding: "12px 14px", borderLeft: `4px solid ${riskColor}` }}>
          <p style={{ fontSize: 14, fontWeight: 600, color: "#152d4b", margin: 0, lineHeight: 1.45 }}>⚠️ {message}</p>
          <p style={{ fontSize: 13, color: "#68788b", margin: "6px 0 0", lineHeight: 1.5 }}>{advice}</p>
        </div>

        {/* Stats */}
        <div style={{ display: "flex", gap: 10, padding: "14px 20px 0" }}>
          {[
            { label: "Rainfall",      value: rainfall },
            { label: "Water level",   value: waterLevel },
            { label: "Time to flood", value: minutesUntilFlood ? `~${minutesUntilFlood} min` : "—" },
          ].map(({ label, value }) => (
            <div key={label} style={{ flex: 1, background: "#f4f7fa", borderRadius: 12, padding: "10px 8px", textAlign: "center" }}>
              <div style={{ fontSize: 15, fontWeight: 800, color: "#152d4b" }}>{value}</div>
              <div style={{ fontSize: 11, color: "#68788b", marginTop: 2 }}>{label}</div>
            </div>
          ))}
        </div>

        {/* Timer */}
        {minutesUntilFlood && (
          <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "12px 20px 0" }}>
            <Clock size={14} color={riskColor} />
            <span style={{ fontSize: 12, color: riskColor, fontWeight: 600 }}>
              Estimated flooding in ~{minutesUntilFlood} minutes
            </span>
          </div>
        )}

        {/* ── Water-level report section ── */}
        <div style={{ margin: "18px 20px 0", borderTop: "1px solid #e4eaf0", paddingTop: 16 }}>
          <div style={{ fontWeight: 700, fontSize: 14, color: "#152d4b", marginBottom: 4 }}>
            Report what you see
          </div>
          <div style={{ fontSize: 12, color: "#68788b", marginBottom: 12, lineHeight: 1.5 }}>
            One tap helps other drivers nearby. Your report is saved to crowd_reports.csv.
          </div>

          {/* Success state */}
          {submitState === "success" && submitted && (
            <div style={{ display: "flex", alignItems: "center", gap: 10, background: "#e8f5ee", border: "1.5px solid #86efac", borderRadius: 12, padding: "12px 14px", marginBottom: 12 }}>
              <CheckCircle size={18} color="#23875b" />
              <div>
                <div style={{ fontWeight: 700, fontSize: 13, color: "#166534" }}>Report submitted</div>
                <div style={{ fontSize: 12, color: "#166534", marginTop: 2 }}>{submitted.label} · saved to crowd_reports.csv</div>
              </div>
            </div>
          )}

          {/* Error state */}
          {submitState === "error" && (
            <div style={{ background: "#fdeaea", border: "1.5px solid #fca5a5", borderRadius: 12, padding: "10px 14px", marginBottom: 12, fontSize: 13, color: "#991b1b" }}>
              ⚠️ {errorMsg} — check that the API server is running on port 8000.
            </div>
          )}

          {/* Option buttons — hidden after success */}
          {submitState !== "success" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {WATER_OPTIONS.map((opt) => {
                const isLoading = submitState === "loading" && submitted?.key === opt.key;
                return (
                  <button
                    key={opt.key}
                    onClick={() => handleReport(opt)}
                    disabled={submitState === "loading"}
                    style={{
                      display:        "flex",
                      alignItems:     "center",
                      justifyContent: "space-between",
                      width:          "100%",
                      padding:        "12px 14px",
                      borderRadius:   12,
                      border:         `1.5px solid ${opt.color}30`,
                      background:     `${opt.color}0d`,
                      cursor:         submitState === "loading" ? "not-allowed" : "pointer",
                      opacity:        submitState === "loading" && submitted?.key !== opt.key ? 0.5 : 1,
                      transition:     "opacity 0.15s",
                    }}
                  >
                    <span style={{ fontSize: 14, fontWeight: 600, color: "#152d4b" }}>{opt.label}</span>
                    {isLoading
                      ? <Loader size={16} color={opt.color} style={{ animation: "spin 1s linear infinite" }} />
                      : <span style={{ fontSize: 12, color: opt.color, fontWeight: 700 }}>Report →</span>
                    }
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* ── Primary actions ── */}
        <div style={{ padding: "16px 20px 0", display: "flex", flexDirection: "column", gap: 10 }}>
          <button
            onClick={handleClose}
            style={{
              width:          "100%",
              height:         50,
              borderRadius:   14,
              background:     "#152d4b",
              color:          "#fff",
              border:         "none",
              fontWeight:     700,
              fontSize:       15,
              cursor:         "pointer",
              display:        "flex",
              alignItems:     "center",
              justifyContent: "center",
              gap:            8,
            }}
          >
            View Safety Tips
            <ChevronRight size={18} />
          </button>
          <button
            onClick={handleClose}
            style={{
              width:        "100%",
              height:       44,
              borderRadius: 14,
              background:   "transparent",
              color:        "#68788b",
              border:       "1.5px solid #e4eaf0",
              fontWeight:   600,
              fontSize:     14,
              cursor:       "pointer",
            }}
          >
            Dismiss
          </button>
        </div>
      </div>

      <style>{`
        @keyframes slideUp {
          from { transform: translateY(100%); opacity: 0; }
          to   { transform: translateY(0);    opacity: 1; }
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
