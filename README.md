# FloodGuard AI — Flash Flood Predictor starter

## Important
This is a **software prototype**. `data/synthetic_flood_training_data.csv` is artificially generated and is **not real Malaysian flood data**. The model's probabilities and evaluation scores are not validated for real-world use. Do not use this prototype to make evacuation or emergency decisions.

## Run locally (Windows)
1. Install Python 3.10+.
2. Extract this folder and open a terminal inside it.
3. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt:
   ```bat
   .venv\Scripts\activate.bat
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## Dataset columns
- `rainfall_1h_mm`, `rainfall_3h_mm`, `rainfall_24h_mm`: synthetic rainfall amounts.
- `water_level_m`, `water_level_change_m_per_h`: synthetic water level and rate of change.
- `drainage_capacity_index`: synthetic index from 0 (poor) to 1 (good).
- `elevation_m`, `impervious_surface_pct`, `near_river`: synthetic location/context features.
- `flood_within_next_3h`: synthetic binary target (1 means generated example flood event).
- `flood_mechanism`: synthetic illustrative mechanism label.

## Real-data plan
A credible Malaysian model needs aligned historical observations and flood-event labels:
- Explore JPS Public Infobanjir: https://publicinfobanjir.water.gov.my/
- Explore MET Malaysia: https://www.met.gov.my/
- Add official flood incident / inundation labels with timestamps and geolocation.
- Check data access terms and timestamp/station metadata.
- Split data by time and preferably by station/region to reduce leakage.
- Evaluate precision, recall, PR-AUC, calibration, false-alarm rate, and missed-event rate. Test on held-out periods and regions.
- Only issue operational warnings after expert review and validation.

## Suggested next features
1. Real geospatial map with verified station coordinates.
2. Historical rainfall/water-level time-series charts.
3. Calibrated forecast probability and uncertainty.
4. Road-corridor risk and route alternatives from verified road/flood closure data.
5. SOS flow connected to an actual backend and confirmed alert delivery.
