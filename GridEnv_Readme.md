# GridNavEnv 接口文档

## 环境描述
- 尺寸：21行 × 16列，坐标 (row, col)，row∈[0,20], col∈[0,15]
- 障碍物：硬编码于 `grid_obstacle_const.py`
- 目标：默认由 `GOAL_POS` 常量定义（当前为 (1,8)），可在初始化时通过 `goal` 参数指定

## 状态空间
- `observation_space`: Box(4,)，表示 [row, col, goal_row, goal_col]，整型

## 动作空间
- Discrete(4)：0-上, 1-下, 2-左, 3-右（边界内移动，越界则停在原地）

## 接口
- `reset(start=None)` -> obs (ndarray, 4维)
  - 若未指定起点，随机生成非障碍、非目标位置
- `step(action)` -> (obs, reward, done, info)
  - reward: 每步-0.1，碰撞-5，到达目标+10（额外）
  - info: 包含 `collision`(bool), `steps`, `is_success`

## 使用示例（与 PPO 对接）
```python
from env_module.GridEnv import GridNavEnv
env = GridNavEnv(goal=(20,15))   # 设定目标
obs = env.reset()                # obs.shape = (4,)
obs, reward, done, info = env.step(0)
