# -*- coding: utf-8 -*-
"""
FloodAlert — Figma-accurate Streamlit implementation
Screens: Home (map), Location Details, AI Safety Tips, Community Help Nearby
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
import streamlit.components.v1 as components

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FloodAlert",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ROOT       = Path(__file__).parent
DATA_DIR   = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
TRAIN_PATH = DATA_DIR / "synthetic_flood_training_data.csv"
LOC_PATH   = DATA_DIR / "sample_locations.csv"
CROWD_PATH = DATA_DIR / "crowd_reports.csv"

# ── Synthetic data generation ─────────────────────────────────────────────────
def generate_data():
    rng = np.random.default_rng(42)
    n   = 3000
    rain1  = rng.exponential(15, n).clip(0, 250)
    rain3  = (rain1 * 2.5 + rng.exponential(10, n)).clip(0, 500)
    rain24 = (rain3 * 3.5 + rng.exponential(20, n)).clip(0, 1000)
    water  = rng.uniform(0.5, 6.0, n)
    wchange = rng.normal(0.05, 0.2, n).clip(-2, 3)
    drain  = rng.uniform(0.1, 1.0, n)
    elev   = rng.exponential(12, n).clip(1, 500)
    imperv = rng.integers(20, 100, n)
    near_r = rng.integers(0, 2, n)
    score  = (
        0.30*(rain1/60) + 0.20*(rain3/150) + 0.10*(rain24/300)
        + 0.15*(water/6) + 0.10*(wchange.clip(0,3)/3)
        + 0.08*(1-drain) + 0.04*(imperv/100) + 0.03*near_r
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
        ("Shah Alam",     "Petaling",   "Selangor", 3.0738,101.5183, 38, 85,190,3.1,0.22,0.38, 7,82,1,"Basement Parking Flooding"),
        ("Kota Bharu",    "Kota Bharu", "Kelantan", 6.1254,102.2381, 55,130,280,4.5,0.41,0.30, 5,65,1,"Blocked Highway Route"),
        ("Kuantan",       "Kuantan",    "Pahang",   3.8126,103.3256, 20, 45,100,1.8,0.08,0.60,12,55,1,"Blocked Highway Route"),
        ("Kuala Lumpur",  "KL City",    "W.P. KL",  3.1390,101.6869, 42, 95,200,2.9,0.18,0.35, 9,88,1,"Basement Parking Flooding"),
        ("Johor Bahru",   "JB City",    "Johor",    1.4927,103.7414, 15, 35, 80,1.2,0.03,0.65,15,70,0,"Blocked Highway Route"),
        ("Kota Kinabalu", "KK City",    "Sabah",    5.9804,116.0735, 28, 62,140,2.2,0.12,0.52, 8,60,1,"Basement Parking Flooding"),
        ("Kuching",       "Kuching",    "Sarawak",  1.5535,110.3593, 12, 28, 65,1.0,0.02,0.72,20,45,0,"Blocked Highway Route"),
    ], columns=[
        "name","district","state","lat","lon",
        "rainfall_1h_mm","rainfall_3h_mm","rainfall_24h_mm",
        "water_level_m","water_level_change_m_per_h",
        "drainage_capacity_index","elevation_m","impervious_surface_pct",
        "near_river","threat_type",
    ]).to_csv(LOC_PATH, index=False)

    pd.DataFrame({
        "location": ["Shah Alam","Kota Bharu","Kuala Lumpur","Kota Bharu","Shah Alam"],
        "water_level_report": ["At wheel height","Above knee","Ankle deep","Waist deep","At wheel height"],
        "reported_at": ["2026-10-10 14:05","2026-10-10 13:58","2026-10-10 14:10","2026-10-10 14:15","2026-10-10 14:28"],
        "lat": [3.0720,6.1230,3.1380,6.1260,3.0745],
        "lon": [101.5160,102.2360,101.6855,102.2390,101.5190],
    }).to_csv(CROWD_PATH, index=False)

if not TRAIN_PATH.exists():
    generate_data()

# ── ML model ──────────────────────────────────────────────────────────────────
FEATURES = [
    "rainfall_1h_mm","rainfall_3h_mm","rainfall_24h_mm",
    "water_level_m","water_level_change_m_per_h",
    "drainage_capacity_index","elevation_m","impervious_surface_pct","near_river",
]

@st.cache_resource
def train_model():
    df = pd.read_csv(TRAIN_PATH)
    X, y = df[FEATURES], df["flood_within_next_3h"]
    Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)
    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("clf", RandomForestClassifier(n_estimators=250, class_weight="balanced",
                                       random_state=42, min_samples_leaf=4, n_jobs=-1)),
    ])
    pipe.fit(Xtr, ytr)
    pred = pipe.predict(Xte)
    prob = pipe.predict_proba(Xte)[:,1]
    return pipe, {
        "Accuracy": round(accuracy_score(yte,pred),3),
        "F1":       round(f1_score(yte,pred,zero_division=0),3),
        "ROC AUC":  round(roc_auc_score(yte,prob),3),
    }

model, model_metrics = train_model()

def predict_risk(row_dict):
    row  = pd.DataFrame([{f: row_dict[f] for f in FEATURES}])
    prob = float(model.predict_proba(row)[0,1])
    pct  = round(prob * 100)
    if   pct < 20: cat,color,minutes = "Low",   "#23875b",None
    elif pct < 45: cat,color,minutes = "Medium","#b77810",30
    elif pct < 70: cat,color,minutes = "High",  "#d64045",20
    else:          cat,color,minutes = "Severe","#c62828",12
    return pct, cat, color, minutes

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_locations():
    df = pd.read_csv(LOC_PATH)
    rows = []
    for _, r in df.iterrows():
        rd = r.to_dict()
        pct,cat,color,mins = predict_risk(rd)
        rd.update({"risk_pct":pct,"risk_cat":cat,"risk_color":color,"minutes":mins})
        rows.append(rd)
    return pd.DataFrame(rows)

@st.cache_data
def load_crowd():
    return pd.read_csv(CROWD_PATH)

locs  = load_locations()
crowd = load_crowd()

# ── Session state ─────────────────────────────────────────────────────────────
def _ss(k, v):
    if k not in st.session_state: st.session_state[k] = v

_ss("page",              "home")
_ss("selected_loc",      "Shah Alam")
_ss("community_filter",  "All")
_ss("emergency_cleared", {})
_ss("safety_confirmed",  {})
_ss("ping_sent",         {})
_ss("crowd_reports",     [])
_ss("emergency_contact", "")
_ss("help_requests",     [
    {"cat":"Transport","title":"Transport assistance needed",
     "status":"Pending verification","area":"Serdang area","approx":True,"time":"09:30"},
    {"cat":"Supplies","title":"Essential supplies requested",
     "status":"Pending verification","area":"Seri Kembangan area","approx":True,"time":"10:00"},
])

# ── Design tokens ─────────────────────────────────────────────────────────────
CAT_COLORS = {"Low":"#23875b","Medium":"#b77810","High":"#d64045","Severe":"#c62828"}
CAT_BG     = {"Low":"#e8f5ee","Medium":"#fef3e0","High":"#fdeaea","Severe":"#fde8e8"}

def hyper_local_advice(loc_row):
    name, threat, mins = loc_row["name"], loc_row["threat_type"], loc_row["minutes"]
    if threat == "Basement Parking Flooding":
        if loc_row["risk_cat"] in ("High","Severe"):
            return (f"Basement drainage in {name} overwhelmed — move vehicle to Level 2+ immediately.",
                    "🅿️ Elevated Safe Parking: Nearby elevated multi-storey car parks on higher floors.")
        return (f"Rainfall accumulating; basement flood risk building in {name}.",
                "🅿️ Monitor basement water sensors. Consider moving vehicle to upper floors.")
    else:
        if loc_row["risk_cat"] in ("High","Severe"):
            return (f"Upstream river rising rapidly; {name} main route will submerge in ~{mins} mins.",
                    "🔀 Alternative Route: Take elevated expressway or inland road. Avoid low-lying underpasses.")
        return (f"Surface runoff increasing near {name} highway corridor.",
                "🔀 Stay on elevated roads. Monitor traffic alerts before departing.")

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

*,*::before,*::after { box-sizing:border-box; font-family:'Inter',system-ui,sans-serif; }

/* ── Hide Streamlit chrome ── */
[data-testid="stSidebar"],
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu, footer, hr { display:none !important; }

/* ── Mobile canvas ── */
[data-testid="stAppViewContainer"] {
    background: #e8ecf0 !important;
    min-height: 100dvh !important;
}
[data-testid="stAppViewContainer"] > .main {
    padding: 0 !important;
    background: #e8ecf0 !important;
}
[data-testid="stAppViewContainer"] > .main > .block-container {
    width: 100% !important;
    max-width: 390px !important;
    min-height: 100dvh !important;
    padding: 0 0 180px 0 !important;
    margin: 0 auto !important;
    background: #f4f7fa !important;
    position: relative !important;
}
@media (min-width: 420px) {
    [data-testid="stAppViewContainer"] > .main > .block-container {
        box-shadow: 0 0 0 1px #d1d9e0, 0 8px 48px rgba(21,45,75,0.14);
    }
}
.element-container, .stMarkdown { padding: 0 !important; }

/* ── Sticky white header (home) ── */
.fa-header {
    background:#fff; border-bottom:1px solid #e4eaf0;
    position:sticky; top:0; z-index:200; width:100%;
}
.fa-status-bar {
    display:flex; justify-content:space-between; align-items:center;
    height:32px; padding:0 24px;
}
.fa-time { font-weight:600; font-size:14px; color:#152d4b; }
.fa-status-icons { display:flex; gap:5px; align-items:center; }
.fa-brand-row {
    display:flex; align-items:center; gap:10px;
    height:58px; padding:0 20px;
}
.fa-logo {
    background:#152d4b; width:36px; height:36px; border-radius:11px;
    display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.fa-app-name { font-weight:700; font-size:25px; color:#152d4b; line-height:1; }
.fa-country  { margin-left:auto; font-weight:600; font-size:10px; color:#68788b; letter-spacing:.8px; text-transform:uppercase; }
.fa-search-wrap { padding:0 20px 12px; }
.fa-search-field {
    display:flex; align-items:center; gap:11px;
    background:#fff; border:1px solid #e4eaf0; border-radius:14px;
    height:52px; padding:0 15px;
    box-shadow:0 3px 12px rgba(21,45,75,.05);
}
.fa-search-ph { flex:1; font-size:14px; color:#68788b; }

/* ── Sub-page header (back arrow style) ── */
.fa-subheader {
    background:#fff; border-bottom:1px solid #e4eaf0;
    position:sticky; top:0; z-index:200; width:100%;
    padding:0;
}
.fa-subheader-status {
    display:flex; justify-content:space-between; align-items:center;
    height:32px; padding:0 24px;
}
.fa-subheader-title-row {
    display:flex; align-items:center; gap:12px;
    height:46px; padding:0 20px;
}
.fa-back-btn {
    width:30px; height:30px; border-radius:8px;
    display:flex; align-items:center; justify-content:center;
    color:#152d4b; flex-shrink:0; cursor:pointer;
}
.fa-subheader-title { font-weight:700; font-size:22px; color:#152d4b; line-height:1.1; }
.fa-subheader-loc-row {
    display:flex; align-items:center; gap:6px;
    padding:4px 20px 10px;
}
.fa-subheader-loc  { font-weight:600; font-size:13px; color:#152d4b; }
.fa-subheader-sub  { font-size:12px; color:#68788b; margin-top:2px; padding:0 20px 10px; }

/* ── Page content wrapper ── */
.fa-page { padding:0 20px; }

/* ── Map container ── */
.fa-map-wrap {
    border-radius:20px; border:1px solid #e4eaf0; overflow:hidden;
    background:#f1f3ef; box-shadow:0 3px 12px rgba(21,45,75,.05); margin:8px 0 4px;
}

/* ── Risk legend ── */
.fa-risk-legend { display:flex; align-items:center; gap:8px; padding:6px 0 4px; }
.fa-legend-label { font-size:11px; font-weight:600; color:#68788b; flex-shrink:0; }
.fa-legend-item  { display:flex; align-items:center; gap:4px; }
.fa-dot { width:8px; height:8px; border-radius:50%; display:inline-block; flex-shrink:0; }
.fa-legend-arrow { font-size:11px; color:#68788b; }

/* ── Cards ── */
.fa-card {
    background:#fff; border-radius:16px; padding:16px;
    margin:8px 0; box-shadow:0 2px 8px rgba(21,45,75,.06);
}
.fa-card-bordered {
    background:#fff; border-radius:16px; padding:16px;
    margin:8px 0; border:1px solid #e4eaf0;
    box-shadow:0 2px 8px rgba(21,45,75,.04);
}
.risk-card {
    background:#fff; border-radius:16px; padding:16px;
    margin:6px 0; border-left:4px solid;
    box-shadow:0 2px 8px rgba(21,45,75,.06);
}
.risk-card-title { font-weight:700; font-size:1.05rem; color:#152d4b; }
.risk-card-sub   { font-size:.78rem; color:#68788b; margin-top:2px; }
.risk-badge {
    color:#fff; padding:3px 10px; border-radius:99px;
    font-size:.75rem; font-weight:700; white-space:nowrap;
}

/* ── Progress bar ── */
.prob-bar-track { background:#e4eaf0; border-radius:99px; height:6px; overflow:hidden; }
.prob-bar-fill  { height:6px; border-radius:99px; }

/* ── Risk level progress bar (Figma style: LOW / MEDIUM / HIGH segments) ── */
.risk-seg-bar { display:flex; gap:4px; margin:8px 0 4px; }
.risk-seg {
    flex:1; height:24px; border-radius:6px; display:flex;
    align-items:center; justify-content:center;
    font-size:10px; font-weight:700; color:#68788b;
    border:1.5px solid #e4eaf0; background:#f4f7fa;
}
.risk-seg.active-low    { background:#e8f5ee; color:#23875b; border-color:#23875b; }
.risk-seg.active-medium { background:#fef3e0; color:#b77810; border-color:#b77810; }
.risk-seg.active-high   { background:#fdeaea; color:#d64045; border-color:#d64045; }
.risk-seg.active-severe { background:#fde8e8; color:#c62828; border-color:#c62828; }

/* ── Filter chips ── */
.fa-chip-row { display:flex; gap:6px; padding:4px 0 10px; overflow-x:auto; scrollbar-width:none; }
.fa-chip-row::-webkit-scrollbar { display:none; }
.fa-chip {
    border-radius:99px; padding:5px 14px; font-size:12px; font-weight:600;
    border:1.5px solid #e4eaf0; background:#fff; color:#152d4b;
    white-space:nowrap; cursor:pointer; flex-shrink:0;
}
.fa-chip.active { background:#152d4b; color:#fff; border-color:#152d4b; }

/* ── Action list rows (Location Details "What You Should Do") ── */
.fa-action-row {
    display:flex; align-items:center; gap:12px;
    padding:14px 16px; background:#fff; border-radius:12px;
    margin:6px 0; cursor:pointer; border:1px solid #e4eaf0;
}
.fa-action-icon { font-size:18px; flex-shrink:0; }
.fa-action-label { flex:1; font-weight:600; font-size:14px; color:#152d4b; }
.fa-action-arrow { font-size:16px; color:#68788b; }

/* ── Safety tip rows ── */
.fa-tip-card {
    display:flex; align-items:flex-start; gap:12px;
    padding:14px 16px; background:#fff; border-radius:12px;
    margin:6px 0; border:1px solid #e4eaf0;
}
.fa-tip-icon { font-size:20px; flex-shrink:0; margin-top:1px; }
.fa-tip-title { font-weight:700; font-size:14px; color:#152d4b; line-height:1.3; }
.fa-tip-body  { font-size:12px; color:#68788b; margin-top:3px; line-height:1.4; }

/* ── Help request card ── */
.fa-request-card {
    background:#fff; border-radius:14px; padding:16px;
    margin:8px 0; border:1px solid #e4eaf0;
    box-shadow:0 1px 4px rgba(21,45,75,.05);
}
.fa-request-cat   { font-size:11px; font-weight:700; color:#68788b; text-transform:uppercase; letter-spacing:.6px; margin-bottom:4px; }
.fa-request-title { font-size:16px; font-weight:800; color:#152d4b; line-height:1.25; margin-bottom:6px; }
.fa-request-badge {
    display:inline-block; padding:2px 10px; border-radius:99px;
    font-size:11px; font-weight:600; background:#f4f7fa; color:#68788b;
    border:1px solid #e4eaf0; margin-bottom:8px;
}
.fa-request-meta { font-size:12px; color:#68788b; margin-bottom:2px; }
.fa-request-footer { display:flex; align-items:center; justify-content:space-between; margin-top:10px; }
.fa-view-details { font-size:13px; font-weight:700; color:#152d4b; display:flex; align-items:center; gap:4px; }
.fa-report-btn   { font-size:12px; font-weight:600; color:#68788b; display:flex; align-items:center; gap:4px; }

/* ── Info note ── */
.fa-info-note {
    background:#e8f5ee; border-radius:12px; padding:12px 14px;
    display:flex; align-items:center; gap:10px; margin:8px 0;
    font-size:13px; color:#152d4b;
}

/* ── Bottom SOS + nav (fixed) ── */
.fa-footer {
    position:fixed; bottom:0; left:50%; transform:translateX(-50%);
    width:390px; z-index:300; background:#f4f7fa;
}
.fa-sos-wrap { padding:6px 20px 0; }
.fa-sos-btn {
    display:flex; align-items:center; justify-content:center; gap:10px;
    width:100%; height:50px; border-radius:14px;
    background:#c62828; color:#fff; border:none;
    font-weight:700; font-size:17px; cursor:pointer;
    box-shadow:0 3px 12px rgba(198,40,40,.25);
}
.fa-sos-sub {
    text-align:center; font-size:10px; color:#68788b;
    padding:4px 0 5px; line-height:16px;
}
.fa-nav {
    background:#fff; border-top:1px solid #e4eaf0;
    display:flex; padding:5px 20px 0;
    box-shadow:0 -2px 10px rgba(21,45,75,.06);
}
.fa-nav-item { flex:1; display:flex; flex-direction:column; align-items:center; gap:3px; padding-bottom:4px; }
.fa-nav-pill { width:52px; height:28px; border-radius:100px; display:flex; align-items:center; justify-content:center; font-size:19px; }
.fa-nav-pill.active { background:#f4f7fa; }
.fa-nav-label { font-size:11px; font-weight:500; color:#68788b; }
.fa-nav-label.active { font-weight:700; color:#152d4b; }
.fa-home-ind { width:134px; height:5px; background:#152d4b; border-radius:100px; margin:4px auto 0; }

/* ── Offer Help button ── */
.fa-offer-btn {
    display:flex; align-items:center; justify-content:center; gap:8px;
    width:100%; height:50px; border-radius:14px;
    background:#152d4b; color:#fff; border:none;
    font-weight:700; font-size:16px; cursor:pointer;
    box-shadow:0 3px 12px rgba(21,45,75,.2);
    margin-bottom:8px;
}

/* ── Weather card ── */
.fa-weather-card {
    background:#fff; border-radius:16px; padding:16px;
    margin:8px 0; border:1px solid #e4eaf0;
    box-shadow:0 2px 8px rgba(21,45,75,.05);
}
.fa-weather-title { font-weight:700; font-size:15px; color:#152d4b; margin-bottom:10px; }
.fa-weather-main  { display:flex; align-items:center; gap:12px; margin-bottom:10px; }
.fa-weather-temp  { font-weight:800; font-size:36px; color:#152d4b; line-height:1; }
.fa-weather-cond  { font-size:13px; color:#68788b; margin-top:2px; }
.fa-weather-grid  {
    display:grid; grid-template-columns:1fr 1fr; gap:6px 0;
    border-top:1px solid #e4eaf0; padding-top:10px; margin-top:6px;
}
.fa-weather-row  { display:flex; justify-content:space-between; font-size:12px; color:#68788b; padding:3px 0; }
.fa-weather-val  { font-weight:700; color:#152d4b; }

/* ── Emergency overlay ── */
.emergency-overlay {
    background:linear-gradient(135deg,#7f1d1d,#c62828);
    border-radius:16px; margin:8px 0; padding:20px;
    color:#fff; text-align:center; animation:fa-pulse 1.4s ease-in-out infinite;
}
@keyframes fa-pulse { 0%,100%{opacity:1} 50%{opacity:.88} }
.emergency-title { font-size:1.3rem; font-weight:900; letter-spacing:1px; }
.emergency-sub   { font-size:.85rem; opacity:.92; margin:6px 0 14px; }

/* Safety status */
.safety-ok   { background:#e8f5ee; border:1.5px solid #86efac; border-radius:12px; padding:14px; margin:6px 0; }
.safety-warn { background:#fdeaea; border:1.5px solid #fca5a5; border-radius:12px; padding:14px; margin:6px 0; }

/* Section label */
.section-label {
    font-size:11px; font-weight:700; text-transform:uppercase;
    letter-spacing:1.2px; color:#68788b; padding:14px 0 6px;
}
.page-title { font-size:1.3rem; font-weight:800; color:#152d4b; padding:16px 0 2px; }
.page-sub   { font-size:.82rem; color:#68788b; padding:0 0 10px; }

/* Streamlit widget overrides */
div[data-testid="stHorizontalBlock"] button { border-radius:10px !important; font-weight:600 !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers: shared SVG icons ─────────────────────────────────────────────────
ICO_SIGNAL = """<svg width="18" height="12" viewBox="0 0 18 12" fill="#152d4b">
  <rect x="0" y="6" width="3" height="6" rx="1"/>
  <rect x="4" y="4" width="3" height="8" rx="1"/>
  <rect x="8" y="2" width="3" height="10" rx="1"/>
  <rect x="12" y="0" width="3" height="12" rx="1"/>
