#!/usr/bin/env python3
"""
手势识别 + UDP 发送端
识别常见手势并通过UDP发送到指定地址
"""

import cv2
import mediapipe as mp
import socket
import json
import time
import sys
import numpy as np

# ============ 配置 ============
UDP_HOST = '127.0.0.1'      # UDP目标地址
UDP_PORT = 8888              # UDP目标端口
DEBUG_MODE = True            # 调试模式：显示更多信息

# MediaPipe 关键点索引
# 0: 手腕
# 4: 拇指指尖, 3: 拇指远端关节, 2: 拇指中关节, 1: 拇指基关节
# 8: 食指指尖, 7: 食指远端关节, 6: 食指中关节, 5: 食指基关节
# 12: 中指指尖, 11: 中指远端关节, 10: 中指中关节, 9: 中指基关节
# 16: 无名指指尖, 15: 无名指远端关节, 14: 无名指中关节, 13: 无名指基关节
# 20: 小指指尖, 19: 小指远端关节, 18: 小指中关节, 17: 小指基关节

THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20

THUMB_IP = 3    # 拇指指间关节
INDEX_IP = 7    # 食指指间关节
MIDDLE_IP = 11  # 中指指间关节
RING_IP = 15    # 无名指指间关节
PINKY_IP = 19   # 小指指间关节

THUMB_MCP = 1   # 拇指基关节
INDEX_MCP = 5   # 食指基关节
MIDDLE_MCP = 9  # 中指基关节
RING_MCP = 13   # 无名指基关节
PINKY_MCP = 17  # 小指基关节

WRIST = 0

def calculate_distance(p1, p2):
    """计算两点之间的欧氏距离"""
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def calculate_angle(p1, p2, p3):
    """计算三点形成的角度（p2为顶点）"""
    v1 = np.array([p1.x - p2.x, p1.y - p2.y])
    v2 = np.array([p3.x - p2.x, p3.y - p2.y])
    
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
    cos_angle = np.clip(cos_angle, -1, 1)
    angle = np.arccos(cos_angle)
    return np.degrees(angle)

def is_finger_extended(landmarks, tip_idx, mcp_idx, ip_idx=None):
    """判断手指是否伸直"""
    tip = landmarks[tip_idx]
    mcp = landmarks[mcp_idx]
    
    # 简单判断：指尖y坐标小于（图像上方）基关节y坐标
    # 注意：图像坐标系y向下增加，所以"向上"伸直意味着y更小
    if tip.y < mcp.y:
        # 进一步检查指尖是否在基关节上方一定距离
        if ip_idx:
            ip = landmarks[ip_idx]
            return tip.y < ip.y < mcp.y
        return True
    return False

def is_finger_curled(landmarks, tip_idx, mcp_idx):
    """判断手指是否弯曲（指尖在基关节下方）"""
    tip = landmarks[tip_idx]
    mcp = landmarks[mcp_idx]
    return tip.y > mcp.y

