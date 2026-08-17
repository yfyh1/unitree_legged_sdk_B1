"""
目标：从随机起点到定终点
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
            shape=(8,),
            dtype=np.float32
        )

        # ---- 静态障碍物列表（坐标均在 0~15, 0~20 范围内） ----
                # 格式：(列号x, 行号y)
        # self.obstacles = [
        #     (4, 9), (5, 9), (6, 9), (13, 9),
        #     (4, 10), (5, 10), (6, 10), (13, 10),
        #     (0, 11), (14, 11),
        #     (0, 12), (15, 12)
        # ]
        # -------- 障碍物整数区间 (x_min, x_max, y_min, y_max) ----------
        obstacle_rects_int = [
            (1, 12, 0, 1),    # 1
            (13, 16, 0, 1),   # 2
            (6, 8, 1, 2),     # 3
            (14, 15, 1, 2),   # 4
            (0, 1, 2, 18),    # 5
            (4, 6, 10, 12),   # 6
            (15, 16, 5, 6),   # 7
            (14, 15, 9, 10),  # 8
            (14, 16, 10, 13), # 9
            (0, 7, 20, 21),   # 10
            (14, 15, 20, 21), # 11
            (8, 15, 15, 20),  # 12
            # -------- 添加的四条边界墙壁 ----------
            (0, 15, 0, 0),    # 上边界 (y=0)
            (0, 15, 20, 20),  # 下边界 (y=20)
            (0, 0, 0, 20),    # 左边界 (x=0)
            (15, 15, 0, 20)   # 右边界 (x=15)
        
        
            # (0, 12, 0, 1),    # 1
            # (13, 16, 0, 1),   # 2
            # (6, 8, 1, 2),     # 3
            # (14, 15, 1, 2),   # 4
            # (0, 1, 2, 10),    # 5
            # (15, 16, 2, 9),   # 6
            # (14, 15, 5, 6),   # 7
            # (14, 15, 9, 10),  # 8
            # (4, 7, 10, 12), # 9
            # (13, 14, 10, 12),   # 10
            # (13, 16, 12, 15), # 11
            # (1, 8, 15, 19),  # 12
            # (11, 16, 15, 19),
            # (1, 16, 19, 20),
            # (0, 7, 20, 21),
            # (14, 16, 20, 21),
            # (0, 1, 17, 18),
            # # -------- 添加的四条边界墙壁 ----------
            # (0, 15, 0, 0),    # 上边界 (y=0)
            # (0, 15, 20, 20),  # 下边界 (y=20)
            # (0, 0, 0, 20),    # 左边界 (x=0)
            # (15, 15, 0, 20)   # 右边界 (x=15)
        ]

        # -------- 生成障碍物坐标 ----------
        self.obstacles = []
        for (x_min, x_max, y_min, y_max) in obstacle_rects_int:
            for x in range(x_min, x_max ):
                for y in range(y_min, y_max ):
                    # 确保坐标在网格范围内（防止越界）
                    if 0 <= x < self.grid_size_x and 0 <= y < self.grid_size_y:
                        self.obstacles.append((x, y))


        # Pygame 窗口和时钟（渲染时使用，初始为 None）
        self.window = None
        self.clock = None

    # ----------------------------------------------------------
    # 1.2 reset：重置环境到初始状态（起点和终点固定）
    # ----------------------------------------------------------
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # 设置目标终点（新位置，在右下角安全区）
        self.goal_pos = [1, 18]     # x=14（最大15），y=19（最大20）

        # ---- 随机生成起点（排除障碍物和终点） ----
        # 收集所有合法的白色格子（避开边界、障碍物、终点）
        valid_positions = []
        for x in range(0, self.grid_size_x):   # x: 0~15
            for y in range(0, self.grid_size_y):  # y: 0~20
                # 排除：障碍物、终点
                if (x, y) not in self.obstacles and [x, y] != self.goal_pos:
                    valid_positions.append([x, y])

        # 在 reset() 中，生成 valid_positions 之后，添加以下代码
        custom_boundary_points = [(0,0), (13,20), (15,9), (15,20)]
        # 过滤：排除障碍物和终点
        valid_boundary_points = [p for p in custom_boundary_points if p not in self.obstacles and list(p) != self.goal_pos]

        # 随机选择起点：30% 概率从边界点选，70% 从所有合法点选
        if valid_boundary_points and random.random() < 0.3:
            self.agent_pos = random.choice(valid_boundary_points)
        else:
            self.agent_pos = random.choice(valid_positions)

        # # 从合法位置中随机选择一个作为起点
        # self.agent_pos = random.choice(valid_positions)

        return self._get_obs(), {}


    # ----------------------------------------------------------
    # 1.3 辅助方法：生成观测值（4 维数组）
    # ----------------------------------------------------------
    # def _get_obs(self):
    #     return np.array([
    #         self.agent_pos[0],
    #         self.agent_pos[1],
    #         self.goal_pos[0],
    #         self.goal_pos[1]
    #     ], dtype=np.float32)


    def _get_obs(self):
        x, y = self.agent_pos
        gx, gy = self.goal_pos

        # 检查四个方向是否可走（1=可走，0=不可走/撞墙）
        up = 0 if (y - 1 < 0 or (x, y - 1) in self.obstacles) else 1
        down = 0 if (y + 1 >= self.grid_size_y or (x, y + 1) in self.obstacles) else 1
        left = 0 if (x - 1 < 0 or (x - 1, y) in self.obstacles) else 1
        right = 0 if (x + 1 >= self.grid_size_x or (x + 1, y) in self.obstacles) else 1

        return np.array([x, y, gx, gy, up, down, left, right], dtype=np.float32)



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
          - 碰撞惩罚：撞墙/撞障碍物 -20，立即终止
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
            reward = -20.0
            terminated = True

        elif tuple(new_pos) in self.obstacles:
            reward = -20.0
            terminated = True

        else:
            self.agent_pos = new_pos
            new_dist = self._manhattan_distance(self.agent_pos, self.goal_pos)
            reward = (old_dist - new_dist) * 2.0
            reward -= 0.2

        # ===== 新增：濒墙惩罚（靠近墙/障碍物就扣分） =====
        x, y = self.agent_pos
        # 检查上下左右是否有墙或障碍物
        near_wall = 0
        if y-1 < 0 or (x, y-1) in self.obstacles: near_wall += 1
        if y+1 >= self.grid_size_y or (x, y+1) in self.obstacles: near_wall += 1
        if x-1 < 0 or (x-1, y) in self.obstacles: near_wall += 1
        if x+1 >= self.grid_size_x or (x+1, y) in self.obstacles: near_wall += 1
        reward -= near_wall * 0.2   # 每靠近一个墙方向扣0.2分


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
            pygame.display.set_caption("AI Grid Navigation System")
            self.clock = pygame.time.Clock()

        pygame.event.pump()
        self.window.fill((255, 255, 255))

        # ---- 画网格线 ----
        # 竖线（x不变）
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.window, (220, 220, 220), (x, 0), (x, self.height))
        # 横线（y翻转）
        for y_logical in range(self.grid_size_y):
            screen_y = (self.grid_size_y - 1 - y_logical) * self.cell_size
            pygame.draw.line(self.window, (220, 220, 220), (0, screen_y), (self.width, screen_y))

        # ---- 画障碍物 ----
        for obs in self.obstacles:
            x, y = obs
            screen_x = x * self.cell_size
            screen_y = (self.grid_size_y - 1 - y) * self.cell_size
            rect = pygame.Rect(screen_x, screen_y, self.cell_size, self.cell_size)
            pygame.draw.rect(self.window, (0, 0, 0), rect)

        # ---- 画目标点（红色） ----
        gx, gy = self.goal_pos
        screen_gx = gx * self.cell_size
        screen_gy = (self.grid_size_y - 1 - gy) * self.cell_size
        goal_rect = pygame.Rect(screen_gx, screen_gy, self.cell_size, self.cell_size)
        pygame.draw.rect(self.window, (231, 76, 60), goal_rect)

        # ---- 画智能体（绿色） ----
        ax, ay = self.agent_pos
        screen_ax = ax * self.cell_size
        screen_ay = (self.grid_size_y - 1 - ay) * self.cell_size
        agent_rect = pygame.Rect(screen_ax, screen_ay, self.cell_size, self.cell_size)
        pygame.draw.rect(self.window, (46, 204, 113), agent_rect)

        pygame.display.flip()
        self.clock.tick(self.metadata["render_fps"])

    # ----------------------------------------------------------
    # 1.7 close：关闭 Pygame 窗口（释放资源）
    # ----------------------------------------------------------
    def close(self):
        if self.window is not None:
            pygame.quit()
