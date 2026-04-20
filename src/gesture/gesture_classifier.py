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

        if self.debug:
            print(
                f"手指状态: {fingers}, "
                f"palm_span={palm_span:.3f}, "
                f"index_middle_distance={index_middle_distance:.3f}, "
                f"dist(index/middle/ring/pinky)=({index_dist:.3f}/{middle_dist:.3f}/{ring_dist:.3f}/{pinky_dist:.3f})"
            )

        # 1. OPEN_PALM
        if extended_count >= 4 and palm_span > 0.35:
            return self.OPEN_PALM

        # 2. FIST
        # 拳头时各指通常都不突出，手掌跨度较小
        if extended_count <= 1 and palm_span < 0.30:
            # 若食指没有明显突出，则判拳头
            if not (
                index_dist > middle_dist + 0.20 and
                index_dist > ring_dist + 0.25 and
                index_dist > pinky_dist + 0.25
            ):
                return self.FIST

        # 3. VICTORY
        if index == 1 and middle == 1 and ring == 0 and pinky == 0 and index_middle_distance > 0.08:
            return self.VICTORY

        if index == 1 and middle == 1 and (ring + pinky) <= 1 and index_middle_distance > 0.09:
            return self.VICTORY

        # 4. POINT_INDEX
        # 这是你现在最需要加强的
        # 标准食指：[0,1,0,0,0]
        if (
            thumb == 0 and
            index == 1 and
            middle == 0 and
            ring == 0 and
            pinky == 0 and
            index_dist > middle_dist + 0.25 and
            index_dist > ring_dist + 0.35 and
            index_dist > pinky_dist + 0.35
        ):
            return self.POINT_INDEX

        # 宽松食指：允许拇指偶尔误判为1，但食指必须非常突出
        if (
            index == 1 and
            middle == 0 and
            ring == 0 and
            pinky == 0 and
            index_dist > middle_dist + 0.22 and
            index_dist > ring_dist + 0.30 and
            index_dist > pinky_dist + 0.30 and
            index_middle_distance > 0.20
        ):
            return self.POINT_INDEX

        # 几何兜底：即使 fingers_extended 没完全稳定，只要食指异常突出也算
        if (
            index_dist > 0.65 and
            index_dist > middle_dist + 0.30 and
            index_dist > ring_dist + 0.40 and
            index_dist > pinky_dist + 0.40
        ):
            return self.POINT_INDEX

        # 5. THUMBS_UP
        # 放在 POINT_INDEX 后面，避免食指再被吃掉
        if thumb == 1 and middle == 0 and ring == 0 and pinky == 0:
            # 如果食指没有非常突出，则更像点赞
            if not (
                index == 1 and
                index_dist > middle_dist + 0.22 and
                index_dist > ring_dist + 0.30 and
                index_dist > pinky_dist + 0.30
            ):
                return self.THUMBS_UP

        # 典型点赞兜底：[1,0,0,0,0]
        if fingers == [1, 0, 0, 0, 0]:
            # 食指不够夸张突出时，优先判点赞
            if not (
                index_dist > 0.65 and
                index_dist > middle_dist + 0.25 and
                index_dist > ring_dist + 0.35 and
                index_dist > pinky_dist + 0.35
            ):
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