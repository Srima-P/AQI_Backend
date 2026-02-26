def health_recommendation(aqi):
    """Generate health recommendation based on AQI"""
    aqi = int(aqi)
    
    if aqi <= 50:
        return "Good: Air quality is satisfactory, enjoy outdoor activities"
    elif aqi <= 100:
        return "Moderate: Acceptable air quality for most people"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups: Reduce prolonged outdoor exertion"
    elif aqi <= 200:
        return "Unhealthy: Everyone should reduce outdoor activity"
    elif aqi <= 300:
        return "Very Unhealthy: Avoid outdoor activities"
    else:
        return "Hazardous: Stay indoors, health alert"