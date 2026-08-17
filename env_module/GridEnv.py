"""
目标：从随机起点到定终点
坐标系：原点在左下角，x向右增加，y向上增加
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import random

class GridNavEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 10}
    
    def __init__(self):
        super().__init__()

        # ---- 地图尺寸（16列 × 21行） ----
        self.grid_size_x = 16   # x: 0 ~ 15
        self.grid_size_y = 21   # y: 0 ~ 20

        # 渲染用：每个格子 40 像素
        self.cell_size = 40
        self.width = self.grid_size_x * self.cell_size   # 640
        self.height = self.grid_size_y * self.cell_size  # 840

        # ---- 动作空间：离散4个动作 ----
        # 0: 上 (Up)   -> y+1
        # 1: 下 (Down) -> y-1
        # 2: 左 (Left) -> x-1
        # 3: 右 (Right)-> x+1
        self.action_space = spaces.Discrete(4)

        # ---- 观测空间：8维（坐标 + 4方向可走性） ----
        self.observation_space = spaces.Box(
            low=0,
            high=max(self.grid_size_x, self.grid_size_y) - 1,
            shape=(8,),
            dtype=np.float32
        )

        # ---- 静态障碍物 ----
        self.obstacles = [
            (1,0), (2,0), (3,0), (4,0), (5,0), (6,0), (7,0), (8,0), (9,0), (10,0), (11,0),
            (13,0), (14,0), (15,0),
            (6,1), (7,1),
            (14,1),
            (0,2), (0,3), (0,4), (0,5), (0,6), (0,7), (0,8), (0,9), (0,10), (0,11), (0,12), (0,13), (0,14), (0,15), (0,16), (0,17),
            (4,10), (4,11), (5,10), (5,11),
            (15,5),
            (14,9),
            (14,10), (14,11), (14,12), (15,10), (15,11), (15,12),
            (0,20), (1,20), (2,20), (3,20), (4,20), (5,20), (6,20),
            (14,20),
            (8,15), (8,16), (8,17), (8,18), (8,19),
            (9,15), (9,16), (9,17), (9,18), (9,19),
            (10,15), (10,16), (10,17), (10,18), (10,19),
            (11,15), (11,16), (11,17), (11,18), (11,19),
            (12,15), (12,16), (12,17), (12,18), (12,19),
            (13,15), (13,16), (13,17), (13,18), (13,19),
            (14,15), (14,16), (14,17), (14,18), (14,19)
        ]

        # Pygame 相关
        self.window = None
        self.clock = None

    # ----------------------------------------------------------
    # reset：随机起点，终点固定
    # ----------------------------------------------------------
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # ---- 终点固定 ----
        self.goal_pos = [1, 18]   

        # ---- 随机生成起点（排除障碍物和终点） ----
        valid_positions = []
        for x in range(self.grid_size_x):
            for y in range(self.grid_size_y):
                if (x, y) not in self.obstacles and [x, y] != self.goal_pos:
                    valid_positions.append([x, y])

        # ---- 自定义边界点----
        custom_boundary_points = [
            (0,0),
            (0,18),
            # (4,9),
            (5,9),
            (6,10),
            # (6,11),
            (13,20),
            (15,1),
            (15,9),
            (15,20)
        ]
        valid_boundary_points = [p for p in custom_boundary_points if p not in self.obstacles and list(p) != self.goal_pos]

        # 混合采样：30% 从边界点选，70% 从全体合法点选
        if valid_boundary_points and random.random() < 0.4:
            self.agent_pos = random.choice(valid_boundary_points)
        else:
            self.agent_pos = random.choice(valid_positions)

        return self._get_obs(), {}

    # ----------------------------------------------------------
    # 辅助方法：生成观测值（8维）
    # ----------------------------------------------------------
    def _get_obs(self):
        x, y = self.agent_pos
        gx, gy = self.goal_pos

        # 四个方向是否可走（左下角原点坐标系）
        up = 0 if (y + 1 >= self.grid_size_y or (x, y + 1) in self.obstacles) else 1
        down = 0 if (y - 1 < 0 or (x, y - 1) in self.obstacles) else 1
        left = 0 if (x - 1 < 0 or (x - 1, y) in self.obstacles) else 1
        right = 0 if (x + 1 >= self.grid_size_x or (x + 1, y) in self.obstacles) else 1

        return np.array([x, y, gx, gy, up, down, left, right], dtype=np.float32)

    # ----------------------------------------------------------
    # 曼哈顿距离
    # ----------------------------------------------------------
    def _manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # ----------------------------------------------------------
    # step：核心逻辑（左下角原点坐标系）
    # ----------------------------------------------------------
    def step(self, action):
        old_dist = self._manhattan_distance(self.agent_pos, self.goal_pos)

        new_pos = list(self.agent_pos)
        if action == 0:    new_pos[1] += 1   # 上
        elif action == 1:  new_pos[1] -= 1   # 下
        elif action == 2:  new_pos[0] -= 1   # 左
        elif action == 3:  new_pos[0] += 1   # 右

        terminated = False
        reward = 0.0

        # 边界碰撞
        if (new_pos[0] < 0 or new_pos[0] >= self.grid_size_x or
            new_pos[1] < 0 or new_pos[1] >= self.grid_size_y):
            reward = -50.0
            terminated = True
        # 障碍物碰撞
        elif tuple(new_pos) in self.obstacles:
            reward = -50.0
            terminated = True
        else:
            self.agent_pos = new_pos
            new_dist = self._manhattan_distance(self.agent_pos, self.goal_pos)
            reward = (old_dist - new_dist) * 1.0
            reward -= 0.2

        # 濒墙惩罚
        x, y = self.agent_pos
        near_wall = 0
        if y+1 >= self.grid_size_y or (x, y+1) in self.obstacles: near_wall += 1
        if y-1 < 0 or (x, y-1) in self.obstacles: near_wall += 1
        if x-1 < 0 or (x-1, y) in self.obstacles: near_wall += 1
        if x+1 >= self.grid_size_x or (x+1, y) in self.obstacles: near_wall += 1
        reward -= near_wall * 0.1

        # 到达终点
        if self.agent_pos == self.goal_pos:
            reward = 100.0
            terminated = True

        return self._get_obs(), reward, terminated, False, {}

    def render(self):
        if self.window is None:
            pygame.init()
            self.window = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("AI Grid Navigation System (左下角原点)")
            self.clock = pygame.time.Clock()

        pygame.event.pump()
        self.window.fill((255, 255, 255))

        # 画网格线
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.window, (220, 220, 220), (x, 0), (x, self.height))
        for y_logical in range(self.grid_size_y):
            screen_y = (self.grid_size_y - 1 - y_logical) * self.cell_size
            pygame.draw.line(self.window, (220, 220, 220), (0, screen_y), (self.width, screen_y))

        # 画障碍物
        for obs in self.obstacles:
            x, y = obs
            screen_x = x * self.cell_size
            screen_y = (self.grid_size_y - 1 - y) * self.cell_size
            rect = pygame.Rect(screen_x, screen_y, self.cell_size, self.cell_size)
            pygame.draw.rect(self.window, (0, 0, 0), rect)

        # 画目标点（红色）
        gx, gy = self.goal_pos
        screen_gx = gx * self.cell_size
        screen_gy = (self.grid_size_y - 1 - gy) * self.cell_size
        goal_rect = pygame.Rect(screen_gx, screen_gy, self.cell_size, self.cell_size)
        pygame.draw.rect(self.window, (231, 76, 60), goal_rect)

        # 画智能体（绿色）
        ax, ay = self.agent_pos
        screen_ax = ax * self.cell_size
        screen_ay = (self.grid_size_y - 1 - ay) * self.cell_size
        agent_rect = pygame.Rect(screen_ax, screen_ay, self.cell_size, self.cell_size)
        pygame.draw.rect(self.window, (46, 204, 113), agent_rect)

        pygame.display.flip()
        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.window is not None:
            pygame.quit()