</svg>"""
ICO_WIFI = """<svg width="16" height="12" viewBox="0 0 16 12" fill="#152d4b">
  <path d="M8 3C5.2 3 2.7 4.2 1 6.2L0 5C2 2.7 4.8 1 8 1s6 1.7 8 4.2l-1 1.2C13.3 4.2 10.8 3 8 3z"/>
  <path d="M8 6c-1.7 0-3.2.7-4.3 1.8L2.7 6.6C4.1 5.2 5.9 4 8 4s3.9 1.2 5.3 2.6l-1 1.2C11.2 6.7 9.7 6 8 6z"/>
  <circle cx="8" cy="10" r="2"/>
</svg>"""
ICO_BATT = """<svg width="25" height="12" viewBox="0 0 25 12" fill="none">
  <rect x=".5" y=".5" width="21" height="11" rx="3.5" stroke="#152d4b" stroke-opacity=".35"/>
  <rect x="2" y="2" width="17" height="8" rx="2" fill="#152d4b"/>
  <path d="M23 4v4a2 2 0 000-4z" fill="#152d4b" fill-opacity=".4"/>
</svg>"""
ICO_SEARCH = """<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
  <circle cx="8.5" cy="8.5" r="5.5" stroke="#68788b" stroke-width="1.5"/>
  <path d="M13 13l3.5 3.5" stroke="#68788b" stroke-width="1.5" stroke-linecap="round"/>
