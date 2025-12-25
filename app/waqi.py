import requests
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("WAQI_TOKEN")

def fetch_city_aqi(city):
    url = f"https://api.waqi.info/feed/{city}/?token={TOKEN}"
    r = requests.get(url).json()
    if r["status"] != "ok":
        return None
    return r["data"]["aqi"]

def fetch_online_aqi_latlon(lat, lon):
    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={TOKEN}"
    r = requests.get(url).json()
    if r["status"] != "ok":
        return None
    return r["data"]["aqi"]
