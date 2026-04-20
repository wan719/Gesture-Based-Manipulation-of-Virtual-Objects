#!/usr/bin/env python3
"""
手势识别 + UDP 发送端
使用 MediaPipe Hands + 改进的手势分类算法
"""

import cv2
import mediapipe as mp
import socket
import json
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ============ 配置 ============
UDP_HOST = '127.0.0.1'
UDP_PORT = 8888
DEBUG_MODE = True

# 关键点索引
THUMB_TIP, THUMB_IP, THUMB_MCP = 4, 3, 1
INDEX_TIP, INDEX_IP, INDEX_MCP = 8, 7, 5
MIDDLE_TIP, MIDDLE_IP, MIDDLE_MCP = 12, 11, 9
RING_TIP, RING_IP, RING_MCP = 16, 15, 13
PINKY_TIP, PINKY_IP, PINKY_MCP = 20, 19, 17
WRIST = 0

# 手势名称中英文映射
GESTURE_NAMES = {
    "Thumb_Up": "点赞",
    "Open_Palm": "手掌",
    "Pointing_Up": "指向",
    "Victory": "剪刀",
    "Rock": "石头",
    "ILoveYou": "我爱你",
    "Peace": "和平",
    "Heart": "比心",
    "Ok": "OK",
    "Fist": "拳头",
    "Unknown": "未知"
}

def draw_chinese_text(img, text, position, color=(0, 255, 0)):
    """在图像上绘制中文"""
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # 尝试加载中文字体
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 50)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 50)
        except:
            font = ImageFont.load_default()
    
    draw.text(position, text, font=font, fill=color)
    img[:] = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def get_finger_states(landmarks):
    """获取各手指状态"""
    # 指尖和基关节的位置
    fingers = {
        'thumb': {'tip': landmarks[THUMB_TIP], 'ip': landmarks[THUMB_IP], 'mcp': landmarks[THUMB_MCP]},
        'index': {'tip': landmarks[INDEX_TIP], 'ip': landmarks[INDEX_IP], 'mcp': landmarks[INDEX_MCP]},
        'middle': {'tip': landmarks[MIDDLE_TIP], 'ip': landmarks[MIDDLE_IP], 'mcp': landmarks[MIDDLE_MCP]},
        'ring': {'tip': landmarks[RING_TIP], 'ip': landmarks[RING_IP], 'mcp': landmarks[RING_MCP]},
        'pinky': {'tip': landmarks[PINKY_TIP], 'ip': landmarks[PINKY_IP], 'mcp': landmarks[PINKY_MCP]}
    }
    
    states = {}
    
    # 拇指：判断是否向侧面伸直
    thumb_tip = fingers['thumb']['tip']
    thumb_mcp = fingers['thumb']['mcp']
    wrist = landmarks[WRIST]
    
    # 拇指横向判断（区分左右手）
    handedness = "Right" if thumb_tip.x < 0.5 else "Left"
    if handedness == "Right":
        states['thumb'] = thumb_tip.x > wrist.x + 0.05  # 拇指在手腕右侧
    else:
        states['thumb'] = thumb_tip.x < wrist.x - 0.05  # 拇指在手腕左侧
    
    # 其他手指：判断是否向上伸直（指尖y < 基关节y）
    for name in ['index', 'middle', 'ring', 'pinky']:
        tip = fingers[name]['tip']
        mcp = fingers[name]['mcp']
        # 加上ip关节的二次确认
        ip = fingers[name]['ip']
        states[name] = tip.y < mcp.y and tip.y < ip.y
    
    return states, handedness

