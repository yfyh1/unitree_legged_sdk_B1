#!/usr/bin/python3
# 强制控制台UTF-8编码，解决Windows中文乱码
import sys
# Windows专属编码，Linux/WSL注释这行
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
import time
import math
import pyrealsense2 as rs
import numpy as np

# D430标准分辨率（修正64笔误）
DEPTH_W = 640
DEPTH_H = 480
FPS = 30

if __name__ == '__main__':
    # 初始化RealSense管道
    pipeline = rs.pipeline()
    cfg = rs.config()
    # D430 红外流必须用 y8 代替 mono8
    cfg.enable_stream(rs.stream.depth, DEPTH_W, DEPTH_H, rs.format.z16, FPS)
    cfg.enable_stream(rs.stream.infrared, 1, DEPTH_W, DEPTH_H, rs.format.y8, FPS)
    cfg.enable_stream(rs.stream.infrared, 2, DEPTH_W, DEPTH_H, rs.format.y8, FPS)

    try:
        pipeline.start(cfg)
        print("D430相机启动成功")
    except Exception as e:
        print("相机启动失败，请检查USB3.0接口/RealSense驱动：", e)
        sys.exit(1)

    motiontime = 0
    # 缓存图像、系统时间戳，用于和机器狗IMU匹配
    img_cache = []
    try:
        while True:
            time.sleep(0.002)
            motiontime += 1
            print("当前motiontime：", motiontime)

            # 读取D430所有帧
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            ir1_frame = frames.get_infrared_frame(1)
            ir2_frame = frames.get_infrared_frame(2)
            sys_ts = time.time()  # 全局统一时间戳，和B1 state配对

            if depth_frame and ir1_frame:
                # 转图像数组
                depth_img = np.asanyarray(depth_frame.get_data())
                ir_left = np.asanyarray(ir1_frame.get_data())
                # 存入缓存
                img_cache.append({
                    "sys_ts": sys_ts,
                    "depth": depth_img,
                    "ir_left": ir_left
                })
                # 限制缓存长度防止爆内存
                if len(img_cache) > 300:
                    img_cache.pop(0)

                print(f"图像系统时间戳: {sys_ts:.4f}")
                print(f"深度图尺寸: {depth_img.shape}, 左红外尺寸: {ir_left.shape}")
            print("-"*50)
    except KeyboardInterrupt:
        print("\n收到终止信号，关闭相机")
    finally:
        pipeline.stop()
        print("相机程序正常退出")