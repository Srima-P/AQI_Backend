import os
import uvicorn
from fastapi import FastAPI, Query
from app.csv_manager import update_all_city_csv
from app.predictor import predict_city, predict_latlon
from app.waqi import fetch_city_aqi, fetch_online_aqi_latlon
from app.health import health_recommendation

app = FastAPI(title="AQI Prediction Backend")


# ---------------- STARTUP ----------------
@app.on_event("startup")
def startup():
    update_all_city_csv()


# ---------------- MANUAL UPDATE ----------------
@app.get("/update/all")
def manual_update():
    update_all_city_csv()
    return {"status": "All cities update triggered"}


# ---------------- CITY PREDICTION ----------------
@app.get("/predict/city")
def predict_by_city(city: str):
    current = fetch_city_aqi(city)

    history, next_day = predict_city(city)

    next_day = int(float(next_day))

    return {
        "city": city,
        "current_aqi": current,
        "predicted_next_day": next_day,
        "health": health_recommendation(next_day),
    }


# ---------------- GPS PREDICTION ----------------
@app.get("/predict/gps")
def predict_by_gps(
    lat: float = Query(...),
    lon: float = Query(...)
):
    current = fetch_online_aqi_latlon(lat, lon)

    city, history, next_day = predict_latlon(lat, lon)

    next_day = int(float(next_day))

    return {
        "nearest_city": city,
        "current_aqi": current,
        "predicted_next_day": next_day,
        "health": health_recommendation(next_day),
    }
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)