def calculate_distance(p1, p2):
    """计算两点欧氏距离"""
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def recognize_gesture(landmarks):
    """
    使用改进的算法识别手势
    返回: (手势名称, 置信度)
    """
    states, handedness = get_finger_states(landmarks)
    
    fingers_extended = [states['index'], states['middle'], states['ring'], states['pinky']]
    extended_count = sum(fingers_extended)
    
    # 提取关键点
    thumb_tip = landmarks[THUMB_TIP]
    index_tip = landmarks[INDEX_TIP]
    middle_tip = landmarks[MIDDLE_TIP]
    ring_tip = landmarks[RING_TIP]
    pinky_tip = landmarks[PINKY_TIP]
    index_mcp = landmarks[INDEX_MCP]
    wrist = landmarks[WRIST]
    
    # 1. 点赞 (Thumb Up) - 拇指伸直，其他手指弯曲
    if states['thumb'] and not states['index'] and not states['middle']:
        if not states['ring'] and not states['pinky']:
            return ("Thumb_Up", 0.95)
    
    # 2. 拳头 (Fist) - 所有手指弯曲
    if not any(fingers_extended):
        return ("Fist", 0.90)
    
    # 3. 手掌 (Open Palm) - 所有手指伸直
    if all(fingers_extended):
        # 检查手指之间有间隙
        gap1 = calculate_distance(index_tip, middle_tip)
        gap2 = calculate_distance(middle_tip, ring_tip)
        gap3 = calculate_distance(ring_tip, pinky_tip)
        if gap1 > 0.05 and gap2 > 0.05 and gap3 > 0.05:
            return ("Open_Palm", 0.90)
    
    # 4. 剪刀 (Victory) - 食指和中指伸直，其他弯曲
    if states['index'] and states['middle'] and not states['ring'] and not states['pinky']:
        # 检查两根手指有分叉
        gap = calculate_distance(index_tip, middle_tip)
        if gap > 0.03:
            return ("Victory", 0.92)
    
    # 5. 指向 (Pointing Up) - 只有食指伸直
    if states['index'] and not states['middle'] and not states['ring'] and not states['pinky']:
        # 食指明显比其他手指高
        if index_tip.y < middle_tip.y - 0.05:
            return ("Pointing_Up", 0.88)
    
    # 6. 石头 (Rock) - 拇指和食指伸直形成L形
    if states['thumb'] and states['index'] and not states['middle'] and not states['ring']:
        if not states['pinky']:
            return ("Rock", 0.85)
    
    # 7. OK手势 - 拇指和食指相碰形成圆圈
    ok_dist = calculate_distance(thumb_tip, index_tip)
    if ok_dist < 0.05 and not states['middle'] and not states['ring'] and not states['pinky']:
        return ("Ok", 0.88)
    
    # 8. 比心 (Heart) - 拇指和食指相碰，其他手指伸直
    if ok_dist < 0.06 and states['middle'] and states['ring'] and states['pinky']:
        return ("Heart", 0.82)
    
    # 9. 数字2 (Peace) - 食指和中指伸直（类似剪刀但无名指小指可伸可屈）
    if states['index'] and states['middle'] and not states['ring'] and not states['pinky']:
        return ("Peace", 0.85)
    
    # 10. 我爱你 (ILoveYou) - 拇指、小指伸直，食指中指无名指弯曲
    if states['thumb'] and not states['index'] and not states['middle'] and not states['ring'] and states['pinky']:
        return ("ILoveYou", 0.80)
    
    return ("Unknown", 0.0)

def main():
    print("="*50)
    print("手势识别 + UDP 发送端 (改进算法)")
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
    last_gesture = "none"
    gesture_stable_count = 0
    
    while True:
        success, img = cap.read()
        if not success:
            continue
        
        frame_count += 1
        img = cv2.flip(img, 1)
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        
        gesture = "Unknown"
        confidence = 0.0
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                gesture, confidence = recognize_gesture(hand_landmarks.landmark)
                
                # 稳定检测
                if gesture == last_gesture and gesture != "Unknown":
                    gesture_stable_count += 1
                else:
                    gesture_stable_count = 0
                last_gesture = gesture
                
                # 显示中文
                if gesture != "Unknown":
                    chinese_name = GESTURE_NAMES.get(gesture, gesture)
                    text = f"{chinese_name}: {confidence:.2f}"
                    color = (0, 255, 0) if confidence > 0.7 else (0, 165, 255)
                    draw_chinese_text(img, text, (10, 20), color)
                
                # 指尖画红点
                h, w, c = img.shape
                for id in [4, 8, 12, 16, 20]:
                    lm = hand_landmarks.landmark[id]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 8, (0, 0, 255), -1)
                
                # UDP发送
                if frame_count % 10 == 0 or gesture_stable_count == 5:
                    if gesture != "Unknown":
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
        
        if gesture == "Unknown":
            draw_chinese_text(img, "未识别", (10, 20), (100, 100, 100))
        
        cv2.imshow("Gesture Recognition", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    sock.close()
    print("程序结束")

if __name__ == '__main__':
    main()
