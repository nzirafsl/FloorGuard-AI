
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).parent
TRAIN_PATH = ROOT / "data" / "synthetic_flood_training_data.csv"

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

app = FastAPI(title="FloodGuard AI API")

# Allows your Expo web frontend to call this API during development.
# Restrict origins to your deployed frontend when publishing.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class FloodInput(BaseModel):
    rainfall_1h_mm: float = Field(ge=0, le=250)
    rainfall_3h_mm: float = Field(ge=0, le=500)
    rainfall_24h_mm: float = Field(ge=0, le=1000)
    water_level_m: float = Field(ge=0, le=20)
    water_level_change_m_per_h: float = Field(ge=-2, le=3)
    drainage_capacity_index: float = Field(ge=0, le=1)
    elevation_m: float = Field(ge=0, le=1000)
    impervious_surface_pct: float = Field(ge=0, le=100)
    near_river: int = Field(ge=0, le=1)


if not TRAIN_PATH.exists():
    raise FileNotFoundError(
        f"Training data not found: {TRAIN_PATH}\n"
        "Run your existing Streamlit app once to generate it."
    )

df = pd.read_csv(TRAIN_PATH)
X = df[FEATURES]
y = df["flood_within_next_3h"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

model = Pipeline([
    ("imp", SimpleImputer(strategy="median")),
    ("clf", RandomForestClassifier(
        n_estimators=250,
        class_weight="balanced",
        random_state=42,
        min_samples_leaf=4,
        n_jobs=-1,
    )),
])

model.fit(X_train, y_train)

pred = model.predict(X_test)
prob = model.predict_proba(X_test)[:, 1]

metrics = {
    "accuracy": round(float(accuracy_score(y_test, pred)), 3),
    "f1": round(float(f1_score(y_test, pred, zero_division=0)), 3),
    "roc_auc": round(float(roc_auc_score(y_test, prob)), 3),
}


@app.get("/")
def home():
    return {"message": "FloodGuard AI API is running"}


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True}


@app.get("/metrics")
def get_metrics():
    return metrics


@app.post("/predict")
def predict(data: FloodInput):
    row = pd.DataFrame([data.model_dump()])
    probability = float(model.predict_proba(row)[0, 1])
    percentage = round(probability * 100)

    if percentage < 20:
        category, color, minutes = "Low", "#22c55e", None
    elif percentage < 45:
        category, color, minutes = "Medium", "#f59e0b", 30
    elif percentage < 70:
        category, color, minutes = "High", "#f97316", 20
    else:
        category, color, minutes = "Severe", "#ef4444", 12

    return {
        "risk_pct": percentage,
        "risk_cat": category,
        "risk_color": color,
        "minutes": minutes,
        "model_probability": round(probability, 4),
        "prediction_horizon": "next 3 hours",
    }
