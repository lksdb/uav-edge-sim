import os
import time
import requests

from uav import UAV
from utility import load_specs, load_config

CONFIG_PATH = "/config/uav_config.json"
CONTROLLER_URL = os.getenv("CONTROLLER_URL")

def main():
    config = load_config(CONFIG_PATH)
    specs = load_specs(config["model"], "/app/uav_specs.json")
    
    if(config["edge_device"] == ""):
        edge_specs = None
    else:
        edge_specs = load_specs(config["edge_device"], "/app/edge_specs.json")
   
    uav = UAV(
        name=config["uav_id"],
        model_specs=specs,
        edge_device=edge_specs,
        curr_battery=config["battery"]
    )

    while True:
        # simulate step
        uav.step(1, "hover")

        # send telemetry
        try:
            requests.post(f"{CONTROLLER_URL}/status", json=uav.get_telemetry())
        except:
            pass

        time.sleep(1)
        uav.status()

if __name__ == "__main__":
    main()