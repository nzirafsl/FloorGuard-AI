import { Shield, AlertTriangle, Package, Droplets, RefreshCw, Cpu } from "lucide-react";

const TIPS_BY_RISK = {
  Low: [
    { Icon: AlertTriangle, title: "Monitor rainfall and official forecasts",    body: "Check MET Malaysia updates before travel. Conditions can change rapidly." },
    { Icon: Droplets,      title: "Avoid flood-prone roads after heavy rain",   body: "Even when it looks clear, drains may still be overflowing underneath."    },
    { Icon: Package,       title: "Prepare a basic go-bag",                     body: "Keep documents, medication, water and a charged phone ready just in case." },
    { Icon: Shield,        title: "Follow official JPS and NADMA instructions", body: "AI guidance is supplementary — not a substitute for official warnings."    },
  ],
  Medium: [
    { Icon: AlertTriangle, title: "Stay on high ground and monitor updates",    body: "Water levels can rise fast. Move belongings upstairs if possible."         },
    { Icon: Droplets,      title: "Avoid crossing flooded roads",               body: "30 cm of fast water can sweep a car. Turn around, don't drown."            },
    { Icon: Package,       title: "Charge devices and top up emergency kit",    body: "Power outages often accompany flooding. Have a torch and power bank ready." },
    { Icon: Shield,        title: "Know your nearest evacuation centre",        body: "Check the Evacuation Places tab and identify your route now."               },
  ],
  High: [
    { Icon: AlertTriangle, title: "Be ready to evacuate immediately",           body: "If authorities advise evacuation, leave at once. Do not wait."             },
    { Icon: Droplets,      title: "Never walk through floodwater",              body: "Waist-deep water is life-threatening. Await rescue if trapped."             },
    { Icon: Package,       title: "Take your emergency kit and documents",      body: "Grab your go-bag: IDs, medication, phone charger, cash, water."             },
    { Icon: Shield,        title: "Call 999 or go to an evacuation centre",     body: "Report trapped persons to BOMBA (994) immediately."                         },
  ],
  Severe: [
    { Icon: AlertTriangle, title: "SEVERE RISK — evacuate now if advised",      body: "This is an emergency. Follow all official instructions without delay."     },
    { Icon: Droplets,      title: "Stay off all roads and away from rivers",    body: "Flood surges can arrive without warning at severe risk levels."             },
    { Icon: Package,       title: "Move to highest ground available",           body: "If you cannot evacuate, go to the highest floor and signal for rescue."    },
    { Icon: Shield,        title: "Activate SOS if in immediate danger",        body: "Use the SOS button below or call 999. Share your GPS location."             },
  ],
};

const RISK_CONFIG = {
  Low:    { color: "#1a7a4a", bg: "#e6f4ed", label: "LOW RISK"    },
  Medium: { color: "#b77810", bg: "#fef7e6", label: "MEDIUM RISK" },
  High:   { color: "#c62828", bg: "#fdeaea", label: "HIGH RISK"   },
  Severe: { color: "#7b1fa2", bg: "#f3e5f5", label: "SEVERE RISK" },
};

// Simple gauge bar
function RiskGauge({ pct, color }) {
  return (
    <div style={gaugeWrap}>
      <div style={{ ...gaugeBar, width: `${pct}%`, background: color }} />
    </div>
  );
}

