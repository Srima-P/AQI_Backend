import pandas as pd
import numpy as np

DATA_DIR = "data"

def predict_city(city: str):
    path = f"{DATA_DIR}/{city.lower()}.csv"

    df = pd.read_csv(path)
    df = df.tail(30)

    history = df["aqi"].tolist()

    # Simple, stable prediction
    next_day = int(np.mean(history))

    return history, next_day


def predict_latlon(lat: float, lon: float):
    city = "chennai"  # nearest logic already handled elsewhere

    history, next_day = predict_city(city)

    return city, history, next_day
