# convert_model.py
import torch

OLD_MODEL_PATH = "model/nbeats_aqi.pth"
NEW_MODEL_PATH = "model/nbeats_state_dict.pth"
DEVICE = torch.device("cpu")

# Load FULL model (not state_dict)
model = torch.load(OLD_MODEL_PATH, map_location=DEVICE)

# Save ONLY state_dict
torch.save(model.state_dict(), NEW_MODEL_PATH)

print("✅ Conversion successful!")
print(f"Saved state_dict at: {NEW_MODEL_PATH}")