</svg>"""
ICO_PIN = """<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
  <path d="M10 2C7.24 2 5 4.24 5 7c0 3.75 5 11 5 11s5-7.25 5-11c0-2.76-2.24-5-5-5zm0 6.5a1.5 1.5 0 110-3 1.5 1.5 0 010 3z" fill="#68788b"/>
</svg>"""
ICO_SHIELD = """<svg width="21" height="21" viewBox="0 0 24 24" fill="none">
  <path d="M12 2L4 6v6c0 5.25 3.5 10.14 8 11.35C16.5 22.14 20 17.25 20 12V6l-8-4z" stroke="#152d4b" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M9 12l2 2 4-4" stroke="#152d4b" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""
ICO_SHIELD_WHITE = """<svg width="21" height="21" viewBox="0 0 24 24" fill="none">
  <path d="M12 2L4 6v6c0 5.25 3.5 10.14 8 11.35C16.5 22.14 20 17.25 20 12V6l-8-4z" stroke="white" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M9 12l2 2 4-4" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""
ICO_HOUSE = """<svg width="21" height="21" viewBox="0 0 24 24" fill="none">
  <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H5a1 1 0 01-1-1V9.5z" stroke="#152d4b" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M9 21V12h6v9" stroke="#152d4b" stroke-width="1.8" stroke-linejoin="round"/>
