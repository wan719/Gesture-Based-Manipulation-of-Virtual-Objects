"""
gesture_recognizer.py - 完整的手势识别系统
功能：整合手部检测、特征提取、规则分类，实时识别手势
"""

import cv2
import mediapipe as mp
from feature_extractor import FeatureExtractor
from gesture_classifier import GestureClassifier

class GestureRecognizer:
    def __init__(self, debug=False):
        # 初始化MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # 初始化特征提取器和分类器
        self.feature_extractor = FeatureExtractor()
        self.classifier = GestureClassifier()
        self.classifier.debug = debug
        
        # 调试模式
        self.debug = debug
        
        # 指尖ID（用于画图）
        self.fingertip_ids = [4, 8, 12, 16, 20]
    
    def process_frame(self, frame):
        """
        处理单帧图像
        Returns: 标注后的图像，识别到的手势列表
        """
        # 水平翻转
        frame = cv2.flip(frame, 1)
        
        # 转换为RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 手部检测
        results = self.hands.process(frame_rgb)
        
        detected_gestures = []
        
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # 画骨架
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2),
                    self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2)
                )
                
                # 画指尖
                h, w, c = frame.shape
                for tip_id in self.fingertip_ids:
                    lm = hand_landmarks.landmark[tip_id]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 8, (0, 0, 255), cv2.FILLED)
                
                # 提取特征
                features = self.feature_extractor.extract_features(hand_landmarks)
                
                # 识别手势
                gesture = self.classifier.classify(features)
                detected_gestures.append(gesture)
                
                # 在画面上显示手势
                cv2.putText(frame, f"Hand {hand_idx+1}: {gesture}", 
                           (10, 60 + hand_idx*30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # 如果处于调试模式，显示手指状态
                if self.debug:
                    fingers = features['fingers_extended']
                    cv2.putText(frame, f"Fingers: {fingers}", 
                               (10, 120 + hand_idx*30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # 显示帧率
        cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0]-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame, detected_gestures
    
    def run(self):
        """运行实时识别"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("无法打开摄像头")
            return
        
        print("="*50)
        print("手势识别系统启动")
        print("支持的手势：握拳、手掌、食指、剪刀手、点赞")
        print("按 'q' 退出")
        print("按 'd' 切换调试模式")
        print("="*50)
        
        while True:
            success, frame = cap.read()
            if not success:
                continue
            
            # 处理帧
            frame, gestures = self.process_frame(frame)
            
            # 显示画面
            cv2.imshow("Gesture Recognition", frame)
            
            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('d'):
                self.debug = not self.debug
                self.classifier.debug = self.debug
                print(f"调试模式: {'开启' if self.debug else '关闭'}")
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    recognizer = GestureRecognizer(debug=True)
    recognizer.run()