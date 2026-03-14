"""
feature_extractor.py - 特征提取模块
功能：从21个关键点中提取用于手势识别的特征
"""

import math

class FeatureExtractor:
    def __init__(self):
        # 手指定义：每根手指的关键点ID
        self.finger_indices = {
            'thumb': [1, 2, 3, 4],      # 拇指：掌骨、近节、远节、指尖
            'index': [5, 6, 7, 8],       # 食指：掌骨、近节、远节、指尖
            'middle': [9, 10, 11, 12],   # 中指
            'ring': [13, 14, 15, 16],    # 无名指
            'pinky': [17, 18, 19, 20]    # 小指
        }
        
        # 指尖ID
        self.fingertip_ids = [4, 8, 12, 16, 20]
        # 手指名称
        self.finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
    
    def calculate_distance(self, p1, p2):
        """计算两点之间的欧氏距离"""
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
    
    def calculate_angle(self, p1, p2, p3):
        """
        计算三点之间的角度（以p2为顶点）
        返回角度值（度）
        """
        # 向量 p2p1 和 p2p3
        v1 = (p1.x - p2.x, p1.y - p2.y)
        v2 = (p3.x - p2.x, p3.y - p2.y)
        
        # 计算点积
        dot_product = v1[0]*v2[0] + v1[1]*v2[1]
        
        # 计算模长
        len_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
        len_v2 = math.sqrt(v2[0]**2 + v2[1]**2)
        
        # 避免除零
        if len_v1 == 0 or len_v2 == 0:
            return 0
        
        # 计算角度（弧度转角度）
        cos_angle = dot_product / (len_v1 * len_v2)
        # 处理浮点误差
        cos_angle = max(-1, min(1, cos_angle))
        angle_rad = math.acos(cos_angle)
        angle_deg = math.degrees(angle_rad)
        
        return angle_deg
    
    def extract_features(self, hand_landmarks):
        """
        从手部关键点提取所有特征
        
        Args:
            hand_landmarks: MediaPipe返回的21个关键点
            
        Returns:
            dict: 包含各种特征的字典
        """
        features = {}
        
        # 1. 计算指尖到手腕的距离（归一化）
        wrist = hand_landmarks.landmark[0]
        for i, tip_id in enumerate(self.fingertip_ids):
            tip = hand_landmarks.landmark[tip_id]
            distance = self.calculate_distance(wrist, tip)
            features[f'{self.finger_names[i]}_tip_distance'] = distance
        
        # 2. 计算每根手指的弯曲角度
        # 食指、中指、无名指、小指：计算指尖-中间关节-根部关节的角度
        for finger_name, indices in self.finger_indices.items():
            if len(indices) >= 3:
                p1 = hand_landmarks.landmark[indices[-1]]  # 指尖
                p2 = hand_landmarks.landmark[indices[-2]]  # 中间关节
                p3 = hand_landmarks.landmark[indices[-3]]  # 根部关节
                angle = self.calculate_angle(p1, p2, p3)
                features[f'{finger_name}_bend_angle'] = angle
        
        # 3. 判断每根手指是否伸直（布尔值）
        fingers_extended = []
        
        # 大拇指特殊处理（比较x坐标）
        thumb_tip = hand_landmarks.landmark[4]
        thumb_ip = hand_landmarks.landmark[3]  # 拇指远节
        if thumb_tip.x > thumb_ip.x:  # 假设右手，左手会相反
            fingers_extended.append(1)
        else:
            fingers_extended.append(0)
        
        # 其他四指：比较指尖和指根的y坐标
        for tip_id in [8, 12, 16, 20]:
            tip = hand_landmarks.landmark[tip_id]
            pip = hand_landmarks.landmark[tip_id - 2]  # 近端指间关节
            if tip.y < pip.y:  # y越小越高（图像坐标系原点在左上角）
                fingers_extended.append(1)
            else:
                fingers_extended.append(0)
        
        features['fingers_extended'] = fingers_extended
        
        # 4. 计算指尖间的距离（判断手指分开程度）
        for i in range(4):  # 相邻指尖的距离
            tip1 = hand_landmarks.landmark[self.fingertip_ids[i]]
            tip2 = hand_landmarks.landmark[self.fingertip_ids[i+1]]
            distance = self.calculate_distance(tip1, tip2)
            features[f'tip_distance_{i}_{i+1}'] = distance
        
        # 5. 计算手掌张开程度（拇指尖到小指尖的距离）
        thumb_tip = hand_landmarks.landmark[4]
        pinky_tip = hand_landmarks.landmark[20]
        features['palm_span'] = self.calculate_distance(thumb_tip, pinky_tip)
        
        return features
    
    def print_features(self, features):
        """打印特征（调试用）"""
        print("\n=== 手部特征 ===")
        print(f"手指状态: {features['fingers_extended']}")
        print(f"手掌跨度: {features['palm_span']:.3f}")
        for name in self.finger_names:
            angle_key = f'{name}_bend_angle'
            if angle_key in features:
                print(f"{name}弯曲角度: {features[angle_key]:.1f}°")
