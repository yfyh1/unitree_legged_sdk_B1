import socket
import json
import time

RELAY_IP = "192.168.123.220"
RELAY_PORT = 5091

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_vel(vx: float, vy: float, yaw: float):
    # 发送三轴速度：前后vx、横向vy、旋转yaw
    cmd = {"vx": vx, "vy": vy, "yaw": yaw}
    send_data = json.dumps(cmd).encode("utf-8")
    udp_sock.sendto(send_data, (RELAY_IP, RELAY_PORT))
    print(f"发送 vx={vx:.2f}, vy={vy:.2f}, yaw={yaw:.2f}")

if __name__ == "__main__":
    print("===== 纯横向右移0.6米，机身朝向保持不变 =====")
    lateral_speed = 0.2
    duration = 3.0
    # vy=0.2 向右横移，vx、yaw置0，不旋转
    send_vel(0.0, lateral_speed, 0.0)
    time.sleep(duration)
    # 停机归零
    send_vel(0.0, 0.0, 0.0)
    print("右移动作完成，朝向不变，停机")
    udp_sock.close()
