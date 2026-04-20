import socket
import json
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5052

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

gesture_map = {
    "fist": 0,
    "open_palm": 1,
    "one": 2,
    "two": 3,
    "thumb_up": 4
}

def send_gesture(gesture_name):
    data = {
        "hand_id": 0,
        "gesture_id": gesture_map[gesture_name],
        "gesture_name": gesture_name,
        "timestamp": int(time.time() * 1000)
    }

    msg = json.dumps(data, ensure_ascii=False)
    sock.sendto(msg.encode("utf-8"), (UDP_IP, UDP_PORT))
    print("已发送:", msg)

if __name__ == "__main__":
    for g in ["open_palm", "one", "two", "fist", "thumb_up"]:
        send_gesture(g)
        time.sleep(2)