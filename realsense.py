#!/usr/bin/python3
# 强制控制台UTF-8编码，解决Windows中文乱码
import sys
# Windows专属编码，Linux/WSL注释这行
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
import time
import math
import numpy as np
import socket
import struct

# WiFi机器狗IP（B1主板局域网IP，同WiFi）
REMOTE_IP = "192.168.123.10"
REMOTE_PORT = 8890
DEPTH_W = 640
DEPTH_H = 480
# 缓存图像、系统时间戳，用于和B1 IMU匹配
img_cache = []

# 连接远程相机服务
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((REMOTE_IP, REMOTE_PORT))
print("已连接WiFi远程D430")

motiontime = 0
# 预分配缓冲区
depth_size = DEPTH_W * DEPTH_H * 2
ir_size = DEPTH_W * DEPTH_H
try:
    while True:
        time.sleep(0.002)
        motiontime += 1
        print("当前motiontime：", motiontime)
        # 先读8字节时间戳
        ts_data = client.recv(8)
        sys_ts = struct.unpack("d", ts_data)[0]
        # 读深度长度
        len_d = struct.unpack("I", client.recv(4))[0]
        depth_raw = b""
        while len(depth_raw) < len_d:
            depth_raw += client.recv(4096)
        depth_img = np.frombuffer(depth_raw, dtype=np.uint16).reshape(DEPTH_H, DEPTH_W)
        # 读红外长度
        len_i = struct.unpack("I", client.recv(4))[0]
        ir_raw = b""
        while len(ir_raw) < len_i:
            ir_raw += client.recv(4096)
        ir_left = np.frombuffer(ir_raw, dtype=np.uint8).reshape(DEPTH_H, DEPTH_W)

        # 存入缓存
        img_cache.append({
            "sys_ts": sys_ts,
            "depth": depth_img,
            "ir_left": ir_left
        })
        if len(img_cache) > 300:
            img_cache.pop(0)

        print(f"图像系统时间戳: {sys_ts:.4f}")
        print(f"深度图尺寸: {depth_img.shape}, 左红外尺寸: {ir_left.shape}")
        print("-"*50)
except KeyboardInterrupt:
    print("\n收到终止信号，断开WiFi连接")
finally:
    client.close()
    print("程序正常退出")