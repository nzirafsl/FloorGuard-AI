/**
 * api.js — typed client for the FloodGuard AI FastAPI backend
 * Base URL: http://localhost:8000  (set VITE_API_URL in .env to override)
 */

const BASE = import.meta.env.VITE_API_URL ?? "https://floodguard-ai-backend-o5mv.onrender.com";

// ── Generic fetch wrapper ─────────────────────────────────────────────────────
async function request(method, path, body) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);

  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${method} ${path} → ${res.status}: ${text}`);
  }
  return res.json();
}

// ── Health ────────────────────────────────────────────────────────────────────
/** @returns {{ status: string, model_loaded: boolean }} */
export const getHealth = () => request("GET", "/health");

// ── Model metrics ─────────────────────────────────────────────────────────────
/** @returns {{ accuracy: number, f1: number, roc_auc: number }} */
export const getMetrics = () => request("GET", "/metrics");

// ── Flood risk prediction ─────────────────────────────────────────────────────
/**
 * @param {{
 *   rainfall_1h_mm: number,
 *   rainfall_3h_mm: number,
 *   rainfall_24h_mm: number,
 *   water_level_m: number,
 *   water_level_change_m_per_h: number,
 *   drainage_capacity_index: number,
 *   elevation_m: number,
 *   impervious_surface_pct: number,
 *   near_river: number,
 * }} input
 * @returns {{
 *   risk_pct: number,
 *   risk_cat: "Low"|"Medium"|"High"|"Severe",
 *   risk_color: string,
 *   minutes: number|null,
 *   model_probability: number,
 *   prediction_horizon: string,
 * }}
 */
export const predict = (input) => request("POST", "/predict", input);

// ── Crowd reports ─────────────────────────────────────────────────────────────
/**
 * @param {{
 *   location: string,
 *   water_level_key: "dry"|"ankle"|"wheel"|"knee"|"waist",
 *   lat: number,
 *   lon: number,
 * }} report
 */
export const submitReport = (report) => request("POST", "/report", report);

/** @param {number} limit */
export const getReports = (limit = 50) => request("GET", `/reports?limit=${limit}`);

// ── Convenience: predict with Serdang defaults ────────────────────────────────
/**
 * Runs a prediction with the current sensor snapshot.
 * Override any field by passing a partial object.
 */
export function predictSerdang(overrides = {}) {
  return predict({
    rainfall_1h_mm:             42,
    rainfall_3h_mm:             98,
    rainfall_24h_mm:            210,
    water_level_m:              3.1,
    water_level_change_m_per_h: 0.4,
    drainage_capacity_index:    0.35,
    elevation_m:                8,
    impervious_surface_pct:     62,
    near_river:                 1,
    ...overrides,
  });
}
