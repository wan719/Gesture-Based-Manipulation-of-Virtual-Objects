import math
from collections import deque


class FeatureExtractor:
    def __init__(self, smooth_window=3):
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

        # 时序平滑
        self.smooth_window = smooth_window
        self._fingers_history = deque(maxlen=smooth_window)

        # 上一次平滑后的手指状态
        self._last_smoothed_fingers = None

    def calculate_distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def calculate_3d_distance(self, p1, p2):
        """计算3D欧氏距离（使用x, y, z坐标）"""
        return math.sqrt(
            (p1.x - p2.x) ** 2 +
            (p1.y - p2.y) ** 2 +
            (p1.z - p2.z) ** 2
        )

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

    def calculate_3d_angle(self, p1, p2, p3):
        """计算3D空间三点夹角，p2为顶点"""
        v1 = (p1.x - p2.x, p1.y - p2.y, p1.z - p2.z)
        v2 = (p3.x - p2.x, p3.y - p2.y, p3.z - p2.z)

        dot_product = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
        len_v1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2 + v1[2] ** 2)
        len_v2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2 + v2[2] ** 2)

        if len_v1 == 0 or len_v2 == 0:
            return 0

        cos_angle = dot_product / (len_v1 * len_v2)
        cos_angle = max(-1, min(1, cos_angle))
        angle_rad = math.acos(cos_angle)
        return math.degrees(angle_rad)

    def _get_finger_z_extended(self, hand_landmarks, tip_id, mcp_id):
        """
        利用Z坐标判断手指是否前伸：
        返回指尖相对于手腕的Z轴突出程度
        正值表示指尖在手掌前方（伸出），负值表示在后方（收起）
        """
        wrist = hand_landmarks.landmark[0]
        tip = hand_landmarks.landmark[tip_id]
        mcp = hand_landmarks.landmark[mcp_id]

        # 用MCP的Z作为基准（手掌平面），指尖的Z差值反映前后深度
        # 考虑到摄像头视角，Z越小（更负/更前）表示越伸出
        return wrist.z - tip.z  # 差值越大说明指尖越前伸

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
        改进的大拇指判断：
        综合角度、距离和Z坐标：
        1. thumb_mcp-thumb_ip-thumb_tip 的弯曲角度
        2. 指尖到食指根部的距离
        3. Z坐标深度（拇指是否明显前伸）
        """
        thumb_cmc = hand_landmarks.landmark[1]
        thumb_mcp = hand_landmarks.landmark[2]
        thumb_ip = hand_landmarks.landmark[3]
        thumb_tip = hand_landmarks.landmark[4]

        index_mcp = hand_landmarks.landmark[5]
        wrist = hand_landmarks.landmark[0]

        angle1 = self.calculate_angle(thumb_cmc, thumb_mcp, thumb_ip)
        angle2 = self.calculate_angle(thumb_mcp, thumb_ip, thumb_tip)

        tip_to_index_mcp = self.calculate_distance(thumb_tip, index_mcp)
        ip_to_index_mcp = self.calculate_distance(thumb_ip, index_mcp)

        # Z坐标辅助：拇指前伸时，tip的z应该比ip的z更小（更靠近摄像头/更前）
        thumb_z_extend = self._get_finger_z_extended(hand_landmarks, 4, 1)

        # 条件解释：
        # 1. 两个角度都较大，说明拇指比较直
        # 2. 指尖比IP关节离食指根部更远，说明拇指是"伸出去"的
        # 3. Z坐标前伸量 > 0.05 表示拇指明显前伸
        if angle1 > 135 and angle2 > 145 and tip_to_index_mcp > ip_to_index_mcp:
            if thumb_z_extend > 0.02:  # Z坐标辅助验证
                return 1
            # 放宽条件：如果距离足够大也认为伸直
            if tip_to_index_mcp > 0.25:
                return 1
        return 0

    def _smooth_fingers(self, fingers):
        """
        时序平滑：对fingers_extended进行滑动平均
        减少因单帧抖动导致的误判
        """
        self._fingers_history.append(fingers)
        if len(self._fingers_history) < 2:
            return fingers

        # 对每个手指位置做多数投票
        smoothed = []
        for i in range(5):
            votes = [frame[i] for frame in self._fingers_history]
            smoothed.append(1 if sum(votes) > len(votes) / 2 else 0)
        return smoothed

    def extract_features(self, hand_landmarks, use_smooth=True):
        features = {}

        # 1. 指尖到手腕距离（2D）
        wrist = hand_landmarks.landmark[0]
        for i, tip_id in enumerate(self.fingertip_ids):
            tip = hand_landmarks.landmark[tip_id]
            distance = self.calculate_distance(wrist, tip)
            features[f'{self.finger_names[i]}_tip_distance'] = distance

        # 1b. 指尖到手腕距离（3D）- 新增
        for i, tip_id in enumerate(self.fingertip_ids):
            tip = hand_landmarks.landmark[tip_id]
            distance_3d = self.calculate_3d_distance(wrist, tip)
            features[f'{self.finger_names[i]}_tip_distance_3d'] = distance_3d

        # 2. 每根手指弯曲角度
        for finger_name, indices in self.finger_indices.items():
            if len(indices) >= 3:
                p1 = hand_landmarks.landmark[indices[-1]]
                p2 = hand_landmarks.landmark[indices[-2]]
                p3 = hand_landmarks.landmark[indices[-3]]
                angle = self.calculate_angle(p1, p2, p3)
                features[f'{finger_name}_bend_angle'] = angle

        # 3. Z坐标特征 - 新增：每根手指前伸程度
        z_extends = []
        z_mcp_ids = [1, 5, 9, 13, 17]  # 各手指MCP节点
        for i, (tip_id, mcp_id) in enumerate(zip(self.fingertip_ids, z_mcp_ids)):
            z_extend = self._get_finger_z_extended(hand_landmarks, tip_id, mcp_id)
            z_extends.append(z_extend)
            features[f'{self.finger_names[i]}_z_extend'] = z_extend
        features['z_extends'] = z_extends

        # 4. 综合手指状态（带时序平滑）
        fingers_extended = self._compute_fingers_extended(hand_landmarks)

        if use_smooth:
            fingers_extended = self._smooth_fingers(fingers_extended)

        self._last_smoothed_fingers = fingers_extended
        features['fingers_extended'] = fingers_extended

        # 5. 相邻指尖距离
        for i in range(4):
            tip1 = hand_landmarks.landmark[self.fingertip_ids[i]]
            tip2 = hand_landmarks.landmark[self.fingertip_ids[i + 1]]
            distance = self.calculate_distance(tip1, tip2)
            features[f'tip_distance_{i}_{i+1}'] = distance

        # 6. 手掌跨度
        thumb_tip = hand_landmarks.landmark[4]
        pinky_tip = hand_landmarks.landmark[20]
        features['palm_span'] = self.calculate_distance(thumb_tip, pinky_tip)

        # 7. 食指与中指的Z差值 - 用于区分POINT_INDEX和VICTORY
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        features['index_z_minus_middle_z'] = index_tip.z - middle_tip.z

        return features

    def _compute_fingers_extended(self, hand_landmarks):
        """计算手指伸直状态（不含平滑）"""
        fingers_extended = []

        # 拇指
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

        return fingers_extended

    def get_last_smoothed_fingers(self):
        """获取最近一次平滑后的手指状态"""
        return self._last_smoothed_fingers

    def reset_smooth(self):
        """重置时序平滑历史"""
        self._fingers_history.clear()
        self._last_smoothed_fingers = None

    def print_features(self, features):
        print("\n=== 手部特征 ===")
        fingers = features['fingers_extended']
        print(f"手指状态: {fingers}")
        print(f"手掌跨度: {features['palm_span']:.3f}")
        if 'z_extends' in features:
            print(f"Z轴前伸: {[f'{z:.3f}' for z in features['z_extends']]}")
        for name in self.finger_names:
            angle_key = f'{name}_bend_angle'
            if angle_key in features:
                print(f"{name}弯曲角度: {features[angle_key]:.1f}°")
