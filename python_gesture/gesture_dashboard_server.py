import argparse
import asyncio
import json
import sys
import threading
import time
from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel


ROOT_DIR = Path(__file__).resolve().parents[1]
GESTURE_SRC = ROOT_DIR / "src" / "gesture"
if str(GESTURE_SRC) not in sys.path:
    sys.path.insert(0, str(GESTURE_SRC))

from feature_extractor import FeatureExtractor  # noqa: E402
from gesture_classifier import GestureClassifier  # noqa: E402
from udp_sender import UDPSender  # noqa: E402


GESTURE_TO_ACTION = {
    "FIST": "sit",
    "OPEN_PALM": "idle",
    "POINT_INDEX": "forward",
    "VICTORY": "backward",
    "THUMBS_UP": "wave",
    "ROCK": "jump",
    "THREE": "stand",
    "UNKNOWN": "none",
}

DEFAULT_STATE = {
    "gesture": "OPEN_PALM",
    "gestureId": 1,
    "action": "idle",
    "udpStatus": "Disabled",
    "timestamp": "--:--:--",
    "source": "python",
    "stableCount": 0,
    "requiredStableFrames": 4,
}


class StatusUpdate(BaseModel):
    gesture: str = "OPEN_PALM"
    gestureId: int = 1
    action: str = "idle"
    udpStatus: Optional[str] = None
    timestamp: Optional[str] = None
    source: str = "manual"
    stableCount: int = 4


