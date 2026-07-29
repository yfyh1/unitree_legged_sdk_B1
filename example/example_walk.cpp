/*****************************************************************
 Copyright (c) 2020, Unitree Robotics.Co.Ltd. All rights reserved.
******************************************************************/

#include "unitree_legged_sdk/unitree_legged_sdk.h"  // 包含Unitree机器人SDK的头文件
#include <math.h>                                   // 包含数学函数库
#include <iostream>                                 // 包含输入输出流库
#include <unistd.h>                                 // 包含UNIX标准函数库，用于sleep等函数
#include <string.h>                                 // 包含字符串处理函数库

using namespace UNITREE_LEGGED_SDK;  // 使用Unitree机器人SDK的命名空间

class Custom  // 定义一个名为Custom的类
{
public:
    Custom(uint8_t level) : safe(LeggedType::B1),  // 构造函数，初始化安全控制和UDP通信
                            udp(level, 8090, "192.168.123.220", 8082)  // 初始化UDP通信参数
    {
        udp.InitCmdData(cmd);  // 初始化命令数据
        // udp.print = true;    // 可以启用UDP通信的打印功能（已注释掉）
    }
    void UDPRecv();  // 声明接收UDP数据的方法
    void UDPSend();  // 声明发送UDP数据的方法
    void RobotControl();  // 声明机器人控制的方法

    Safety safe;          // 定义安全控制对象
    UDP udp;              // 定义UDP通信对象
    HighCmd cmd = {0};    // 定义高级命令结构体，初始化为0
    HighState state = {0};// 定义高级状态结构体，初始化为0
    int motiontime = 0;   // 定义运动时间变量
    float dt = 0.002;     // 定义时间间隔，单位秒，范围0.001~0.01
};

void Custom::UDPRecv()  // 实现接收UDP数据的方法
{
    udp.Recv();  // 调用UDP对象的接收方法
}

void Custom::UDPSend()  // 实现发送UDP数据的方法
{
    udp.Send();  // 调用UDP对象的发送方法
}

void Custom::RobotControl()  // 实现机器人控制的方法
{
    motiontime += 2;  // 每次调用时，运动时间增加2
    udp.GetRecv(state);  // 从UDP接收数据并更新机器人状态
    printf("%d   %f\n", motiontime, state.imu.rpy[2]);  // 打印当前运动时间和IMU的偏航角

    // 初始化机器人命令参数
    cmd.mode = 0; // 0:空闲模式，默认站立  1:强制站立  2:连续行走
    cmd.gaitType = 0;  // 步态类型，0为默认
    cmd.speedLevel = 0;  // 速度等级，0为默认
    cmd.footRaiseHeight = 0;  // 抬脚高度，0为默认
    cmd.bodyHeight = 0;  // 身体高度，0为默认
    cmd.euler[0] = 0;  // 欧拉角x，0为默认
    cmd.euler[1] = 0;  // 欧拉角y，0为默认
    cmd.euler[2] = 0;  // 欧拉角z，0为默认
    cmd.velocity[0] = 0.0f;  // x轴速度，0为默认
    cmd.velocity[1] = 0.0f;  // y轴速度，0为默认
    cmd.yawSpeed = 0.0f;  // 偏航速度，0为默认
    cmd.reserve = 0;  // 保留字段，0为默认

    // 根据运动时间设置不同的命令参数
    if (motiontime > 0 && motiontime < 2000)
    {
        cmd.mode = 6;  // 设置模式为6
        std::cout<<"mode 6"<<std::endl;
    }
    else if(motiontime >= 2000 && motiontime < 3000)
    {
        cmd.mode = 1;  // 设置模式为1，强制站立
        std::cout<<"mode 1"<<std::endl;
    }


    else if(motiontime >= 3000 && motiontime < 6000)
    {
        cmd.mode = 2;  // 设置模式为1，强制站立
        cmd.velocity[0]=0.2;
        std::cout<<"mode 2 velocity[0]=0.2"<<std::endl;
    }
    else if(motiontime >= 6000 && motiontime < 9000)
    {
        cmd.mode = 2;  // 设置模式为1，强制站立
        cmd.velocity[0]=-0.2;
        std::cout<<"mode 2 velocity[0]=-0.2"<<std::endl;
    }
    else if(motiontime >= 9000 && motiontime < 12000)
    {
        cmd.mode = 2;  // 设置模式为1，强制站立
        cmd.velocity[1]=0.2;
        std::cout<<"mode 2 velocity[1]=0.2"<<std::endl;
    }
    else if(motiontime >= 12000 && motiontime < 15000)
    {
        cmd.mode = 2;  // 设置模式为1，强制站立
        cmd.velocity[1]=-0.2;
        std::cout<<"mode 2 velocity[1]=-0.2"<<std::endl;
    }
    else if(motiontime >= 15000 && motiontime < 18000)
    {
        cmd.mode = 2;  // 设置模式为1，强制站立
        cmd.yawSpeed=0.2;
        std::cout<<"mode 2 yawSpeed=0.2"<<std::endl;
    }
    else if(motiontime >= 18000 && motiontime < 21000)
    {
        cmd.mode = 2;  // 设置模式为1，强制站立
        cmd.yawSpeed=-0.2;
        std::cout<<"mode 2 yawSpeed=-0.2"<<std::endl;
    }
    else if(motiontime >= 21000 && motiontime < 22000)
    {
        cmd.mode = 2;  // 设置模式为1，强制站立
        
        std::cout<<"mode 2 "<<std::endl;
    }


    else if(motiontime >= 22000 && motiontime < 25000)
    {
        cmd.mode = 1;  // 设置模式为1，强制站立
        std::cout<<"mode 1"<<std::endl;
    }
    else if(motiontime >= 25000 && motiontime < 28000)
    {
        cmd.mode = 6;  // 设置模式为6
        std::cout<<"mode 6"<<std::endl;
    }
    else if(motiontime >= 28000 && motiontime < 31000)
    {
        cmd.mode = 5;  // 设置模式为5
        std::cout<<"mode 5"<<std::endl;
    }
    else if(motiontime >= 31000 && motiontime < 34000)
    {
        cmd.mode = 7;  // 设置模式为7
        std::cout<<"mode 7"<<std::endl;
    }
    else 
    {
        cmd.mode = 0;  // 设置模式为0，空闲模式
        std::cout<<"mode 0"<<std::endl;
    }
    
    udp.SetSend(cmd);  // 设置要发送的命令
}

int main(void)
{
    std::cout << "Communication level is set to HIGH-level." << std::endl
              << "WARNING: Make sure the robot is standing on the ground." << std::endl
              << "Press Enter to continue..." << std::endl;
    std::cin.ignore();  // 等待用户按下Enter键继续

    Custom custom(HIGHLEVEL);  // 创建Custom对象，设置通信级别为HIGH
    InitEnvironment();  // 初始化环境
    LoopFunc loop_control("control_loop", custom.dt, boost::bind(&Custom::RobotControl, &custom));  // 创建控制循环
    LoopFunc loop_udpSend("udp_send", custom.dt, 3, boost::bind(&Custom::UDPSend, &custom));  // 创建UDP发送循环
    LoopFunc loop_udpRecv("udp_recv", custom.dt, 3, boost::bind(&Custom::UDPRecv, &custom));  // 创建UDP接收循环

    loop_udpSend.start();  // 启动UDP发送循环
    loop_udpRecv.start();  // 启动UDP接收循环
    loop_control.start();  // 启动控制循环

    while (1)
    {
        sleep(10);  // 主循环，每10秒休眠一次
    };

    return 0;
}