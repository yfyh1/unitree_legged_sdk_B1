##!/usr/bin/python

import sys
import time
import math

sys.path.append('../lib/python/amd64')
import robot_interface as sdk


if __name__ == '__main__':

    HIGHLEVEL = 0xee
    LOWLEVEL  = 0xff

    # udp = sdk.UDP(8080, "192.168.123.161", 8082, 129, 1087, False, sdk.RecvEnum.nonBlock)
    udp = sdk.UDP(HIGHLEVEL, 8080, "192.168.123.220", 8082)

    cmd = sdk.HighCmd()
    state = sdk.HighState()
    udp.InitCmdData(cmd)

    motiontime = 0
    while True:
        time.sleep(0.002)
        motiontime = motiontime + 2

        print(motiontime)
        # print(state.imu.rpy[0])
        
        
        udp.Recv()
        udp.GetRecv(state)
        

        # print(motiontime, state.motorState[0].q, state.motorState[1].q, state.motorState[2].q)
        # print(state.imu.rpy[0])

        cmd.mode = 0      # 0:idle, default stand      1:forced stand     2:walk continuously
        cmd.gaitType = 0
        cmd.speedLevel = 0
        cmd.footRaiseHeight = 0
        cmd.bodyHeight = 0
        cmd.euler = [0, 0, 0]
        cmd.velocity = [0, 0]
        cmd.yawSpeed = 0.0
        cmd.reserve = 0

        if motiontime > 0 and motiontime < 2000:
    
            cmd.mode = 6
    
        elif motiontime >= 2000 and motiontime < 3000:
    
            cmd.mode = 1
    
        elif motiontime >= 3000 and motiontime < 4000:
    
            cmd.mode = 1
            cmd.euler[0] = 0.3
    
        elif motiontime >= 4000 and motiontime < 6000:
    
            cmd.mode = 1
            cmd.euler[0] = -0.3
    
        elif motiontime >= 6000 and motiontime < 8000:
    
            cmd.mode = 1
            cmd.euler[1] = 0.3
    
        elif motiontime >= 8000 and motiontime < 10000:
            
            cmd.mode = 1
            cmd.euler[1] = -0.3
    
        elif motiontime >= 10000 and motiontime < 12000:
            
            cmd.mode = 1
            cmd.euler[2] = 0.3
    
        elif motiontime >= 12000 and motiontime < 14000:
            
            cmd.mode = 1
            cmd.euler[2] = -0.3
    
        elif motiontime >= 14000 and motiontime < 15000:
    
            cmd.mode = 1
    
        elif motiontime >= 15000 and motiontime < 18000:
            
            cmd.mode = 2
            cmd.velocity[0] = 0.3
            cmd.yawSpeed = 0.2
    
        elif motiontime >= 18000 and motiontime < 21000:

            cmd.mode = 2
            cmd.velocity[1] = -0.3
            cmd.yawSpeed = -0.2
    
        elif motiontime >= 21000 and motiontime < 22000:
    
            cmd.mode = 1
    
        elif motiontime >= 22000 and motiontime < 25000:
    
            cmd.mode = 2
            cmd.gaitType = 3
    
        elif motiontime >= 25000 and motiontime < 26000:
    
            cmd.mode = 1
    
        else:
    
            cmd.mode = 0
    
    

        cmd.mode = 2
        cmd.gaitType = 1
        # cmd.position = [1, 0]
        # cmd.position[0] = 2
        cmd.velocity = [-0.2, 0] # -1  ~ +1
        cmd.yawSpeed = 0
        cmd.bodyHeight = 0.1

        Go1
        if(motiontime > 0 and motiontime < 1000):
            cmd.mode = 1
            cmd.euler = [-0.3, 0, 0]
        
        if(motiontime > 1000 and motiontime < 2000):
            cmd.mode = 1
            cmd.euler = [0.3, 0, 0]
        
        if(motiontime > 2000 and motiontime < 3000):
            cmd.mode = 1
            cmd.euler = [0, -0.2, 0]
        
        if(motiontime > 3000 and motiontime < 4000):
            cmd.mode = 1
            cmd.euler = [0, 0.2, 0]
        
        if(motiontime > 4000 and motiontime < 5000):
            cmd.mode = 1
            cmd.euler = [0, 0, -0.2]
        
        if(motiontime > 5000 and motiontime < 6000):
            cmd.mode = 1
            cmd.euler = [0.2, 0, 0]
        
        if(motiontime > 6000 and motiontime < 7000):
            cmd.mode = 1
            cmd.bodyHeight = -0.2
        
        if(motiontime > 7000 and motiontime < 8000):
            cmd.mode = 1
            cmd.bodyHeight = 0.1
        
        if(motiontime > 8000 and motiontime < 9000):
            cmd.mode = 1
            cmd.bodyHeight = 0.0
        
        if(motiontime > 9000 and motiontime < 11000):
            cmd.mode = 5
        
        if(motiontime > 11000 and motiontime < 13000):
            cmd.mode = 6
        
        if(motiontime > 13000 and motiontime < 14000):
            cmd.mode = 0
        
        if(motiontime > 14000 and motiontime < 18000):
            cmd.mode = 2
            cmd.gaitType = 2
            cmd.velocity = [0.4, 0] # -1  ~ +1
            cmd.yawSpeed = 2
            cmd.footRaiseHeight = 0.1
            # printf("walk\n")
        
        if(motiontime > 18000 and motiontime < 20000):
            cmd.mode = 0
            cmd.velocity = [0, 0]
        
        if(motiontime > 20000 and motiontime < 24000):
            cmd.mode = 2
            cmd.gaitType = 1
            cmd.velocity = [0.2, 0] # -1  ~ +1
            cmd.bodyHeight = 0.1
            # printf("walk\n")
            

        udp.SetSend(cmd)
        udp.Send()
