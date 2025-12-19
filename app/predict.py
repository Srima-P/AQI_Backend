import pandas as pd
import torch
import numpy as np

DATA_PATH = "data/aqi_history.csv"
SEQ_LEN = 30

df = pd.read_csv(DATA_PATH, parse_dates=["date"])

def nearest_city(lat, lon):
    df["dist"] = (df["latitude"] - lat) ** 2 + (df["longitude"] - lon) ** 2
    row = df.loc[df["dist"].idxmin()]
    return row["city"]

def predict_city(model, city):
    city_df = df[df["city"] == city].sort_values("date")

    series = city_df["aqi"].values
    dates = city_df["date"].values

    x = torch.tensor(series[-SEQ_LEN:], dtype=torch.float32).view(1, SEQ_LEN, 1)

    with torch.no_grad():
        _, forecast = model(x)

    return dates, series, series[-(len(series)-SEQ_LEN):], forecast.item()

def predict_latlon(model, lat, lon):
    city = nearest_city(lat, lon)
    dates, actual, predicted, next_day = predict_city(model, city)
    return city, dates, actual, predicted, next_day
