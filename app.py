# -*- coding: utf-8 -*-
"""
FloodGuard AI — Full-featured demo
All 5 key features implemented in a single-file Streamlit app.
Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import datetime
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FloodGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
TRAIN_PATH  = DATA_DIR / "synthetic_flood_training_data.csv"
LOC_PATH    = DATA_DIR / "sample_locations.csv"
CROWD_PATH  = DATA_DIR / "crowd_reports.csv"

# ── Generate synthetic data on first run ───────────────────────────────────────
def generate_data():
    rng = np.random.default_rng(42)
    n = 3000
    rain1  = rng.exponential(15, n).clip(0, 250)
    rain3  = (rain1 * 2.5 + rng.exponential(10, n)).clip(0, 500)
    rain24 = (rain3 * 3.5 + rng.exponential(20, n)).clip(0, 1000)
    water  = rng.uniform(0.5, 6.0, n)
    wchange= rng.normal(0.05, 0.2, n).clip(-2, 3)
    drain  = rng.uniform(0.1, 1.0, n)
    elev   = rng.exponential(12, n).clip(1, 500)
    imperv = rng.integers(20, 100, n)
    near_r = rng.integers(0, 2, n)
    score  = (
        0.30*(rain1/60) + 0.20*(rain3/150) + 0.10*(rain24/300)
      + 0.15*(water/6)  + 0.10*(wchange.clip(0,3)/3)
      + 0.08*(1-drain)  + 0.04*(imperv/100) + 0.03*near_r
      - 0.05*(elev/500) + rng.normal(0, 0.05, n)
    ).clip(0, 1)
    pd.DataFrame({
        "rainfall_1h_mm": rain1.round(1), "rainfall_3h_mm": rain3.round(1),
        "rainfall_24h_mm": rain24.round(1), "water_level_m": water.round(2),
        "water_level_change_m_per_h": wchange.round(3),
        "drainage_capacity_index": drain.round(3), "elevation_m": elev.round(1),
        "impervious_surface_pct": imperv.astype(int), "near_river": near_r.astype(int),
        "flood_within_next_3h": (score > 0.42).astype(int),
    }).to_csv(TRAIN_PATH, index=False)

    pd.DataFrame([
        ("Shah Alam",    "Petaling",  "Selangor", 3.0738,101.5183, 38,85,190,3.1,0.22,0.38,7, 82,1,"Basement Parking Flooding"),
        ("Kota Bharu",   "Kota Bharu","Kelantan", 6.1254,102.2381, 55,130,280,4.5,0.41,0.30,5, 65,1,"Blocked Highway Route"),
        ("Kuantan",      "Kuantan",   "Pahang",   3.8126,103.3256, 20,45,100,1.8,0.08,0.60,12,55,1,"Blocked Highway Route"),
        ("Kuala Lumpur", "KL City",   "W.P. KL",  3.1390,101.6869, 42,95,200,2.9,0.18,0.35,9, 88,1,"Basement Parking Flooding"),
        ("Johor Bahru",  "JB City",   "Johor",    1.4927,103.7414, 15,35, 80,1.2,0.03,0.65,15,70,0,"Blocked Highway Route"),
        ("Kota Kinabalu","KK City",   "Sabah",    5.9804,116.0735, 28,62,140,2.2,0.12,0.52,8, 60,1,"Basement Parking Flooding"),
        ("Kuching",      "Kuching",   "Sarawak",  1.5535,110.3593, 12,28, 65,1.0,0.02,0.72,20,45,0,"Blocked Highway Route"),
    ], columns=[
        "name","district","state","lat","lon",
        "rainfall_1h_mm","rainfall_3h_mm","rainfall_24h_mm",
        "water_level_m","water_level_change_m_per_h",
        "drainage_capacity_index","elevation_m","impervious_surface_pct",
        "near_river","threat_type"
    ]).to_csv(LOC_PATH, index=False)

    pd.DataFrame({
        "location":  ["Shah Alam","Kota Bharu","Kuala Lumpur","Kota Bharu","Shah Alam"],
        "water_level_report": ["At wheel height","Above knee","Ankle deep","Waist deep","At wheel height"],
        "reported_at": ["2026-10-10 14:05","2026-10-10 13:58","2026-10-10 14:10","2026-10-10 14:15","2026-10-10 14:28"],
        "lat":  [3.0720,6.1230,3.1380,6.1260,3.0745],
        "lon":  [101.5160,102.2360,101.6855,102.2390,101.5190],
    }).to_csv(CROWD_PATH, index=False)

if not TRAIN_PATH.exists():
    generate_data()

# ── Train model ────────────────────────────────────────────────────────────────
FEATURES = [
    "rainfall_1h_mm","rainfall_3h_mm","rainfall_24h_mm",
    "water_level_m","water_level_change_m_per_h",
    "drainage_capacity_index","elevation_m","impervious_surface_pct","near_river"
]

@st.cache_resource
def train_model():
    df = pd.read_csv(TRAIN_PATH)
    X, y = df[FEATURES], df["flood_within_next_3h"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("clf", RandomForestClassifier(n_estimators=250, class_weight="balanced",
                                       random_state=42, min_samples_leaf=4, n_jobs=-1))
    ])
    pipe.fit(Xtr, ytr)
    pred = pipe.predict(Xte)
    prob = pipe.predict_proba(Xte)[:,1]
    return pipe, {
        "Accuracy": round(accuracy_score(yte, pred),3),
        "F1":       round(f1_score(yte, pred, zero_division=0),3),
        "ROC AUC":  round(roc_auc_score(yte, prob),3),
    }

model, model_metrics = train_model()

def predict_risk(row_dict):
    row = pd.DataFrame([{f: row_dict[f] for f in FEATURES}])
    prob = float(model.predict_proba(row)[0,1])
    pct  = round(prob * 100)
    if   pct < 20: cat, color, minutes = "Low",    "#22c55e", None
    elif pct < 45: cat, color, minutes = "Medium", "#f59e0b", 30
    elif pct < 70: cat, color, minutes = "High",   "#f97316", 20
    else:          cat, color, minutes = "Severe", "#ef4444", 12
    return pct, cat, color, minutes

# ── Load location data ─────────────────────────────────────────────────────────
@st.cache_data
def load_locations():
    df = pd.read_csv(LOC_PATH)
    rows = []
    for _, r in df.iterrows():
        row_dict = r.to_dict()
        pct, cat, color, mins = predict_risk(row_dict)
        row_dict.update({"risk_pct": pct, "risk_cat": cat, "risk_color": color, "minutes": mins})
        rows.append(row_dict)
    return pd.DataFrame(rows)

@st.cache_data
def load_crowd():
    return pd.read_csv(CROWD_PATH)

locs   = load_locations()
crowd  = load_crowd()

# ── Session state defaults ─────────────────────────────────────────────────────
if "page"              not in st.session_state: st.session_state.page = "map"
if "selected_loc"      not in st.session_state: st.session_state.selected_loc = "Shah Alam"
if "filter_cat"        not in st.session_state: st.session_state.filter_cat = "All"
if "emergency_cleared" not in st.session_state: st.session_state.emergency_cleared = {}
if "safety_confirmed"  not in st.session_state: st.session_state.safety_confirmed = {}
if "crowd_reports"     not in st.session_state: st.session_state.crowd_reports = []
if "emergency_contact" not in st.session_state: st.session_state.emergency_contact = ""
if "ping_sent"         not in st.session_state: st.session_state.ping_sent = {}

# ── Helpers ────────────────────────────────────────────────────────────────────
CAT_ORDER = ["Low", "Medium", "High", "Severe"]
CAT_COLORS = {"Low":"#22c55e","Medium":"#f59e0b","High":"#f97316","Severe":"#ef4444"}
CAT_BG     = {"Low":"#dcfce7","Medium":"#fef9c3","High":"#ffedd5","Severe":"#fee2e2"}

def cat_badge(cat):
    c = CAT_COLORS.get(cat,"#888")
    return f'<span style="background:{c};color:#fff;padding:2px 10px;border-radius:99px;font-size:0.78rem;font-weight:700">{cat}</span>'

def hyper_local_advice(loc_row):
    name = loc_row["name"]
    threat = loc_row["threat_type"]
    wc = loc_row["water_level_change_m_per_h"]
    rain1 = loc_row["rainfall_1h_mm"]
    mins = loc_row["minutes"]

    if threat == "Basement Parking Flooding":
        if loc_row["risk_cat"] in ("High","Severe"):
            return (
                f"Basement drainage in {name} overwhelmed — move vehicle to Level 2+ immediately.",
                "🅿️ Elevated Safe Parking: Nearby elevated multi-storey car parks on higher floors."
            )
        return (
            f"Rainfall accumulating; basement flood risk building in {name}.",
            "🅿️ Monitor basement water sensors. Consider moving vehicle to upper floors."
        )
    else:  # Blocked Highway Route
        if loc_row["risk_cat"] in ("High","Severe"):
            return (
                f"Upstream river rising rapidly; {name} main route will submerge in ~{mins} mins.",
                "🔀 Alternative Route: Take elevated expressway or inland road. Avoid low-lying underpasses."
            )
        return (
            f"Surface runoff increasing near {name} highway corridor.",
            "🔀 Stay on elevated roads. Monitor traffic alerts before departing."
        )

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Force narrow mobile-style canvas */
[data-testid="stAppViewContainer"] > .main > .block-container {
    max-width: 430px !important;
    padding: 0 0 80px 0 !important;
    margin: 0 auto !important;
}
[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }

/* Bottom nav bar */
.bottom-nav {
    position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
    width: 430px; background: #fff; border-top: 1px solid #e5e7eb;
    display: flex; z-index: 1000; box-shadow: 0 -2px 10px rgba(0,0,0,.08);
}
.nav-item {
    flex: 1; display: flex; flex-direction: column; align-items: center;
    padding: 8px 4px 10px; cursor: pointer; color: #6b7280; font-size: 0.68rem;
    border: none; background: transparent;
}
.nav-item.active { color: #2563eb; font-weight: 700; }
.nav-icon { font-size: 1.35rem; margin-bottom: 2px; }

/* Top app bar */
.app-bar {
    background: #1e3a5f; color: #fff;
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px; position: sticky; top: 0; z-index: 999;
}
.app-bar-title { font-weight: 800; font-size: 1.05rem; letter-spacing:.3px; }
.sos-btn {
    background: #ef4444; color: #fff; border: none; border-radius: 8px;
    padding: 5px 14px; font-weight: 800; font-size: 0.85rem; cursor: pointer;
    letter-spacing: 1px;
}
.demo-banner {
    background: #eff6ff; border-bottom: 1px solid #bfdbfe;
    padding: 5px 16px; font-size: 0.72rem; color: #2563eb;
    display: flex; align-items: center; gap: 6px;
}

/* Risk cards */
.risk-card {
    border-radius: 16px; padding: 16px; margin: 8px 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,.08); background: #fff;
}
.risk-card-header { display:flex; justify-content:space-between; align-items:flex-start; }
.risk-card-title { font-weight: 700; font-size: 1.05rem; color: #111827; }
.risk-card-sub   { font-size: 0.78rem; color: #6b7280; margin-top: 2px; }
.risk-card-meta  { font-size: 0.7rem; color: #9ca3af; margin-top: 10px; }

/* Filter chips */
.chip-row { display:flex; gap:6px; padding: 0 12px 8px; overflow-x:auto; flex-wrap:nowrap; }
.chip {
    border-radius: 99px; padding: 5px 14px; font-size: 0.78rem; font-weight: 600;
    border: 1.5px solid #e5e7eb; background:#f9fafb; color:#374151; white-space:nowrap;
    cursor:pointer;
}
.chip.active { background:#2563eb; color:#fff; border-color:#2563eb; }

/* Emergency overlay */
.emergency-overlay {
    background: linear-gradient(135deg,#7f1d1d,#ef4444);
    border-radius: 16px; margin: 8px 12px; padding: 20px;
    color: #fff; text-align: center; animation: pulse 1s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.85} }
.emergency-title { font-size: 1.4rem; font-weight: 900; letter-spacing: 1px; }
.emergency-sub   { font-size: 0.85rem; opacity:.9; margin: 8px 0 16px; }

/* Progress bar */
.prob-bar-track { background:#e5e7eb; border-radius:99px; height:8px; overflow:hidden; }
.prob-bar-fill  { height:8px; border-radius:99px; transition:width .4s; }

/* Section header */
.section-label {
    font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.2px; color: #9ca3af; padding: 12px 16px 4px;
}

/* Info row */
.info-row { display:flex; gap:8px; padding: 0 12px; flex-wrap:wrap; }
.info-tile {
    flex:1; min-width:80px; background:#f3f4f6; border-radius:12px;
    padding: 10px 12px; text-align:center;
}
.info-tile-val { font-size:1.1rem; font-weight:800; color:#111827; }
.info-tile-lbl { font-size:0.65rem; color:#6b7280; margin-top:2px; }

/* Alert list */
.alert-item {
    display:flex; align-items:flex-start; gap:12px;
    border-left: 4px solid; padding: 12px 14px; margin: 6px 12px;
    border-radius: 0 12px 12px 0; background:#fff;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.alert-icon { font-size:1.3rem; }
.alert-title { font-weight:700; font-size:0.9rem; }
.alert-body  { font-size:0.78rem; color:#4b5563; margin-top:3px; line-height:1.4; }
.alert-time  { font-size:0.68rem; color:#9ca3af; margin-top:6px; }

/* Crowd report form */
.crowd-btn {
    display:flex; align-items:center; justify-content:center; gap:8px;
    width:100%; padding:14px; border-radius:12px; font-size:0.88rem; font-weight:700;
    border:2px solid; cursor:pointer; background:#fff; margin:4px 0;
}

/* Safety status */
.safety-ok   { background:#dcfce7; border:1.5px solid #86efac; border-radius:12px; padding:14px 16px; margin:6px 12px; }
.safety-warn { background:#fee2e2; border:1.5px solid #fca5a5; border-radius:12px; padding:14px 16px; margin:6px 12px; }
</style>
""", unsafe_allow_html=True)

