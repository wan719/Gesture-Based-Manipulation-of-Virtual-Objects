"""
udp_receiver_test.py - UDP接收测试程序
功能：接收手势识别发送的UDP数据并显示
"""

import socket
import json

def main():
    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 8888))
    sock.settimeout(1.0)
    
    print("="*50)
    print("UDP接收测试程序启动")
    print(f"监听地址: 127.0.0.1:8888")
    print("等待接收数据...")
    print("="*50)
    
    packet_count = 0
    
    try:
        while True:
            try:
                # 接收数据
                data, addr = sock.recvfrom(1024)  # 缓冲区大小1024字节
                packet_count += 1
                
                # 解析JSON
                message = data.decode('utf-8')
                gesture_data = json.loads(message)
                
                # 显示
                print(f"[{packet_count}] 从 {addr} 收到:")
                print(f"  手部ID: {gesture_data['hand_id']}")
                print(f"  手势ID: {gesture_data['gesture_id']}")
                print(f"  手势名称: {gesture_data['gesture_name']}")
                print(f"  时间戳: {gesture_data['timestamp']}")
                print("-" * 30)
                
            except socket.timeout:
                # 超时继续
                continue
                
    except KeyboardInterrupt:
        print("\n用户中断")
    
    sock.close()
    print(f"共接收 {packet_count} 个数据包")

if __name__ == "__main__":
    main()