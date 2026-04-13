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

        # 指尖 ID（画红点用）
        self.fingertip_ids = [4, 8, 12, 16, 20]

        # 避免重复发送
        self.last_gestures = [None, None]
        self.last_send_time = [0.0, 0.0]
        self.send_interval = 0.3  # 秒

        # 手势显示颜色
        self.color_map = {
            "FIST": (0, 0, 255),         # 红
            "OPEN_PALM": (0, 255, 0),    # 绿
            "POINT_INDEX": (255, 0, 0),  # 蓝
            "VICTORY": (255, 255, 0),    # 青
            "THUMBS_UP": (255, 0, 255),  # 紫
            "UNKNOWN": (128, 128, 128)   # 灰
        }

    def should_send_gesture(self, hand_idx, gesture):
        """控制 UDP 发送频率，避免每帧重复发送"""
        now = time.time()

        # 手势变化了
        if self.last_gestures[hand_idx] != gesture:
            self.last_gestures[hand_idx] = gesture
            self.last_send_time[hand_idx] = now
            return True

        # 相同手势超过最小发送间隔，也允许补发一次
        if now - self.last_send_time[hand_idx] > self.send_interval:
            self.last_send_time[hand_idx] = now
            return True

        return False

    def process_frame(self, frame):
        """处理单帧图像"""
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

                # 画指尖红点
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
                detected_gestures.append((gesture, gesture_id))

                # UDP 发送
                if self.enable_udp and gesture != self.classifier.UNKNOWN:
                    if self.should_send_gesture(hand_idx, gesture):
                        self.udp_sender.send_gesture(hand_idx, gesture_id, gesture)

                # 显示手势信息
                color = self.color_map.get(gesture, (255, 255, 255))
                base_y = 60 + hand_idx * 70

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
                    f"ID: {gesture_id}",
                    (10, base_y + 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    1
                )

                if self.debug:
                    fingers = features.get('fingers_extended', [])
                    cv2.putText(
                        frame,
                        f"Fingers: {fingers}",
                        (10, base_y + 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 0),
                        1
                    )

        # 底部状态信息
        if self.enable_udp:
            cv2.putText(
                frame,
                "UDP: Sending to 127.0.0.1:5052",
                (10, frame.shape[0] - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1
            )

        cv2.putText(
            frame,
            "Press 'q' to quit | Press 'd' to toggle debug",
            (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1
        )

        return frame, detected_gestures

    def run(self):
        """运行实时识别"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("无法打开摄像头")
            return

        print("=" * 50)
        print("手势识别系统启动")
        print("支持的手势：握拳、手掌、食指、剪刀手、点赞")
        if self.enable_udp:
            print("UDP通信已开启，正在向 127.0.0.1:5052 发送数据")
        print("按 'q' 退出")
        print("按 'd' 切换调试模式")
        print("=" * 50)

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