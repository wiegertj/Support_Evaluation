import os
import sys

import yaml

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

current_file_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_file_dir, "config.yaml")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

new_dir = os.path.join(config["working_dir"], config["run_name"])
os.makedirs(new_dir, exist_ok=True)

runtimes_dir = os.path.join(new_dir, "runtimes")
os.makedirs(runtimes_dir, exist_ok=True)