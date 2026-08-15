"""
目标：从定起点到定终点
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import random

# ============================================================
# 1. 环境主类：继承 gymnasium.Env，必须实现 reset、step、render 等接口
# ============================================================
class GridNavEnv(gym.Env):
    """
    16×21 离散栅格环境，智能体从起点导航至终点，避开静态障碍物。
    观测空间：4维 [agent_x, agent_y, goal_x, goal_y]
    动作空间：离散4 (0上, 1下, 2左, 3右)
    奖励函数：距离奖励 + 步数惩罚 + 碰撞惩罚 + 到达奖励（详见 step 方法）
    """
    # 元数据：告诉 Gymnasium 渲染模式和帧率（每秒10帧，方便观察移动过程）
    metadata = {"render_modes": ["human"], "render_fps": 10}
    
    # ----------------------------------------------------------
    # 1.1 初始化：定义地图尺寸、动作空间、观测空间、障碍物列表
    # ----------------------------------------------------------
    def __init__(self):
        super().__init__()

        # ---- 地图尺寸（修改为 16列 × 21行） ----
        # 列号（x）：0 ~ 15，行号（y）：0 ~ 20
        self.grid_size_x = 16   # 列数（水平方向）
        self.grid_size_y = 21   # 行数（垂直方向）

        # 渲染用：每个格子 40 像素，窗口总宽高
        self.cell_size = 40
        self.width = self.grid_size_x * self.cell_size   # 640 像素
        self.height = self.grid_size_y * self.cell_size  # 840 像素

        # ---- 动作空间：离散 4 个动作 ----
        # 0: 上 (Up), 1: 下 (Down), 2: 左 (Left), 3: 右 (Right)
        self.action_space = spaces.Discrete(4)

        # ---- 观测空间：智能体坐标 (x,y) 和目标坐标 (x,y) ----
        # 共 4 个连续值，范围 0 ~ max(16,21)-1 = 20
        self.observation_space = spaces.Box(
            low=0,
            high=max(self.grid_size_x, self.grid_size_y) - 1,  # = 20
            shape=(4,),
            dtype=np.float32
        )

    # ---- 静态障碍物列表（坐标均在 0~15, 0~20 范围内）----
# 格式：(列号x, 行号y)
# 每个矩形区间 [x_min, x_max] × [y_min, y_max] 自动展开为格子坐标
obstacle_rects = [
    (0.5, 11.5, -0.5, 0.5),    # 1
    (5.5,  7.5,  0.5, 1.5),    # 2
    (12.5, 15.5, -0.5, 0.5),   # 3
    (13.5, 14.5,  0.5, 1.5),   # 4
    (-0.5, 0.5,  1.5, 17.5),   # 5
    (3.5,  5.5,  9.5, 11.5),   # 6
    (14.5, 15.5,  4.5, 5.5),   # 7
    (13.5, 14.5,  8.5, 9.5),   # 8
    (13.5, 15.5,  9.5, 12.5),  # 9
    (-0.5, 6.5, 19.5, 20.5),   # 10
    (13.5, 14.5, 19.5, 20.5),  # 11
    (7.5, 14.5, 14.5, 19.5),   # 12
]

self.obstacles = []
for x_min, x_max, y_min, y_max in obstacle_rects:
    for x in range(int(x_min + 0.5), int(x_max + 0.5) + 1):
        for y in range(int(y_min + 0.5), int(y_max + 0.5) + 1):
            self.obstacles.append((x, y))

        # Pygame 窗口和时钟（渲染时使用，初始为 None）
        self.window = None
        self.clock = None

    # ----------------------------------------------------------
    # 1.2 reset：重置环境到初始状态（起点和终点固定）
    # ----------------------------------------------------------
    def reset(self, seed=None, options=None):
        """
        重置环境，返回初始观测值。
        - 起点固定为 (1, 1)（必须为白色通路）
        - 终点固定为 (14, 19)（必须为白色通路）
        - 返回：(obs, info) 元组，info 为空字典
        """
        super().reset(seed=seed)

        # 设置目标终点（新位置，在右下角安全区）
        self.goal_pos = [14, 13]     # x=14（最大15），y=19（最大20）

        # ---- 随机生成起点（排除障碍物和终点） ----
        # 收集所有合法的白色格子（避开边界、障碍物、终点）
        valid_positions = []
        for x in range(0, self.grid_size_x):   # x: 0~15
            for y in range(0, self.grid_size_y):  # y: 0~20
                # 排除：障碍物、终点
                if (x, y) not in self.obstacles and [x, y] != self.goal_pos:
                    valid_positions.append([x, y])

        # 从合法位置中随机选择一个作为起点
        self.agent_pos = random.choice(valid_positions)

        return self._get_obs(), {}

    # ----------------------------------------------------------
    # 1.3 辅助方法：生成观测值（4 维数组）
    # ----------------------------------------------------------
    def _get_obs(self):
        return np.array([
            self.agent_pos[0],
            self.agent_pos[1],
            self.goal_pos[0],
            self.goal_pos[1]
        ], dtype=np.float32)

    # ----------------------------------------------------------
    # 1.4 辅助方法：计算曼哈顿距离（用于奖励塑形）
    # ----------------------------------------------------------
    def _manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # ----------------------------------------------------------
    # 1.5 step：核心逻辑——执行动作，计算奖励，返回新状态
    # ----------------------------------------------------------
    def step(self, action):
        """
        接收动作（0~3），执行一步移动，返回 (obs, reward, terminated, truncated, info)。

        奖励函数包含四项：
          - 距离奖励：靠近目标 +2/格，远离目标 -2/格
          - 步数惩罚：每步 -0.5（鼓励最短路径）
          - 碰撞惩罚：撞墙/撞障碍物 -10，立即终止
          - 到达奖励：到达终点 +100，立即终止
        """

        old_dist = self._manhattan_distance(self.agent_pos, self.goal_pos)

        new_pos = list(self.agent_pos)
        if action == 0:    new_pos[1] -= 1
        elif action == 1:  new_pos[1] += 1
        elif action == 2:  new_pos[0] -= 1
        elif action == 3:  new_pos[0] += 1

        terminated = False
        reward = 0.0

        # 边界碰撞检测（使用 grid_size_x 和 grid_size_y）
        if (new_pos[0] < 0 or new_pos[0] >= self.grid_size_x or
            new_pos[1] < 0 or new_pos[1] >= self.grid_size_y):
            reward = -10.0
            terminated = True

        elif tuple(new_pos) in self.obstacles:
            reward = -10.0
            terminated = True

        else:
            self.agent_pos = new_pos
            new_dist = self._manhattan_distance(self.agent_pos, self.goal_pos)
            reward = (old_dist - new_dist) * 2.0
            reward -= 0.5


        if self.agent_pos == self.goal_pos:
            reward = 100.0
            terminated = True
        # # ---- 4. 到达终点检测（放宽条件：距离≤1即成功） ----
        # if self._manhattan_distance(self.agent_pos, self.goal_pos) <= 1:
        #     reward = 100.0
        #     terminated = True

        return self._get_obs(), reward, terminated, False, {}

    # ----------------------------------------------------------
    # 1.6 render：可视化渲染（Pygame 窗口）
    # ----------------------------------------------------------
    def render(self):
        if self.window is None:
            pygame.init()
            self.window = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("AI Grid Navigation System (16x21)")
            self.clock = pygame.time.Clock()

        pygame.event.pump()
        self.window.fill((255, 255, 255))

        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.window, (220, 220, 220), (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.window, (220, 220, 220), (0, y), (self.width, y))

        for obs in self.obstacles:
            rect = pygame.Rect(
                obs[0] * self.cell_size,
                obs[1] * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(self.window, (0, 0, 0), rect)

        goal_rect = pygame.Rect(
            self.goal_pos[0] * self.cell_size,
            self.goal_pos[1] * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        pygame.draw.rect(self.window, (231, 76, 60), goal_rect)

        agent_rect = pygame.Rect(
            self.agent_pos[0] * self.cell_size,
            self.agent_pos[1] * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        pygame.draw.rect(self.window, (46, 204, 113), agent_rect)

        pygame.display.flip()
        self.clock.tick(self.metadata["render_fps"])

    # ----------------------------------------------------------
    # 1.7 close：关闭 Pygame 窗口（释放资源）
    # ----------------------------------------------------------
    def close(self):
        if self.window is not None:
            pygame.quit()
