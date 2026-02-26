import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ✅ Correct env variable
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not OPENWEATHER_API_KEY:
    print("❌ ERROR: OPENWEATHER_API_KEY not found in .env file!")
else:
    print(f"🔑 Using API Key: {OPENWEATHER_API_KEY[:10]}...")

# City coordinates
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
    "Ooty": (11.4102, 76.6950),
}

def calculate_aqi_from_pm25(pm25):
    if pm25 <= 12.0:
        return int((50 / 12.0) * pm25)
    elif pm25 <= 35.4:
        return int(50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1))
    elif pm25 <= 55.4:
        return int(100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5))
    elif pm25 <= 150.4:
        return int(150 + ((200 - 150) / (150.4 - 55.5)) * (pm25 - 55.5))
    elif pm25 <= 250.4:
        return int(200 + ((300 - 200) / (250.4 - 150.5)) * (pm25 - 150.5))
    else:
        return int(300 + ((500 - 300) / (500.4 - 250.5)) * (pm25 - 250.5))


def predict_city(city_name):
    try:
        if city_name not in CITY_COORDS:
            return None, None

        lat, lon = CITY_COORDS[city_name]

        # Current AQI
        current_url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution?"
            f"lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        )

        current_res = requests.get(current_url, timeout=10)
        if current_res.status_code != 200:
            print(current_res.text)
            return None, None

        data = current_res.json()
        pm25 = data["list"][0]["components"]["pm2_5"]
        current_aqi = calculate_aqi_from_pm25(pm25)

        # Forecast AQI
        forecast_url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?"
            f"lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        )

        forecast_res = requests.get(forecast_url, timeout=10)

        if forecast_res.status_code == 200:
            forecast_data = forecast_res.json()
            if len(forecast_data["list"]) >= 24:
                tomorrow_pm25 = forecast_data["list"][24]["components"]["pm2_5"]
                predicted_aqi = calculate_aqi_from_pm25(tomorrow_pm25)
            else:
                predicted_aqi = current_aqi + 5
        else:
            predicted_aqi = current_aqi + 5

        return [current_aqi], predicted_aqi

    except Exception as e:
        print("Error:", e)
        return None, None


def predict_latlon(lat, lon):
    try:
        current_url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution?"
            f"lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        )

        res = requests.get(current_url, timeout=10)
        if res.status_code != 200:
            return None, None, None

        data = res.json()
        pm25 = data["list"][0]["components"]["pm2_5"]
        current_aqi = calculate_aqi_from_pm25(pm25)

        forecast_url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?"
            f"lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        )

        forecast_res = requests.get(forecast_url, timeout=10)

        if forecast_res.status_code == 200:
            forecast_data = forecast_res.json()
            if len(forecast_data["list"]) >= 24:
                tomorrow_pm25 = forecast_data["list"][24]["components"]["pm2_5"]
                predicted_aqi = calculate_aqi_from_pm25(tomorrow_pm25)
            else:
                predicted_aqi = current_aqi + 5
        else:
            predicted_aqi = current_aqi + 5

        city = find_nearest_city(lat, lon)
        return city, [current_aqi], predicted_aqi

    except Exception as e:
        print("Error:", e)
        return None, None, None


def find_nearest_city(lat, lon):
    import math
    min_dist = float("inf")
    nearest = "Coimbatore"

    for city, (clat, clon) in CITY_COORDS.items():
        dist = math.sqrt((lat - clat)**2 + (lon - clon)**2)
        if dist < min_dist:
            min_dist = dist
            nearest = city

    return nearest