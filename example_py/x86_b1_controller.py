"""
Unitree B1 high-level control wrapper for x86.

This file lazy-loads robot_interface so dry-run mode can still import the x86
controller script on machines without the Unitree SDK.
"""

from __future__ import annotations

import os
import sys
import time

_HIGHLEVEL = 0xEE


class B1Controller:
    def __init__(self, remote_ip, local_port, remote_port, sdk_lib_dir="./lib"):
        # type: (str, int, int, str) -> None
        self.sdk = self._load_sdk(sdk_lib_dir)
        self.remote_ip = remote_ip
        self.udp = self.sdk.UDP(_HIGHLEVEL, int(local_port), remote_ip, int(remote_port))
        self.cmd = self.sdk.HighCmd()
        self.state = self.sdk.HighState()
        self.udp.InitCmdData(self.cmd)
        self._last_forward = 0.0
        self._last_yaw = 0.0
        self._last_send_time = 0.0

    def _load_sdk(self, sdk_lib_dir):
        # type: (str) -> object
        candidates = []
        if sdk_lib_dir:
            candidates.append(os.path.abspath(sdk_lib_dir))
        candidates.append(os.path.abspath("./lib"))
        candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

        for path in candidates:
            if path and os.path.isdir(path) and path not in sys.path:
                sys.path.append(path)

        try:
            import robot_interface as sdk  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "failed to import robot_interface. Run from Mediapipe-1 or pass "
                "--b1-sdk-lib-dir pointing to the Unitree SDK lib directory"
            ) from exc
        return sdk

    def _reset_cmd_defaults(self):
        # type: () -> None
        self.cmd.mode = 0
        self.cmd.gaitType = 0
        self.cmd.speedLevel = 0
        self.cmd.footRaiseHeight = 0
        self.cmd.bodyHeight = 0
        self.cmd.euler = [0, 0, 0]
        self.cmd.velocity = [0, 0]
        self.cmd.yawSpeed = 0.0
        self.cmd.reserve = 0

    def send_motion(self, forward_speed, yaw_speed):
        # type: (float, float) -> None
        self.udp.Recv()
        self.udp.GetRecv(self.state)
        self._reset_cmd_defaults()

        forward_speed = float(forward_speed)
        yaw_speed = float(yaw_speed)
        if abs(forward_speed) > 1e-6 or abs(yaw_speed) > 1e-6:
            self.cmd.mode = 2
            self.cmd.velocity = [forward_speed, 0.0]
            self.cmd.yawSpeed = yaw_speed

        self.udp.SetSend(self.cmd)
        self.udp.Send()
        self._last_forward = forward_speed
        self._last_yaw = yaw_speed
        self._last_send_time = time.time()

    def stop(self):
        # type: () -> None
        for _ in range(3):
            self.send_motion(0.0, 0.0)
            time.sleep(0.05)
