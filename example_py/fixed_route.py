import socket
import json
import math
import time
# ===================== 配置 =====================
RELAY_IP = "192.168.123.220"
RELAY_PORT = 5091
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 前进、右移分开两套偏航补偿参数
# 前进补偿：每0.2米顺时针0.65°
FORWARD_COMP_DEG = 0.6
FORWARD_COMP_RAD = math.radians(FORWARD_COMP_DEG)
# 右移补偿：每0.2米顺时针0.1°
RIGHT_COMP_DEG = 0.1
RIGHT_COMP_RAD = math.radians(RIGHT_COMP_DEG)
COMP_ROT_SPEED = 0.2       # 统一旋转角速度 rad/s
FORWARD_COMP_TIME = FORWARD_COMP_RAD / COMP_ROT_SPEED
RIGHT_COMP_TIME = RIGHT_COMP_RAD / COMP_ROT_SPEED

# ===================== 底层指令 =====================
def send_vel(vx: float, vy: float, yaw: float):
    """发送三轴速度指令：前后vx / 左右vy / 旋转yaw"""
    cmd = {"vx": vx, "vy": vy, "yaw": yaw}
    send_data = json.dumps(cmd).encode("utf-8")
    udp_sock.sendto(send_data, (RELAY_IP, RELAY_PORT))
    print(f"  发送指令 vx={vx:.2f}, vy={vy:.2f}, yaw={yaw:.3f}")

def stop():
    """停机稳定姿态"""
    send_vel(0.0, 0.0, 0.0)
    time.sleep(0.3)

# ===================== 运动原语（分段带独立偏航补偿） =====================
def move_forward_with_yaw_compensation(total_distance: float, speed=0.2, step_dist=0.2):
    """向前直行，每0.2m顺时针补偿0.7°"""
    step_count = int(round(total_distance / step_dist))
    single_sleep = step_dist / speed
    print(f"\n>>> 向前直行 {total_distance}m，每段顺时针补偿 {FORWARD_COMP_DEG}°")
    for i in range(step_count):
        send_vel(speed, 0.0, 0.0)
        time.sleep(single_sleep)
        print(f"  已直行 {(i+1)*step_dist:.1f}m")
        # 顺时针补偿 yaw>0
        send_vel(0.0, 0.0, COMP_ROT_SPEED)
        time.sleep(FORWARD_COMP_TIME)
        stop()
    print(f"<<< 前进{total_distance}m完成")

def move_right_with_yaw_compensation(total_distance: float, speed=0.2, step_dist=0.2):
    """向右横移，每0.2m顺时针补偿0.2°"""
    step_count = int(round(total_distance / step_dist))
    single_sleep = step_dist / speed
    print(f"\n>>> 向右横移 {total_distance}m，每段顺时针补偿 {RIGHT_COMP_DEG}°")
    for i in range(step_count):
        send_vel(0.0, speed, 0.0)
        time.sleep(single_sleep)
        print(f"  已右移 {(i+1)*step_dist:.1f}m")
        # 顺时针小幅补偿
        send_vel(0.0, 0.0, COMP_ROT_SPEED)
        time.sleep(RIGHT_COMP_TIME)
        stop()
    print(f"<<< 右移{total_distance}m完成")

def rotate_ccw(angle_deg: float, rot_speed=0.2):
    """原地逆时针旋转"""
    angle_rad = math.radians(angle_deg)
    rot_time = abs(angle_rad) / rot_speed
    print(f"\n原地逆时针旋转 {angle_deg}°")
    send_vel(0.0, 0.0, -rot_speed)
    time.sleep(rot_time)
    stop()

def rotate_cw(angle_deg: float, rot_speed=0.2):
    """原地顺时针旋转"""
    angle_rad = math.radians(angle_deg)
    rot_time = abs(angle_rad) / rot_speed
    print(f"\n原地顺时针旋转 {angle_deg}°")
    send_vel(0.0, 0.0, rot_speed)
    time.sleep(rot_time)
    stop()

# ===================== 固定路径任务序列 =====================
def run_fixed_path():
    task_list = [
        {"step": 1, "action": "forward", "dist": 5.4},
        {"step": 2, "action": "right",   "dist": 1.8},
        {"step": 3, "action": "forward", "dist": 1.8},
        {"step": 4, "action": "right",   "dist": 1.8},
        {"step": 5, "action": "forward", "dist": 1.2},
        {"step": 6, "action": "right",   "dist": 0.6},
        {"step": 7, "action": "forward", "dist": 0.6},
        {"step": 8, "action": "right",   "dist": 0.6},
        {"step": 9, "action": "forward", "dist": 1.2},
        {"step":10, "action": "right",   "dist": 1.2},
    ]
    for task in task_list:
        print(f"\n========== 第{task['step']}步任务 ==========")
        if task["action"] == "forward":
            move_forward_with_yaw_compensation(task["dist"])
        elif task["action"] == "right":
            move_right_with_yaw_compensation(task["dist"])
        print(f"========== 第{task['step']}步执行完毕 ==========\n")
        time.sleep(0.5) # 每步间隔稳定姿态

# ===================== 主程序入口 =====================
if __name__ == "__main__":
    print("===== B1机器狗 固定10步轨迹程序启动 =====")
    print(f"前进每0.2m顺时针补偿{FORWARD_COMP_DEG}°，右移每0.2m顺时针补偿{RIGHT_COMP_DEG}°")
    run_fixed_path()
    print("\n===== 全部10步路径执行完成，机器停机 =====")
    udp_sock.close()
