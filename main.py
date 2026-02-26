import os
import uvicorn
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv  # ✅ ADDED

# Load environment variables
load_dotenv()  # ✅ ADDED

# Your existing modules
from app.predictor import predict_city, predict_latlon
from app.health import health_recommendation

# ---------------- FASTAPI APP ----------------
app = FastAPI(title="AQI Prediction Backend - Real-Time")

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
    api_key = os.getenv("OPENWEATHER_API_KEY")  # ✅ ADDED
    if not api_key:
        print("❌ ERROR: OPENWEATHER_API_KEY not found!")
    else:
        print(f"🔑 API Key Loaded: {api_key[:10]}...")
        
    print("🚀 Starting AQI Backend with Real-Time OpenWeather API...")
    print("✅ All predictions will fetch LIVE data from OpenWeather!")

# ---------------- CITY PREDICTION ----------------
@app.get("/predict/city")
@app.head("/predict/city")  # ✅ ADDED
def predict_by_city(city: str):
    try:
        print(f"\n🔍 API Request for city: {city}")
        
        history, next_day = predict_city(city)

        # ✅ FIXED ERROR HANDLING
        if not history or next_day is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch real-time data for {city}"
            )

        current = history[-1]

        response = {
            "city": city,
            "current_aqi": int(current),
            "predicted_next_day": int(next_day),
            "health": health_recommendation(next_day),
        }
        
        print(f"✅ Response: {response}")
        return response

    except HTTPException as he:  # ✅ IMPORTANT FIX
        raise he
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- GPS PREDICTION ----------------
@app.get("/predict/gps")
@app.head("/predict/gps")  # ✅ ADDED
def predict_by_gps(lat: float = Query(...), lon: float = Query(...)):
    try:
        print(f"\n🔍 API Request for GPS: {lat}, {lon}")
        
        city, history, next_day = predict_latlon(lat, lon)

        # ✅ FIXED CONDITION
        if not history or not city or next_day is None:
            raise HTTPException(
                status_code=404,
                detail="Could not fetch real-time data for this location"
            )

        current = history[-1]

        response = {
            "nearest_city": city,
            "current_aqi": int(current),
            "predicted_next_day": int(next_day),
            "health": health_recommendation(next_day),
        }
        
        print(f"✅ Response: {response}")
        return response

    except HTTPException as he:  # ✅ IMPORTANT FIX
        raise he
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- ROOT ----------------
@app.get("/")
@app.head("/")  # ✅ ADDED
def root():
    return {
        "message": "AQI Backend Running 🚀",
        "status": "Real-Time OpenWeather Integration Active",
        "endpoints": ["/predict/city", "/predict/gps"]
    }

# ---------------- HEALTH CHECK ----------------
@app.get("/health")
@app.head("/health")  # ✅ ADDED
def health():
    return {"status": "ok", "mode": "real-time"}

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)