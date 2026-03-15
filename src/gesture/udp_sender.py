"""
udp_sender.py - UDP通信发送模块
功能：将识别到的手势通过UDP发送给Unity
"""

import socket
import json
import time

class UDPSender:
    def __init__(self, ip="127.0.0.1", port=8888):
        """
        初始化UDP发送端
        Args:
            ip: Unity端IP（本地测试用127.0.0.1）
            port: Unity端端口
        """
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 设置超时，避免阻塞
        self.sock.settimeout(0.1)
        
        # 统计信息
        self.packet_count = 0
        self.last_send_time = time.time()
        
        print(f"UDP发送端初始化完成，目标：{ip}:{port}")
    
    def send_gesture(self, hand_id, gesture_id, gesture_name):
        """
        发送手势数据
        
        Args:
            hand_id: 手部ID（0或1）
            gesture_id: 手势ID（0-5）
            gesture_name: 手势名称
        """
        # 构建数据包
        data = {
            "hand_id": hand_id,
            "gesture_id": gesture_id,
            "gesture_name": gesture_name,
            "timestamp": int(time.time() * 1000)  # 毫秒级时间戳
        }
        
        # 转换为JSON并编码
        message = json.dumps(data)
        message_bytes = message.encode('utf-8')
        
        try:
            # 发送UDP包
            self.sock.sendto(message_bytes, (self.ip, self.port))
            
            # 统计
            self.packet_count += 1
            self.last_send_time = time.time()
            
            # 调试输出（每30帧打印一次）
            if self.packet_count % 30 == 0:
                print(f"已发送 {self.packet_count} 个数据包: {message}")
                
        except Exception as e:
            print(f"发送失败: {e}")
    
    def close(self):
        """关闭socket"""
        self.sock.close()
        print(f"UDP发送端关闭，共发送 {self.packet_count} 个数据包")
