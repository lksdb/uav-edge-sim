from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import asyncio
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# allow browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# in-memory state
uav_states: Dict[str, dict] = {}
clients = []

# UAV → Controller
@app.post("/status")
async def receive_status(data: dict):
    uav_id = data["name"]
    uav_states[uav_id] = data
    return {"ok": True}

# WebSocket → Frontend
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)

    try:
        while True:
            await asyncio.sleep(1)
            await ws.send_json(uav_states)
    except:
        clients.remove(ws)

app.mount("/dashboard", StaticFiles(directory="static", html=True), name="static")