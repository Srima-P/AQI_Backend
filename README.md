# AQI Prediction Backend 🌍

A FastAPI-based backend that predicts Air Quality Index (AQI) using deep learning and live WAQI data.

## Features
- Next-day AQI prediction
- WAQI live data fetching
- Offline fallback using historical data
- AQI visualization
- Health recommendations

## Tech Stack
- FastAPI
- PyTorch
- Python
- Pandas, NumPy
- Matplotlib

## Run Locally

```bash
git clone https://github.com/your-username/AQI_Backend.git
cd AQI_Backend
pip install -r requirements.txt
uvicorn main:app --reload
