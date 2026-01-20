import yaml
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "settings.yaml")
    if not os.path.exists(config_path):
        raise FileNotFoundError("config/settings.yaml not found")
    
    with open(config_path, "r") as f:
        return yaml.safe_load(f)