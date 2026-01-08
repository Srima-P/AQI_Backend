import os
import pandas as pd
import numpy as np
import torch
from app.model_def import NBeatsAQIModel

DATA_DIR = "data"
MODEL_PATH = "model/nbeats_state_dict.pth"

# Load model once globally
device = torch.device("cpu")
model = NBeatsAQIModel(load_from_saved=True)

# Load weights
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
    """
    Predict next-day AQI for a city using the trained N-BEATS model.
    """
    path = f"{DATA_DIR}/{city.lower()}.csv"
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found for city: {city}")
    
    df = pd.read_csv(path)
    df = df.tail(30)  # Get last 30 days
    
    history = df["aqi"].tolist()
    
    # If we don't have 30 days of data, pad with the mean
    if len(history) < 30:
        mean_aqi = np.mean(history)
        history = [mean_aqi] * (30 - len(history)) + history
    
    # Use model if available, otherwise fallback to moving average
    if model is not None:
        try:
            # Normalize input (important for model performance)
            input_data = np.array(history[-30:], dtype=np.float32)
            mean_val = input_data.mean()
            std_val = input_data.std() + 1e-8  # Avoid division by zero
            
            normalized = (input_data - mean_val) / std_val
            
            # Convert to tensor
            x = torch.tensor(normalized, dtype=torch.float32).unsqueeze(0)
            
            # Predict
            with torch.no_grad():
                pred_normalized = model(x).item()
            
            # Denormalize
            next_day = int(pred_normalized * std_val + mean_val)
            
            # Clamp to reasonable AQI range
            next_day = max(0, min(500, next_day))
            
            print(f"🔮 Model prediction for {city}: {next_day}")
            
        except Exception as e:
            print(f"⚠️ Model prediction failed for {city}: {e}")
            # Fallback: weighted moving average (recent days have more weight)
            weights = np.exp(np.linspace(-1, 0, min(7, len(history))))
            weights /= weights.sum()
            next_day = int(np.average(history[-len(weights):], weights=weights))
            print(f"📊 Using fallback prediction for {city}: {next_day}")
    else:
        # Fallback: weighted moving average (recent days have more weight)
        weights = np.exp(np.linspace(-1, 0, min(7, len(history))))
        weights /= weights.sum()
        next_day = int(np.average(history[-len(weights):], weights=weights))
        print(f"📊 Model unavailable, using fallback for {city}: {next_day}")
    
    return history, next_day


def predict_latlon(lat: float, lon: float):
    """
    Predict AQI for a GPS location by finding nearest city.
    """
    from math import radians, cos, sin, asin, sqrt
    
    # City coordinates (same as in csv_manager.py)
    CITY_COORDS = {
        "Chennai": (13.0827, 80.2707),
        "Coimbatore": (11.0168, 76.9558),
        "Madurai": (9.9252, 78.1198),
        "Salem": (11.6643, 78.1460),
        "Trichy": (10.7905, 78.7047),
        "Thanjavur": (10.7867, 79.1378),
        "Tirunelveli": (8.7139, 77.7567),
        "Vellore": (12.9165, 79.1325),
        "Thoothukudi": (8.7642, 78.1348),
        "Erode": (11.3410, 77.7172),
        "Karur": (10.9601, 78.0766),
        "Dindigul": (10.3624, 77.9695),
        "Kanchipuram": (12.8342, 79.7036),
        "Nagercoil": (8.1833, 77.4119),
        "Ooty": (11.4102, 76.6950)
    }
    
    def haversine(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        return 6371 * 2 * asin(sqrt(a))
    
    # Find nearest city
    nearest_city = min(
        CITY_COORDS.items(),
        key=lambda x: haversine(lat, lon, x[1][0], x[1][1])
    )[0]
    
    history, next_day = predict_city(nearest_city)
    
    return nearest_city, history, next_day