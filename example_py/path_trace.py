import socket
import json
import math
import time

# 目标开发板IP与端口
RELAY_IP = "192.168.123.220"
RELAY_PORT = 5091

# 创建UDP套接字
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_vel(vx: float, vy: float, yaw: float):
    """发送三轴速度指令：前后vx / 左右vy / 旋转yaw"""
    cmd = {"vx": vx, "vy": vy, "yaw": yaw}
    send_data = json.dumps(cmd).encode("utf-8")
    udp_sock.sendto(send_data, (RELAY_IP, RELAY_PORT))
    print(f"发送指令 vx={vx:.2f}, vy={vy:.2f}, yaw={yaw:.2f}")

def move_forward(total_distance: float, speed=0.2, step_dist=0.2):
    """
    向前直行，每0.2米发送一次速度指令
    total_distance: 总距离
    speed: 0.2m/s
    step_dist: 单次步长0.2m
    """
    step_count = int(total_distance / step_dist)
    single_sleep = step_dist / speed  # 每0.2米等待1秒
    print(f"\n--- 向前 {total_distance}m，共发送{step_count}次前进指令，单次停留{single_sleep:.1f}s ---")
    for _ in range(step_count):
        send_vel(speed, 0.0, 0.0)
        time.sleep(single_sleep)
    # 全部走完停机，补齐3个参数
    send_vel(0.0, 0.0, 0.0)
    time.sleep(0.3)

def move_right(total_distance: float, speed=0.2, step_dist=0.2):
    """
    向右横移，每0.2米发送一次速度指令
    total_distance: 总距离
    speed: 0.2m/s
    step_dist: 单次步长0.2m
    """
    step_count = int(total_distance / step_dist)
    single_sleep = step_dist / speed
    print(f"\n--- 向右横移 {total_distance}m，共发送{step_count}次右移指令，单次停留{single_sleep:.1f}s ---")
    for _ in range(step_count):
        send_vel(0.0, speed, 0.0)
        time.sleep(single_sleep)
    send_vel(0.0, 0.0, 0.0)
    time.sleep(0.3)

def rotate_ccw(angle_deg: float, rot_speed=0.2):
    """
    逆时针原地旋转（yaw负数=逆时针左转）
    angle_deg：旋转角度(°)
    rot_speed：旋转角速度 rad/s
    """
    angle_rad = math.radians(angle_deg)
    rot_time = abs(angle_rad) / rot_speed
    print(f"\n--- 逆时针旋转 {angle_deg}°，持续{rot_time:.2f}秒 ---")
    send_vel(0.0, 0.0, -rot_speed)
    send_vel(0.0, 0.0, -rot_speed)
    time.sleep(rot_time)
    send_vel(0.0, 0.0, 0.0)
    time.sleep(0.3)

if __name__ == "__main__":
    print("===== 栅格地图轨迹（保留完整原顺序，新增旋转逻辑）开始 =====")
    # 1、第一段前进4.8米后，逆时针旋转20°
    move_forward(4.8)
    rotate_ccw(20)

    # 2、原完整后续控制顺序完全保留，其中每一段前进1.2米执行逆时针5°
    move_right(1.8)

    move_forward(1.8)
    move_right(1.8)

    # 第一段1.2m，转5°
    move_forward(1.2)
    rotate_ccw(5)

    move_right(0.6)

    move_forward(0.6)
    move_right(0.6)

    # 第二段1.2m，转5°
    move_forward(1.2)
    rotate_ccw(5)

    move_right(1.8)

    print("\n===== 全部轨迹执行完毕，机器停机 =====")
    udp_sock.close()
