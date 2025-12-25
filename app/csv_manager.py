import os
import time
import pandas as pd
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from app.waqi import fetch_city_aqi

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# City coordinates (important for fallback)
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


def is_valid_aqi(aqi):
    if aqi is None:
        return False
    if isinstance(aqi, str) and aqi.strip() == "-":
        return False
    try:
        int(aqi)
        return True
    except:
        return False


def get_nearest_valid_city(city):
    lat, lon = CITY_COORDS[city]
    distances = []

    for other, (olat, olon) in CITY_COORDS.items():
        if other == city:
            continue
        aqi = fetch_city_aqi(other)
        if is_valid_aqi(aqi):
            dist = haversine(lat, lon, olat, olon)
            distances.append((dist, other, int(aqi)))

        time.sleep(0.5)

    if not distances:
        raise ValueError("No nearby AQI stations available")

    distances.sort()
    return distances[0][1], distances[0][2]


def update_city_csv(city):
    aqi = fetch_city_aqi(city)
    source = "direct"

    if not is_valid_aqi(aqi):
        nearest_city, aqi = get_nearest_valid_city(city)
        source = f"nearest:{nearest_city}"

    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(DATA_DIR, f"{city.lower()}.csv")

    row = {
        "date": today,
        "city": city,
        "aqi": int(aqi),
        "source": source
    }

    if os.path.exists(path):
        df = pd.read_csv(path)
        if today in df["date"].values:
            return
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_csv(path, index=False)


def update_all_city_csv():
    print("🔄 Updating AQI for all cities...")

    for city in CITY_COORDS:
        try:
            update_city_csv(city)
            print(f"✅ Updated: {city}")
            time.sleep(1)
        except Exception as e:
            print(f"❌ Failed: {city} | {e}")

    print("✅ AQI update completed.")
