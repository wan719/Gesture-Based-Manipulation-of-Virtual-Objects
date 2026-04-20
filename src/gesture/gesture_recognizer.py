import time

import cv2
import mediapipe as mp
import requests

from feature_extractor import FeatureExtractor
from gesture_classifier import GestureClassifier
from udp_sender import UDPSender


DASHBOARD_UPDATE_URL = "http://127.0.0.1:8000/api/update"


def push_status_to_dashboard(gesture_name, gesture_id, action_name):
    """Push the latest status to the dashboard bridge service."""
    try:
        requests.post(
            DASHBOARD_UPDATE_URL,
            json={
                "gesture": gesture_name,
                "gestureId": gesture_id,
                "action": action_name,
            },
            timeout=0.2,
        )
    except Exception:
        # Dashboard push must never block/interrupt the main loop.
        pass


class GestureRecognizer:
    def __init__(self, debug=False, enable_udp=True):
        self.debug = debug

        # MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        try:
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        except FileNotFoundError as err:
            raise RuntimeError(
                "MediaPipe resource loading failed. On Windows, this may happen "
                "if the Python environment path contains non-ASCII characters. "
                "Please use an environment under an ASCII-only path, e.g. E:\\gesture_env."
            ) from err

        self.mp_draw = mp.solutions.drawing_utils

        # Feature extractor and classifier
        self.feature_extractor = FeatureExtractor()
        self.classifier = GestureClassifier()
        self.classifier.debug = debug

        # UDP sender
        self.enable_udp = enable_udp
        self.udp_sender = UDPSender(ip="127.0.0.1", port=5052) if enable_udp else None

        # Fingertip landmark ids
        self.fingertip_ids = [4, 8, 12, 16, 20]

        # Send throttling
        self.last_sent_gesture = [None, None]
        self.last_send_time = [0.0, 0.0]
        self.send_interval = 0.35

        # Stable frame confirmation
        self.stable_candidate = [None, None]
        self.stable_count = [0, 0]
        self.required_stable_frames = 4

        # Last sent info for overlay
        self.last_sent_label = "None"
        self.last_sent_id = -1
        self.last_sent_action = "None"

        self.color_map = {
            "FIST": (0, 0, 255),
            "OPEN_PALM": (0, 255, 0),
            "POINT_INDEX": (255, 0, 0),
            "VICTORY": (255, 255, 0),
            "THUMBS_UP": (255, 0, 255),
            "UNKNOWN": (128, 128, 128),
        }

        self.gesture_to_action = {
            "FIST": "sit",
            "OPEN_PALM": "idle",
            "POINT_INDEX": "forward",
            "VICTORY": "backward",
            "THUMBS_UP": "wave",
            "UNKNOWN": "none",
        }

    def get_action_name(self, gesture):
        return self.gesture_to_action.get(gesture, "none")

    def update_stable_state(self, hand_idx, gesture):
        if self.stable_candidate[hand_idx] == gesture:
            self.stable_count[hand_idx] += 1
        else:
            self.stable_candidate[hand_idx] = gesture
            self.stable_count[hand_idx] = 1

        return self.stable_count[hand_idx] >= self.required_stable_frames

    def should_send_gesture(self, hand_idx, gesture):
        now = time.time()

        if not self.update_stable_state(hand_idx, gesture):
            return False

        if self.last_sent_gesture[hand_idx] != gesture:
            self.last_sent_gesture[hand_idx] = gesture
            self.last_send_time[hand_idx] = now
            return True

        if now - self.last_send_time[hand_idx] > self.send_interval:
            self.last_send_time[hand_idx] = now
            return True

        return False

    def draw_mapping_legend(self, frame):
        legend_lines = [
            "Mapping:",
            "FIST -> ID 0 -> sit",
            "OPEN_PALM -> ID 1 -> idle",
            "POINT_INDEX -> ID 2 -> forward",
            "VICTORY -> ID 3 -> backward",
            "THUMBS_UP -> ID 4 -> wave",
        ]

        start_y = 20
        for i, line in enumerate(legend_lines):
            cv2.putText(
                frame,
                line,
                (frame.shape[1] - 320, start_y + i * 22),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (220, 220, 220),
                1,
            )

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        detected_gestures = []

        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2),
                    self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2),
                )

                h, w, _ = frame.shape
                for tip_id in self.fingertip_ids:
                    lm = hand_landmarks.landmark[tip_id]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 8, (0, 0, 255), cv2.FILLED)

                features = self.feature_extractor.extract_features(hand_landmarks)
                gesture = self.classifier.classify(features)
                gesture_id = self.classifier.get_gesture_id(gesture)
                action_name = self.get_action_name(gesture)

                detected_gestures.append((gesture, gesture_id))

                if self.enable_udp and gesture != self.classifier.UNKNOWN:
                    if self.should_send_gesture(hand_idx, gesture):
                        self.udp_sender.send_gesture(hand_idx, gesture_id, gesture)
                        push_status_to_dashboard(gesture, gesture_id, action_name)
                        self.last_sent_label = gesture
                        self.last_sent_id = gesture_id
                        self.last_sent_action = action_name
                        print(
                            f"[SEND] Hand {hand_idx + 1}: "
                            f"{gesture} -> ID {gesture_id} -> Action {action_name}"
                        )

                color = self.color_map.get(gesture, (255, 255, 255))
                base_y = 70 + hand_idx * 110

                cv2.putText(
                    frame,
                    f"Hand {hand_idx + 1}: {gesture}",
                    (10, base_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    color,
                    2,
                )

                cv2.putText(
                    frame,
                    f"Send ID: {gesture_id}",
                    (10, base_y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1,
                )

                cv2.putText(
                    frame,
                    f"Dog Action: {action_name}",
                    (10, base_y + 56),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 255),
                    1,
                )

                cv2.putText(
                    frame,
                    f"Stable Count: {self.stable_count[hand_idx]}/{self.required_stable_frames}",
                    (10, base_y + 84),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (200, 255, 200),
                    1,
                )

                if self.debug:
                    fingers = features.get("fingers_extended", [])
                    cv2.putText(
                        frame,
                        f"Fingers: {fingers}",
                        (10, base_y + 104),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (255, 255, 0),
                        1,
                    )

        cv2.putText(
            frame,
            "Gesture -> UDP -> Unity RobotDog",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
        )

        self.draw_mapping_legend(frame)

        if self.enable_udp:
            cv2.putText(
                frame,
                "UDP: 127.0.0.1:5052",
                (10, frame.shape[0] - 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (200, 200, 200),
                1,
            )

        cv2.putText(
            frame,
            f"Last Sent: {self.last_sent_label} | ID {self.last_sent_id} | Action {self.last_sent_action}",
            (10, frame.shape[0] - 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            1,
        )

        cv2.putText(
            frame,
            "Press 'q' to quit | Press 'd' to toggle debug",
            (10, frame.shape[0] - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

        return frame, detected_gestures

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera.")
            return

        print("=" * 60)
        print("Gesture recognition started (stable frame send mode)")
        print("Supported mappings:")
        print("FIST        -> ID 0 -> sit")
        print("OPEN_PALM   -> ID 1 -> idle")
        print("POINT_INDEX -> ID 2 -> forward")
        print("VICTORY     -> ID 3 -> backward")
        print("THUMBS_UP   -> ID 4 -> wave")
        if self.enable_udp:
            print("UDP enabled, sending to 127.0.0.1:5052")
        print(f"Stable frame threshold: {self.required_stable_frames}")
        print("Press 'q' to quit")
        print("Press 'd' to toggle debug")
        print("=" * 60)

        while True:
            success, frame = cap.read()
            if not success:
                continue

            frame, _ = self.process_frame(frame)
            cv2.imshow("Gesture Recognition", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("d"):
                self.debug = not self.debug
                self.classifier.debug = self.debug
                print(f"Debug mode: {'ON' if self.debug else 'OFF'}")

        cap.release()
        cv2.destroyAllWindows()

        if self.enable_udp and self.udp_sender:
            self.udp_sender.close()


if __name__ == "__main__":
    recognizer = GestureRecognizer(debug=True, enable_udp=True)
    recognizer.run()
