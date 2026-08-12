# GridEnv.py
import gym
from gym import spaces
import numpy as np
from grid_obstacle_const import OBSTACLE_COORDS, GOAL_POS

class GridNavEnv(gym.Env):
    """
    栅格导航环境，观测为4维: [row, col, goal_row, goal_col]
    动作: 0-上, 1-下, 2-左, 3-右
    """
    def __init__(self, goal=None, max_steps=200):
        super(GridNavEnv, self).__init__()
        
        self.rows = 21
        self.cols = 16
        # 如果未传入 goal，则使用常量中定义的目标点
        if goal is None:
            goal = GOAL_POS
        self.goal = goal
        self.max_steps = max_steps
        
        # 障碍集合
        self.obstacles = set(OBSTACLE_COORDS)
        
        # 动作空间
        self.action_space = spaces.Discrete(4)
        
        # 观测空间：4维 [row, col, goal_r, goal_c]
        high = np.array([self.rows-1, self.cols-1, self.rows-1, self.cols-1], dtype=np.int32)
        self.observation_space = spaces.Box(low=0, high=high, shape=(4,), dtype=np.int32)
        
        self.state = None          # 当前 (row, col)
        self.steps = 0
        self.collision_count = 0
        
    def reset(self, start=None):
        """重置环境，返回4维观测"""
        if start is None:
            while True:
                r = np.random.randint(0, self.rows)
                c = np.random.randint(0, self.cols)
                if (r, c) not in self.obstacles and (r, c) != self.goal:
                    break
            start = (r, c)
        self.state = start
        self.steps = 0
        self.collision_count = 0
        return self._get_obs()
    
    def step(self, action):
        """执行动作，返回 (4维观测, reward, done, info)"""
        r, c = self.state
        # 计算下一位置
        if action == 0:    # 上
            nr, nc = max(r-1, 0), c
        elif action == 1:  # 下
            nr, nc = min(r+1, self.rows-1), c
        elif action == 2:  # 左
            nr, nc = r, max(c-1, 0)
        elif action == 3:  # 右
            nr, nc = r, min(c+1, self.cols-1)
        else:
            raise ValueError("Invalid action")
        
        # 碰撞检测
        if (nr, nc) in self.obstacles:
            nr, nc = r, c   # 原地不动
            collision = True
        else:
            collision = False
        
        self.state = (nr, nc)
        self.steps += 1
        if collision:
            self.collision_count += 1
        
        reward = self._compute_reward(nr, nc, collision)
        
        done = False
        if (nr, nc) == self.goal:
            done = True
            reward += 10.0
        elif self.steps >= self.max_steps:
            done = True
        
        info = {
            'collision': collision,
            'steps': self.steps,
            'is_success': (nr, nc) == self.goal
        }
        return self._get_obs(), reward, done, info
    
    def _compute_reward(self, r, c, collision):
        reward = -0.1
        if collision:
            reward -= 5.0
        if (r, c) == self.goal:
            reward += 10.0
        return reward
    
    def _get_obs(self):
        """构造4维观测数组"""
        r, c = self.state
        gr, gc = self.goal
        return np.array([r, c, gr, gc], dtype=np.int32)
    
    def render(self, mode='human'):
        """简单的控制台渲染，不会导致 sb3 报错"""
        if mode == 'human':
            r, c = self.state
            gr, gc = self.goal
            print(f"位置: ({r},{c})  目标: ({gr},{gc})  步数: {self.steps}")
    
    def close(self):
        pass
