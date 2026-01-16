import os
import numpy as np
import torch
from app.model_def import NBeatsAQIModel
from app.db_manager import get_city_history, CITY_COORDS
from math import radians, cos, sin, asin, sqrt

MODEL_PATH = "model/nbeats_state_dict.pth"

# Load model once globally
device = torch.device("cpu")
model = NBeatsAQIModel()

if os.path.exists(MODEL_PATH):
    try:
        state_dict = torch.load(MODEL_PATH, map_location=device, weights_only=False)
        model.load_state_dict(state_dict, strict=False)
        model.eval()
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"⚠️ Model loading failed: {e}")
        model = None
else:
    print(f"⚠️ Model file not found at {MODEL_PATH}")
    model = None

def predict_city(city: str):
    """Predict next-day AQI using database history"""
    
    # Get history from database
    history = get_city_history(city, days=30)
    
    if len(history) < 7:
        raise ValueError(f"Not enough data for {city}. Need at least 7 days, have {len(history)}.")
    
    # Pad if needed
    if len(history) < 30:
        mean_aqi = np.mean(history)
        history = [mean_aqi] * (30 - len(history)) + history
        print(f"⚠️ Padded {city} history to 30 days")
    
    # Use model if available
    if model is not None:
        try:
            input_data = np.array(history[-30:], dtype=np.float32)
            mean_val = input_data.mean()
            std_val = input_data.std()
            
            if std_val < 1e-8:
                std_val = 1.0
            
            normalized = (input_data - mean_val) / std_val
            x = torch.tensor(normalized, dtype=torch.float32).unsqueeze(0)
            
            with torch.no_grad():
                pred_normalized = model(x).item()
            
            next_day = pred_normalized * std_val + mean_val
            next_day = int(max(0, min(500, next_day)))
            
            print(f"🔮 Model prediction for {city}: Current avg={mean_val:.1f}, Predicted={next_day}")
            return history, next_day
            
        except Exception as e:
            print(f"⚠️ Model prediction failed for {city}: {e}")
    
    # Fallback: weighted average
    weights = np.exp(np.linspace(-1, 0, min(7, len(history))))
    weights /= weights.sum()
    next_day = int(np.average(history[-len(weights):], weights=weights))
    
    print(f"📊 Fallback prediction for {city}: {next_day}")
    return history, next_day

def predict_latlon(lat: float, lon: float):
    """Predict AQI for GPS location"""
    def haversine(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        return 6371 * 2 * asin(sqrt(a))
    
    nearest_city = min(
        CITY_COORDS.items(),
        key=lambda x: haversine(lat, lon, x[1][0], x[1][1])
    )[0]
    
    print(f"📍 Nearest city for ({lat}, {lon}): {nearest_city}")
    
    history, next_day = predict_city(nearest_city)
    return nearest_city, history, next_day