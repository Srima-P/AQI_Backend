import torch
import torch.nn as nn

class NBeatsBlock(nn.Module):
    """
    Single N-BEATS block with 4 fully connected layers.
    """
    def __init__(self, input_size, theta_size, hidden_size=128):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc4 = nn.Linear(hidden_size, hidden_size)
        # Theta layer without bias (based on parameter count)
        self.theta = nn.Linear(hidden_size, theta_size, bias=False)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        x = self.relu(self.fc4(x))
        theta_output = self.theta(x)
        # Return the mean of theta outputs as the block's contribution
        return theta_output.mean(dim=1, keepdim=True)


class NBeatsAQIModel(nn.Module):
    """
    Complete N-BEATS model with 6 stacks (blocks).
    Architecture matches your trained model with 54 parameters.
    
    Structure:
    - 6 blocks total
    - Each block: 4 FC layers (128 units) + 1 theta layer
    - Blocks 0-2: theta_size=4 (trend/seasonality)
    - Blocks 3-5: theta_size=1 (final predictions)
    """
    def __init__(self):
        super().__init__()
        
        self.input_size = 30
        self.hidden_size = 128
        
        # 6 N-BEATS blocks
        # First 3 blocks: theta_size=4 (params 8, 17, 26 show [4, 128])
        # Last 3 blocks: theta_size=1 (params 35, 44, 53 show [1, 128])
        self.blocks = nn.ModuleList([
            NBeatsBlock(self.input_size, theta_size=4, hidden_size=self.hidden_size),  # Block 0
            NBeatsBlock(self.input_size, theta_size=4, hidden_size=self.hidden_size),  # Block 1
            NBeatsBlock(self.input_size, theta_size=4, hidden_size=self.hidden_size),  # Block 2
            NBeatsBlock(self.input_size, theta_size=1, hidden_size=self.hidden_size),  # Block 3
            NBeatsBlock(self.input_size, theta_size=1, hidden_size=self.hidden_size),  # Block 4
            NBeatsBlock(self.input_size, theta_size=1, hidden_size=self.hidden_size),  # Block 5
        ])
    
    def forward(self, x):
        """
        Forward pass: sum contributions from all blocks.
        """
        batch_size = x.shape[0]
        forecast = torch.zeros(batch_size, 1, device=x.device, dtype=x.dtype)
        
        for block in self.blocks:
            block_output = block(x)
            forecast = forecast + block_output
        
        # Return as 1D tensor for batch
        return forecast.squeeze(1)
    
    def load_state_dict(self, state_dict, strict=True):
        """
        Custom loader to map parameters.X format to the model structure.
        
        Parameter mapping (9 params per block):
        - fc1.weight, fc1.bias (params 0-1)
        - fc2.weight, fc2.bias (params 2-3)
        - fc3.weight, fc3.bias (params 4-5)
        - fc4.weight, fc4.bias (params 6-7)
        - theta.weight (param 8, no bias)
        
        Total: 54 parameters = 6 blocks × 9 parameters
        """
        if any(key.startswith('parameters.') for key in state_dict.keys()):
            print("📦 Loading N-BEATS model with 'parameters.X' format")
            
            new_state_dict = {}
            param_idx = 0
            
            for block_num in range(6):
                block_prefix = f"blocks.{block_num}"
                
                # FC1: weight and bias
                new_state_dict[f"{block_prefix}.fc1.weight"] = state_dict[f"parameters.{param_idx}"]
                new_state_dict[f"{block_prefix}.fc1.bias"] = state_dict[f"parameters.{param_idx + 1}"]
                param_idx += 2
                
                # FC2: weight and bias
                new_state_dict[f"{block_prefix}.fc2.weight"] = state_dict[f"parameters.{param_idx}"]
                new_state_dict[f"{block_prefix}.fc2.bias"] = state_dict[f"parameters.{param_idx + 1}"]
                param_idx += 2
                
                # FC3: weight and bias
                new_state_dict[f"{block_prefix}.fc3.weight"] = state_dict[f"parameters.{param_idx}"]
                new_state_dict[f"{block_prefix}.fc3.bias"] = state_dict[f"parameters.{param_idx + 1}"]
                param_idx += 2
                
                # FC4: weight and bias
                new_state_dict[f"{block_prefix}.fc4.weight"] = state_dict[f"parameters.{param_idx}"]
                new_state_dict[f"{block_prefix}.fc4.bias"] = state_dict[f"parameters.{param_idx + 1}"]
                param_idx += 2
                
                # Theta: weight only (no bias)
                new_state_dict[f"{block_prefix}.theta.weight"] = state_dict[f"parameters.{param_idx}"]
                param_idx += 1
            
            # Load the remapped state dict
            result = super().load_state_dict(new_state_dict, strict=strict)
            print(f"✅ Successfully loaded {param_idx} parameters into 6 N-BEATS blocks")
            return result
        else:
            # Standard loading
            return super().load_state_dict(state_dict, strict=strict)