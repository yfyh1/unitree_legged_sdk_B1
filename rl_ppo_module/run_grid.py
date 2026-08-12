# ============================================================
# 1. 导入所需库
# ============================================================
import sys
import os
# 将项目根目录（env_module 的父目录）加入 Python 搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stable_baselines3 import PPO   # 加载保存的 PPO 模型
from env_module.GridEnv import GridNavEnv     # 自定义栅格环境（必须与训练时使用的环境类一致）
import time                         # 用于回合结束后暂停1秒，方便观察

# ============================================================
# 2. 主演示函数
# ============================================================
def main():
    """
    演示流程：
      1. 创建环境实例
      2. 尝试加载 models/ppo_grid_model.zip
      3. 若模型不存在则报错退出
      4. 重置环境，获取初始观测
      5. 循环执行最多 1000 步：
           - 利用模型预测动作（确定性策略）
           - 执行动作，获取奖励和终止状态
           - 渲染当前画面
           - 若回合结束，重置环境并继续
      6. 关闭环境
    """

    # ---- 2.1 创建环境 ----
    # 必须与训练时所用的环境完全一致（包括地图尺寸、障碍物、奖励函数等）
    env = GridNavEnv()

    # ---- 2.2 加载训练好的模型 ----
    print("正在加载 Grid AI Model...")
    try:
        # PPO.load() 会自动读取 .zip 文件中的网络权重和超参数配置
        model = PPO.load("models/ppo_grid_model")
    except FileNotFoundError:
        # 若模型文件不存在，给出提示并退出
        print("错误: 没有找到 Model! 请先运行 'python ppo_grid.py'.")
        return

    # ---- 2.3 开始演示 ----
    print("正在运行. 请观察 Grid Pygame !")

    # 重置环境，获得初始观测值（4维数组）和 info 字典
    obs, info = env.reset()

    # ---- 2.4 主循环（最多执行1000步，防止无限循环） ----
    for _ in range(1000):
        # 模型预测动作
        # deterministic=True 表示采用确定性策略（取概率最高的动作），而非采样
        # _states 用于循环神经网络（此处未使用，返回 None）
        action, _states = model.predict(obs, deterministic=True)

        # 执行动作，得到新观测、奖励、终止标志、截断标志、附加信息
        # terminated 表示因撞墙/撞障碍物/到达目标而结束
        # truncated 表示因时间限制等原因截断（本环境未使用，恒为 False）
        obs, reward, terminated, truncated, info = env.step(action)

        # 渲染当前帧（绘制网格、障碍物、智能体、目标）
        env.render()

        # ---- 2.5 回合结束处理 ----
        if terminated or truncated:
            print("回合结束. Resetting...")
            time.sleep(1)          # 暂停1秒，让用户看清终点或碰撞位置
            obs, info = env.reset() # 重置环境，开始新一局

    # ---- 2.6 关闭资源 ----
    env.close()

# ============================================================
# 3. 脚本入口
# ============================================================
if __name__ == "__main__":
    main()