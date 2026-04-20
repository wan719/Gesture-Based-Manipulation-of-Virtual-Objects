import math


class FeatureExtractor:
    def __init__(self):
        # 每根手指关键点
        self.finger_indices = {
            'thumb': [1, 2, 3, 4],
            'index': [5, 6, 7, 8],
            'middle': [9, 10, 11, 12],
            'ring': [13, 14, 15, 16],
            'pinky': [17, 18, 19, 20]
        }

        self.fingertip_ids = [4, 8, 12, 16, 20]
        self.finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']

    def calculate_distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def calculate_angle(self, p1, p2, p3):
        """
        计算三点夹角，p2 为顶点
        """
        v1 = (p1.x - p2.x, p1.y - p2.y)
        v2 = (p3.x - p2.x, p3.y - p2.y)

        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        len_v1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
        len_v2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

        if len_v1 == 0 or len_v2 == 0:
            return 0

        cos_angle = dot_product / (len_v1 * len_v2)
        cos_angle = max(-1, min(1, cos_angle))
        angle_rad = math.acos(cos_angle)
        return math.degrees(angle_rad)

    def is_finger_extended_by_angle(self, hand_landmarks, mcp_id, pip_id, dip_id, tip_id, angle_threshold=150):
        """
        用关节角度判断手指是否伸直
        """
        mcp = hand_landmarks.landmark[mcp_id]
        pip = hand_landmarks.landmark[pip_id]
        dip = hand_landmarks.landmark[dip_id]
        tip = hand_landmarks.landmark[tip_id]

        angle1 = self.calculate_angle(mcp, pip, dip)
        angle2 = self.calculate_angle(pip, dip, tip)

        # 两个关节都比较直，认为手指伸直
        return 1 if angle1 > angle_threshold and angle2 > angle_threshold else 0

    def is_thumb_extended(self, hand_landmarks):
        """
        更稳的大拇指判断：
        不再直接看 x 的方向，而是综合：
        1. thumb_mcp-thumb_ip-thumb_tip 的弯曲角度
        2. 指尖到食指根部的距离是否足够大
        """
        thumb_cmc = hand_landmarks.landmark[1]
        thumb_mcp = hand_landmarks.landmark[2]
        thumb_ip = hand_landmarks.landmark[3]
        thumb_tip = hand_landmarks.landmark[4]

        index_mcp = hand_landmarks.landmark[5]

        angle1 = self.calculate_angle(thumb_cmc, thumb_mcp, thumb_ip)
        angle2 = self.calculate_angle(thumb_mcp, thumb_ip, thumb_tip)

        tip_to_index_mcp = self.calculate_distance(thumb_tip, index_mcp)
        ip_to_index_mcp = self.calculate_distance(thumb_ip, index_mcp)

        # 条件解释：
        # 1. 两个角度都较大，说明拇指比较直
        # 2. 指尖比 IP 关节离食指根部更远，说明拇指是“伸出去”的
        if angle1 > 135 and angle2 > 145 and tip_to_index_mcp > ip_to_index_mcp:
            return 1
        return 0

    def extract_features(self, hand_landmarks):
        features = {}

        # 1. 指尖到手腕距离
        wrist = hand_landmarks.landmark[0]
        for i, tip_id in enumerate(self.fingertip_ids):
            tip = hand_landmarks.landmark[tip_id]
            distance = self.calculate_distance(wrist, tip)
            features[f'{self.finger_names[i]}_tip_distance'] = distance

        # 2. 每根手指弯曲角度
        for finger_name, indices in self.finger_indices.items():
            if len(indices) >= 3:
                p1 = hand_landmarks.landmark[indices[-1]]
                p2 = hand_landmarks.landmark[indices[-2]]
                p3 = hand_landmarks.landmark[indices[-3]]
                angle = self.calculate_angle(p1, p2, p3)
                features[f'{finger_name}_bend_angle'] = angle

        # 3. 判断每根手指是否伸直
        fingers_extended = []

        # 拇指：单独处理
        thumb_extended = self.is_thumb_extended(hand_landmarks)
        fingers_extended.append(thumb_extended)

        # 食指
        index_extended = self.is_finger_extended_by_angle(hand_landmarks, 5, 6, 7, 8)
        fingers_extended.append(index_extended)

        # 中指
        middle_extended = self.is_finger_extended_by_angle(hand_landmarks, 9, 10, 11, 12)
        fingers_extended.append(middle_extended)

        # 无名指
        ring_extended = self.is_finger_extended_by_angle(hand_landmarks, 13, 14, 15, 16)
        fingers_extended.append(ring_extended)

        # 小指
        pinky_extended = self.is_finger_extended_by_angle(hand_landmarks, 17, 18, 19, 20)
        fingers_extended.append(pinky_extended)

        features['fingers_extended'] = fingers_extended

        # 4. 相邻指尖距离
        for i in range(4):
            tip1 = hand_landmarks.landmark[self.fingertip_ids[i]]
            tip2 = hand_landmarks.landmark[self.fingertip_ids[i + 1]]
            distance = self.calculate_distance(tip1, tip2)
            features[f'tip_distance_{i}_{i+1}'] = distance

        # 5. 手掌跨度
        thumb_tip = hand_landmarks.landmark[4]
        pinky_tip = hand_landmarks.landmark[20]
        features['palm_span'] = self.calculate_distance(thumb_tip, pinky_tip)

        return features

    def print_features(self, features):
        print("\n=== 手部特征 ===")
        print(f"手指状态: {features['fingers_extended']}")
        print(f"手掌跨度: {features['palm_span']:.3f}")
        for name in self.finger_names:
            angle_key = f'{name}_bend_angle'
            if angle_key in features:
                print(f"{name}弯曲角度: {features[angle_key]:.1f}°")