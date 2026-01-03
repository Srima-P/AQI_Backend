import torch
from nbeats_pytorch.model import NBeatsNet

# 🔹 path to your FULL model (current broken one)
FULL_MODEL_PATH = "nbeats_aqi.pth"

# 🔹 output weights-only model
WEIGHTS_PATH = "nbeats_aqi_weights.pth"

# load full model
model = torch.load(FULL_MODEL_PATH, map_location="cpu")

# save only weights
torch.save(model.state_dict(), WEIGHTS_PATH)

print("✅ Model successfully converted to weights-only format")
