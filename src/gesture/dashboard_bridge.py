from datetime import datetime
import json

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_state = {
    "gesture": "OPEN_PALM",
    "gestureId": 1,
    "action": "idle",
    "udpStatus": "Connected",
    "timestamp": "",
    "source": "python"
}

gesture_to_action = {
    "FIST": "sit",
    "OPEN_PALM": "idle",
    "POINT_INDEX": "forward",
    "VICTORY": "backward",
    "THUMBS_UP": "wave",
}

clients = set()


@app.get("/api/status")
async def get_status():
    return latest_state


@app.post("/api/update")
async def update_status(payload: dict):
    global latest_state

    gesture = payload.get("gesture", "UNKNOWN")
    gesture_id = payload.get("gestureId", 5)
    action = payload.get("action") or gesture_to_action.get(gesture, "none")

    latest_state = {
        "gesture": gesture,
        "gestureId": gesture_id,
        "action": action,
        "udpStatus": "Connected",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "source": "python"
    }

    dead_clients = []
    for ws in clients:
        try:
            await ws.send_text(json.dumps(latest_state, ensure_ascii=False))
        except Exception:
            dead_clients.append(ws)

    for ws in dead_clients:
        clients.discard(ws)

    return {"ok": True, "data": latest_state}


@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    try:
        await websocket.send_text(json.dumps(latest_state, ensure_ascii=False))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.discard(websocket)
    except Exception:
        clients.discard(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
