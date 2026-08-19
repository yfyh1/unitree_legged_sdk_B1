import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import socket
import json
import math
import time
import tkinter as tk
from tkinter import simpledialog

# ===================== PPO 模型接口 =====================
from rl_ppo_module.model_interface import get_action_from_position

# ===================== 配置参数 =====================
RELAY_IP = "192.168.123.220"
RELAY_PORT = 5091
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

GRID_SIZE = 0.6          # 每个栅格边长 0.6 m
MAX_ITER = 200

# 目标栅格（到达后自动停止）
TARGET_GRID = (1, 18)

# ===================== 偏航补偿 =====================
# 前进 / 后退：每 0.2m 顺时针补偿 1.5°
FB_COMP_DEG = 0.59
FB_COMP_RAD = math.radians(FB_COMP_DEG)

# 左移 / 右移：每 0.2m 顺时针补偿 0.25°
LR_COMP_DEG = 0.28
LR_COMP_RAD = math.radians(LR_COMP_DEG)

COMP_ROT_SPEED = 0.2   # rad/s

FB_COMP_TIME = FB_COMP_RAD / COMP_ROT_SPEED   # ≈ 0.1309 s
LR_COMP_TIME = LR_COMP_RAD / COMP_ROT_SPEED   # ≈ 0.0218 s

# ===================== 运动速度（已调回 0.2 m/s） =====================
MOVE_SPEED = 0.3
STEP_DIST = 0.2

# ===================== UDP =====================
def send_vel(vx, vy, yaw):
    cmd = {"vx": vx, "vy": vy, "yaw": yaw}
    udp_sock.sendto(json.dumps(cmd).encode(), (RELAY_IP, RELAY_PORT))
    print(f"vx={vx:.2f}, vy={vy:.2f}, yaw={yaw:.3f}")

def stop():
    for _ in range(5):
        send_vel(0, 0, 0)
        time.sleep(0.05)
    time.sleep(0.2)

def yaw_comp(t):
    """顺时针偏航补偿"""
    send_vel(0, 0, COMP_ROT_SPEED)
    time.sleep(t)

# ===================== 运动原语（栅格级） =====================
def forward():
    steps = int(GRID_SIZE / STEP_DIST)
    dt = STEP_DIST / MOVE_SPEED*1.44
    for _ in range(steps):
        send_vel(MOVE_SPEED, 0, 0)
        time.sleep(dt)
        yaw_comp(FB_COMP_TIME)
    stop()

def down():
    steps = int(GRID_SIZE / STEP_DIST)
    dt = STEP_DIST / MOVE_SPEED *1.44
    for _ in range(steps):
        send_vel(-MOVE_SPEED, 0, 0)
        time.sleep(dt)
        yaw_comp(FB_COMP_TIME)
    stop()

def right():
    steps = int(GRID_SIZE / STEP_DIST)
    dt = STEP_DIST / MOVE_SPEED*1.7
    for _ in range(steps):
        send_vel(0, -MOVE_SPEED, 0)
        time.sleep(dt)
        yaw_comp(LR_COMP_TIME)
    stop()

def left():
    steps = int(GRID_SIZE / STEP_DIST)
    dt = STEP_DIST / MOVE_SPEED*1.7
    for _ in range(steps):
        send_vel(0, MOVE_SPEED, 0)
        time.sleep(dt)
        yaw_comp(LR_COMP_TIME)
    stop()

# ===================== 动作 ID → 运动映射 =====================
# PPO 输出约定：
# 0 = 上 (forward, y+1)
# 1 = 下 (down,    y-1)
# 2 = 左 (left,    x-1)
# 3 = 右 (right,   x+1)
def execute_action(action_id, x, y):
    if action_id == 0:
        forward()
        return x, y + 1
    elif action_id == 1:
        down()
        return x, y - 1
    elif action_id == 2:
        left()
        return x - 1, y
    elif action_id == 3:
        right()
        return x + 1, y
    else:
        raise ValueError(f"非法动作ID: {action_id}")

# ===================== 导航主逻辑 =====================
def run(start):
    x, y = start
    print(f"✅ PPO 导航启动：起点({x},{y})，目标{TARGET_GRID}")

    for it in range(MAX_ITER):
        # ===== 到达目标检测（每步先检查） =====
        if (x, y) == TARGET_GRID:
            print(f"\n🎯 已到达目标栅格 {TARGET_GRID}！")
            print("🛑 程序自动停止")
            return

        action_id = get_action_from_position(x, y)
        action_names = ["↑上", "↓下", "←左", "→右"]

        print(f"[{it:03d}] 位置({x},{y}) → PPO动作 {action_id}({action_names[action_id]})")

        x, y = execute_action(action_id, x, y)
        print(f"       当前位置({x},{y})")

        if action_id is None:
            print("✅ PPO 判定到达目标")
            break

        time.sleep(0.3)

    else:
        print("⚠️ 迭代次数超限")

# ===================== 入口 =====================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    sx = simpledialog.askinteger("X", "起点X", initialvalue=14)
    sy = simpledialog.askinteger("Y", "起点Y", initialvalue=2)

    try:
        run((sx, sy))
    finally:
        stop()
        udp_sock.close()
        print("🛑 程序结束，UDP 已关闭")