#!/usr/bin/python
# import sys
# sys.stdout.reconfigure(encoding='utf-8')
# # import sys
# import time
# import math
# # Windows适配：动态判断系统路径，先注释linux amd64库（无硬件不需要sdk）
# # sys.path.append('../lib/python/amd64')
# # import robot_interface as sdk

# # 伪造高层状态结构体简易模拟类
# class FakeHighState:
#     def __init__(self):
#         self.imu = type('obj', (object,), {
#             'rpy': [0.0, 0.0, 0.0],
#             'gyro': [0.0, 0.0, 0.0]
#         })
#         self.motorState = [type('obj', (object,), {'q':0, 'dq':0, 'tau':0}) for _ in range(12)]

# # 伪造高层指令类（空壳，只存参数）
# class FakeHighCmd:
#     def __init__(self):
#         self.mode = 0
#         self.gaitType = 0
#         self.speedLevel = 0
#         self.footRaiseHeight = 0
#         self.bodyHeight = 0
#         self.euler = [0,0,0]
#         self.velocity = [0,0]
#         self.yawSpeed = 0.0
#         self.reserve = 0

# if __name__ == '__main__':
#     HIGHLEVEL = 0xee
#     LOWLEVEL  = 0xff
#     # ========== 屏蔽UDP硬件通信代码 ==========
#     # udp = sdk.UDP(HIGHLEVEL, 8080, "192.168.220", 8082)
#     # cmd = sdk.HighCmd()
#     # state = sdk.HighState()
#     # udp.InitCmdData(cmd)

#     # 改用伪造对象
#     cmd = FakeHighCmd()
#     state = FakeHighState()
#     motiontime = 0

#     while True:
#         time.sleep(0.002)
#         motiontime = motiontime + 2
#         print("当前motiontime：", motiontime)

#         # ========== 屏蔽收发硬件数据 ==========
#         # udp.Recv()
#         # udp.GetRecv(state)

#         # 伪造模拟IMU动态数据（模拟机身轻微晃动）
#         state.imu.rpy[0] = 0.1 * math.sin(motiontime * 0.001)
#         state.imu.rpy[1] = 0.1 * math.cos(motiontime * 0.001)

#         # 下面原有的全部分段逻辑完全不动，原样保留
#         cmd.mode = 0
#         cmd.gaitType = 0
#         cmd.speedLevel = 0
#         cmd.footRaiseHeight = 0
#         cmd.bodyHeight = 0
#         cmd.euler = [0, 0, 0]
#         cmd.velocity = [0, 0]
#         cmd.yawSpeed = 0.0
#         cmd.reserve = 0
#         if motiontime > 0 and motiontime < 2000:
#             cmd.mode = 6
#         elif motiontime >= 2000 and motiontime < 3000:
#             cmd.mode = 1
#         elif motiontime >= 3000 and motiontime < 4000:
#             cmd.mode = 1
#             cmd.euler[0] = 0.3
#         elif motiontime >= 4000 and motiontime < 6000:
#             cmd.mode = 1
#             cmd.euler[0] = -0.3
#         elif motiontime >= 6000 and motiontime < 8000:
#             cmd.mode = 1
#             cmd.euler[1] = 0.3
#         elif motiontime >= 8000 and motiontime < 10000:
#             cmd.mode = 1
#             cmd.euler[1] = -0.3
#         elif motiontime >= 10000 and motiontime < 12000:
#             cmd.mode = 1
#             cmd.euler[2] = 0.3
#         elif motiontime >= 12000 and motiontime < 14000:
#             cmd.mode = 1
#             cmd.euler[2] = -0.3
#         elif motiontime >= 14000 and motiontime < 15000:
#             cmd.mode = 1
#         elif motiontime >= 15000 and motiontime < 18000:
#             cmd.mode = 2
#             cmd.velocity[0] = 0.3
#             cmd.yawSpeed = 0.2
#         elif motiontime >= 18000 and motiontime < 21000:
#             cmd.mode = 2
#             cmd.velocity[1] = -0.3
#             cmd.yawSpeed = -0.2
#         elif motiontime >= 21000 and motiontime < 22000:
#             cmd.mode = 1
#         elif motiontime >= 22000 and motiontime < 25000:
#             cmd.mode = 2
#             cmd.gaitType = 3
#         elif motiontime >= 25000 and motiontime < 26000:
#             cmd.mode = 1
#         else:
#             cmd.mode = 0

#         # 打印当前控制指令，验证逻辑是否生效
#         print(f"运行模式:{cmd.mode}, 速度vx:{cmd.velocity[0]}, vy:{cmd.velocity[1]}, 转向角速度:{cmd.yawSpeed}")
#         print(f"机身姿态r/p/y: {state.imu.rpy[0]:.2f}, {state.imu.rpy[1]:.2f}, {state.imu.rpy[2]:.2f}")
#         print("-"*50)

#         # udp.SetSend(cmd)
#         # udp.Send()