export default function SafetyTips({
  riskLevel  = "High",
  riskColor  = "#c62828",
  riskPct    = 68,
  aiLoading  = false,
  aiError    = null,
}) {
  const cfg  = RISK_CONFIG[riskLevel] ?? RISK_CONFIG.High;
  const tips = TIPS_BY_RISK[riskLevel] ?? TIPS_BY_RISK.High;

  return (
    <div style={page}>

      {/* ── Header ── */}
      <div style={heading}>
        <div style={titleRow}>
          <Cpu size={20} color="#152d4b" />
          <span style={titleText}>AI Safety Tips</span>
        </div>
        <div style={subtitle}>
          Advice adapts to the live AI prediction. Not an official warning.
        </div>
      </div>

      {/* ── AI Prediction card ── */}
      <div style={predCard}>
        <div style={predHeader}>
          <div style={predLabel}>
            <Cpu size={14} color="#1565c0" />
            AI Flood Prediction
          </div>
          {aiLoading
            ? <span style={loadingChip}><RefreshCw size={11} /> Updating…</span>
            : <span style={liveChip}>● LIVE</span>
          }
        </div>

        {aiError && (
          <div style={errorRow}>⚠️ {aiError}</div>
        )}

        {/* Risk level badge */}
        <div style={{ ...riskBadge, background: cfg.bg }}>
          <span style={{ ...riskDot, background: cfg.color }} />
          <span style={{ ...riskBadgeText, color: cfg.color }}>{cfg.label}</span>
        </div>

        {/* Probability gauge */}
        <div style={gaugeSection}>
          <div style={gaugeLabel}>
            <span>Flood probability (next 3 hrs)</span>
            <span style={{ color: cfg.color, fontWeight: 700 }}>{riskPct}%</span>
          </div>
          <RiskGauge pct={riskPct} color={cfg.color} />
        </div>

        {/* Risk scale pills */}
        <div style={scalePills}>
          {[["Low","#1a7a4a"], ["Medium","#b77810"], ["High","#c62828"], ["Severe","#7b1fa2"]].map(([label, color]) => (
            <div
              key={label}
              style={{
                ...scalePill,
                background: riskLevel === label ? color : "#f0f4f8",
                color:      riskLevel === label ? "#fff"  : "#68788b",
                fontWeight: riskLevel === label ? 700     : 500,
              }}
            >
              {label}
            </div>
          ))}
        </div>

        <div style={predFooter}>
          Powered by RandomForest · trained on local flood sensor data
        </div>
      </div>

      {/* ── Dynamic tips ── */}
      <div style={tipsHeader}>
        <div style={tipsTitle}>Recommended Actions</div>
        <div style={tipsSub}>Based on current AI risk level: <strong>{riskLevel}</strong></div>
      </div>

      <div style={tipsList}>
        {tips.map(({ Icon, title, body }) => (
          <div key={title} style={tipCard}>
            <div style={tipIcon}>
              <Icon size={18} color="#152d4b" />
            </div>
            <div>
              <div style={tipTitle}>{title}</div>
              <div style={tipBody}>{body}</div>
            </div>
          </div>
        ))}
      </div>

      <div style={disclaimer}>
        ⚠️ AI guidance is not a substitute for official JPS, NADMA, or BOMBA warnings.
      </div>

    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const page = {
  padding:       "20px 16px 8px",
  display:       "flex",
  flexDirection: "column",
  gap:           14,
};

const heading = {
  display:       "flex",
  flexDirection: "column",
  gap:           4,
};

const titleRow = {
  display:    "flex",
  alignItems: "center",
  gap:        8,
};

const titleText = {
  fontWeight: 800,
  fontSize:   22,
  color:      "#152d4b",
};

const subtitle = {
  fontSize:   13,
  color:      "#68788b",
  lineHeight: 1.5,
};

const predCard = {
  background:   "#fff",
  borderRadius: 16,
  padding:      "14px 16px",
  boxShadow:    "0 2px 10px rgba(21,45,75,.07)",
  border:       "1px solid #e4eaf0",
  display:      "flex",
  flexDirection: "column",
  gap:          10,
};

const predHeader = {
  display:        "flex",
  justifyContent: "space-between",
  alignItems:     "center",
};

const predLabel = {
  display:    "flex",
  alignItems: "center",
  gap:        6,
  fontWeight: 700,
  fontSize:   13,
  color:      "#152d4b",
};

const liveChip = {
  fontSize:     10,
  fontWeight:   700,
  color:        "#1a7a4a",
  background:   "#e6f4ed",
  padding:      "3px 8px",
  borderRadius: 99,
};

const loadingChip = {
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

const errorRow = {
  fontSize:     11,
  color:        "#b77810",
  background:   "#fef7e6",
  padding:      "6px 10px",
  borderRadius: 8,
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
  flexShrink:   0,
};

const riskBadgeText = {
  fontWeight: 700,
  fontSize:   13,
};

const gaugeSection = {
  display:       "flex",
  flexDirection: "column",
  gap:           5,
};

const gaugeLabel = {
  display:        "flex",
  justifyContent: "space-between",
  fontSize:       12,
  color:          "#68788b",
};

const gaugeWrap = {
  height:       10,
  background:   "#f0f4f8",
  borderRadius: 99,
  overflow:     "hidden",
};

const gaugeBar = {
  height:       "100%",
  borderRadius: 99,
  transition:   "width 0.6s ease",
};

const scalePills = {
  display: "flex",
  gap:     6,
};

const scalePill = {
  flex:         1,
  textAlign:    "center",
  fontSize:     11,
  padding:      "5px 4px",
  borderRadius: 8,
};

const predFooter = {
  fontSize:  10,
  color:     "#a0aab4",
  textAlign: "center",
};

const tipsHeader = {
  display:       "flex",
  flexDirection: "column",
  gap:           2,
};

const tipsTitle = {
  fontWeight: 700,
  fontSize:   15,
  color:      "#152d4b",
};

const tipsSub = {
  fontSize: 12,
  color:    "#68788b",
};

const tipsList = {
  display:       "flex",
  flexDirection: "column",
  gap:           10,
};

const tipCard = {
  display:      "flex",
  alignItems:   "flex-start",
  gap:          14,
  background:   "#fff",
  borderRadius: 14,
  padding:      "14px 16px",
  border:       "1px solid #e4eaf0",
  boxShadow:    "0 1px 4px rgba(21,45,75,.05)",
};

const tipIcon = {
  background:     "#f4f7fa",
  borderRadius:   10,
  padding:        8,
  flexShrink:     0,
  display:        "flex",
  alignItems:     "center",
  justifyContent: "center",
};

const tipTitle = {
  fontWeight: 700,
  fontSize:   14,
  color:      "#152d4b",
  lineHeight: 1.3,
};

const tipBody = {
  fontSize:   12,
  color:      "#68788b",
  marginTop:  3,
  lineHeight: 1.45,
};

const disclaimer = {
  fontSize:      11,
  color:         "#68788b",
  textAlign:     "center",
  lineHeight:    1.5,
  paddingBottom: 4,
};
