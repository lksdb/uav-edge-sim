import os
import ast
import time
import requests
import threading
import queue

from uav import UAV
from onnx_inference import predict
from utility import load_specs, load_config

CONFIG_PATH = "/config/uav_config.json"
CONTROLLER_URL = os.getenv("CONTROLLER_URL")
IMG_RANGE = ast.literal_eval(os.getenv("IMG_RANGE"))

lock = threading.Lock()
infer_queue = queue.Queue()

def inference_worker():
    while True:
        task = infer_queue.get()   # waits for task from main loop
        
        start = time.perf_counter()
        result = predict(task[0])  # run inference 
        end = time.perf_counter()

        task[1].run_inference(end-start) 

        try:
            requests.post(f"{CONTROLLER_URL}/inference_result", json={"name":task[1].name, "is_fire":result["is_fire"]})
        except:
            pass
        infer_queue.task_done()

def register(uav):
    while True:
        try:
            res = requests.post(
                f"{CONTROLLER_URL}/register",
                json={"name": uav.name}
            )
            if res.status_code == 200:
                print(f"{uav.name} registered")
                return
        except:
            pass

        time.sleep(1)  # retry until controller is up


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
    register(uav)
    threading.Thread(target=inference_worker, daemon=True).start()

    i=IMG_RANGE[0]
    while True:
        uav.step(1, "hover")
            
        if infer_queue.empty() and i < IMG_RANGE[1]:   # one task at most
            infer_queue.put((f"/cam_feed/{i}.jpg", uav))
            i += 1

        # send telemetry
        try:
            requests.post(f"{CONTROLLER_URL}/status", json=uav.get_telemetry())
        except:
            pass

        time.sleep(1)

if __name__ == "__main__":
    main()