</svg>"""
ICO_HOUSE_GREY = ICO_HOUSE.replace('#152d4b','#68788b')
ICO_MAP = """<svg width="21" height="21" viewBox="0 0 24 24" fill="none">
  <polygon points="1,6 1,22 8,18 16,22 23,18 23,2 16,6 8,2" stroke="#68788b" stroke-width="1.8" stroke-linejoin="round"/>
  <line x1="8" y1="2" x2="8" y2="18" stroke="#68788b" stroke-width="1.8"/>
  <line x1="16" y1="6" x2="16" y2="22" stroke="#68788b" stroke-width="1.8"/>
</svg>"""
ICO_MAP_NAVY = ICO_MAP.replace('#68788b','#152d4b')
ICO_PHONE = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none">
  <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.81a19.79 19.79 0 01-3.07-8.63A2 2 0 012 0h3a2 2 0 012 1.72c.13.96.36 1.9.7 2.81a2 2 0 01-.45 2.11L6.09 7.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0122 14.92v2z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""
ICO_BACK = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
  <path d="M19 12H5M12 19l-7-7 7-7" stroke="#152d4b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""
ICO_LOCPIN = """<svg width="16" height="16" viewBox="0 0 24 24" fill="none">
  <path d="M12 2C8.69 2 6 4.69 6 8c0 4.5 6 12 6 12s6-7.5 6-12c0-3.31-2.69-6-6-6zm0 8.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z" fill="#68788b"/>
</svg>"""
ICO_RAIN = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
  <path d="M20 16.58A5 5 0 0018 7h-1.26A8 8 0 104 15.25" stroke="#68788b" stroke-width="1.8" stroke-linecap="round"/>
  <line x1="8" y1="19" x2="8" y2="21" stroke="#68788b" stroke-width="1.8" stroke-linecap="round"/>
  <line x1="12" y1="17" x2="12" y2="21" stroke="#68788b" stroke-width="1.8" stroke-linecap="round"/>
  <line x1="16" y1="19" x2="16" y2="21" stroke="#68788b" stroke-width="1.8" stroke-linecap="round"/>
</svg>"""

def status_bar_html(time_str=None):
    t = time_str or datetime.datetime.now().strftime("%H:%M")
    return f"""<div class="fa-status-bar">
      <span class="fa-time">{t}</span>
      <div class="fa-status-icons">{ICO_SIGNAL}{ICO_WIFI}{ICO_BATT}</div>
    </div>"""

def subheader_html(title, loc="Serdang, Selangor", subtitle="", back_page="home", time_str=None):
    t = time_str or datetime.datetime.now().strftime("%H:%M")
    return f"""<div class="fa-subheader">
      <div class="fa-subheader-status">
        <span class="fa-time">{t}</span>
        <div class="fa-status-icons">{ICO_SIGNAL}{ICO_WIFI}{ICO_BATT}</div>
      </div>
      <div class="fa-subheader-title-row">
        <div class="fa-back-btn" id="back-btn">{ICO_BACK}</div>
        <span class="fa-subheader-title">{title}</span>
      </div>
      <div class="fa-subheader-loc-row">
        {ICO_LOCPIN}
        <span class="fa-subheader-loc">{loc}</span>
      </div>
      {f'<div class="fa-subheader-sub">{subtitle}</div>' if subtitle else ''}
    </div>"""

