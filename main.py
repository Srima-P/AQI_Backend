import os
import uvicorn
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Your existing modules
from app.db_manager import update_all_cities_db
from app.predictor import predict_city, predict_latlon
from app.health import health_recommendation

# ---------------- FASTAPI APP ----------------
app = FastAPI(title="AQI Prediction Backend")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- STARTUP ----------------
@app.on_event("startup")
def startup():
    print("🚀 Starting AQI Backend...")
    update_all_cities_db()

# ---------------- MANUAL UPDATE ----------------
@app.get("/update/all")
@app.head("/update/all")   # for uptime pings
def manual_update():
    update_all_cities_db()
    return {"status": "All cities database update triggered"}

# ---------------- CITY PREDICTION ----------------
@app.get("/predict/city")
@app.head("/predict/city")
def predict_by_city(city: str):
    try:
        history, next_day = predict_city(city)

        if not history:
            raise HTTPException(status_code=404, detail="City not found")

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
@app.head("/predict/gps")
def predict_by_gps(lat: float = Query(...), lon: float = Query(...)):
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

# ---------------- ROOT ----------------
@app.get("/")
@app.head("/")   # important for Render + uptime monitor
def root():
    return {"message": "AQI Backend Running 🚀"}

# ---------------- HEALTH CHECK ----------------
@app.get("/health")
@app.head("/health")
def health():
    return {"status": "ok"}

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render uses 10000
    uvicorn.run("main:app", host="0.0.0.0", port=port)