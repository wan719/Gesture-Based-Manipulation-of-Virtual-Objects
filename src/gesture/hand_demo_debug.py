import cv2
import mediapipe as mp
import sys

print("="*50)
print("开始运行手势识别程序")
print("Python版本:", sys.version)
print("OpenCV版本:", cv2.__version__)
print("MediaPipe版本:", mp.__version__)
print("="*50)

# 初始化MediaPipe Hands
print("正在初始化MediaPipe Hands...")
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils
print("MediaPipe初始化完成")

# 打开摄像头
print("正在尝试打开摄像头...")
cap = cv2.VideoCapture(0)

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("错误：无法打开摄像头！")
    print("可能的原因：")
    print("1. 摄像头被其他程序占用（如Zoom、浏览器）")
    print("2. 摄像头驱动有问题")
    print("3. 摄像头索引不对，尝试改成 cap = cv2.VideoCapture(1)")
    input("按回车键退出...")
    exit()

print("摄像头打开成功！")
print("按 'q' 退出程序")
print("等待摄像头画面...")

frame_count = 0
while True:
    # 读取一帧
    success, img = cap.read()
    
    if not success:
        print(f"警告：读取第{frame_count}帧失败")
        continue
    
    frame_count += 1
    if frame_count % 30 == 0:  # 每30帧打印一次状态
        print(f"正在运行... 已处理{frame_count}帧")
    
    # 转换为RGB（MediaPipe需要）
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 处理手部检测
    results = hands.process(img_rgb)
    
    # 如果检测到手
    if results.multi_hand_landmarks:
        # 在画面左上角显示"检测到手"
        cv2.putText(img, "Hand Detected!", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
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
                    
                # 可选：在关键点上标数字（调试用）
                # cv2.putText(img, str(id), (cx-5, cy-5), 
                #            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
    
    # 显示画面
    cv2.imshow("Hand Tracking", img)
    
    # 检查窗口是否被关闭
    if cv2.getWindowProperty("Hand Tracking", cv2.WND_PROP_VISIBLE) < 1:
        print("窗口被关闭")
        break
    
    # 按'q'退出
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("用户按q退出")
        break
    elif key == ord('p'):  # 按p暂停
        print("程序暂停，按任意键继续...")
        cv2.waitKey(0)

print("正在释放资源...")
cap.release()
cv2.destroyAllWindows()
print("程序正常结束")
input("按回车键关闭窗口...")