import torch

MODEL_PATH = "model/nbeats_state_dict.pth"

# Load the state dict
state_dict = torch.load(MODEL_PATH, map_location="cpu")

print("=" * 60)
print("MODEL STRUCTURE INSPECTION")
print("=" * 60)

print(f"\nTotal parameters: {len(state_dict)}")
print("\nAll keys in state_dict:")
for key in state_dict.keys():
    print(f"  - {key}: shape {state_dict[key].shape}")

print("\n" + "=" * 60)
print("ANALYZING LAYER STRUCTURE")
print("=" * 60)

# Try to infer the architecture
param_list = list(state_dict.items())

for i, (name, tensor) in enumerate(param_list):
    print(f"\nParameter {i}: {name}")
    print(f"  Shape: {tensor.shape}")
    print(f"  Type: {'Weight' if len(tensor.shape) == 2 else 'Bias'}")