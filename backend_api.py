"""
FloodGuard AI — FastAPI backend
Endpoints:
  GET  /            health check
  GET  /health      detailed health
  GET  /metrics     model evaluation metrics
  POST /predict     flood risk prediction
  POST /report      save a crowd water-level report to data/crowd_reports.csv
  GET  /reports     return recent crowd reports as JSON
"""

import csv
import threading
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).parent
TRAIN_PATH = ROOT / "data" / "synthetic_flood_training_data.csv"
CROWD_PATH = ROOT / "data" / "crowd_reports.csv"

# ── CSV helpers ────────────────────────────────────────────────────────────────
CROWD_COLUMNS = ["location", "water_level_report", "reported_at", "lat", "lon"]

# Thread lock — prevents two concurrent requests corrupting the CSV
_csv_lock = threading.Lock()


def _ensure_crowd_csv() -> None:
    """Create crowd_reports.csv with the correct header if it does not exist."""
    if not CROWD_PATH.exists():
        CROWD_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CROWD_PATH, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=CROWD_COLUMNS).writeheader()


_ensure_crowd_csv()

# ── ML model ───────────────────────────────────────────────────────────────────
FEATURES = [
    "rainfall_1h_mm",
    "rainfall_3h_mm",
    "rainfall_24h_mm",
    "water_level_m",
    "water_level_change_m_per_h",
    "drainage_capacity_index",
    "elevation_m",
    "impervious_surface_pct",
    "near_river",
]

if not TRAIN_PATH.exists():
    raise FileNotFoundError(
        f"Training data not found: {TRAIN_PATH}\n"
        "Run the Streamlit app once to generate it."
    )

_df = pd.read_csv(TRAIN_PATH)
_X  = _df[FEATURES]
_y  = _df["flood_within_next_3h"]

_X_train, _X_test, _y_train, _y_test = train_test_split(
    _X, _y, test_size=0.2, random_state=42, stratify=_y
)

_model = Pipeline([
    ("imp", SimpleImputer(strategy="median")),
    ("clf", RandomForestClassifier(
        n_estimators=250, class_weight="balanced",
        random_state=42, min_samples_leaf=4, n_jobs=-1,
    )),
])
_model.fit(_X_train, _y_train)

_pred = _model.predict(_X_test)
_prob = _model.predict_proba(_X_test)[:, 1]

_metrics = {
    "accuracy": round(float(accuracy_score(_y_test, _pred)), 3),
    "f1":       round(float(f1_score(_y_test, _pred, zero_division=0)), 3),
    "roc_auc":  round(float(roc_auc_score(_y_test, _prob)), 3),
}

# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(title="FloodGuard AI API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # restrict to your frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models ────────────────────────────────────────────────────────────

class FloodInput(BaseModel):
    rainfall_1h_mm:            float = Field(ge=0,   le=250)
    rainfall_3h_mm:            float = Field(ge=0,   le=500)
    rainfall_24h_mm:           float = Field(ge=0,   le=1000)
    water_level_m:             float = Field(ge=0,   le=20)
    water_level_change_m_per_h:float = Field(ge=-2,  le=3)
    drainage_capacity_index:   float = Field(ge=0,   le=1)
    elevation_m:               float = Field(ge=0,   le=1000)
    impervious_surface_pct:    float = Field(ge=0,   le=100)
    near_river:                int   = Field(ge=0,   le=1)


# Water-level labels accepted from the frontend
WATER_LEVEL_OPTIONS: dict[str, str] = {
    "dry":   "Dry — no water on road",
    "ankle": "Ankle deep",
    "wheel": "At wheel height",
    "knee":  "Above knee",
    "waist": "Waist deep — DANGEROUS",
}


class CrowdReportIn(BaseModel):
    """Payload sent from FloodModal when a user reports water conditions."""
    location:        str   = Field(min_length=1, max_length=120)
    water_level_key: str   = Field(pattern=r"^(dry|ankle|wheel|knee|waist)$")
    lat:             float = Field(ge=-90,  le=90)
    lon:             float = Field(ge=-180, le=180)


class CrowdReportOut(BaseModel):
    """Response returned to the frontend after a successful submission."""
    ok:                  bool
    location:            str
    water_level_report:  str
    reported_at:         str
    lat:                 float
    lon:                 float
    danger_flag:         bool   # True when level is knee-deep or worse


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", summary="Root health check")
def root() -> dict:
    return {"message": "FloodGuard AI API is running"}


@app.get("/health", summary="Detailed health")
def health() -> dict:
    return {"status": "ok", "model_loaded": True}


@app.get("/metrics", summary="Model evaluation metrics")
def get_metrics() -> dict:
    return _metrics


@app.post("/predict", summary="Flood risk prediction")
def predict(data: FloodInput) -> dict:
    row         = pd.DataFrame([data.model_dump()])
    probability = float(_model.predict_proba(row)[0, 1])
    percentage  = round(probability * 100)

    if percentage < 20:
        category, color, minutes = "Low",    "#23875b", None
    elif percentage < 45:
        category, color, minutes = "Medium", "#b77810", 30
    elif percentage < 70:
        category, color, minutes = "High",   "#d64045", 20
    else:
        category, color, minutes = "Severe", "#c62828", 12

    return {
        "risk_pct":           percentage,
        "risk_cat":           category,
        "risk_color":         color,
        "minutes":            minutes,
        "model_probability":  round(probability, 4),
        "prediction_horizon": "next 3 hours",
    }


@app.post("/report", response_model=CrowdReportOut, summary="Submit a crowd water-level report")
def submit_report(data: CrowdReportIn) -> CrowdReportOut:
    """
    Accepts a user's water-level observation from FloodModal and appends it
    as a new row to data/crowd_reports.csv.

    CSV columns: location, water_level_report, reported_at, lat, lon
    """
    water_level_report = WATER_LEVEL_OPTIONS[data.water_level_key]
    reported_at        = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    danger_flag        = data.water_level_key in ("knee", "waist")

    row = {
        "location":           data.location,
        "water_level_report": water_level_report,
        "reported_at":        reported_at,
        "lat":                round(data.lat, 6),
        "lon":                round(data.lon, 6),
    }

    with _csv_lock:
        _ensure_crowd_csv()
        with open(CROWD_PATH, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=CROWD_COLUMNS).writerow(row)

    return CrowdReportOut(ok=True, danger_flag=danger_flag, **row)


@app.get("/reports", summary="Fetch recent crowd reports")
def get_reports(limit: int = 50) -> list[dict]:
    """
    Returns the most-recent `limit` rows from crowd_reports.csv as JSON,
    newest first. Returns an empty list if the file has no data yet.
    """
    _ensure_crowd_csv()
    try:
        df = pd.read_csv(CROWD_PATH, dtype=str).fillna("")
    except pd.errors.EmptyDataError:
        return []

    return df.tail(limit).iloc[::-1].to_dict(orient="records")
