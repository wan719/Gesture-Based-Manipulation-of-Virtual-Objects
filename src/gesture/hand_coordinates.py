"""
hand_coordinates.py - 输出21个关键点坐标
功能：实时打印手部关键点的坐标，为后续特征工程做准备
"""

import cv2
import mediapipe as mp
import sys

def main():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    # 指尖ID列表
    fingertip_ids = [4, 8, 12, 16, 20]
    # 手指名称
    finger_names = ["拇指", "食指", "中指", "无名指", "小指"]
    
    print("="*60)
    print("开始输出关键点坐标（按'q'退出）")
    print("格式：手指名 (ID): (x, y) - 归一化坐标")
    print("="*60)
    
    while True:
        success, frame = cap.read()
        if not success:
            continue
        
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # 画骨架
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # 获取图像尺寸
                h, w, c = frame.shape
                
                # 打印这一帧的指尖坐标
                print(f"\n--- 手 {hand_idx+1} ---")
                for i, tip_id in enumerate(fingertip_ids):
                    lm = hand_landmarks.landmark[tip_id]
                    # 归一化坐标（0-1之间）
                    x_norm = lm.x
                    y_norm = lm.y
                    z_norm = lm.z
                    
                    # 像素坐标
                    x_pixel = int(x_norm * w)
                    y_pixel = int(y_norm * h)
                    
                    print(f"{finger_names[i]} (ID:{tip_id}): "
                          f"像素=({x_pixel:3d}, {y_pixel:3d}), "
                          f"归一化=({x_norm:.3f}, {y_norm:.3f}, {z_norm:.3f})")
                    
                    # 在画面上显示坐标（可选）
                    cv2.putText(frame, f"{tip_id}", (x_pixel+5, y_pixel-5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        cv2.imshow("Hand Coordinates", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()