from pathlib import Path
import yaml 

def load_config(path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
    
    #print(config)  # Debug: Print the loaded configuration
    #print(type(config))  # Debug: Print the type of the loaded configuration
    return config

# Test
#load_config()
