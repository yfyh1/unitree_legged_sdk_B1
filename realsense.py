#!/usr/bin/python3
# Windows控制台UTF8编码
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
import time
import numpy as np
import socket
import struct

# 修改为你的机器狗B1局域网WiFi IP
REMOTE_IP = "192.168.1.100"
REMOTE_PORT = 8890
DEPTH_W = 640
DEPTH_H = 480

img_cache = []
motiontime = 0

# 自定义函数：确保精准读取N字节数据
def recv_exact(sock, byte_len):
    buf = b""
    while len(buf) < byte_len:
        data = sock.recv(byte_len - len(buf))
        if not data:
            raise ConnectionResetError("远程服务端断开连接")
        buf += data
    return buf

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((REMOTE_IP, REMOTE_PORT))
    # 等待服务端握手就绪信号
    handshake = recv_exact(client, 2)
    print("✅ 已稳定连接WiFi远程D430相机")

    while True:
        motiontime += 1
        print(f"\n当前motiontime：{motiontime}")

        # 1. 读取8字节时间戳
        ts_bytes = recv_exact(client, 8)
        sys_ts = struct.unpack("d", ts_bytes)[0]

        # 2. 读取深度图像长度(4字节) + 完整深度数据
        depth_len = struct.unpack("I", recv_exact(client, 4))[0]
        depth_raw = recv_exact(client, depth_len)
        depth_img = np.frombuffer(depth_raw, dtype=np.uint16).reshape(DEPTH_H, DEPTH_W)

        # 3. 读取红外图像长度(4字节) + 完整红外数据
        ir_len = struct.unpack("I", recv_exact(client, 4))[0]
        ir_raw = recv_exact(client, ir_len)
        ir_left = np.frombuffer(ir_raw, dtype=np.uint8).reshape(DEPTH_H, DEPTH_W)

        # 缓存图像时间戳对，用于IMU对齐
        img_cache.append({"sys_ts": sys_ts, "depth": depth_img, "ir_left": ir_left})
        if len(img_cache) > 300:
            img_cache.pop(0)

        print(f"图像时间戳: {sys_ts:.4f}")
        print(f"深度图尺寸: {depth_img.shape} | 左红外尺寸: {ir_left.shape}")
        print("-" * 60)

except KeyboardInterrupt:
    print("\n🛑 手动终止程序，断开WiFi连接")
except Exception as err:
    print(f"\n❌ 程序异常退出: {err}")
finally:
    client.close()
    print("程序正常关闭")