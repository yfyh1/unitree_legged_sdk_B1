#!/usr/bin/env python3
"""
B1 control relay — receives (vx, vy, yaw) over UDP and forwards to B1 via SDK.

Listens on a UDP port (default 5091), expects JSON: {"vx": 0.05, "vy": -0.1, "yaw": 0.0}
Has a watchdog timer that stops the robot if no command arrives within timeout.
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
import time
import traceback


def main():
    # type: () -> None
    args = _parse_args()

    # 导入新的三轴控制器，不改动原x86_b1_controller
    from x86_b1_3axis_controller import B13AxisController

    # --- Init B1 ---
    controller = None
    if args.dry_run:
        print("[relay] dry-run enabled; B1 SDK commands will NOT be sent")
    else:
        print("[relay] initializing B1 3axis controller -> %s:%d"
              % (args.b1_remote_ip, args.b1_remote_port))
        controller = B13AxisController(
            remote_ip=args.b1_remote_ip,
            local_port=args.b1_local_port,
            remote_port=args.b1_remote_port,
            sdk_lib_dir=args.b1_sdk_lib_dir,
        )
        controller.stop()
        print("[relay] B1 connected (local=%d remote=%d)"
              % (args.b1_local_port, args.b1_remote_port))

    # --- UDP listen ---
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.listen_host, args.listen_port))
    sock.settimeout(0.1)
    print("[relay] listening on %s:%d" % (args.listen_host, args.listen_port))

    last_command_time = time.time()

    print("[relay] watchdog=%.1fs" % args.watchdog_timeout_s)

    try:
        while True:
            try:
                data, addr = sock.recvfrom(4096)
            except socket.timeout:
                # Watchdog: if no command for too long, stop the robot
                if time.time() - last_command_time > args.watchdog_timeout_s:
                    if controller is not None:
                        try:
                            # 三轴停机，全部置0
                            controller.send_motion(0.0, 0.0, 0.0)
                        except Exception:
                            pass
                continue

            try:
                msg = json.loads(data.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                print("[relay] invalid JSON from %s:%d" % addr)
                continue

            # 解析vx、vy、yaw，无对应字段默认0
            vx = float(msg.get("vx", 0.0))
            vy = float(msg.get("vy", 0.0))
            yaw = float(msg.get("yaw", 0.0))

            if args.dry_run:
                print("[relay] dry-run vx=%.3f vy=%.3f yaw=%.3f from %s:%d"
                      % (vx, vy, yaw, addr[0], addr[1]))
            else:
                # 调用三轴send_motion，传入三个速度参数
                controller.send_motion(vx, vy, yaw)

            last_command_time = time.time()

    except KeyboardInterrupt:
        print("\n[relay] KeyboardInterrupt")
    except Exception:
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("[relay] stopping B1")
        if controller is not None:
            controller.stop()
        sock.close()
        print("[relay] exited")


def _parse_args():
    # type: () -> argparse.Namespace
    p = argparse.ArgumentParser(
        description="B1 3axis control relay — UDP (vx,vy,yaw) to B1 SDK bridge"
    )
    p.add_argument("--listen-host", type=str, default="0.0.0.0")
    p.add_argument("--listen-port", type=int, default=5091)
    p.add_argument("--watchdog-timeout-s", type=float, default=1.0,
                   help="stop robot if no command received within this time")
    p.add_argument("--b1-remote-ip", type=str, default="192.168.123.220")
    p.add_argument("--b1-local-port", type=int, default=8080)
    p.add_argument("--b1-remote-port", type=int, default=8082)
    p.add_argument("--b1-sdk-lib-dir", type=str, default="./lib")
    p.add_argument("--dry-run", action="store_true", default=False)
    return p.parse_args()


if __name__ == "__main__":
    main()
