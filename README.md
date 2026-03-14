# Gesture-Based-Manipulation-of-Virtual-Objects
# HandPilot：基于手势识别的虚拟机械狗交互控制系统

## 项目简介
通过摄像头实时识别手势，控制虚拟机械狗做出蹲下、前进、后退等动作。

## 技术栈
- 手势识别：MediaPipe Hands + Python
- 虚拟狗控制：Unity 3D + C#
- 通信：UDP Socket

## 快速开始
```bash
pip install opencv-python mediapipe numpy
python hand_demo.py