def footer_html(page, sos_sub="Follow official flood alerts · Call 999 in real emergencies"):
    nav_items = [("home","Home",ICO_HOUSE,ICO_HOUSE_GREY),
                 ("location","Map",ICO_MAP_NAVY,ICO_MAP),
                 ("safety","Safety",ICO_SHIELD,ICO_SHIELD_WHITE)]
    items_html = ""
    for pk, lbl, ico_active, ico_inactive in nav_items:
        active = page == pk
        pill = f'<div class="fa-nav-pill{"  active" if active else ""}">{ico_active if active else ico_inactive}</div>'
        lab  = f'<span class="fa-nav-label{"  active" if active else ""}">{lbl}</span>'
        items_html += f'<div class="fa-nav-item">{pill}{lab}</div>'
    return f"""<div class="fa-footer">
      <div class="fa-sos-wrap">
        <div class="fa-sos-btn">{ICO_PHONE}<span>SOS Emergency</span></div>
        <div class="fa-sos-sub">{sos_sub}</div>
      </div>
      <div class="fa-nav">{items_html}</div>
      <div class="fa-home-ind"></div>
    </div>"""

# ── Computed globals ──────────────────────────────────────────────────────────
severe_locs = locs[locs["risk_cat"]=="Severe"]

# ── Viewport meta injection ───────────────────────────────────────────────────
components.html("""<script>
var m=document.querySelector('meta[name="viewport"]');
if(!m){m=document.createElement('meta');m.name='viewport';document.head.appendChild(m);}
m.content='width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no';
</script>""", height=0)