# ── Compute counts ─────────────────────────────────────────────────────────────
counts = {cat: int((locs["risk_cat"]==cat).sum()) for cat in CAT_ORDER}
severe_locs = locs[locs["risk_cat"]=="Severe"]
high_locs   = locs[locs["risk_cat"]=="High"]

# ══════════════════════════════════════════════════════════════════════════════
# TOP APP BAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="app-bar">
  <div style="display:flex;align-items:center;gap:10px">
    <span style="font-size:1.5rem">🛡️</span>
    <span class="app-bar-title">FloodGuard AI</span>
  </div>
  <div style="display:flex;align-items:center;gap:10px">
    <span style="font-size:1.3rem;cursor:pointer">🔔</span>
    <button class="sos-btn">SOS</button>
  </div>
</div>
<div class="demo-banner">
  ℹ️ <span><b>Demo mode · Sample data</b> — Not for emergency use. Follow official JPS/MET warnings.</span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# EMERGENCY OVERRIDE — shown above everything if any Severe location
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "map":
    for _, srow in severe_locs.iterrows():
        loc_name = srow["name"]
        if not st.session_state.emergency_cleared.get(loc_name, False):
            advice_text, action_text = hyper_local_advice(srow)
            mins = srow["minutes"]
            st.markdown(f"""
            <div class="emergency-overlay">
              <div class="emergency-title">🚨 SEVERE FLOOD WARNING</div>
              <div class="emergency-sub">{loc_name} · Imminent threat in ~{mins} minutes</div>
              <div style="font-size:0.88rem;background:rgba(255,255,255,.15);
                   border-radius:10px;padding:10px 14px;text-align:left;margin-bottom:12px">
                ⚠️ {advice_text}<br><br>
                {action_text}
              </div>
              <div style="font-size:0.75rem;opacity:.8;margin-bottom:12px">
                📳 Priority alert — confirm action below to dismiss
              </div>
            </div>
            """, unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Vehicle Moved", key=f"moved_{loc_name}", use_container_width=True):
                    st.session_state.emergency_cleared[loc_name] = True
                    st.rerun()
            with col_b:
                if st.button("🔀 Route Changed", key=f"route_{loc_name}", use_container_width=True):
                    st.session_state.emergency_cleared[loc_name] = True
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME / MAP
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "map":

    # Hero text
    st.markdown("""
    <div style="padding:16px 16px 4px">
      <div style="font-size:1.6rem;font-weight:900;color:#111827;line-height:1.2">Know your risk.</div>
      <div style="font-size:0.85rem;color:#6b7280;margin-top:4px">Explore 7 sample locations across Malaysia.</div>
    </div>
    """, unsafe_allow_html=True)

    # Search bar (static UI)
    st.markdown("""
    <div style="margin:10px 12px">
      <div style="display:flex;align-items:center;gap:8px;background:#f3f4f6;
           border-radius:12px;padding:10px 14px">
        <span style="color:#9ca3af">🔍</span>
        <span style="color:#9ca3af;font-size:0.88rem">Search a location in Malaysia...</span>
      </div>
    </div>
    <div style="display:flex;align-items:center;justify-content:space-between;padding:4px 16px 8px">
      <div style="font-size:0.82rem;color:#2563eb;font-weight:600">📍 Shah Alam, Selangor</div>
      <div style="font-size:0.78rem;color:#2563eb;font-weight:600">⊕ Use My Location</div>
    </div>
    """, unsafe_allow_html=True)

    # Risk count tiles
    st.markdown('<div class="info-row">', unsafe_allow_html=True)
    for cat in CAT_ORDER:
        c = CAT_COLORS[cat]
        bg = CAT_BG[cat]
        cnt = counts[cat]
        st.markdown(f"""
        <div class="info-tile" style="background:{bg}">
          <div class="info-tile-val" style="color:{c}">{cnt:02d}</div>
          <div class="info-tile-lbl">{cat}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Filter chips — use actual buttons
    st.markdown('<div style="padding:8px 12px 4px;font-size:0.72rem;color:#9ca3af;font-weight:700;text-transform:uppercase;letter-spacing:1px">Filter by risk level</div>', unsafe_allow_html=True)
    chip_cols = st.columns(5)
    chip_labels = ["All"] + CAT_ORDER
    for i, label in enumerate(chip_labels):
        with chip_cols[i]:
            active = st.session_state.filter_cat == label
            if st.button(
                label,
                key=f"chip_{label}",
                use_container_width=True,
                type="primary" if active else "secondary"
            ):
                st.session_state.filter_cat = label
                st.rerun()

    # ── Interactive Map via Leaflet (HTML component) ───────────────────────────
    import streamlit.components.v1 as components

    map_markers = []
    for _, r in locs.iterrows():
        map_markers.append({
            "name": r["name"], "state": r["state"],
            "lat": r["lat"], "lon": r["lon"],
            "cat": r["risk_cat"], "pct": int(r["risk_pct"]),
            "color": r["risk_color"], "threat": r["threat_type"],
        })

    crowd_markers = []
    for _, r in crowd.iterrows():
        crowd_markers.append({
            "loc": r["location"], "report": r["water_level_report"],
            "lat": float(r["lat"]), "lon": float(r["lon"]),
        })

    markers_json  = json.dumps(map_markers)
    crowd_json    = json.dumps(crowd_markers)

    map_html = f"""
    <!DOCTYPE html><html><head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
      body{{margin:0;padding:0;font-family:system-ui,sans-serif}}
      #map{{height:320px;width:100%;border-radius:12px}}
      .legend{{background:#fff;padding:8px 12px;border-radius:10px;
               box-shadow:0 1px 6px rgba(0,0,0,.15);font-size:11px;line-height:1.8}}
      .marker-label{{font-weight:700;font-size:11px;white-space:nowrap}}
    </style>
    </head><body>
    <div id="map"></div>
    <div style="padding:4px 6px;font-size:10px;color:#9ca3af;text-align:center">
      Geographic illustration · 7 sample markers · Not for navigation
    </div>
    <script>
    var markers = {markers_json};
    var crowd   = {crowd_json};
    var map = L.map('map',{{zoomControl:false}}).setView([4.2,109.5],5);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
      {{attribution:'© OSM',maxZoom:18}}).addTo(map);
    L.control.zoom({{position:'bottomright'}}).addTo(map);

    function colorIcon(color,cat){{
      var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="38" viewBox="0 0 30 38">'
        + '<path d="M15 0C7 0 0 7 0 15c0 11 15 23 15 23S30 26 30 15C30 7 23 0 15 0z" fill="'+color+'"/>'
        + '<circle cx="15" cy="15" r="8" fill="white"/>'
        + '<text x="15" y="19" text-anchor="middle" font-size="8" font-weight="bold" fill="'+color+'">'+cat.substring(0,1)+'</text>'
        + '</svg>';
      return L.divIcon({{
        html: svg, iconSize:[30,38], iconAnchor:[15,38], popupAnchor:[0,-38],
        className:''
      }});
    }}

    markers.forEach(function(m){{
      var mk = L.marker([m.lat,m.lon],{{icon:colorIcon(m.color,m.cat)}}).addTo(map);
      mk.bindPopup('<b>'+m.name+'</b><br><span style="color:'+m.color+'">'+m.cat+'</span> · '+m.pct+'%<br><small>'+m.threat+'</small>');
    }});

    // Crowd dots
    crowd.forEach(function(c){{
      L.circleMarker([c.lat,c.lon],{{
        radius:6,fillColor:'#6366f1',color:'#fff',weight:2,fillOpacity:.9
      }}).addTo(map).bindPopup('<b>👥 '+c.loc+'</b><br>'+c.report);
    }});

    // Legend
    var legend = L.control({{position:'bottomleft'}});
    legend.onAdd = function(){{
      var div = L.DomUtil.create('div','legend');
      div.innerHTML = '<b>Risk Level</b><br>'
        + '<span style="color:#22c55e">●</span> Low &nbsp;'
        + '<span style="color:#f59e0b">●</span> Medium &nbsp;'
        + '<span style="color:#f97316">●</span> High &nbsp;'
        + '<span style="color:#ef4444">●</span> Severe<br>'
        + '<span style="color:#6366f1">●</span> Crowd report';
      return div;
    }};
    legend.addTo(map);
    </script>
    </body></html>
    """
    components.html(map_html, height=370, scrolling=False)

    # ── Location cards ────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Active Locations</div>', unsafe_allow_html=True)

    filt = st.session_state.filter_cat
    display_locs = locs if filt == "All" else locs[locs["risk_cat"] == filt]

    for _, row in display_locs.iterrows():
        cat   = row["risk_cat"]
        color = row["risk_color"]
        pct   = row["risk_pct"]
        bg    = CAT_BG[cat]
        advice, action = hyper_local_advice(row)
        mins  = row["minutes"]

        st.markdown(f"""
        <div class="risk-card" style="border-left:4px solid {color}">
          <div class="risk-card-header">
            <div>
              <div class="risk-card-title">{row['name']}</div>
              <div class="risk-card-sub">{row['state']} · {row['district']} district</div>
            </div>
            <div style="text-align:right">
              <span style="background:{color};color:#fff;padding:3px 10px;
                border-radius:99px;font-size:0.75rem;font-weight:700">{cat}</span>
              <div style="font-size:0.7rem;color:#9ca3af;margin-top:4px">Sample</div>
            </div>
          </div>
          <div style="margin:10px 0 4px">
            <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#6b7280;margin-bottom:4px">
              <span>Flood probability</span><span style="font-weight:700;color:{color}">{pct}%</span>
            </div>
            <div class="prob-bar-track">
              <div class="prob-bar-fill" style="width:{pct}%;background:{color}"></div>
            </div>
          </div>
          <div style="font-size:0.78rem;color:#374151;margin-top:8px;
               background:{bg};border-radius:8px;padding:8px 10px">
            ⚠️ {advice}
          </div>
          <div style="font-size:0.75rem;color:#6b7280;margin-top:6px">
            🛠 {action}
          </div>
          <div class="risk-card-meta">
            🌧 {row['rainfall_1h_mm']}mm/1h · 💧 {row['water_level_m']}m water level
            {f"· ⏱ ~{mins} mins" if mins else ""}
            · Sample update · {datetime.datetime.now().strftime("%H:%M")} MYT
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Dead-Man's Switch — for High/Severe only
        if cat in ("High","Severe"):
            loc_name = row["name"]
            if not st.session_state.safety_confirmed.get(loc_name, False):
                ping_sent = st.session_state.ping_sent.get(loc_name, False)
                if not ping_sent:
                    st.markdown(f"""
                    <div class="safety-warn">
                      <div style="font-weight:700;color:#991b1b;font-size:0.88rem">🔴 Safety Check Required</div>
                      <div style="font-size:0.78rem;color:#7f1d1d;margin-top:4px">
                        You appear to be in or near a {cat.lower()} zone. Confirm your safety within 3 minutes
                        or an automatic location ping will be sent to your emergency contact.
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ I'm Safe — {loc_name}", key=f"safe_{loc_name}", use_container_width=True):
                            st.session_state.safety_confirmed[loc_name] = True
                            st.rerun()
                    with col2:
                        if st.button(f"📲 Send Ping Now", key=f"ping_{loc_name}", use_container_width=True):
                            st.session_state.ping_sent[loc_name] = True
                            st.rerun()
                else:
                    st.markdown(f"""
                    <div class="safety-warn">
                      <div style="font-weight:700;color:#991b1b">📲 Location Ping Sent</div>
                      <div style="font-size:0.78rem;color:#7f1d1d;margin-top:4px">
                        Your coordinates near <b>{loc_name}</b> have been sent to your emergency contact
                        via SMS. Stay safe and move to higher ground.
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="safety-ok">
                  <div style="font-weight:700;color:#166534;font-size:0.85rem">✅ Safety confirmed for {loc_name}</div>
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ALERTS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "alerts":
    st.markdown('<div style="padding:16px 16px 4px;font-size:1.3rem;font-weight:900;color:#111827">Active Alerts</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 16px 12px;font-size:0.82rem;color:#6b7280">Real-time risk events across monitored locations</div>', unsafe_allow_html=True)

    alert_data = [
        {
            "icon":"🚨","cat":"Severe","color":"#ef4444","loc":"Kota Bharu",
            "title":"Upstream river rising rapidly",
            "body":"Kelantan River gauge at +0.41m/h. Federal Highway route may submerge within 12 minutes. Evacuate low-lying areas immediately.",
            "time":"14:28 MYT · 2 mins ago"
        },
        {
            "icon":"🔶","cat":"High","color":"#f97316","loc":"Shah Alam",
            "title":"Basement flood risk — parking alert",
            "body":"Drainage systems at capacity. Underground car parks in Section 7 & 13 at imminent overflow risk. Move vehicles to Level 2+.",
            "time":"14:30 MYT · Just now"
        },
        {
            "icon":"🔶","cat":"High","color":"#f97316","loc":"Kuala Lumpur",
            "title":"Urban drainage overload",
            "body":"Heavy rainfall overwhelming storm drains near Masjid India and Chow Kit. Flash flood possible within 20 minutes.",
            "time":"14:25 MYT · 7 mins ago"
        },
        {
            "icon":"⚠️","cat":"Medium","color":"#f59e0b","loc":"Kota Kinabalu",
            "title":"Moderate risk — monitor conditions",
            "body":"Moderate rainfall. Basement flood risk building slowly. No immediate action required, but monitor updates.",
            "time":"14:15 MYT · 17 mins ago"
        },
        {
            "icon":"ℹ️","cat":"Low","color":"#22c55e","loc":"Kuching",
            "title":"Conditions stable",
            "body":"Light rainfall. All drainage systems operating normally. No flood risk expected in the next 3 hours.",
            "time":"14:00 MYT · 32 mins ago"
        },
    ]

    for a in alert_data:
        st.markdown(f"""
        <div class="alert-item" style="border-color:{a['color']}">
          <span class="alert-icon">{a['icon']}</span>
          <div style="flex:1">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:2px">
              <span class="alert-title">{a['title']}</span>
              <span style="background:{a['color']};color:#fff;padding:1px 8px;
                border-radius:99px;font-size:0.68rem;font-weight:700">{a['cat']}</span>
            </div>
            <div style="font-size:0.72rem;color:#9ca3af;margin-bottom:4px">📍 {a['loc']}</div>
            <div class="alert-body">{a['body']}</div>
            <div class="alert-time">{a['time']}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Crowd verification section
    st.markdown('<div class="section-label" style="margin-top:16px">👥 Crowd Reports — Ground Verification</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 16px 8px;font-size:0.78rem;color:#6b7280">1-tap reports from commuters on the ground help refine predictions for nearby drivers.</div>', unsafe_allow_html=True)

    all_reports = list(crowd.itertuples()) + [
        type('R', (), {"location": r["location"], "water_level_report": r["report"],
                       "reported_at": datetime.datetime.now().strftime("%H:%M MYT")})()
        for r in st.session_state.crowd_reports
    ]

    for r in crowd.itertuples():
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 16px;
             border-bottom:1px solid #f3f4f6">
          <span style="font-size:1.1rem">👤</span>
          <div>
            <div style="font-weight:600;font-size:0.82rem">{r.location}</div>
            <div style="font-size:0.75rem;color:#6b7280">{r.water_level_report}</div>
          </div>
          <div style="margin-left:auto;font-size:0.68rem;color:#9ca3af">
            {str(r.reported_at)[-5:]} MYT
          </div>
        </div>
        """, unsafe_allow_html=True)

    for r in st.session_state.crowd_reports:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 16px;
             border-bottom:1px solid #f3f4f6;background:#eff6ff">
          <span style="font-size:1.1rem">🙋</span>
          <div>
            <div style="font-weight:600;font-size:0.82rem">{r['location']}</div>
            <div style="font-size:0.75rem;color:#2563eb">{r['report']} · <i>Your report</i></div>
          </div>
          <div style="margin-left:auto;font-size:0.68rem;color:#9ca3af">Just now</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SAFETY (1-tap ground check + hyper-local guidance)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "safety":
    st.markdown('<div style="padding:16px 16px 4px;font-size:1.3rem;font-weight:900;color:#111827">Safety Hub</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 16px 12px;font-size:0.82rem;color:#6b7280">Report conditions and get hyper-local guidance</div>', unsafe_allow_html=True)

    # ── 1-Tap Ground Check ─────────────────────────────────────────────────────
    st.markdown('<div class="section-label">1-Tap Ground Check</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 16px 8px;font-size:0.78rem;color:#4b5563">Help nearby drivers by reporting current water levels at your location. One tap is all it takes.</div>', unsafe_allow_html=True)

    sel_loc = st.selectbox("Your location", locs["name"].tolist(), key="crowd_loc",
                            label_visibility="collapsed")

    water_options = [
        ("💧 Dry / No water", "Dry — no water on road"),
        ("👟 Ankle deep",     "Ankle deep"),
        ("🚗 At wheel height","At wheel height"),
        ("🦵 Above knee",     "Above knee"),
        ("🌊 Waist deep",     "Waist deep — DANGEROUS"),
    ]

    st.markdown('<div style="padding:0 12px">', unsafe_allow_html=True)
    for emoji_label, report_val in water_options:
        if st.button(emoji_label, key=f"crowd_{report_val}", use_container_width=True):
            st.session_state.crowd_reports.append({
                "location": sel_loc, "report": report_val,
                "time": datetime.datetime.now().strftime("%H:%M MYT")
            })
            # Danger auto-flag
            if "knee" in report_val.lower() or "waist" in report_val.lower():
                st.error(f"⚠️ Dangerous level reported at {sel_loc}. Triggering HIGH risk flag — alert sent to nearby users.")
            else:
                st.success(f"✅ Report submitted for {sel_loc}: '{report_val}'. Thank you for helping others stay safe!")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Hyper-local guidance panel ─────────────────────────────────────────────
    st.markdown('<div class="section-label" style="margin-top:16px">Hyper-Local Guidance</div>', unsafe_allow_html=True)

    for _, row in locs[locs["risk_cat"].isin(["High","Severe"])].iterrows():
        advice, action = hyper_local_advice(row)
        color = row["risk_color"]
        cat   = row["risk_cat"]
        bg    = CAT_BG[cat]
        st.markdown(f"""
        <div class="risk-card" style="border-left:4px solid {color}">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
            <span style="font-size:1.1rem">📍</span>
            <span style="font-weight:700">{row['name']}</span>
            <span style="background:{color};color:#fff;padding:2px 8px;
              border-radius:99px;font-size:0.72rem;font-weight:700;margin-left:auto">{cat}</span>
          </div>
          <div style="font-size:0.82rem;font-weight:600;color:#111827">⚠️ {advice}</div>
          <div style="font-size:0.78rem;color:#374151;margin-top:6px;
               background:{bg};border-radius:8px;padding:8px 10px">
            {action}
          </div>
          <div style="font-size:0.75rem;color:#6b7280;margin-top:8px">
            🌧 Rain: {row['rainfall_1h_mm']}mm/1h · 💧 Water: {row['water_level_m']}m
            · 📈 Rise: +{row['water_level_change_m_per_h']}m/h
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Safe Parking Suggestions ────────────────────────────────────────────────
    st.markdown('<div class="section-label">🅿️ Elevated Safe Parking Nearby</div>', unsafe_allow_html=True)
    safe_parks = [
        ("Shah Alam","SACC Mall Car Park — Level 3+","3.0721, 101.5134","~0.8km"),
        ("Kuala Lumpur","Berjaya Times Square — Level 5+","3.1425, 101.7103","~1.2km"),
        ("Kota Bharu","KB Mall Multi-Storey — Level 2+","6.1280, 102.2410","~0.5km"),
    ]
    for loc_n, park_n, coords, dist in safe_parks:
        st.markdown(f"""
        <div style="display:flex;gap:12px;align-items:flex-start;padding:10px 16px;
             border-bottom:1px solid #f3f4f6">
          <span style="font-size:1.3rem;margin-top:2px">🅿️</span>
          <div>
            <div style="font-weight:700;font-size:0.85rem">{park_n}</div>
            <div style="font-size:0.75rem;color:#6b7280">{loc_n} · {dist} · {coords}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "profile":
    st.markdown('<div style="padding:16px 16px 4px;font-size:1.3rem;font-weight:900;color:#111827">My Profile</div>', unsafe_allow_html=True)

    # Avatar
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;padding:24px 16px 16px">
      <div style="width:72px;height:72px;border-radius:50%;background:#dbeafe;
           display:flex;align-items:center;justify-content:center;font-size:2rem">👤</div>
      <div style="font-weight:700;font-size:1.05rem;margin-top:8px">Demo User</div>
      <div style="font-size:0.8rem;color:#6b7280">Shah Alam, Selangor</div>
    </div>
    """, unsafe_allow_html=True)

    # Emergency contact
    st.markdown('<div class="section-label">🆘 Emergency Contact (Dead-Man\'s Switch)</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 16px 8px;font-size:0.78rem;color:#4b5563">If you\'re in a danger zone and don\'t confirm safety within 3 minutes, your GPS coordinates will be sent to this contact via SMS.</div>', unsafe_allow_html=True)
    contact = st.text_input("Emergency contact phone number", value=st.session_state.emergency_contact,
                             placeholder="+60 12-345 6789", label_visibility="collapsed")
    if contact != st.session_state.emergency_contact:
        st.session_state.emergency_contact = contact
    if contact:
        st.success(f"✅ Emergency contact saved: {contact}")
    else:
        st.warning("⚠️ No emergency contact set. Add one to activate the Dead-Man's Switch.")

    # Notification preferences
    st.markdown('<div class="section-label" style="margin-top:12px">🔔 Notification Preferences</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("Severe alerts", value=True)
        st.checkbox("High alerts", value=True)
    with col2:
        st.checkbox("Medium alerts", value=False)
        st.checkbox("Crowd reports nearby", value=True)

    # Model performance
    st.markdown('<div class="section-label" style="margin-top:12px">🤖 Demo Model Performance</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 16px 6px;font-size:0.72rem;color:#9ca3af">Synthetic data only — not validated for real Malaysian flood events.</div>', unsafe_allow_html=True)
    met_df = pd.DataFrame({"Metric": list(model_metrics.keys()), "Score": list(model_metrics.values())})
    st.dataframe(met_df, hide_index=True, use_container_width=True)

    # Data sources
    st.markdown('<div class="section-label" style="margin-top:12px">📡 Data Sources (Production)</div>', unsafe_allow_html=True)
    sources = [
        ("🌊","JPS Public Infobanjir","Real-time river gauge & rainfall data","publicinfobanjir.water.gov.my"),
        ("🌤","MET Malaysia","Official weather forecasts","met.gov.my"),
        ("🛰","JUPEM","Elevation & terrain data","jupem.gov.my"),
        ("📱","Crowd Reports","Community water-level verification","In-app"),
    ]
    for icon, name, desc, url in sources:
        st.markdown(f"""
        <div style="display:flex;gap:12px;align-items:center;padding:10px 16px;
             border-bottom:1px solid #f3f4f6">
          <span style="font-size:1.3rem">{icon}</span>
          <div>
            <div style="font-weight:600;font-size:0.82rem">{name}</div>
            <div style="font-size:0.72rem;color:#6b7280">{desc} · {url}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:20px 16px;text-align:center;font-size:0.72rem;color:#9ca3af">
      FloodGuard AI v1.0 · Demo Mode<br>
      ⚠️ For demonstration purposes only.<br>
      Always follow official JPS & NADMA emergency instructions.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BOTTOM NAVIGATION BAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
nav_cols = st.columns(4)
nav_items = [
    ("map",     "🗺️", "Home/Map"),
    ("alerts",  "🔔", "Alerts"),
    ("safety",  "🛡️", "Safety"),
    ("profile", "👤", "Profile"),
]
for i, (page_key, icon, label) in enumerate(nav_items):
    with nav_cols[i]:
        active = st.session_state.page == page_key
        if st.button(
            f"{icon}\n{label}",
            key=f"nav_{page_key}",
            use_container_width=True,
            type="primary" if active else "secondary"
        ):
            st.session_state.page = page_key
            st.rerun()
