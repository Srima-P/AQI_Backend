import os
import uvicorn
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.db_manager import update_all_cities_db
from app.predictor import predict_city, predict_latlon
from app.waqi import fetch_city_aqi  # Only used if you want online current
from app.health import health_recommendation

app = FastAPI(title="AQI Prediction Backend")

# ---------------- CORS (IMPORTANT FOR FLUTTER) ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    try:
        history, next_day = predict_city(city)

        if not history:
            raise HTTPException(status_code=404, detail="City not found in database")

        current = history[-1]

        return {
            "city": city,
            "current_aqi": int(current),
            "predicted_next_day": int(next_day),
            "health": health_recommendation(next_day),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- GPS PREDICTION ----------------
@app.get("/predict/gps")
def predict_by_gps(
    lat: float = Query(...),
    lon: float = Query(...)
):
    try:
        city, history, next_day = predict_latlon(lat, lon)

        if not history:
            raise HTTPException(status_code=404, detail="No nearby city found")

        current = history[-1]

        return {
            "nearest_city": city,
            "current_aqi": int(current),
            "predicted_next_day": int(next_day),
            "health": health_recommendation(next_day),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- ROOT CHECK ----------------
@app.get("/")
def root():
    return {"message": "AQI Prediction Backend Running 🚀"}


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)