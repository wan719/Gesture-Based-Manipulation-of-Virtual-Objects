#!/usr/bin/env python3
"""
单手指识别 - 识别哪根手指伸直
使用关节角度检测 + 时间平滑
"""

import cv2
import mediapipe as mp
import socket
import json
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from collections import deque

# ============ 配置 ============
UDP_HOST = '127.0.0.1'
UDP_PORT = 8888
DEBUG_MODE = True

# 置信度阈值（自行调整）
CONFIDENCE_THRESHOLD = 0.5  # 大于等于这个值才认为是有效手势

# 关键点索引
THUMB_TIP, THUMB_IP, THUMB_MCP = 4, 3, 1
INDEX_TIP, INDEX_IP, INDEX_MCP = 8, 7, 5
MIDDLE_TIP, MIDDLE_IP, MIDDLE_MCP = 12, 11, 9
RING_TIP, RING_IP, RING_MCP = 16, 15, 13
PINKY_TIP, PINKY_IP, PINKY_MCP = 20, 19, 17
WRIST = 0

# 手指名称中英文
FINGER_NAMES = {
    "Thumb": "拇指",
    "Index": "食指",
    "Middle": "中指",
    "Ring": "无名指",
    "Pinky": "小指",
    "Unknown": "未识别"
}

# 时间平滑缓冲区
gesture_buffer = deque(maxlen=8)

def calculate_angle(a, b, c):
    """计算三个点形成的角度（b为顶点）"""
    import numpy as np
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])
    
    ba = a - b
    bc = c - b
    
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.degrees(np.arccos(np.clip(cosine, -1, 1)))
    
    return angle

def get_extended_finger(landmarks):
    """
    使用关节角度检测哪根手指伸直
    返回: (手指名称, 置信度)
    """
    # 获取各关键点
    thumb_tip = landmarks[THUMB_TIP]
    thumb_ip = landmarks[THUMB_IP]
    thumb_mcp = landmarks[THUMB_MCP]
    index_tip = landmarks[INDEX_TIP]
    index_ip = landmarks[INDEX_IP]
    index_mcp = landmarks[INDEX_MCP]
    middle_tip = landmarks[MIDDLE_TIP]
    middle_ip = landmarks[MIDDLE_IP]
    middle_mcp = landmarks[MIDDLE_MCP]
    ring_tip = landmarks[RING_TIP]
    ring_ip = landmarks[RING_IP]
    ring_mcp = landmarks[RING_MCP]
    pinky_tip = landmarks[PINKY_TIP]
    pinky_ip = landmarks[PINKY_IP]
    pinky_mcp = landmarks[PINKY_MCP]
    wrist = landmarks[WRIST]
    
    # ====== 使用关节角度判断手指是否伸直 ======
    # 阈值：角度 > 160 表示手指完全伸直
    
    # 拇指角度
    thumb_angle = calculate_angle(thumb_mcp, thumb_ip, thumb_tip)
    thumb_extended = thumb_angle > 160
    # 置信度 = (角度 - 阈值) / 20，这样160度=0，180度=1
    thumb_conf = min(max((thumb_angle - 160) / 20, 0), 0.99) if thumb_extended else 0
    
    # 食指角度
    index_angle = calculate_angle(index_mcp, index_ip, index_tip)
    index_extended = index_angle > 160
    index_conf = min(max((index_angle - 160) / 20, 0), 0.99) if index_extended else 0
    
    # 中指角度
    middle_angle = calculate_angle(middle_mcp, middle_ip, middle_tip)
    middle_extended = middle_angle > 160
    middle_conf = min(max((middle_angle - 160) / 20, 0), 0.99) if middle_extended else 0
    
    # 无名指角度
    ring_angle = calculate_angle(ring_mcp, ring_ip, ring_tip)
    ring_extended = ring_angle > 160
    ring_conf = min(max((ring_angle - 160) / 20, 0), 0.99) if ring_extended else 0
    
    # 小指角度
    pinky_angle = calculate_angle(pinky_mcp, pinky_ip, pinky_tip)
    pinky_extended = pinky_angle > 160
    pinky_conf = min(max((pinky_angle - 160) / 20, 0), 0.99) if pinky_extended else 0
    
    # ====== 只识别单手指 ======
    # 统计伸直的手指数量
    extended_fingers = []
    if thumb_extended and thumb_conf >= CONFIDENCE_THRESHOLD:
        extended_fingers.append(("Thumb", thumb_conf))
    if index_extended and index_conf >= CONFIDENCE_THRESHOLD:
        extended_fingers.append(("Index", index_conf))
    if middle_extended and middle_conf >= CONFIDENCE_THRESHOLD:
        extended_fingers.append(("Middle", middle_conf))
    if ring_extended and ring_conf >= CONFIDENCE_THRESHOLD:
        extended_fingers.append(("Ring", ring_conf))
    if pinky_extended and pinky_conf >= CONFIDENCE_THRESHOLD:
        extended_fingers.append(("Pinky", pinky_conf))
    
    # 只返回单手指的情况
    if len(extended_fingers) == 1:
        finger_name, conf = extended_fingers[0]
        return (finger_name, round(conf, 2))
    
    # 零个或多个手指伸直
    return ("Unknown", 0.0)

