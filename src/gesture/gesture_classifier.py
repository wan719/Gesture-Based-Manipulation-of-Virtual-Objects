"""
gesture_classifier.py - 手势分类器
功能：基于特征用规则判断识别5种手势
"""

class GestureClassifier:
    def __init__(self):
        # 手势常量
        self.FIST = "FIST"              # 握拳
        self.OPEN_PALM = "OPEN_PALM"    # 手掌张开
        self.POINT_INDEX = "POINT_INDEX" # 食指指向
        self.VICTORY = "VICTORY"         # 剪刀手
        self.THUMBS_UP = "THUMBS_UP"     # 点赞
        self.UNKNOWN = "UNKNOWN"         # 未知
        
        # 调试模式
        self.debug = False
    
    def classify(self, features):
        """
        根据特征识别手势
        
        Args:
            features: feature_extractor返回的特征字典
            
        Returns:
            str: 手势名称
        """
        fingers = features['fingers_extended']
        palm_span = features['palm_span']
        
        if self.debug:
            print(f"手指状态: {fingers}")
        
        # 规则1：握拳 - 所有手指都弯曲
        if fingers == [0, 0, 0, 0, 0]:
            return self.FIST
        
        # 规则2：手掌张开 - 所有手指都伸直
        elif fingers == [1, 1, 1, 1, 1]:
            # 再检查一下手掌跨度，确保不是半握拳
            if palm_span > 0.4:  # 阈值需要根据实际调整
                return self.OPEN_PALM
            else:
                return self.UNKNOWN
        
        # 规则3：食指指向 - 只有食指伸直
        elif fingers == [0, 1, 0, 0, 0]:
            return self.POINT_INDEX
        
        # 规则4：剪刀手 - 食指和中指伸直
        elif fingers == [0, 1, 1, 0, 0]:
            return self.VICTORY
        
        # 规则5：点赞 - 大拇指伸直，其他弯曲
        elif fingers == [1, 0, 0, 0, 0]:
            return self.THUMBS_UP
        
        # 其他情况
        else:
            return self.UNKNOWN
    
    def get_gesture_id(self, gesture_name):
        """将手势名称转换为ID（用于UDP通信）"""
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
        """将手势ID转换为名称"""
        id_to_gesture = {
            0: self.FIST,
            1: self.OPEN_PALM,
            2: self.POINT_INDEX,
            3: self.VICTORY,
            4: self.THUMBS_UP,
            5: self.UNKNOWN
        }
        return id_to_gesture.get(gesture_id, self.UNKNOWN)
