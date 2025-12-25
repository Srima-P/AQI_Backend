def health_recommendation(aqi):
    if aqi <= 50:
        return "Good: Safe for everyone"
    if aqi <= 100:
        return "Moderate: Sensitive groups should be cautious"
    if aqi <= 200:
        return "Poor: Avoid prolonged outdoor activity"
    if aqi <= 300:
        return "Very Poor: Health risk for all"
    return "Severe: Emergency conditions"
