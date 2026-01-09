import torch
import numpy as np
from app.model_def import NBeatsAQIModel

# Load model
MODEL_PATH = "model/nbeats_state_dict.pth"
device = torch.device("cpu")

model = NBeatsAQIModel()
state_dict = torch.load(MODEL_PATH, map_location=device, weights_only=False)
model.load_state_dict(state_dict, strict=False)
model.eval()

print("=" * 60)
print("MODEL TESTING")
print("=" * 60)

# Create dummy input (30 values)
dummy_input = torch.randn(1, 30)

print(f"\nInput shape: {dummy_input.shape}")

# Test each block
with torch.no_grad():
    for i, block in enumerate(model.blocks):
        try:
            output = block(dummy_input)
            print(f"Block {i} output shape: {output.shape}")
        except Exception as e:
            print(f"Block {i} ERROR: {e}")

# Test full forward pass
print("\n" + "=" * 60)
print("FULL FORWARD PASS")
print("=" * 60)

try:
    with torch.no_grad():
        output = model(dummy_input)
    print(f"✅ Model output shape: {output.shape}")
    print(f"✅ Model output value: {output.item()}")
except Exception as e:
    print(f"❌ Model forward pass FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test with real AQI data
print("\n" + "=" * 60)
print("TEST WITH REAL DATA")
print("=" * 60)

# Simulate 30 days of AQI
real_aqi = np.array([75, 78, 82, 79, 85, 88, 91, 87, 83, 80,
                     77, 79, 81, 84, 82, 78, 75, 73, 76, 79,
                     82, 85, 88, 90, 87, 84, 81, 79, 77, 80], dtype=np.float32)

# Normalize
mean_val = real_aqi.mean()
std_val = real_aqi.std() + 1e-8
normalized = (real_aqi - mean_val) / std_val

x = torch.tensor(normalized, dtype=torch.float32).unsqueeze(0)

print(f"Input AQI: {real_aqi[-5:]}")  # Last 5 days
print(f"Normalized input: {normalized[-5:]}")

try:
    with torch.no_grad():
        pred_normalized = model(x).item()
    
    # Denormalize
    pred_aqi = int(pred_normalized * std_val + mean_val)
    
    print(f"✅ Predicted (normalized): {pred_normalized:.4f}")
    print(f"✅ Predicted AQI: {pred_aqi}")
except Exception as e:
    print(f"❌ Prediction FAILED: {e}")
    import traceback
    traceback.print_exc()