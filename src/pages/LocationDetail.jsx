import { ChevronLeft, MapPin, Cloud, Droplets, LifeBuoy, ShieldCheck, Users, Cpu, RefreshCw } from "lucide-react";

// ── Risk config ───────────────────────────────────────────────────────────────
const RISK = {
  Low: {
    label:    "LOW RISK",
    color:    "#1a7a4a",
    bg:       "#e6f4ed",
    border:   "#a8d5bc",
    cardBg:   "#edf7f1",
    barColor: "#1a7a4a",
    barPos:   0,           // 0 = left segment active
    desc:     "Low estimated risk. Stay alert to changing rainfall.\nFollow official flood alerts.",
  },
  Medium: {
    label:    "MEDIUM RISK",
    color:    "#b77810",
    bg:       "#fef7e6",
    border:   "#f0d080",
    cardBg:   "#fef9ee",
    barColor: "#b77810",
    barPos:   1,
    desc:     "Moderate risk. Monitor water levels closely.\nAvoid flood-prone roads.",
  },
  High: {
    label:    "HIGH RISK",
    color:    "#c62828",
    bg:       "#fdeaea",
    border:   "#f5a5a5",
    cardBg:   "#fff0f0",
    barColor: "#c62828",
    barPos:   2,
    desc:     "High risk. Prepare to evacuate if advised.\nStay away from rivers and drains.",
  },
};

const ACTION_ITEMS = [
  { icon: ShieldCheck, label: "AI Safety Tips",        key: "safety"    },
  { icon: MapPin,      label: "Evacuation Places",     key: "map"       },
  { icon: Users,       label: "Community Help Nearby", key: "community" },
];

/**
 * LocationDetail
 *
 * Props:
 *   onBack            {function}  — called when the ← back button is tapped
 *   onNavigate        {function}  — called with a tab key when an action row is tapped
 *   locationName      {string}
 *   riskLevel         {string}   "Low" | "Medium" | "High"
 *   riskPct           {number}   0-100 from AI model
 *   minutesUntilFlood {number|null}
 *   modelProbability  {number}   0-1 raw probability
 *   predictionHorizon {string}
 *   aiLoading         {boolean}
 *   weather           {object}   { condition, tempC, sunshine, rainfall, forecast }
 */
