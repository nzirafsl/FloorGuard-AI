import { useState, useEffect } from "react";
import { Home as HomeIcon, Map, Shield, LifeBuoy, Phone, Users } from "lucide-react";
import FloodModal      from "./components/FloodModal.jsx";
import SosModal        from "./components/SosModal.jsx";
import HomPage         from "./pages/Home.jsx";
import SafetyTips      from "./pages/SafetyTips.jsx";
import SafePlaces      from "./pages/SafePlaces.jsx";
import RequestHelp     from "./pages/RequestHelp.jsx";
import CommunityHelp   from "./pages/CommunityHelp.jsx";
import LocationDetail  from "./pages/LocationDetail.jsx";
import { predictSerdang } from "./api.js";

// ── Sample alert — fallback used until AI prediction loads ────────────────────
const FALLBACK_ALERT = {
  location:          "Serdang, Selangor",
  riskLevel:         "High",
  riskColor:         "#d64045",
  riskPct:           68,
  message:           "Upstream river rising rapidly. Main route may submerge soon.",
  advice:            "Take the elevated expressway. Avoid low-lying underpasses near Mines Resort City.",
  minutesUntilFlood: 20,
  rainfall:          "42 mm/h",
  waterLevel:        "3.1 m",
  lat:               3.0738,
  lon:               101.5183,
};

// ── Bottom nav tab definitions ────────────────────────────────────────────────
const TABS = [
  { key: "home",      label: "Home",      Icon: HomeIcon },
  { key: "map",       label: "Map",       Icon: Map      },
  { key: "safety",    label: "Safety",    Icon: Shield   },
  { key: "help",      label: "Help",      Icon: LifeBuoy },
  { key: "community", label: "Community", Icon: Users    },
];

