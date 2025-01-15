import yaml
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(BASE_DIR, '../config/config.yml')


class Config:

    def __init__(self):
        with open(PATH, 'r') as file:
            self.config_data = yaml.safe_load(file)

    def get_config(self):
        return self.config_data
