import torch
import pandas as pd
import numpy as np
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_PATH = BASE_DIR / "model" / "nbeats_aqi.pth"

# --------------------------------------------------
# Load model (FULL MODEL, NOT state_dict)
# --------------------------------------------------
device = "cpu"
model = torch.load(MODEL_PATH, map_location=device, weights_only=False)
model.eval()

# --------------------------------------------------
# Load city CSV
# --------------------------------------------------
def load_city_csv(city: str) -> pd.DataFrame:
    file_path = DATA_DIR / f"{city}.csv"
    if not file_path.exists():
        raise ValueError(f"City data not found: {city}")

    df = pd.read_csv(file_path)
    return df.sort_values("date")


# --------------------------------------------------
# Get AQI time series for model
# --------------------------------------------------
def get_city_series(city: str, lookback: int = 30):
    df = load_city_csv(city)

    if len(df) < lookback:
        raise ValueError(f"Not enough data for city: {city}")

    series = df["aqi"].values[-lookback:]
    return torch.tensor(series, dtype=torch.float32).unsqueeze(0)


# --------------------------------------------------
# Predict by City
# --------------------------------------------------
def predict_city(city: str):
    x = get_city_series(city)

    with torch.no_grad():
        backcast, forecast = model(x)

    next_day_aqi = float(forecast.squeeze().item())

    df = load_city_csv(city)
    history = df.tail(7).to_dict(orient="records")

    return history, round(next_day_aqi, 2)


# --------------------------------------------------
# Find nearest city using lat/lon
# --------------------------------------------------
def get_nearest_city(lat: float, lon: float) -> float:
    min_dist = float("inf")
    nearest_city = None

    for csv_file in DATA_DIR.glob("*.csv"):
        df = pd.read_csv(csv_file)
        row = df.iloc[0]

        dist = np.sqrt(
            (row["latitude"] - lat) ** 2 +
            (row["longitude"] - lon) ** 2
        )

        if dist < min_dist:
            min_dist = dist
            nearest_city = row["city"]

    if nearest_city is None:
        raise ValueError("No city data available")

    return nearest_city


# --------------------------------------------------
# Predict by GPS
# --------------------------------------------------
def predict_latlon(lat: float, lon: float):
    city = get_nearest_city(lat, lon)
    history, prediction = predict_city(city)
    
    return {
        "nearest_city": city,
        "prediction": prediction,
        "history": history
    }
