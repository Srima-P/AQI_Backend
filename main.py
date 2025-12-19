from fastapi import FastAPI, Query, HTTPException

from app.model import load_model
from app.predict import predict_city, predict_latlon
from app.plot import plot_wave
from app.waqi import fetch_online_aqi, fetch_online_aqi_latlon

app = FastAPI(title="AQI Prediction API")
model = load_model()

# ===============================
# CITY-BASED PREDICTION
# ===============================
@app.get("/predict/city")
def predict_by_city(city: str = Query(..., description="City name")):
    current = fetch_online_aqi(city)

    dates, actual, predicted, next_day = predict_city(model, city)
    plot_path = plot_wave(city, dates, actual, predicted, next_day)

    return format_response(city, current, next_day, plot_path)


# ===============================
# GPS-BASED PREDICTION
# ===============================
@app.get("/predict/gps")
def predict_by_gps(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    current = fetch_online_aqi_latlon(lat, lon)

    city, dates, actual, predicted, next_day = predict_latlon(model, lat, lon)
    plot_path = plot_wave(city, dates, actual, predicted, next_day)

    return format_response(city, current, next_day, plot_path)


# ===============================
# COMMON RESPONSE FORMAT
# ===============================
def format_response(city, current, next_day, plot_path):
    if next_day <= 50:
        quality = "Good"
        advice = "Safe for outdoor activities"
    elif next_day <= 100:
        quality = "Moderate"
        advice = "Limit outdoor exposure"
    else:
        quality = "Unhealthy"
        advice = "Avoid outdoor activities"

    return {
        "city": city,
        "predicted_next_day_aqi": round(float(next_day), 2),
        "air_quality": quality,
        "health_advice": advice,
        "plot_path": plot_path
    }
