import math


class GestureClassifier:
    def __init__(self):
        self.FIST = "FIST"
        self.OPEN_PALM = "OPEN_PALM"
        self.POINT_INDEX = "POINT_INDEX"
        self.VICTORY = "VICTORY"
        self.THUMBS_UP = "THUMBS_UP"
        self.UNKNOWN = "UNKNOWN"

        self.debug = False

    def classify(self, features):
        fingers = features['fingers_extended']
        palm_span = features['palm_span']
        index_middle_distance = features.get('tip_distance_1_2', 0.0)

        thumb, index, middle, ring, pinky = fingers
        extended_count = sum(fingers)

        thumb_dist = features.get('thumb_tip_distance', 0.0)
        index_dist = features.get('index_tip_distance', 0.0)
        middle_dist = features.get('middle_tip_distance', 0.0)
        ring_dist = features.get('ring_tip_distance', 0.0)
        pinky_dist = features.get('pinky_tip_distance', 0.0)

        # Z坐标特征（新增）
        z_extends = features.get('z_extends', [0.0] * 5)
        index_z, middle_z, ring_z, pinky_z = z_extends[1], z_extends[2], z_extends[3], z_extends[4]
        index_z_minus_middle = features.get('index_z_minus_middle_z', 0.0)

        if self.debug:
            print(
                f"手指状态: {fingers}, "
                f"palm_span={palm_span:.3f}, "
                f"index_middle_distance={index_middle_distance:.3f}, "
                f"dist(index/middle/ring/pinky)=({index_dist:.3f}/{middle_dist:.3f}/{ring_dist:.3f}/{pinky_dist:.3f}), "
                f"Z(index/middle/ring/pinky)=({index_z:.3f}/{middle_z:.3f}/{ring_z:.3f}/{pinky_z:.3f})"
            )

        # 1. OPEN_PALM - 五指张开，手掌跨度大
        if extended_count >= 4 and palm_span > 0.35:
            return self.OPEN_PALM

        # 2. FIST - 拳头：多数手指收起，手掌跨度小
        if extended_count <= 1 and palm_span < 0.30:
            if not (
                index_dist > middle_dist + 0.20 and
                index_dist > ring_dist + 0.25 and
                index_dist > pinky_dist + 0.25
            ):
                return self.FIST

        # 3. VICTORY - 两指分开（食指+中指）
        # 关键区分：用Z坐标判断食指是否明显前伸
        # VICTORY时食指和中指几乎同高，POINT_INDEX时食指明显更前
        if index == 1 and middle == 1 and ring == 0 and pinky == 0:
            # Z坐标辅助：VICTORY时两根手指深度相近
            if abs(index_z - middle_z) < 0.08:
                return self.VICTORY
            # 也允许中指略微落后
            if index_z - middle_z > 0 and index_z - middle_z < 0.15:
                return self.VICTORY

        # 宽松VICTORY：允许无名指轻微弯曲
        if index == 1 and middle == 1 and (ring + pinky) <= 1:
            if index_middle_distance > 0.09:
                if abs(index_z - middle_z) < 0.12:
                    return self.VICTORY

        # 4. POINT_INDEX - 单食指前伸
        # 关键区分：食指的Z坐标明显小于其他手指（更前伸）
        # index_z_minus_middle > 0 表示食指比中指更靠前
        if thumb == 0 and index == 1 and middle == 0 and ring == 0 and pinky == 0:
            if index_z < middle_z - 0.05:  # 食指明显比中指前
                return self.POINT_INDEX

        # 宽松食指判断
        if index == 1 and middle == 0 and ring == 0 and pinky == 0:
            # 食指距离必须明显大于其他手指
            if index_dist > middle_dist + 0.22 and index_dist > ring_dist + 0.30:
                # Z坐标验证：食指前伸程度要明显
                if index_z > middle_z + 0.05:
                    return self.POINT_INDEX
                # 或者食指异常突出
                if index_dist > 0.65:
                    return self.POINT_INDEX

        # 几何兜底：即使fingers_extended不稳定，只要食指异常突出+Z坐标验证
        if index_dist > 0.65 and index_dist > middle_dist + 0.30:
            if index_z > middle_z + 0.08:
                return self.POINT_INDEX

        # 5. THUMBS_UP - 点赞：只有拇指伸直
        if thumb == 1 and middle == 0 and ring == 0 and pinky == 0:
            # 食指不能太前伸（否则更像POINT_INDEX）
            if not (index == 1 and index_dist > middle_dist + 0.22):
                return self.THUMBS_UP

        # 典型点赞兜底
        if fingers == [1, 0, 0, 0, 0]:
            if not (index_dist > 0.65 and index_dist > middle_dist + 0.25):
                return self.THUMBS_UP

        return self.UNKNOWN

    def get_gesture_id(self, gesture_name):
        gesture_to_id = {
            self.FIST: 0,
            self.OPEN_PALM: 1,
            self.POINT_INDEX: 2,
            self.VICTORY: 3,
            self.THUMBS_UP: 4,
            self.UNKNOWN: 5
        }
        return gesture_to_id.get(gesture_name, 5)

    def get_gesture_name(self, gesture_id):
        id_to_gesture = {
            0: self.FIST,
            1: self.OPEN_PALM,
            2: self.POINT_INDEX,
            3: self.VICTORY,
            4: self.THUMBS_UP,
            5: self.UNKNOWN
        }
        return id_to_gesture.get(gesture_id, self.UNKNOWN)
