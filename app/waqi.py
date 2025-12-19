import requests
import os

WAQI_TOKEN = os.getenv("WAQI_TOKEN", "")

def fetch_online_aqi(city):
    if not WAQI_TOKEN:
        return None

    url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
    r = requests.get(url, timeout=5).json()

    if r["status"] == "ok":
        return r["data"]["aqi"]
    return None

def fetch_online_aqi_latlon(lat, lon):
    if not WAQI_TOKEN:
        return None

    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={WAQI_TOKEN}"
    r = requests.get(url, timeout=5).json()

    if r["status"] == "ok":
        return r["data"]["aqi"]
    return None
