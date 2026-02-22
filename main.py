import os
import uvicorn
from fastapi import FastAPI, Query
from app.db_manager import update_all_cities_db
from app.predictor import predict_city, predict_latlon
from app.waqi import fetch_city_aqi, fetch_online_aqi_latlon
from app.health import health_recommendation

app = FastAPI(title="AQI Prediction Backend")


# ---------------- STARTUP ----------------
@app.on_event("startup")
def startup():
    print("🚀 Starting AQI Backend with PostgreSQL...")
    update_all_cities_db()


# ---------------- MANUAL UPDATE ----------------
@app.get("/update/all")
def manual_update():
    update_all_cities_db()
    return {"status": "All cities database update triggered"}


# ---------------- CITY PREDICTION ----------------
@app.get("/predict/city")
def predict_by_city(city: str):
    current = fetch_city_aqi(city)
    history, next_day = predict_city(city)
    
    return {
        "city": city,
        "current_aqi": current,
        "predicted_next_day": int(next_day),
        "health": health_recommendation(next_day),
    }


# ---------------- GPS PREDICTION ----------------
@app.get("/predict/gps")
def predict_by_gps(
    lat: float = Query(...),
    lon: float = Query(...)
):
    city, history, next_day = predict_latlon(lat, lon)

    # Get current AQI from YOUR DATABASE instead of WAQI
    current = history[-1] if history else None

    return {
        "nearest_city": city,
        "current_aqi": int(current) if current else None,
        "predicted_next_day": int(next_day),
        "health": health_recommendation(next_day),
    }
__name__ == "__main__":
port = int(os.environ.get("PORT", 8000))
uvicorn.run("main:app", host="0.0.0.0", port=port)