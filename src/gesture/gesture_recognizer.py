import cv2
import mediapipe as mp
import time

from feature_extractor import FeatureExtractor
from gesture_classifier import GestureClassifier
from udp_sender import UDPSender


class GestureRecognizer:
    def __init__(self, debug=False, enable_udp=True):
        # MediaPipe Hands 初始化
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        # 特征提取与分类器
        self.feature_extractor = FeatureExtractor()
        self.classifier = GestureClassifier()
        self.classifier.debug = debug

        # UDP 通信
        self.enable_udp = enable_udp
        if self.enable_udp:
            self.udp_sender = UDPSender(ip="127.0.0.1", port=5052)

        # 调试模式
        self.debug = debug

        # 指尖 ID
        self.fingertip_ids = [4, 8, 12, 16, 20]

        # 发送节流
        self.last_sent_gesture = [None, None]
        self.last_send_time = [0.0, 0.0]
        self.send_interval = 0.35  # 秒

        # 稳定帧确认
        self.stable_candidate = [None, None]
        self.stable_count = [0, 0]
        self.required_stable_frames = 4

        # 最近一次已发送内容，方便显示
        self.last_sent_label = "None"
        self.last_sent_id = -1
        self.last_sent_action = "None"

        # 手势显示颜色
        self.color_map = {
            "FIST": (0, 0, 255),
            "OPEN_PALM": (0, 255, 0),
            "POINT_INDEX": (255, 0, 0),
            "VICTORY": (255, 255, 0),
            "THUMBS_UP": (255, 0, 255),
            "UNKNOWN": (128, 128, 128)
        }

        # 手势 -> Unity 动作映射
        self.gesture_to_action = {
            "FIST": "sit",
            "OPEN_PALM": "idle",
            "POINT_INDEX": "forward",
            "VICTORY": "backward",
            "THUMBS_UP": "wave",
            "UNKNOWN": "none"
        }

    def get_action_name(self, gesture):
        return self.gesture_to_action.get(gesture, "none")

    def update_stable_state(self, hand_idx, gesture):
        """
        稳定帧确认：
        只有连续多帧识别成同一手势，才认为真正稳定
        """
        if self.stable_candidate[hand_idx] == gesture:
            self.stable_count[hand_idx] += 1
        else:
            self.stable_candidate[hand_idx] = gesture
            self.stable_count[hand_idx] = 1

        if self.stable_count[hand_idx] >= self.required_stable_frames:
            return True
        return False

    def should_send_gesture(self, hand_idx, gesture):
        """
        同时满足：
        1. 手势已经稳定多帧
        2. 距上次发送超过最小时间间隔，或者与上次发送不同
        """
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
            "THUMBS_UP -> ID 4 -> wave"
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
                1
            )

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        detected_gestures = []

        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # 画骨架
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2),
                    self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2)
                )

                # 画指尖
                h, w, _ = frame.shape
                for tip_id in self.fingertip_ids:
                    lm = hand_landmarks.landmark[tip_id]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 8, (0, 0, 255), cv2.FILLED)

                # 特征提取
                features = self.feature_extractor.extract_features(hand_landmarks)

                # 手势识别
                gesture = self.classifier.classify(features)
                gesture_id = self.classifier.get_gesture_id(gesture)
                action_name = self.get_action_name(gesture)

                detected_gestures.append((gesture, gesture_id))

                # UDP 发送（发送前稳定帧确认）
                if self.enable_udp and gesture != self.classifier.UNKNOWN:
                    if self.should_send_gesture(hand_idx, gesture):
                        self.udp_sender.send_gesture(hand_idx, gesture_id, gesture)
                        self.last_sent_label = gesture
                        self.last_sent_id = gesture_id
                        self.last_sent_action = action_name
                        print(f"[SEND] Hand {hand_idx + 1}: {gesture} -> ID {gesture_id} -> Action {action_name}")

                # 显示信息
                color = self.color_map.get(gesture, (255, 255, 255))
                base_y = 70 + hand_idx * 110

                cv2.putText(
                    frame,
                    f"Hand {hand_idx + 1}: {gesture}",
                    (10, base_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    color,
                    2
                )

                cv2.putText(
                    frame,
                    f"Send ID: {gesture_id}",
                    (10, base_y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1
                )

                cv2.putText(
                    frame,
                    f"Dog Action: {action_name}",
                    (10, base_y + 56),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 255),
                    1
                )

                cv2.putText(
                    frame,
                    f"Stable Count: {self.stable_count[hand_idx]}/{self.required_stable_frames}",
                    (10, base_y + 84),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (200, 255, 200),
                    1
                )

                if self.debug:
                    fingers = features.get('fingers_extended', [])
                    cv2.putText(
                        frame,
                        f"Fingers: {fingers}",
                        (10, base_y + 104),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (255, 255, 0),
                        1
                    )

        # 顶部状态
        cv2.putText(
            frame,
            "Gesture -> UDP -> Unity RobotDog",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        # 右上角映射表
        self.draw_mapping_legend(frame)

        # 底部状态
        if self.enable_udp:
            cv2.putText(
                frame,
                "UDP: 127.0.0.1:5052",
                (10, frame.shape[0] - 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (200, 200, 200),
                1
            )

        cv2.putText(
            frame,
            f"Last Sent: {self.last_sent_label} | ID {self.last_sent_id} | Action {self.last_sent_action}",
            (10, frame.shape[0] - 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            1
        )

        cv2.putText(
            frame,
            "Press 'q' to quit | Press 'd' to toggle debug",
            (10, frame.shape[0] - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1
        )

        return frame, detected_gestures

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("无法打开摄像头")
            return

        print("=" * 60)
        print("手势识别系统启动（稳定帧发送版）")
        print("支持的手势与机械狗动作映射：")
        print("FIST        -> ID 0 -> sit")
        print("OPEN_PALM   -> ID 1 -> idle")
        print("POINT_INDEX -> ID 2 -> forward")
        print("VICTORY     -> ID 3 -> backward")
        print("THUMBS_UP   -> ID 4 -> wave")
        if self.enable_udp:
            print("UDP通信已开启，正在向 127.0.0.1:5052 发送数据")
        print(f"稳定帧阈值: {self.required_stable_frames} 帧")
        print("按 'q' 退出")
        print("按 'd' 切换调试模式")
        print("=" * 60)

        while True:
            success, frame = cap.read()
            if not success:
                continue

            frame, gestures = self.process_frame(frame)
            cv2.imshow("Gesture Recognition", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('d'):
                self.debug = not self.debug
                self.classifier.debug = self.debug
                print(f"调试模式: {'开启' if self.debug else '关闭'}")

        cap.release()
        cv2.destroyAllWindows()

        if self.enable_udp:
            self.udp_sender.close()


if __name__ == "__main__":
    recognizer = GestureRecognizer(debug=True, enable_udp=True)
    recognizer.run()