def draw_chinese_text(img, text, position, color=(0, 255, 0)):
    """在图像上绘制中文"""
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 50)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 50)
        except:
            font = ImageFont.load_default()
    
    draw.text(position, text, font=font, fill=color)
    img[:] = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def main():
    print("="*50)
    print("单手指识别 (关节角度版)")
    print(f"目标: {UDP_HOST}:{UDP_PORT}")
    print("="*50)
    
    # 初始化MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils
    
    # 初始化UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("错误：无法打开摄像头")
        return
    
    print("程序运行中...")
    print("按 'q' 退出")
    
    frame_count = 0
    last_finger = "Unknown"
    finger_stable_count = 0
    
    while True:
        success, img = cap.read()
        if not success:
            continue
        
        frame_count += 1
        img = cv2.flip(img, 1)
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        
        finger = "Unknown"
        confidence = 0.0
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                finger, confidence = get_extended_finger(hand_landmarks.landmark)
                
                # ====== 时间平滑 ======
                gesture_buffer.append(finger)
                
                # 使用多数投票得到稳定结果（至少3帧一致）
                if len(gesture_buffer) >= 5:
                    # 统计各手势出现次数
                    counts = {}
                    for f in gesture_buffer:
                        counts[f] = counts.get(f, 0) + 1
                    # 找到出现最多的
                    max_count = max(counts.values())
                    if max_count >= 4:  # 8帧中至少4帧一致
                        finger = max(counts, key=counts.get)
                
                # 稳定检测
                if finger == last_finger and finger != "Unknown":
                    finger_stable_count += 1
                else:
                    finger_stable_count = 0
                last_finger = finger
                
                # 显示中文
                if finger != "Unknown":
                    chinese_name = FINGER_NAMES.get(finger, finger)
                    text = f"{chinese_name}: {confidence:.2f}"
                    color = (0, 255, 0)
                    draw_chinese_text(img, text, (10, 20), color)
                
                # 指尖画红点
                h, w, c = img.shape
                for id in [4, 8, 12, 16, 20]:
                    lm = hand_landmarks.landmark[id]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 8, (0, 0, 255), -1)
                
                # UDP发送
                if frame_count % 10 == 0 or finger_stable_count == 5:
                    if finger != "Unknown":
                        data = {
                            "finger": finger,
                            "confidence": round(confidence, 2),
                            "frame": frame_count,
                            "timestamp": time.time()
                        }
                        try:
                            sock.sendto(json.dumps(data).encode('utf-8'), 
                                       (UDP_HOST, UDP_PORT))
                            if DEBUG_MODE and finger_stable_count == 5:
                                print(f"[UDP发送] {finger} ({confidence:.2f})")
                        except Exception as e:
                            print(f"UDP发送错误: {e}")
        
        if finger == "Unknown":
            draw_chinese_text(img, "请伸出单根手指", (10, 20), (100, 100, 100))
        
        cv2.imshow("Single Finger Recognition", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    sock.close()
    print("程序结束")

if __name__ == '__main__':
    main()
