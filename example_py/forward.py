import socket
import json
import time

RELAY_IP = "192.168.123.220"
RELAY_PORT = 5091

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_vel(vx: float, yaw: float):
    cmd = {"vx": vx, "yaw": yaw}
    send_data = json.dumps(cmd).encode("utf-8")
    udp_sock.sendto(send_data, (RELAY_IP, RELAY_PORT))
    print(f"发送 vx={vx:.2f}, yaw={yaw:.2f}")

if __name__ == "__main__":
    print("===== 向前0.6米，朝向保持不变 =====")
    # 直行3秒，0.2m/s ×3s=0.6m
    send_vel(0.2, 0.0)
    time.sleep(3.0)
    send_vel(0.0, 0.0)
    print("前进动作完成，停机")
