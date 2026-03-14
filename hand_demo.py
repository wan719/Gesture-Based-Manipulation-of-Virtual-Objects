import cv2
import mediapipe as mp

# 初始化MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# 打开摄像头
cap = cv2.VideoCapture(0)
print("按 'q' 退出")

while True:
    success, img = cap.read()
    if not success:
        break
    
    # 转换为RGB（MediaPipe需要）
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    # 如果检测到手
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 画出手部骨架
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # 获取21个关键点的坐标
            h, w, c = img.shape
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                # 在指尖画个大红点（指尖ID：4,8,12,16,20）
                if id in [4, 8, 12, 16, 20]:
                    cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)
    
    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()