export default function LocationDetail({
  onBack            = () => {},
  onNavigate        = () => {},
  locationName      = "Serdang, Selangor",
  riskLevel         = "Low",
  riskPct           = 18,
  minutesUntilFlood = null,
  modelProbability  = null,
  predictionHorizon = "next 3 hours",
  aiLoading         = false,
  weather           = {
    condition: "Partly Cloudy",
    tempC:     29,
    sunshine:  "Moderate",
    rainfall:  "8 mm/h",
    forecast:  "12 mm",
  },
}) {
  const risk = RISK[riskLevel] ?? RISK.Low;

  return (
    <div style={page}>

      {/* ── Header bar ── */}
      <div style={headerBar}>
        <button onClick={onBack} style={backBtn} aria-label="Back">
          <ChevronLeft size={22} color="#152d4b" strokeWidth={2.5} />
        </button>
        <div style={headerText}>
          <div style={headerTitle}>Location Details</div>
          <div style={headerSub}>
            <MapPin size={11} color="#68788b" />
            {locationName}
          </div>
          <div style={headerCaption}>Local weather and flood risk</div>
        </div>
      </div>

      {/* ── Weather Today card ── */}
      <div style={card}>
        <div style={cardRowBetween}>
          <div style={cardLabel}>Weather Today</div>
          <Cloud size={22} color="#68788b" />
        </div>

        <div style={weatherMain}>
          {/* Sun/cloud emoji */}
          <span style={weatherEmoji}>⛅</span>
          <div>
            <div style={weatherCondition}>{weather.condition}</div>
            <div style={tempText}>{weather.tempC} °C</div>
          </div>
        </div>

        <div style={weatherGrid}>
          <div style={weatherCell}>
            <div style={weatherCellLabel}>Sunshine</div>
            <div style={weatherCellValue}>{weather.sunshine}</div>
          </div>
          <div style={{ ...weatherCell, textAlign: "right" }}>
            <div style={weatherCellLabel}>Measured rainfall intensity</div>
            <div style={weatherCellValue}>{weather.rainfall}</div>
          </div>
        </div>

        <div style={forecastRow}>
          <Droplets size={13} color="#68788b" />
          <span style={forecastText}>Forecast next 2 hours</span>
          <span style={forecastValue}>{weather.forecast}</span>
        </div>
      </div>

      {/* ── AI Prediction strip ── */}
      <div style={aiCard}>
        <div style={aiCardHeader}>
          <div style={aiCardLabel}>
            <Cpu size={14} color="#1565c0" />
            AI Prediction
          </div>
          {aiLoading
            ? <span style={aiChipLoading}><RefreshCw size={10} /> Updating…</span>
            : <span style={aiChipLive}>● LIVE</span>
          }
        </div>

        {/* Probability bar */}
        <div style={aiBarLabel}>
          <span style={{ fontSize: 12, color: "#68788b" }}>Flood probability ({predictionHorizon ?? "next 3 hrs"})</span>
          <span style={{ fontWeight: 700, fontSize: 13, color: risk.color }}>{riskPct}%</span>
        </div>
        <div style={aiBarTrack}>
          <div style={{ ...aiBarFill, width: `${riskPct}%`, background: risk.color }} />
        </div>

        {/* Minutes + probability row */}
        <div style={aiMetaRow}>
          {minutesUntilFlood != null && (
            <div style={aiMetaChip}>
              <span style={{ fontSize: 16 }}>⏱</span>
              <div>
                <div style={{ fontWeight: 700, fontSize: 13, color: risk.color }}>{minutesUntilFlood} min</div>
                <div style={{ fontSize: 10, color: "#68788b" }}>est. until flood</div>
              </div>
            </div>
          )}
          {modelProbability != null && (
            <div style={aiMetaChip}>
              <span style={{ fontSize: 16 }}>🤖</span>
              <div>
                <div style={{ fontWeight: 700, fontSize: 13, color: "#152d4b" }}>{(modelProbability * 100).toFixed(1)}%</div>
                <div style={{ fontSize: 10, color: "#68788b" }}>model confidence</div>
              </div>
            </div>
          )}
        </div>
        <div style={{ fontSize: 10, color: "#a0aab4", textAlign: "center" }}>
          RandomForest · trained on local sensor data
        </div>
      </div>

      {/* ── Current Flood Risk card ── */}
      <div style={{ ...card, background: risk.cardBg, border: `1.5px solid ${risk.border}` }}>
        <div style={cardLabel}>Current Flood Risk</div>

        {/* Risk badge */}
        <div style={{ ...riskBadge, background: risk.bg, border: `1.5px solid ${risk.border}` }}>
          <span style={{ ...riskDot, background: risk.color }} />
          <span style={{ ...riskBadgeText, color: risk.color }}>{risk.label}</span>
        </div>

        {/* Risk bar */}
        <div style={riskBarWrap}>
          {["LOW", "MEDIUM", "HIGH"].map((seg, i) => {
            const segColors = ["#1a7a4a", "#b77810", "#c62828"];
            const active    = i === risk.barPos;
            return (
              <div
                key={seg}
                style={{
                  ...riskBarSeg,
                  background: active ? segColors[i] : "#e4eaf0",
                  color:      active ? "#fff"        : "#68788b",
                  fontWeight: active ? 700            : 500,
                }}
              >
                {active && <span style={riskBarCheck}>✓ </span>}
                {seg}
              </div>
            );
          })}
        </div>

        {/* Description */}
        <div style={riskDesc}>
          {risk.desc.split("\n").map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>
      </div>

      {/* ── What You Should Do ── */}
      <div style={sectionTitle}>What You Should Do</div>
      <div style={sectionCaption}>
        Monitor official alerts. Explore safety advice and nearby safe places.
      </div>

      <div style={actionList}>
        {ACTION_ITEMS.map(({ icon: Icon, label, key }) => (
          <button key={key} onClick={() => onNavigate(key)} style={actionRow}>
            <div style={actionIcon}>
              <Icon size={18} color="#152d4b" strokeWidth={1.8} />
            </div>
            <span style={actionLabel}>{label}</span>
            <span style={actionArrow}>→</span>
          </button>
        ))}
      </div>

      {/* ── Bottom action buttons ── */}
      <div style={bottomBtns}>
        <button onClick={() => onNavigate("help")} style={helpBtn}>
          <LifeBuoy size={18} strokeWidth={2} />
          Request Help
        </button>
        <button style={sosBtn}>
          <span style={sosBtnIcon}>🆘</span>
          <div style={{ textAlign: "left" }}>
            <div style={{ fontWeight: 700, fontSize: 15 }}>SOS Emergency</div>
            <div style={{ fontSize: 11, opacity: 0.85 }}>Immediate danger</div>
          </div>
        </button>
      </div>

      <div style={bottomCaption}>Nothing is sent automatically.</div>

    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const page = {
  padding:       "0 0 16px",
  display:       "flex",
  flexDirection: "column",
  gap:           12,
  fontFamily:    "'Inter', system-ui, sans-serif",
};

const headerBar = {
  display:    "flex",
  alignItems: "flex-start",
  gap:        8,
  padding:    "16px 16px 4px",
};

const backBtn = {
  background:   "#fff",
  border:       "1.5px solid #e4eaf0",
  borderRadius: 10,
  width:        36,
  height:       36,
  display:      "flex",
  alignItems:   "center",
  justifyContent: "center",
  cursor:       "pointer",
  flexShrink:   0,
  marginTop:    2,
};

const headerText = {
  display:       "flex",
  flexDirection: "column",
  gap:           2,
};

const headerTitle = {
  fontWeight: 800,
  fontSize:   22,
  color:      "#152d4b",
  lineHeight: 1.1,
};

const headerSub = {
  display:    "flex",
  alignItems: "center",
  gap:        4,
  fontSize:   13,
  color:      "#68788b",
  fontWeight: 500,
};

const headerCaption = {
  fontSize: 11,
  color:    "#a0aab4",
};

const card = {
  background:   "#fff",
  borderRadius: 16,
  padding:      "14px 16px",
  margin:       "0 16px",
  boxShadow:    "0 2px 10px rgba(21,45,75,.07)",
  display:      "flex",
  flexDirection: "column",
  gap:          10,
};

const cardRowBetween = {
  display:        "flex",
  justifyContent: "space-between",
  alignItems:     "center",
};

const cardLabel = {
  fontWeight: 700,
  fontSize:   13,
  color:      "#152d4b",
};

const weatherMain = {
  display:    "flex",
  alignItems: "center",
  gap:        12,
};

const weatherEmoji = {
  fontSize:   44,
  lineHeight: 1,
};

const weatherCondition = {
  fontSize:   13,
  color:      "#68788b",
  marginBottom: 2,
};

const tempText = {
  fontWeight: 800,
  fontSize:   36,
  color:      "#152d4b",
  lineHeight: 1,
};

const weatherGrid = {
  display:        "flex",
  justifyContent: "space-between",
};

const weatherCell = {
  display:       "flex",
  flexDirection: "column",
  gap:           2,
};

const weatherCellLabel = {
  fontSize: 11,
  color:    "#68788b",
};

const weatherCellValue = {
  fontWeight: 700,
  fontSize:   13,
  color:      "#152d4b",
};

const forecastRow = {
  display:    "flex",
  alignItems: "center",
  gap:        5,
  background: "#f4f7fa",
  borderRadius: 8,
  padding:    "6px 10px",
};

const forecastText = {
  fontSize: 11,
  color:    "#68788b",
  flex:     1,
};

const forecastValue = {
  fontWeight: 700,
  fontSize:   13,
  color:      "#152d4b",
};

const riskBadge = {
  display:      "flex",
  alignItems:   "center",
  gap:          7,
  borderRadius: 99,
  padding:      "5px 14px",
  alignSelf:    "flex-start",
};

const riskDot = {
  width:        9,
  height:       9,
  borderRadius: "50%",
  display:      "inline-block",
  flexShrink:   0,
};

const riskBadgeText = {
  fontWeight: 700,
  fontSize:   13,
};

const riskBarWrap = {
  display:      "flex",
  borderRadius: 8,
  overflow:     "hidden",
  gap:          3,
};

const riskBarSeg = {
  flex:           1,
  padding:        "6px 4px",
  textAlign:      "center",
  fontSize:       11,
  borderRadius:   6,
  display:        "flex",
  alignItems:     "center",
  justifyContent: "center",
  gap:            2,
};

const riskBarCheck = {
  fontSize: 10,
};

const riskDesc = {
  fontSize:   12,
  color:      "#4a6070",
  lineHeight: 1.6,
  display:    "flex",
  flexDirection: "column",
  gap:        2,
};

const sectionTitle = {
  fontWeight: 800,
  fontSize:   17,
  color:      "#152d4b",
  padding:    "0 16px",
};

const sectionCaption = {
  fontSize:    12,
  color:       "#68788b",
  padding:     "0 16px",
  lineHeight:  1.5,
  marginTop:   -6,
};

const actionList = {
  display:       "flex",
  flexDirection: "column",
  gap:           8,
  padding:       "0 16px",
};

const actionRow = {
  display:      "flex",
  alignItems:   "center",
  gap:          14,
  background:   "#fff",
  border:       "1px solid #e4eaf0",
  borderRadius: 14,
  padding:      "14px 16px",
  cursor:       "pointer",
  boxShadow:    "0 1px 4px rgba(21,45,75,.05)",
  textAlign:    "left",
  width:        "100%",
};

const actionIcon = {
  width:          38,
  height:         38,
  borderRadius:   11,
  background:     "#f4f7fa",
  display:        "flex",
  alignItems:     "center",
  justifyContent: "center",
  flexShrink:     0,
};

const actionLabel = {
  flex:       1,
  fontWeight: 600,
  fontSize:   14,
  color:      "#152d4b",
};

const actionArrow = {
  fontSize: 16,
  color:    "#68788b",
};

const bottomBtns = {
  display: "flex",
  gap:     10,
  padding: "4px 16px 0",
};

const helpBtn = {
  flex:           1,
  display:        "flex",
  alignItems:     "center",
  justifyContent: "center",
  gap:            8,
  background:     "#fff",
  border:         "2px solid #152d4b",
  borderRadius:   14,
  padding:        "13px 8px",
  fontWeight:     700,
  fontSize:       14,
  color:          "#152d4b",
  cursor:         "pointer",
  fontFamily:     "'Inter', system-ui, sans-serif",
};

const sosBtn = {
  flex:           1.4,
  display:        "flex",
  alignItems:     "center",
  gap:            10,
  background:     "#c62828",
  border:         "none",
  borderRadius:   14,
  padding:        "11px 14px",
  color:          "#fff",
  cursor:         "pointer",
  fontFamily:     "'Inter', system-ui, sans-serif",
  boxShadow:      "0 3px 12px rgba(198,40,40,.3)",
};

const sosBtnIcon = {
  fontSize: 22,
};

const bottomCaption = {
  textAlign: "center",
  fontSize:  11,
  color:     "#a0aab4",
  padding:   "0 16px",
};

// ── AI card styles ────────────────────────────────────────────────────────────
const aiCard = {
  background:   "#f0f6ff",
  border:       "1.5px solid #c5d8f5",
  borderRadius: 14,
  padding:      "12px 14px",
  margin:       "0 16px",
  display:      "flex",
  flexDirection: "column",
  gap:          8,
};

const aiCardHeader = {
  display:        "flex",
  justifyContent: "space-between",
  alignItems:     "center",
};

const aiCardLabel = {
  display:    "flex",
  alignItems: "center",
  gap:        6,
  fontWeight: 700,
  fontSize:   13,
  color:      "#1565c0",
};

const aiChipLive = {
  fontSize:     10,
  fontWeight:   700,
  color:        "#1a7a4a",
  background:   "#e6f4ed",
  padding:      "3px 8px",
  borderRadius: 99,
};

const aiChipLoading = {
  fontSize:     10,
  fontWeight:   600,
  color:        "#1565c0",
  background:   "#e8f0fb",
  padding:      "3px 8px",
  borderRadius: 99,
  display:      "flex",
  alignItems:   "center",
  gap:          4,
};

const aiBarLabel = {
  display:        "flex",
  justifyContent: "space-between",
  alignItems:     "center",
};

const aiBarTrack = {
  height:       10,
  background:   "#dce8f8",
  borderRadius: 99,
  overflow:     "hidden",
};

const aiBarFill = {
  height:       "100%",
  borderRadius: 99,
  transition:   "width 0.7s ease",
};

const aiMetaRow = {
  display: "flex",
  gap:     10,
};

const aiMetaChip = {
  flex:         1,
  display:      "flex",
  alignItems:   "center",
  gap:          8,
  background:   "#fff",
  borderRadius: 10,
  padding:      "8px 10px",
  border:       "1px solid #d0e4f7",
};