page = st.session_state.page

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME (map overview)
# ══════════════════════════════════════════════════════════════════════════════
if page == "home":

    # Header
    now = datetime.datetime.now().strftime("%H:%M")
    st.markdown(f"""<div class="fa-header">
      {status_bar_html(now)}
      <div class="fa-brand-row">
        <div class="fa-logo">{ICO_SHIELD_WHITE}</div>
        <span class="fa-app-name">FloodAlert</span>
        <span class="fa-country">Malaysia</span>
      </div>
      <div class="fa-search-wrap">
        <div class="fa-search-field">
          {ICO_SEARCH}
          <span class="fa-search-ph">Search your location</span>
          {ICO_PIN}
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Emergency override
    for _, srow in severe_locs.iterrows():
        loc_name = srow["name"]
        if not st.session_state.emergency_cleared.get(loc_name, False):
            adv, act = hyper_local_advice(srow)
            st.markdown(f"""<div class="fa-page"><div class="emergency-overlay">
              <div class="emergency-title">🚨 SEVERE FLOOD WARNING</div>
              <div class="emergency-sub">{loc_name} · Imminent threat in ~{srow['minutes']} minutes</div>
              <div style="font-size:.85rem;background:rgba(255,255,255,.15);border-radius:10px;padding:10px 14px;text-align:left;margin-bottom:10px">
                ⚠️ {adv}<br><br>{act}
              </div>
            </div></div>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Vehicle Moved", key=f"moved_{loc_name}", use_container_width=True):
                    st.session_state.emergency_cleared[loc_name] = True; st.rerun()
            with c2:
                if st.button("🔀 Route Changed", key=f"route_{loc_name}", use_container_width=True):
                    st.session_state.emergency_cleared[loc_name] = True; st.rerun()

    st.markdown('<div class="fa-page">', unsafe_allow_html=True)

    # Location heading
    sel_row = locs[locs["name"]==st.session_state.selected_loc].iloc[0]
    st.markdown(f"""<div style="padding:10px 0 4px">
      <div style="font-weight:700;font-size:17px;color:#152d4b">{sel_row['name']}, {sel_row['state']}</div>
      <div style="font-size:11px;color:#68788b;margin-top:2px">{sel_row['state']} · Malaysia</div>
    </div>""", unsafe_allow_html=True)

    # Leaflet map — zoomed in on selected location
    map_markers, crowd_markers = [], []
    for _, r in locs.iterrows():
        map_markers.append({"name":r["name"],"lat":r["lat"],"lon":r["lon"],
                             "cat":r["risk_cat"],"pct":int(r["risk_pct"]),"color":r["risk_color"],"threat":r["threat_type"]})
    for _, r in crowd.iterrows():
        crowd_markers.append({"loc":r["location"],"report":r["water_level_report"],"lat":float(r["lat"]),"lon":float(r["lon"])})

    sel_lat, sel_lon = float(sel_row["lat"]), float(sel_row["lon"])
    mjson, cjson = json.dumps(map_markers), json.dumps(crowd_markers)

    map_html = f"""<!DOCTYPE html><html><head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
      body{{margin:0;padding:0;background:#f1f3ef;font-family:Inter,sans-serif;}}
      #map{{height:436px;width:100%;}}
      .leaflet-control-zoom{{border:none!important;box-shadow:0 2px 8px rgba(21,45,75,.12)!important;}}
      .leaflet-control-zoom a{{background:#fff!important;color:#152d4b!important;border-radius:8px!important;border-bottom:1px solid #e4eaf0!important;}}
      .recenter{{position:absolute;top:13px;right:13px;z-index:500;width:36px;height:36px;
        background:#fff;border-radius:10px;display:flex;align-items:center;justify-content:center;
        box-shadow:0 3px 12px rgba(21,45,75,.1);cursor:pointer;border:none;}}
      .osm-bar{{position:absolute;bottom:8px;left:50%;transform:translateX(-50%);
        background:rgba(255,255,255,.82);border-radius:6px;padding:2px 10px;
        font-size:9px;color:#68788b;white-space:nowrap;pointer-events:none;z-index:400;}}
    </style></head><body>
    <div style="position:relative">
      <div id="map"></div>
      <div class="osm-bar">© OpenStreetMap contributors</div>
      <button class="recenter" onclick="map.setView([{sel_lat},{sel_lon}],13)">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="3.5" stroke="#152d4b" stroke-width="1.8"/>
          <path d="M12 2v3M12 19v3M2 12h3M19 12h3" stroke="#152d4b" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
    <script>
    var markers={mjson}, crowd={cjson};
    var map=L.map('map',{{zoomControl:false}}).setView([{sel_lat},{sel_lon}],13);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{attribution:'',maxZoom:18}}).addTo(map);
    L.control.zoom({{position:'topright'}}).addTo(map);

    // Selected position marker
    L.circleMarker([{sel_lat},{sel_lon}],{{
      radius:8,fillColor:'rgba(21,45,75,.15)',fillOpacity:1,color:'rgba(21,45,75,.4)',weight:1.5
    }}).addTo(map);

    function riskMarker(color,cat,name){{
      var h='<div style="display:flex;flex-direction:column;align-items:center;gap:3px;pointer-events:none">'
        +'<div style="background:#fff;border-radius:8px;padding:5px 9px;box-shadow:0 3px 12px rgba(21,45,75,.12);white-space:nowrap;text-align:center">'
        +'<div style="font-size:11px;font-weight:600;color:#152d4b;font-family:Inter,sans-serif">'+name+'</div>'
        +'<div style="font-size:9px;font-weight:700;color:'+color+';font-family:Inter,sans-serif">'+cat.toUpperCase()+'</div>'
        +'</div>'
        +'<div style="width:32px;height:32px;border-radius:50%;background:'+color+';opacity:.35;border:3px solid '+color+'"></div>'
        +'<div style="width:14px;height:14px;border-radius:50%;background:'+color+';border:2.5px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.2);margin-top:-23px"></div>'
        +'</div>';
      return L.divIcon({{html:h,iconSize:[120,70],iconAnchor:[60,70],popupAnchor:[0,-70],className:''}});
    }}
    markers.forEach(function(m){{
      L.marker([m.lat,m.lon],{{icon:riskMarker(m.color,m.cat,m.name)}}).addTo(map)
       .bindPopup('<b style="color:#152d4b">'+m.name+'</b><br><span style="color:'+m.color+';font-weight:700">'+m.cat+'</span> · '+m.pct+'%<br><small style="color:#68788b">'+m.threat+'</small>');
    }});
    crowd.forEach(function(c){{
      L.circleMarker([c.lat,c.lon],{{radius:7,fillColor:'#152d4b',color:'#fff',weight:2.5,fillOpacity:.85}}).addTo(map)
       .bindPopup('<b>👥 '+c.loc+'</b><br><small>'+c.report+'</small>');
    }});
    </script></body></html>"""

    st.markdown('<div class="fa-map-wrap">', unsafe_allow_html=True)
    components.html(map_html, height=436, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

    # Risk legend (Figma: only LOW / MEDIUM / HIGH, no SEVERE)
    st.markdown("""<div class="fa-risk-legend">
      <span class="fa-legend-label">Risk level</span>
      <div class="fa-legend-item"><span class="fa-dot" style="background:#23875b"></span>
        <span style="color:#23875b;font-weight:700;font-size:10px">LOW</span></div>
      <span class="fa-legend-arrow">→</span>
      <div class="fa-legend-item"><span class="fa-dot" style="background:#b77810"></span>
        <span style="color:#b77810;font-weight:700;font-size:10px">MEDIUM</span></div>
      <span class="fa-legend-arrow">→</span>
      <div class="fa-legend-item"><span class="fa-dot" style="background:#d64045"></span>
        <span style="color:#d64045;font-weight:700;font-size:10px">HIGH</span></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # end fa-page

    # Footer
    st.markdown(footer_html("home"), unsafe_allow_html=True)

    # Nav buttons (invisible — just for routing)
    nc = st.columns(3)
    with nc[0]:
        if st.button("Home", key="nav_home", use_container_width=True, type="primary"):
            st.session_state.page="home"; st.rerun()
    with nc[1]:
        if st.button("Map",  key="nav_map",  use_container_width=True):
            st.session_state.page="location"; st.rerun()
    with nc[2]:
        if st.button("Safety",key="nav_safety",use_container_width=True):
            st.session_state.page="safety"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: LOCATION DETAILS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "location":
    sel_row = locs[locs["name"]==st.session_state.selected_loc].iloc[0]
    cat, color, pct = sel_row["risk_cat"], sel_row["risk_color"], int(sel_row["risk_pct"])
    bg = CAT_BG[cat]

    st.markdown(subheader_html(
        "Location Details",
        loc=f"{sel_row['name']}, {sel_row['state']}",
        subtitle="Local weather and flood risk",
        back_page="home",
    ), unsafe_allow_html=True)

    st.markdown('<div class="fa-page">', unsafe_allow_html=True)

    # Weather card
    rain_intensity = "Moderate" if sel_row["rainfall_1h_mm"] > 20 else "Light"
    temp_approx    = round(25 + (1 - sel_row["water_level_m"]/6)*6, 0)
    st.markdown(f"""<div class="fa-weather-card">
      <div class="fa-weather-title">Weather Today</div>
      <div class="fa-weather-main">
        <div style="font-size:40px;line-height:1">{'⛅' if sel_row['rainfall_1h_mm'] > 10 else '☀️'}</div>
        <div>
          <div style="font-size:12px;color:#68788b">{'Partly Cloudy' if sel_row['rainfall_1h_mm'] > 10 else 'Mostly Sunny'}</div>
          <div class="fa-weather-temp">{int(temp_approx)} °C</div>
        </div>
      </div>
      <div class="fa-weather-grid">
        <div class="fa-weather-row"><span>Sunshine</span><span class="fa-weather-val">{rain_intensity}</span></div>
        <div class="fa-weather-row"><span>Measured rainfall intensity</span><span class="fa-weather-val">{sel_row['rainfall_1h_mm']} mm/h</span></div>
        <div class="fa-weather-row"><span>Forecast next 2 hours</span><span class="fa-weather-val">{sel_row['rainfall_3h_mm']:.0f} mm</span></div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Flood risk card
    seg_low    = "active-low"    if cat=="Low"    else ""
    seg_medium = "active-medium" if cat=="Medium" else ""
    seg_high   = "active-high"   if cat in ("High","Severe") else ""
    st.markdown(f"""<div class="fa-card" style="background:{bg};border:1px solid {color}30">
      <div style="font-weight:700;font-size:14px;color:#152d4b;margin-bottom:10px">Current Flood Risk</div>
      <span style="background:{color};color:#fff;padding:4px 14px;border-radius:99px;
            font-size:13px;font-weight:700;display:inline-flex;align-items:center;gap:6px">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="9" stroke="white" stroke-width="2"/>
          <path d="M12 8v4M12 16h.01" stroke="white" stroke-width="2" stroke-linecap="round"/>
        </svg>
        {cat.upper()} RISK
      </span>
      <div class="risk-seg-bar" style="margin-top:10px">
        <div class="risk-seg {seg_low}">✓ LOW</div>
        <div class="risk-seg {seg_medium}">MEDIUM</div>
        <div class="risk-seg {seg_high}">HIGH</div>
      </div>
      <div style="font-size:12px;color:#152d4b;margin-top:8px">
        {cat} estimated risk. Stay alert to changing rainfall.
      </div>
      <div style="font-size:11px;color:#68788b;margin-top:2px">Follow official flood alerts.</div>
    </div>""", unsafe_allow_html=True)

    # What You Should Do
    st.markdown('<div class="section-label">What You Should Do</div>', unsafe_allow_html=True)
    st.markdown("""<div style="font-size:12px;color:#68788b;padding-bottom:8px">
      Monitor official alerts. Explore safety advice and nearby safe places.</div>""", unsafe_allow_html=True)

    for action_label, action_page, ico in [
        ("AI Safety Tips",       "safety",    "🛡️"),
        ("Evacuation Places",    "evacuation","📍"),
        ("Community Help Nearby","community", "👥"),
    ]:
        st.markdown(f"""<div class="fa-action-row">
          <span class="fa-action-icon">{ico}</span>
          <span class="fa-action-label">{action_label}</span>
          <span class="fa-action-arrow">→</span>
        </div>""", unsafe_allow_html=True)
        if st.button(f"Go to {action_label}", key=f"act_{action_page}", use_container_width=True):
            st.session_state.page = action_page; st.rerun()

    # Dead-Man's Switch for High/Severe
    if cat in ("High","Severe"):
        loc_name  = sel_row["name"]
        confirmed = st.session_state.safety_confirmed.get(loc_name, False)
        ping_sent = st.session_state.ping_sent.get(loc_name, False)
        if not confirmed:
            if not ping_sent:
                st.markdown(f"""<div class="safety-warn">
                  <div style="font-weight:700;color:#991b1b;font-size:.88rem">🔴 Safety Check Required</div>
                  <div style="font-size:.78rem;color:#7f1d1d;margin-top:4px">
                    You appear to be near a <b>{cat.lower()}</b> zone. Confirm your safety within 3 minutes.
                  </div></div>""", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ I'm Safe", key=f"safe_{loc_name}2", use_container_width=True):
                        st.session_state.safety_confirmed[loc_name]=True; st.rerun()
                with c2:
                    if st.button("📲 Send Ping", key=f"ping_{loc_name}2", use_container_width=True):
                        st.session_state.ping_sent[loc_name]=True; st.rerun()
            else:
                st.markdown(f"""<div class="safety-warn">
                  <div style="font-weight:700;color:#991b1b">📲 Location Ping Sent</div>
                  <div style="font-size:.78rem;color:#7f1d1d;margin-top:4px">
                    Your coordinates near <b>{loc_name}</b> have been sent to your emergency contact.
                  </div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="safety-ok">
              <div style="font-weight:700;color:#166534;font-size:.85rem">✅ Safety confirmed for {loc_name}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Two-button footer (Request Help + SOS)
    st.markdown(f"""<div class="fa-footer">
      <div class="fa-sos-wrap" style="display:flex;gap:8px">
        <button class="fa-offer-btn" style="background:#152d4b;height:50px;font-size:15px;border-radius:14px;flex:1;display:flex;align-items:center;justify-content:center;gap:8px;color:#fff;border:none;font-weight:700">
          {ICO_SHIELD_WHITE} Request Help
        </button>
        <button class="fa-sos-btn" style="flex:1.3">
          {ICO_PHONE} <span>SOS Emergency<br><span style="font-size:11px;font-weight:500;opacity:.85">Immediate danger</span></span>
        </button>
      </div>
      <div class="fa-sos-sub">Nothing is sent automatically.</div>
      <div class="fa-nav">
        <div class="fa-nav-item"><div class="fa-nav-pill">{ICO_HOUSE_GREY}</div><span class="fa-nav-label">Home</span></div>
        <div class="fa-nav-item"><div class="fa-nav-pill active">{ICO_MAP_NAVY}</div><span class="fa-nav-label active">Map</span></div>
        <div class="fa-nav-item"><div class="fa-nav-pill">{ICO_SHIELD}</div><span class="fa-nav-label">Safety</span></div>
      </div>
      <div class="fa-home-ind"></div>
    </div>""", unsafe_allow_html=True)

    nc = st.columns(3)
    with nc[0]:
        if st.button("← Home", key="nav_home2", use_container_width=True):
            st.session_state.page="home"; st.rerun()
    with nc[1]:
        if st.button("Map", key="nav_map2", use_container_width=True, type="primary"):
            st.session_state.page="location"; st.rerun()
    with nc[2]:
        if st.button("Safety", key="nav_safety2", use_container_width=True):
            st.session_state.page="safety"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AI SAFETY TIPS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "safety":
    sel_row = locs[locs["name"]==st.session_state.selected_loc].iloc[0]
    cat, color, pct = sel_row["risk_cat"], sel_row["risk_color"], int(sel_row["risk_pct"])
    bg = CAT_BG[cat]

    st.markdown(subheader_html(
        "AI Safety Tips",
        loc=f"{sel_row['name']}, {sel_row['state']}",
        subtitle=f"Estimated {cat.upper()} risk · Follow official instructions.",
    ), unsafe_allow_html=True)

    st.markdown('<div class="fa-page">', unsafe_allow_html=True)

    # Current flood risk card
    st.markdown(f"""<div class="fa-card-bordered">
      <div style="font-weight:700;font-size:14px;color:#152d4b;margin-bottom:10px">Current flood risk</div>
      <span style="background:{color};color:#fff;padding:5px 16px;border-radius:99px;font-size:14px;font-weight:700">
        {cat.upper()} RISK
      </span>
      <div style="float:right;font-size:12px;color:#68788b;margin-top:4px">Estimated</div>
      <div style="clear:both;margin-top:10px;font-size:12px;color:#68788b">AI guidance is not an official warning.</div>
    </div>""", unsafe_allow_html=True)

    # Safety tips
    st.markdown('<div class="section-label">Practical safety tips</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#68788b;padding-bottom:6px">Practical advice for changing conditions.</div>', unsafe_allow_html=True)

    tips = [
        ("🌧️", "Monitor rainfall and official forecasts", "Check MET Malaysia updates before travel."),
        ("📍", "Avoid entering floodwater and check local exposure", "Ask local authorities before travel."),
        ("🎒", "Prepare essential supplies if flood-prone", "Keep documents, medication, water and a charged phone ready."),
    ]
    for ico, title, body in tips:
        st.markdown(f"""<div class="fa-tip-card">
          <span class="fa-tip-icon">{ico}</span>
          <div>
            <div class="fa-tip-title">{title}</div>
            <div class="fa-tip-body">{body}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Why these tips
    adv, act = hyper_local_advice(sel_row)
    st.markdown(f"""<div class="fa-tip-card" style="background:#f4f7fa">
      <span class="fa-tip-icon">⚠️</span>
      <div>
        <div class="fa-tip-title">Why these tips?</div>
        <div class="fa-tip-body">Rainfall can change quickly, local exposure varies, and essentials help if conditions change.</div>
        <div class="fa-tip-body" style="margin-top:6px;color:#152d4b">{adv}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="font-size:11px;color:#68788b;padding:8px 0 4px">AI guidance is not an official warning.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer with "Immediate danger" SOS sub
    st.markdown(f"""<div class="fa-footer">
      <div class="fa-sos-wrap">
        <div class="fa-sos-btn">{ICO_PHONE}
          <div style="display:flex;flex-direction:column;align-items:flex-start">
            <span>SOS Emergency</span>
            <span style="font-size:11px;font-weight:500;opacity:.85">Immediate danger</span>
          </div>
        </div>
        <div class="fa-sos-sub">Follow official instructions.</div>
      </div>
      <div class="fa-nav">
        <div class="fa-nav-item"><div class="fa-nav-pill">{ICO_HOUSE_GREY}</div><span class="fa-nav-label">Home</span></div>
        <div class="fa-nav-item"><div class="fa-nav-pill">{ICO_MAP}</div><span class="fa-nav-label">Map</span></div>
        <div class="fa-nav-item"><div class="fa-nav-pill active">{ICO_SHIELD}</div><span class="fa-nav-label active">Safety</span></div>
      </div>
      <div class="fa-home-ind"></div>
    </div>""", unsafe_allow_html=True)

    nc = st.columns(3)
    with nc[0]:
        if st.button("Home",   key="nav_home3",   use_container_width=True):
            st.session_state.page="home"; st.rerun()
    with nc[1]:
        if st.button("Map",    key="nav_map3",    use_container_width=True):
            st.session_state.page="location"; st.rerun()
    with nc[2]:
        if st.button("Safety", key="nav_safety3", use_container_width=True, type="primary"):
            st.session_state.page="safety"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COMMUNITY HELP NEARBY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "community":
    sel_row = locs[locs["name"]==st.session_state.selected_loc].iloc[0]

    st.markdown(subheader_html(
        "Community Help",
        loc=f"{sel_row['name']}, {sel_row['state']}",
        subtitle="Nearby community requests",
    ), unsafe_allow_html=True)

    st.markdown('<div class="fa-page">', unsafe_allow_html=True)

    # Filter chips
    st.markdown('<div class="section-label">Nearby requests</div>', unsafe_allow_html=True)
    cats_filter = ["All","Transport","Supplies","Other"]
    active_cf   = st.session_state.community_filter
    chips_html  = '<div class="fa-chip-row">'
    for c in cats_filter:
        cls = "fa-chip active" if c==active_cf else "fa-chip"
        chips_html += f'<span class="{cls}">{c}</span>'
    chips_html += '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)

    cf_cols = st.columns(len(cats_filter))
    for i, c in enumerate(cats_filter):
        with cf_cols[i]:
            if st.button(c, key=f"cf_{c}", use_container_width=True,
                         type="primary" if c==active_cf else "secondary"):
                st.session_state.community_filter=c; st.rerun()

    # Request cards
    requests = st.session_state.help_requests
    if active_cf != "All":
        requests = [r for r in requests if r["cat"]==active_cf]

    for req in requests:
        approx_note = " · Approximate location" if req.get("approx") else ""
        st.markdown(f"""<div class="fa-request-card">
          <div class="fa-request-cat">{req['cat']}</div>
          <div class="fa-request-title">{req['title']}</div>
          <div><span class="fa-request-badge">{req['status']}</span></div>
          <div class="fa-request-meta">{req['area']}{approx_note}</div>
          <div class="fa-request-meta">{req['time']}</div>
          <div class="fa-request-footer">
            <span class="fa-view-details">View Details →</span>
            <span class="fa-report-btn">⚑ Report</span>
          </div>
        </div>""", unsafe_allow_html=True)

    # Info note
    st.markdown("""<div class="fa-info-note">
      <span style="font-size:18px">ℹ️</span>
      <span>Verify requests before offering help.</span>
    </div>""", unsafe_allow_html=True)

    # Submit request form
    st.markdown('<div class="section-label">Submit a Help Request</div>', unsafe_allow_html=True)
    new_cat   = st.selectbox("Category", ["Transport","Supplies","Other"], key="new_req_cat", label_visibility="collapsed")
    new_title = st.text_input("Title", placeholder="Describe what you need...", key="new_req_title", label_visibility="collapsed")
    new_area  = st.text_input("Area", placeholder="Your area (e.g. Serdang area)", key="new_req_area", label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    # Offer Help + SOS footer
    st.markdown(f"""<div class="fa-footer">
      <div class="fa-sos-wrap">
        <button class="fa-offer-btn">{'+'}  Offer Help</button>
        <div class="fa-sos-btn">{ICO_PHONE}<span>SOS Emergency</span></div>
        <div class="fa-sos-sub">Does not contact emergency services</div>
      </div>
      <div class="fa-nav">
        <div class="fa-nav-item"><div class="fa-nav-pill">{ICO_HOUSE_GREY}</div><span class="fa-nav-label">Home</span></div>
        <div class="fa-nav-item"><div class="fa-nav-pill">{ICO_MAP}</div><span class="fa-nav-label">Map</span></div>
        <div class="fa-nav-item"><div class="fa-nav-pill active">{ICO_SHIELD}</div><span class="fa-nav-label active">Safety</span></div>
      </div>
      <div class="fa-home-ind"></div>
    </div>""", unsafe_allow_html=True)

    submit_col, back_col = st.columns(2)
    with submit_col:
        if st.button("Submit Request", key="submit_req", use_container_width=True, type="primary"):
            if new_title and new_area:
                st.session_state.help_requests.append({
                    "cat":new_cat,"title":new_title,"status":"Pending verification",
                    "area":new_area,"approx":False,
                    "time":datetime.datetime.now().strftime("%H:%M"),
                })
                st.success("✅ Request submitted."); st.rerun()
            else:
                st.warning("Please fill in title and area.")
    with back_col:
        if st.button("← Back", key="back_comm", use_container_width=True):
            st.session_state.page="location"; st.rerun()

    nc = st.columns(3)
    with nc[0]:
        if st.button("Home",   key="nav_home4",   use_container_width=True):
            st.session_state.page="home"; st.rerun()
    with nc[1]:
        if st.button("Map",    key="nav_map4",    use_container_width=True):
            st.session_state.page="location"; st.rerun()
    with nc[2]:
        if st.button("Safety", key="nav_safety4", use_container_width=True):
            st.session_state.page="safety"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EVACUATION PLACES (bonus screen)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "evacuation":
    sel_row = locs[locs["name"]==st.session_state.selected_loc].iloc[0]

    st.markdown(subheader_html(
        "Safe Places",
        loc=f"{sel_row['name']}, {sel_row['state']}",
        subtitle="Nearby evacuation & safe locations",
    ), unsafe_allow_html=True)

    st.markdown('<div class="fa-page">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Nearby safe locations</div>', unsafe_allow_html=True)

    safe_places = [
        ("🏫","Sekolah Kebangsaan Serdang","1.2 km","Open · 200 capacity"),
        ("🏥","Hospital Putrajaya","3.4 km","Open · Emergency only"),
        ("🅿️","SACC Mall Car Park Level 3+","0.8 km","Dry · Elevated parking"),
        ("🏛️","Dewan Orang Ramai Serdang","0.6 km","Open · 150 capacity"),
    ]
    for ico, name, dist, note in safe_places:
        st.markdown(f"""<div class="fa-action-row">
          <span class="fa-action-icon">{ico}</span>
          <div style="flex:1">
            <div style="font-weight:700;font-size:14px;color:#152d4b">{name}</div>
            <div style="font-size:12px;color:#68788b;margin-top:2px">{dist} · {note}</div>
          </div>
          <span class="fa-action-arrow">→</span>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(footer_html("safety"), unsafe_allow_html=True)

    nc = st.columns(3)
    with nc[0]:
        if st.button("Home",   key="nav_home5",   use_container_width=True):
            st.session_state.page="home"; st.rerun()
    with nc[1]:
        if st.button("Map",    key="nav_map5",    use_container_width=True):
            st.session_state.page="location"; st.rerun()
    with nc[2]:
        if st.button("Safety", key="nav_safety5", use_container_width=True):
            st.session_state.page="safety"; st.rerun()
