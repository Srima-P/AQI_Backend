import os
import torch
import numpy as np
import pandas as pd
from nbeats_pytorch.model import NBeatsNet

DEVICE = torch.device("cpu")

model = NBeatsNet(
    stack_types=(NBeatsNet.GENERIC_BLOCK,),
    nb_blocks_per_stack=3,
    forecast_length=1,
    backcast_length=30,
    hidden_layer_units=128,
)

model.load_state_dict(
    torch.load("model/nbeats_state_dict.pth", map_location=DEVICE)
)

model.eval()


def predict_city(city: str):
    df = pd.read_csv(CSV_PATH)
    city_df = df[df["city"].str.lower() == city.lower()].tail(30)

    if len(city_df) < 30:
        raise ValueError("Not enough data for prediction")

    series = torch.tensor(
        city_df["aqi"].values, dtype=torch.float32
    ).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        forecast = model(series)[0][0].item()

    return round(float(forecast), 2)


def predict_latlon(lat: float, lon: float):
    df = pd.read_csv(CSV_PATH)
    df["dist"] = (df["latitude"] - lat) ** 2 + (df["longitude"] - lon) ** 2
    nearest_city = df.sort_values("dist").iloc[-30:]["city"].iloc[0]
    return predict_city(nearest_city)