class GestureDashboardRuntime:
    def __init__(self, camera_index=0, enable_udp=False, udp_ip="127.0.0.1", udp_port=5052):
        self.camera_index = camera_index
        self.enable_udp = enable_udp
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.required_stable_frames = 4
        self.lock = threading.Lock()
        self.running = False
        self.thread = None
        self.latest_frame = self._make_placeholder_frame("Starting Python gesture server...")
        self.latest_state = dict(DEFAULT_STATE)
        self.latest_state["udpStatus"] = "Enabled" if enable_udp else "Disabled"
        self.stable_candidate = "UNKNOWN"
        self.stable_count = 0
        self.last_official_gesture = self.latest_state["gesture"]
        self.feature_extractor = None
        self.classifier = None
        self.hands = None
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.udp_sender = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._recognition_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.udp_sender:
            self.udp_sender.close()

    def get_state(self):
        with self.lock:
            return dict(self.latest_state)

    def set_state(self, state):
        with self.lock:
            self.latest_state = {
                **self.latest_state,
                **state,
                "timestamp": state.get("timestamp") or self._now(),
            }

    def get_jpeg_frame(self):
        with self.lock:
            frame = self.latest_frame.copy()
        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            fallback = self._make_placeholder_frame("Frame encoding failed.")
            ok, buffer = cv2.imencode(".jpg", fallback)
        return buffer.tobytes()

    def _recognition_loop(self):
        try:
            self.feature_extractor = FeatureExtractor()
            self.classifier = GestureClassifier()
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            if self.enable_udp:
                self.udp_sender = UDPSender(ip=self.udp_ip, port=self.udp_port)
        except Exception as exc:
            self._set_camera_unavailable(f"Recognizer init failed: {exc}")
            return

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self._set_camera_unavailable("Camera Unavailable")
            return

        while self.running:
            success, frame = cap.read()
            if not success:
                self._set_camera_unavailable("Camera frame read failed")
                time.sleep(0.2)
                continue

            processed = self._process_frame(frame)
            with self.lock:
                self.latest_frame = processed

        cap.release()

    def _process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        candidate = "UNKNOWN"
        gesture_id = 5
        action = "none"

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2),
                self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2),
            )
            features = self.feature_extractor.extract_features(hand_landmarks)
            candidate = self.classifier.classify(features)
            gesture_id = self.classifier.get_gesture_id(candidate)
            action = GESTURE_TO_ACTION.get(candidate, "none")

            if self.stable_candidate == candidate:
                self.stable_count += 1
            else:
                self.stable_candidate = candidate
                self.stable_count = 1

            if (
                candidate != self.classifier.UNKNOWN
                and self.stable_count >= self.required_stable_frames
            ):
                self._commit_stable_gesture(candidate, gesture_id, action)
        else:
            self.stable_candidate = "UNKNOWN"
            self.stable_count = 0

        self._draw_overlay(frame, candidate, gesture_id, action)
        return frame

    def _commit_stable_gesture(self, gesture, gesture_id, action):
        udp_status = "Disabled"
        if self.enable_udp and self.udp_sender:
            try:
                self.udp_sender.send_gesture(0, gesture_id, gesture)
                udp_status = "Connected"
            except Exception:
                udp_status = "UDP Send Failed"

        with self.lock:
            self.latest_state = {
                "gesture": gesture,
                "gestureId": gesture_id,
                "action": action,
                "udpStatus": udp_status,
                "timestamp": self._now(),
                "source": "python",
                "stableCount": min(self.stable_count, self.required_stable_frames),
                "requiredStableFrames": self.required_stable_frames,
            }
            self.last_official_gesture = gesture

    def _draw_overlay(self, frame, candidate, gesture_id, action):
        state = self.get_state()
        stable_count = min(self.stable_count, self.required_stable_frames)
        lines = [
            "Python MediaPipe Recognition Server",
            f"Current Gesture: {state.get('gesture', 'UNKNOWN')}",
            f"Candidate: {candidate}",
            f"Gesture ID: {state.get('gestureId', gesture_id)}",
            f"Dog Action: {state.get('action', action)}",
            f"Stable Count: {stable_count}/{self.required_stable_frames}",
            "New: ROCK -> jump | THREE -> stand",
        ]
        y = 28
        for index, line in enumerate(lines):
            color = (255, 255, 255) if index == 0 else (80, 240, 255)
            cv2.putText(frame, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.64, color, 2)
            y += 30

    def _set_camera_unavailable(self, message):
        frame = self._make_placeholder_frame(message)
        with self.lock:
            self.latest_frame = frame
            self.latest_state = {
                **self.latest_state,
                "gesture": "CAMERA_UNAVAILABLE",
                "gestureId": -1,
                "action": "none",
                "udpStatus": "Camera Unavailable",
                "timestamp": self._now(),
                "source": "python",
                "stableCount": 0,
            }

    @staticmethod
    def _now():
        return time.strftime("%H:%M:%S")

    @staticmethod
    def _make_placeholder_frame(message):
        frame = np.zeros((480, 640, 3), dtype="uint8")
        frame[:] = (8, 18, 30)
        cv2.rectangle(frame, (20, 20), (620, 460), (60, 210, 255), 2)
        cv2.putText(frame, message, (42, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (80, 240, 255), 2)
        cv2.putText(frame, "Check camera permission and device index.", (42, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (190, 210, 220), 1)
        return frame


runtime = GestureDashboardRuntime()
app = FastAPI(title="Gesture Dashboard Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    runtime.start()


@app.on_event("shutdown")
def on_shutdown():
    runtime.stop()


@app.get("/api/status")
def get_status():
    return JSONResponse(runtime.get_state())


@app.post("/api/update")
def update_status(update: StatusUpdate):
    payload = update.model_dump() if hasattr(update, "model_dump") else update.dict()
    runtime.set_state(payload)
    return JSONResponse(runtime.get_state())


@app.get("/video_feed")
def video_feed():
    def frame_generator():
        while True:
            frame = runtime.get_jpeg_frame()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
            time.sleep(0.04)

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    await websocket.accept()
    try:
        last_payload = ""
        while True:
            payload = json.dumps(runtime.get_state(), ensure_ascii=False)
            if payload != last_payload:
                await websocket.send_text(payload)
                last_payload = payload
            await asyncio.sleep(0.12)
    except WebSocketDisconnect:
        return


def parse_args():
    parser = argparse.ArgumentParser(description="Run the FastAPI gesture dashboard server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--enable-udp", action="store_true")
    parser.add_argument("--udp-ip", default="127.0.0.1")
    parser.add_argument("--udp-port", type=int, default=5052)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    runtime.camera_index = args.camera_index
    runtime.enable_udp = args.enable_udp
    runtime.udp_ip = args.udp_ip
    runtime.udp_port = args.udp_port
    runtime.latest_state["udpStatus"] = "Enabled" if args.enable_udp else "Disabled"
    uvicorn.run(app, host=args.host, port=args.port)
