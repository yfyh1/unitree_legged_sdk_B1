#!/usr/bin/python

import sys
import time
import math

sys.path.append('../lib/python/amd64')
import robot_interface as sdk

YAWSPEED = 0.2
R = 1


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

        if motiontime <= 10471:
            cmd.mode = 2
            cmd.velocity=[0,YAWSPEED * R]
            cmd.yawSpeed=YAWSPEED * (-1.0)  
        else:
            exit()
            

        udp.SetSend(cmd)
        udp.Send()
