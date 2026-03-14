"""
hand_demo_stable.py - MediaPipe手部检测演示程序（稳定版）
功能：打开摄像头，实时检测手部21个关键点，并在指尖画红点
按 'q' 退出程序
"""

import cv2
import mediapipe as mp
import sys
import time

def main():
    print("="*50)
    print("开始运行手部检测程序")
    print("Python版本:", sys.version)
    print("OpenCV版本:", cv2.__version__)
    print("MediaPipe版本:", mp.__version__)
    print("="*50)
    
    # 初始化MediaPipe Hands
    print("\n正在初始化MediaPipe Hands...")
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils
    print("MediaPipe初始化成功！")
    
    # 打开摄像头
    print("\n正在打开摄像头...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("摄像头0失败，尝试摄像头1...")
        cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("错误：无法打开摄像头！")
        input("按回车键退出...")
        return
    
    # 设置摄像头分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("摄像头打开成功！")
    print("\n按 'q' 退出程序")
    print("-"*50)
    
    frame_count = 0
    
    while True:
        success, frame = cap.read()
        if not success:
            continue
        
        frame_count += 1
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            cv2.putText(frame, f"Hands: {len(results.multi_hand_landmarks)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            for hand_landmarks in results.multi_hand_landmarks:
                # 画骨架
                mp_draw.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2)
                )
                
                # 画指尖红点
                h, w, _ = frame.shape
                fingertip_ids = [4, 8, 12, 16, 20]
                
                for id, lm in enumerate(hand_landmarks.landmark):
                    if id in fingertip_ids:
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        cv2.circle(frame, (cx, cy), 10, (0, 0, 255), cv2.FILLED)
        
        cv2.imshow("Hand Tracking Demo", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("程序结束")

if __name__ == "__main__":
    main()