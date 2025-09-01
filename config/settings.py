import os
import sys
import yaml

class Config:

    def __init__(self):
        if hasattr(sys, '_MEIPASS'):
            base_dir = os.path.join(sys._MEIPASS, 'config')
        else:
            base_dir = os.path.abspath(os.path.dirname(__file__))

        config_path = os.path.join(base_dir, 'config.yml')

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"❌ Config file not found: {config_path}")

        with open(config_path, 'r', encoding="utf-8") as file:
            self.config_data = yaml.safe_load(file)

    def get_config(self):
        return self.config_data