def recognize_gesture(landmarks):
    """
    识别手势
    返回: (手势名称, 置信度)
    """
    # 提取关键点坐标（便于计算）
    thumb_tip = landmarks[THUMB_TIP]
    index_tip = landmarks[INDEX_TIP]
    middle_tip = landmarks[MIDDLE_TIP]
    ring_tip = landmarks[RING_TIP]
    pinky_tip = landmarks[PINKY_TIP]
    
    thumb_ip = landmarks[THUMB_IP]
    index_ip = landmarks[INDEX_IP]
    middle_ip = landmarks[MIDDLE_IP]
    ring_ip = landmarks[RING_IP]
    pinky_ip = landmarks[PINKY_IP]
    
    thumb_mcp = landmarks[THUMB_MCP]
    index_mcp = landmarks[INDEX_MCP]
    middle_mcp = landmarks[MIDDLE_MCP]
    ring_mcp = landmarks[RING_MCP]
    pinky_mcp = landmarks[PINKY_MCP]
    
    wrist = landmarks[WRIST]
    
    # 判断各手指状态
    thumb_extended = thumb_tip.y < thumb_ip.y
    index_extended = index_tip.y < index_ip.y
    middle_extended = middle_tip.y < middle_ip.y
    ring_extended = ring_tip.y < ring_ip.y
    pinky_extended = pinky_tip.y < pinky_ip.y
    
    # 计算手指伸展程度（用于更精确判断）
    index_straight = index_tip.y < index_mcp.y
    middle_straight = middle_tip.y < middle_mcp.y
    ring_straight = ring_tip.y < ring_mcp.y
    pinky_straight = pinky_tip.y < pinky_mcp.y
    
    # === 手势识别逻辑 ===
    
    # 1. 拳头 (Fist) - 所有手指弯曲
    if (not index_straight and not middle_straight and 
        not ring_straight and not pinky_straight):
        # 进一步判断拇指是否也弯曲
        thumb_curled = thumb_tip.y > thumb_mcp.y
        if thumb_curled:
            return ("fist", 0.9)
    
    # 2. 布/手掌 (Open Hand / Five) - 所有手指伸直
    if index_straight and middle_straight and ring_straight and pinky_straight:
        # 检查手指之间有明显间隙
        gap1 = calculate_distance(index_tip, middle_tip)
        gap2 = calculate_distance(middle_tip, ring_tip)
        gap3 = calculate_distance(ring_tip, pinky_tip)
        if gap1 > 0.05 and gap2 > 0.05 and gap3 > 0.05:
            return ("open_hand", 0.85)
    
    # 3. 石头 (Rock) - 拇指和食指伸直形成L形，其他弯曲
    if index_straight and not middle_straight and not ring_straight and not pinky_straight:
        # 拇指伸向侧面
        if thumb_tip.x < index_mcp.x:  # 左手
            thumb_side = thumb_tip.x > wrist.x
        else:  # 右手
            thumb_side = thumb_tip.x < wrist.x
        if thumb_side and thumb_extended:
            return ("rock", 0.8)
    
    # 4. 剪刀 (Scissors) - 食指和中指伸直，无名指和小指弯曲
    if index_straight and middle_straight and not ring_straight and not pinky_straight:
        return ("scissors", 0.85)
    
    # 5. 指向 (Point) - 只有食指伸直
    if index_straight and not middle_straight and not ring_straight and not pinky_straight:
        # 拇指可以伸直或弯曲
        return ("point", 0.8)
    
    # 6. 点赞 (Thumbs Up)
    if thumb_extended and not index_straight and not middle_straight:
        if not ring_straight and not pinky_straight:
            return ("thumbs_up", 0.85)
    
    # 7. OK手势 - 拇指和食指指尖相碰形成圆圈
    ok_distance = calculate_distance(thumb_tip, index_tip)
    if ok_distance < 0.05:  # 距离很近
        if not middle_straight and not ring_straight and not pinky_straight:
            return ("ok", 0.8)
    
    # 8. 比心 - 拇指和食指指尖相碰，中无名小指伸直
    if ok_distance < 0.06:
        if middle_straight and ring_straight and pinky_straight:
            return ("heart", 0.75)
    
    # 9. 数字1 - 只有食指伸直
    if index_straight and not middle_straight and not ring_straight and not pinky_straight:
        # 检查其他手指都弯曲
        if not middle_extended and not ring_extended and not pinky_extended:
            return ("one", 0.8)
    
    # 10. 数字2 - 食指和中指伸直
    if index_straight and middle_straight and not ring_straight and not pinky_straight:
        # 检查两根手指有一定夹角
        return ("two", 0.8)
    
    # 11. 数字3 - 食指、中指、无名指伸直
    if index_straight and middle_straight and ring_straight and not pinky_straight:
        return ("three", 0.8)
    
    # 12. 数字4 - 食指、无名指、小指伸直（类似四）
    if index_straight and not middle_straight and ring_straight and pinky_straight:
        return ("four", 0.75)
    
    # 13. 数字5 - 同手掌
    if index_straight and middle_straight and ring_straight and pinky_straight:
        if not thumb_extended:  # 拇指不伸直
            return ("five", 0.7)
    
    # 14. 六手势 - 拇指和小指伸直
    if thumb_extended and not index_extended and not middle_extended and not ring_extended and pinky_extended:
        return ("six", 0.7)
    
    # 15. 八手势 - 拇指和食指伸直
    if thumb_extended and index_extended and not middle_extended and not ring_extended and not pinky_extended:
        return ("eight", 0.7)
    
    # 16. 七手势 - 拇指、食指、小指伸直
    if thumb_extended and index_extended and not middle_extended and not ring_extended and pinky_extended:
        return ("seven", 0.65)
    
    return ("unknown", 0.0)

def draw_gesture_text(img, gesture, confidence):
    """在手势画面上显示识别结果"""
    text = f"{gesture}: {confidence:.2f}"
    cv2.putText(img, text, (10, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    
    # 显示置信度颜色
    color = (0, 255, 0) if confidence > 0.7 else (0, 165, 255)
    cv2.putText(img, text, (10, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

def main():
    print("="*50)
    print("手势识别 + UDP 发送端")
    print(f"目标: {UDP_HOST}:{UDP_PORT}")
    print("="*50)
    
    # 初始化MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,  # 简化：只检测一只手
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils
    
    # 初始化UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("错误：无法打开摄像头")
        return
    
    print("程序运行中...")
    print("按 'q' 退出")
    
    frame_count = 0
    last_gesture = "none"
    gesture_stable_count = 0  # 手势稳定计数
    
    while True:
        success, img = cap.read()
        if not success:
            continue
        
        frame_count += 1
        
        # 镜像翻转（更符合直觉）
        img = cv2.flip(img, 1)
        
        # 转换为RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        
        current_gesture = "none"
        confidence = 0.0
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 画骨架
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # 识别手势
                gesture, conf = recognize_gesture(hand_landmarks.landmark)
                current_gesture = gesture
                confidence = conf
                
                # 手势稳定检测（连续5帧相同才确认）
                if gesture == last_gesture and gesture != "unknown":
                    gesture_stable_count += 1
                else:
                    gesture_stable_count = 0
                
                last_gesture = gesture
                
                # 显示结果
                draw_gesture_text(img, gesture, confidence)
                
                # 在指尖画红点
                h, w, c = img.shape
                for id in [4, 8, 12, 16, 20]:
                    lm = hand_landmarks.landmark[id]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 8, (0, 0, 255), cv2.FILLED)
                
                # 通过UDP发送数据（每10帧或手势变化时）
                if frame_count % 10 == 0 or gesture_stable_count == 5:
                    if gesture != "unknown":
                        data = {
                            "gesture": gesture,
                            "confidence": round(confidence, 2),
                            "frame": frame_count,
                            "timestamp": time.time()
                        }
                        try:
                            sock.sendto(json.dumps(data).encode('utf-8'), 
                                       (UDP_HOST, UDP_PORT))
                            if DEBUG_MODE and gesture_stable_count == 5:
                                print(f"[UDP发送] {gesture} ({confidence:.2f})")
                        except Exception as e:
                            print(f"UDP发送错误: {e}")
        
        # 显示画面
        cv2.imshow("Gesture Recognition + UDP", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    sock.close()
    print("程序结束")

if __name__ == '__main__':
    main()
