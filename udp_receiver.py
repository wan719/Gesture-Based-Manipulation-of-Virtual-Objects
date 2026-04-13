#!/usr/bin/env python3
"""
UDP 接收端 - 用于测试手势数据传输
监听本地 8888 端口，显示收到的数据
"""

import socket

# 配置
LISTEN_HOST = '127.0.0.1'  # 本机
LISTEN_PORT = 8888         # 端口

def main():
    # 创建 UDP 套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 允许地址复用（可选）
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 绑定地址和端口
    sock.bind((LISTEN_HOST, LISTEN_PORT))
    
    print(f"=" * 50)
    print(f"UDP 接收端已启动")
    print(f"监听地址: {LISTEN_HOST}:{LISTEN_PORT}")
    print(f"等待数据...")
    print(f"=" * 50)
    
    while True:
        try:
            # 接收数据（最大 1024 字节）
            # recvfrom 返回 (数据, 发送方地址)
            data, client_addr = sock.recvfrom(1024)
            
            # 解码并显示
            message = data.decode('utf-8')
            print(f"[{client_addr}] {message}")
            
        except KeyboardInterrupt:
            print("\n用户中断，退出程序")
            break
        except Exception as e:
            print(f"错误: {e}")

    sock.close()

if __name__ == '__main__':
    main()
