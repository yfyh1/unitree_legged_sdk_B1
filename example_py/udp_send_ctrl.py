import socket
import json
import time

# ========= 开发板IP（已修正为192.168.123.23） =========
RELAY_IP = "192.168.123.220"
RELAY_PORT = 5091

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_vel(vx: float, yaw: float):
    """
    vx>0前进，vx<0后退；yaw>0右转，yaw<0左转
    vx范围建议：-0.4 ~ 0.4
    yaw范围建议：-0.3 ~ 0.3
    """
    cmd = {"vx": vx, "yaw": yaw}
    send_data = json.dumps(cmd).encode("utf-8")
    udp_sock.sendto(send_data, (RELAY_IP, RELAY_PORT))
    print(f"发送速度 vx={vx:.2f}, yaw={yaw:.2f} 至 {RELAY_IP}:{RELAY_PORT}")

if __name__ == "__main__":
    print("==== Windows远程控制B1发送程序（加大动作幅度版） ====")
    print("1. 先在开发板启动b1_control_relay.py")
    print("2. Windows再运行此脚本下发运动指令\n")

    # 1. 直行前进：原0.2 → 放大到0.4（最大安全前进速度）
    send_vel(0.4, 0.0)
    time.sleep(3)

    # 2. 前进+右转：vx原0.15→0.3，yaw原0.12→0.25（大幅转弯）
    send_vel(0.3, 0.25)
    time.sleep(2)

    # 3. 后退：原-0.2 → -0.4（最大后退速度）
    send_vel(-0.4, 0.0)
    time.sleep(2)

    # 4. 原地左转：原-0.18 → -0.3（最大左转角速度）
    send_vel(0.0, -0.3)
    time.sleep(2)

    # 停机归零
    send_vel(0.0, 0.0)
    print("\n动作全部完成，机器人停机")
    udp_sock.close()
