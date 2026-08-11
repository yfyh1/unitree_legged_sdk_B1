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
    print("===== 向后0.6米，朝向保持不变 =====")
    send_vel(-0.2, 0.0)
    time.sleep(3.0)
    send_vel(0.0, 0.0)
    print("后退动作完成，停机")
