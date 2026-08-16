"""
目标：从定起点到定终点
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame

class GridNavEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 10}

    def __init__(self):
        super().__init__()

        self.grid_size_x = 16
        self.grid_size_y = 21
        self.cell_size = 40
        self.width = self.grid_size_x * self.cell_size
        self.height = self.grid_size_y * self.cell_size

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0,
            high=max(self.grid_size_x, self.grid_size_y) - 1,
            shape=(4,),
            dtype=np.float32
        )

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
        ]

        # -------- 生成障碍物坐标 ----------
        self.obstacles = []
        for (x_min, x_max, y_min, y_max) in obstacle_rects_int:
            for x in range(x_min, x_max ):
                for y in range(y_min, y_max ):
                    # 确保坐标在网格范围内（防止越界）
                    if 0 <= x < self.grid_size_x and 0 <= y < self.grid_size_y:
                        self.obstacles.append((x, y))

        self.window = None
        self.clock = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.agent_pos = [12,2]      # 固定起点
        self.goal_pos = [0,19]     # 固定终点
        return self._get_obs(), {}

    def _get_obs(self):
        return np.array([
            self.agent_pos[0],
            self.agent_pos[1],
            self.goal_pos[0],
            self.goal_pos[1]
        ], dtype=np.float32)

    def _manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def step(self, action):
        old_dist = self._manhattan_distance(self.agent_pos, self.goal_pos)
        new_pos = list(self.agent_pos)
        if action == 0:    new_pos[1] -= 1
        elif action == 1:  new_pos[1] += 1
        elif action == 2:  new_pos[0] -= 1
        elif action == 3:  new_pos[0] += 1

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
            reward = (old_dist - new_dist) * 2.0 - 0.5

        # 到达终点
        if self.agent_pos == self.goal_pos:
            reward = 100.0
            terminated = True

        return self._get_obs(), reward, terminated, False, {}

    def render(self, mode='human'):
        if mode == 'rgb_array':
            # 在内存中绘制
            surf = pygame.Surface((self.width, self.height))
            surf.fill((255, 255, 255))
            # 画网格线
            for x in range(0, self.width, self.cell_size):
                pygame.draw.line(surf, (220, 220, 220), (x, 0), (x, self.height))
            for y in range(0, self.height, self.cell_size):
                pygame.draw.line(surf, (220, 220, 220), (0, y), (self.width, y))
            # 画障碍物
            for obs in self.obstacles:
                rect = pygame.Rect(obs[0]*self.cell_size, obs[1]*self.cell_size,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(surf, (0, 0, 0), rect)
            # 画目标
            goal_rect = pygame.Rect(self.goal_pos[0]*self.cell_size,
                                    self.goal_pos[1]*self.cell_size,
                                    self.cell_size, self.cell_size)
            pygame.draw.rect(surf, (231, 76, 60), goal_rect)
            # 画智能体
            agent_rect = pygame.Rect(self.agent_pos[0]*self.cell_size,
                                     self.agent_pos[1]*self.cell_size,
                                     self.cell_size, self.cell_size)
            pygame.draw.rect(surf, (46, 204, 113), agent_rect)
            # 转为 numpy 数组并转置为 (height, width, 3)
            view = pygame.surfarray.array3d(surf)
            return view.transpose((1, 0, 2))
        else:
            # human 模式（弹出窗口）
            if self.window is None:
                pygame.init()
                self.window = pygame.display.set_mode((self.width, self.height))
                pygame.display.set_caption("AI Grid Navigation System (16x21)")
                self.clock = pygame.time.Clock()
            self.window.fill((255, 255, 255))
            for x in range(0, self.width, self.cell_size):
                pygame.draw.line(self.window, (220, 220, 220), (x, 0), (x, self.height))
            for y in range(0, self.height, self.cell_size):
                pygame.draw.line(self.window, (220, 220, 220), (0, y), (self.width, y))
            for obs in self.obstacles:
                rect = pygame.Rect(obs[0]*self.cell_size, obs[1]*self.cell_size,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(self.window, (0, 0, 0), rect)
            goal_rect = pygame.Rect(self.goal_pos[0]*self.cell_size,
                                    self.goal_pos[1]*self.cell_size,
                                    self.cell_size, self.cell_size)
            pygame.draw.rect(self.window, (231, 76, 60), goal_rect)
            agent_rect = pygame.Rect(self.agent_pos[0]*self.cell_size,
                                     self.agent_pos[1]*self.cell_size,
                                     self.cell_size, self.cell_size)
            pygame.draw.rect(self.window, (46, 204, 113), agent_rect)
            pygame.display.flip()
            if self.clock:
                self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.window is not None:
            pygame.quit()
            self.window = None