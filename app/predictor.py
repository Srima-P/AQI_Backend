import torch
import numpy as np
from pathlib import Path

from app.model_def import NBeatsAQIModel  # your own model definition

# -----------------------------
# Device
# -----------------------------
device = torch.device("cpu")

# -----------------------------
# Load model architecture
# -----------------------------
model = NBeatsAQIModel()
model.to(device)

# -----------------------------
# Load weights ONLY
# -----------------------------
MODEL_PATH = Path("models/nbeats_aqi_weights.pth")

if not MODEL_PATH.exists():
    raise FileNotFoundError("Model weights not found")

state_dict = torch.load(MODEL_PATH, map_location=device)
model.load_state_dict(state_dict)
model.eval()

# -----------------------------
# Prediction helpers
# -----------------------------
def predict_city(city: str):
    history = np.random.randint(50, 150, size=30)  # replace with CSV logic

    x = torch.tensor(history, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        y = model(x).item()

    return history.tolist(), int(y)


def predict_latlon(lat: float, lon: float):
    city = "Nearest City"  # replace with your logic
    history = np.random.randint(50, 150, size=30)

    x = torch.tensor(history, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        y = model(x).item()

    return city, history.tolist(), int(y)
