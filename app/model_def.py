import torch
import torch.nn as nn

class NBeatsAQIModel(nn.Module):
    """
    N-BEATS style model for AQI prediction.
    This version uses ParameterList to match the saved model structure.
    """
    def __init__(self, load_from_saved=True):
        super().__init__()
        
        if load_from_saved:
            # Use ParameterList to match saved model structure
            # This will be populated when loading state_dict
            self.parameters_list = nn.ParameterList()
        else:
            # Standard Sequential structure for training new models
            self.fc = nn.Sequential(
                nn.Linear(30, 128),
                nn.ReLU(),
                nn.Linear(128, 1)
            )
    
    def forward(self, x):
        # If using ParameterList (loaded model)
        if hasattr(self, 'parameters_list') and len(self.parameters_list) > 0:
            # Reconstruct forward pass from parameters
            # Assuming structure: Linear(30, 128) -> ReLU -> Linear(128, 1)
            
            # First layer: 30 -> 128
            if len(self.parameters_list) >= 2:
                weight1 = self.parameters_list[0]  # Shape: [128, 30]
                bias1 = self.parameters_list[1]    # Shape: [128]
                x = torch.matmul(x, weight1.t()) + bias1
                x = torch.relu(x)
            
            # Second layer: 128 -> 1
            if len(self.parameters_list) >= 4:
                weight2 = self.parameters_list[2]  # Shape: [1, 128]
                bias2 = self.parameters_list[3]    # Shape: [1]
                x = torch.matmul(x, weight2.t()) + bias2
            
            return x.squeeze(1)
        
        # Standard Sequential forward pass
        else:
            return self.fc(x).squeeze(1)
    
    def load_state_dict(self, state_dict, strict=True):
        """
        Custom state_dict loader to handle both formats.
        """
        # Check if state_dict uses 'parameters.X' format
        if any(key.startswith('parameters.') for key in state_dict.keys()):
            print("📦 Loading model with 'parameters.X' format")
            
            # Create ParameterList if not exists
            if not hasattr(self, 'parameters_list'):
                self.parameters_list = nn.ParameterList()
            
            # Clear and populate
            self.parameters_list = nn.ParameterList()
            
            # Sort parameters by index
            sorted_params = sorted(
                [(int(k.split('.')[1]), v) for k, v in state_dict.items() if k.startswith('parameters.')],
                key=lambda x: x[0]
            )
            
            for _, param_tensor in sorted_params:
                self.parameters_list.append(nn.Parameter(param_tensor))
            
            print(f"✅ Loaded {len(self.parameters_list)} parameters")
            return
        
        # Standard loading for 'fc.X' format
        else:
            print("📦 Loading model with standard 'fc.X' format")
            super().load_state_dict(state_dict, strict=strict)