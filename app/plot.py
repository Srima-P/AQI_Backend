import matplotlib.pyplot as plt
import os

def plot_wave(city, dates, actual, predicted, next_day):
    os.makedirs("plots", exist_ok=True)
    path = f"plots/{city}_aqi.png"

    plt.figure(figsize=(12,5))
    plt.plot(dates, actual, label="Historical AQI", alpha=0.6)
    plt.plot(dates[-len(predicted):], predicted, "--", label="Predicted AQI")
    plt.scatter(dates[-1], next_day, color="red", label="Next Day AQI")
    plt.legend()
    plt.title(f"AQI Prediction - {city}")
    plt.xlabel("Date")
    plt.ylabel("AQI")
    plt.grid()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path