export default function App() {
  const [activeTab,    setActiveTab]    = useState("home");
  const [subPage,      setSubPage]      = useState(null);
  const [floodOpen,    setFloodOpen]    = useState(false);
  const [sosOpen,      setSosOpen]      = useState(false);
  const [sosConfirmed, setSosConfirmed] = useState(false);

  // ── AI prediction state ──────────────────────────────────────────────────
  const [alert,        setAlert]        = useState(FALLBACK_ALERT);
  const [aiLoading,    setAiLoading]    = useState(true);
  const [aiError,      setAiError]      = useState(null);

  useEffect(() => {
    let cancelled = false;
    setAiLoading(true);
    predictSerdang()
      .then((res) => {
        if (cancelled) return;
        setAlert((prev) => ({
          ...prev,
          riskLevel:         res.risk_cat,
          riskColor:         res.risk_color,
          riskPct:           res.risk_pct,
          minutesUntilFlood: res.minutes ?? null,
          modelProbability:  res.model_probability,
          predictionHorizon: res.prediction_horizon,
        }));
        setAiError(null);
      })
      .catch((err) => {
        if (cancelled) return;
        console.warn("[AI] prediction failed, using fallback:", err.message);
        setAiError("AI backend offline — showing last known data.");
      })
      .finally(() => { if (!cancelled) setAiLoading(false); });
    return () => { cancelled = true; };
  }, []);

  function handleSosConfirm() {
    setSosConfirmed(true);
    console.log("[SOS] confirmed at", new Date().toISOString());
  }

  function handleNavigate(tabKey) {
    setSubPage(null);
    setActiveTab(tabKey);
  }

  // ── Page content switcher ──────────────────────────────────────────────────
  function renderPage() {
    // Sub-page: Location Detail (drill-down from Home)
    if (subPage === "locationDetail") {
      return (
        <LocationDetail
          locationName={alert.location}
          riskLevel={alert.riskLevel}
          riskPct={alert.riskPct}
          minutesUntilFlood={alert.minutesUntilFlood}
          modelProbability={alert.modelProbability}
          predictionHorizon={alert.predictionHorizon}
          aiLoading={aiLoading}
          onBack={() => setSubPage(null)}
          onNavigate={handleNavigate}
        />
      );
    }

    switch (activeTab) {
      case "home":
        return (
          <HomPage
            locationName={alert.location}
            locationSub="Selangor · Malaysia"
            riskLevel={alert.riskLevel}
            riskColor={alert.riskColor}
            riskPct={alert.riskPct}
            aiLoading={aiLoading}
            alert={alert}
            onOpenFloodModal={() => setSubPage("locationDetail")}
            onOpenSosModal={()   => setSosOpen(true)}
          />
        );
      case "map":
        return <SafePlaces />;
      case "safety":
        return (
          <SafetyTips
            riskLevel={alert.riskLevel}
            riskColor={alert.riskColor}
            riskPct={alert.riskPct}
            aiLoading={aiLoading}
            aiError={aiError}
          />
        );
      case "help":
        return <RequestHelp />;
      case "community":
        return <CommunityHelp />;
      default:
        return null;
    }
  }

  return (
    <div style={shell}>

      {/* ── Sticky header ── */}
      <header style={header}>
        <div style={logo}>🛡️</div>
        <span style={appName}>FloodAlert</span>
        <span style={country}>Malaysia</span>
      </header>

      {/* ── AI status strip ── */}
      {aiError && (
        <div style={aiBanner}>⚠️ {aiError}</div>
      )}
      {aiLoading && (
        <div style={{ ...aiBanner, background: "#e8f0fb", color: "#1565c0" }}>
          🤖 AI model loading prediction…
        </div>
      )}

      {/* ── Scrollable page area ── */}
      <main style={pageArea}>
        {renderPage()}
      </main>

      {/* ── Fixed footer: SOS + bottom nav ── */}
      <footer style={footerWrap}>
        {/* SOS button */}
        <div style={{ padding: "6px 20px 0" }}>
          <button
            onClick={() => { setSosOpen(true); setSosConfirmed(false); }}
            style={sosBtn}
          >
            <Phone size={20} strokeWidth={2.5} />
            SOS Emergency
          </button>
          <div style={sosSub}>
            Follow official flood alerts · Call 999 in real emergencies
          </div>
        </div>

        {/* Nav bar */}
        <nav style={navBar}>
          {TABS.map(({ key, label, Icon }) => {
            const active = activeTab === key;
            return (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                style={navItem}
                aria-label={label}
              >
                <div style={{ ...navPill, background: active ? "#f4f7fa" : "transparent" }}>
                  <Icon size={20} color={active ? "#152d4b" : "#68788b"} strokeWidth={active ? 2.2 : 1.8} />
                </div>
                <span style={{ ...navLabel, fontWeight: active ? 700 : 500, color: active ? "#152d4b" : "#68788b" }}>
                  {label}
                </span>
              </button>
            );
          })}
        </nav>

        {/* Home indicator pill */}
        <div style={homeIndicator} />
      </footer>

      {/* ── Modals (always mounted, visibility via isOpen) ── */}
      <FloodModal
        isOpen={floodOpen}
        onClose={() => setFloodOpen(false)}
        alert={alert}
      />
      <SosModal
        isOpen={sosOpen}
        onClose={() => setSosOpen(false)}
        location={alert.location}
        onConfirm={handleSosConfirm}
      />
    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const shell = {
  minHeight:  "100dvh",
  maxWidth:   390,
  margin:     "0 auto",
  background: "#f4f7fa",
  fontFamily: "'Inter', system-ui, sans-serif",
  display:    "flex",
  flexDirection: "column",
  position:   "relative",
};

const header = {
  background:   "#fff",
  borderBottom: "1px solid #e4eaf0",
  display:      "flex",
  alignItems:   "center",
  gap:          10,
  height:       64,
  padding:      "0 20px",
  position:     "sticky",
  top:          0,
  zIndex:       200,
  flexShrink:   0,
};

const logo = {
  background:     "#152d4b",
  width:          36,
  height:         36,
  borderRadius:   11,
  display:        "flex",
  alignItems:     "center",
  justifyContent: "center",
  fontSize:       18,
  flexShrink:     0,
};

const appName = {
  fontWeight: 700,
  fontSize:   22,
  color:      "#152d4b",
};

const country = {
  marginLeft:    "auto",
  fontWeight:    600,
  fontSize:      10,
  color:         "#68788b",
  textTransform: "uppercase",
  letterSpacing: ".8px",
};

const pageArea = {
  flex:       1,
  overflowY:  "auto",
  // leave room for the fixed footer (~130px: SOS 66px + nav 66px)
  paddingBottom: 130,
};

const footerWrap = {
  position:   "fixed",
  bottom:     0,
  left:       "50%",
  transform:  "translateX(-50%)",
  width:      "100%",
  maxWidth:   390,
  background: "#f4f7fa",
  zIndex:     200,
};

const sosBtn = {
  width:          "100%",
  height:         50,
  borderRadius:   14,
  background:     "#c62828",
  color:          "#fff",
  border:         "none",
  fontWeight:     700,
  fontSize:       17,
  cursor:         "pointer",
  display:        "flex",
  alignItems:     "center",
  justifyContent: "center",
  gap:            10,
  boxShadow:      "0 3px 12px rgba(198,40,40,.25)",
};

const sosSub = {
  textAlign:  "center",
  fontSize:   10,
  color:      "#68788b",
  padding:    "4px 0 5px",
  lineHeight: 1.5,
};

const navBar = {
  background: "#fff",
  borderTop:  "1px solid #e4eaf0",
  display:    "flex",
  padding:    "5px 6px 0",
  boxShadow:  "0 -2px 10px rgba(21,45,75,.06)",
};

const navItem = {
  flex:           1,
  display:        "flex",
  flexDirection:  "column",
  alignItems:     "center",
  gap:            2,
  paddingBottom:  4,
  background:     "none",
  border:         "none",
  cursor:         "pointer",
};

const navPill = {
  width:          48,
  height:         28,
  borderRadius:   100,
  display:        "flex",
  alignItems:     "center",
  justifyContent: "center",
  transition:     "background 0.15s",
};

const navLabel = {
  fontSize: 11,
};

const homeIndicator = {
  width:        134,
  height:       5,
  background:   "#152d4b",
  borderRadius: 100,
  margin:       "4px auto 0",
};

const aiBanner = {
  background:  "#fff8e1",
  color:       "#7a5800",
  fontSize:    11,
  fontWeight:  600,
  padding:     "6px 16px",
  textAlign:   "center",
  flexShrink:  0,
};
