import torch
from nbeats_pytorch.model import NBeatsNet

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model():
    model = torch.load(
        "models/nbeats_aqi_model.pth",
        map_location=device,
        weights_only=False
    )
    model.eval()
    return model
