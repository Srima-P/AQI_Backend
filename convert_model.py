import torch

OLD_MODEL_PATH = "model/nbeats_aqi.pth"   # your existing model
NEW_MODEL_PATH = "model/nbeats_state.pth"  # clean output

DEVICE = "cpu"

# Load FULL model object
full_model = torch.load(OLD_MODEL_PATH, map_location=DEVICE)

# Extract weights safely
state_dict = full_model.state_dict()

# Save only weights
torch.save(state_dict, NEW_MODEL_PATH)

print("✅ State_dict extracted successfully")
print(f"Saved to: {NEW_MODEL_PATH}")
