import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from stable_baselines3 import PPO
from env_module.GridEnv import GridNavEnv
import torch

# ================== 中文字体设置 ==================
plt.rcParams['font.sans-serif'] = [
    'SimHei',
    'Microsoft YaHei',
    'Noto Sans CJK SC',
    'WenQuanYi Zen Hei',
    'WenQuanYi Micro Hei',
    'Noto Sans CJK SC',
    'AR PL UMing CN',
    'Droid Sans Fallback',
    'Arial Unicode MS'
]
plt.rcParams['axes.unicode_minus'] = False


def simulate_path(env, model, start_pos, goal_pos, max_steps=500):
    """
    模拟智能体按策略从起点走到终点，记录路径点。
    使用 8 维观测值。
    """
    env.reset()
    env.agent_pos = start_pos[:]
    env.goal_pos = goal_pos[:]
    obs = env._get_obs()          # 8 维观测
    path = [tuple(start_pos)]
    done = False
    step = 0

    while not done and step < max_steps:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        path.append(tuple(env.agent_pos))
        step += 1

    return path


def visualize_policy():
    # ========== 1. 加载模型 ==========
    model_path = Path(__file__).parent.parent / "models" / "ppo_grid_model.zip"
    if not model_path.exists():
        print(f"❌ 模型文件不存在：{model_path}")
        return
    model = PPO.load(str(model_path))
    print("✅ 模型加载成功")

    # ========== 2. 创建环境并获取参数 ==========
    env = GridNavEnv()
    env.reset()
    grid_x, grid_y = env.grid_size_x, env.grid_size_y
    goal = env.goal_pos          # 目标点
    start = env.agent_pos        # 随机起点
    obstacles = set(env.obstacles)
    print(f"地图尺寸: {grid_x} x {grid_y}, 终点: {goal}, 起点: {start}")

    # ========== 3. 计算每个格子的动作概率 ==========
    action_probs = np.zeros((grid_y, grid_x, 4))

    for y in range(grid_y):
        for x in range(grid_x):
            # 构造 8 维观测值: [x, y, goal_x, goal_y, up, down, left, right]
            # 坐标轴：左下角原点，x向右，y向上
            # up = y+1 方向，down = y-1 方向
            up = 0 if (y + 1 >= grid_y or (x, y + 1) in obstacles) else 1
            down = 0 if (y - 1 < 0 or (x, y - 1) in obstacles) else 1
            left = 0 if (x - 1 < 0 or (x - 1, y) in obstacles) else 1
            right = 0 if (x + 1 >= grid_x or (x + 1, y) in obstacles) else 1
            obs = np.array([x, y, goal[0], goal[1], up, down, left, right], dtype=np.float32)

            obs_tensor = model.policy.obs_to_tensor(obs)[0]
            with torch.no_grad():
                dist = model.policy.get_distribution(obs_tensor)
                probs = dist.distribution.probs
            action_probs[y, x] = probs.cpu().numpy()[0]

    best_actions = np.argmax(action_probs, axis=-1)

    # ========== 4. 模拟真实路径 ==========
    path = simulate_path(env, model, start, goal)
    path_x = [p[0] for p in path]
    path_y = [p[1] for p in path]

    # =========================================================
    # 5. 绘制主图：决策地图
    # =========================================================
    action_names = ['↑ 上', '↓ 下', '← 左', '→ 右']
    cmap = ListedColormap(['#377eb8', '#e41a1c', '#4daf4a', '#984ea3'])

    fig, ax = plt.subplots(figsize=(10, 12))
    im = ax.imshow(best_actions, origin='lower', cmap=cmap, vmin=-0.5, vmax=3.5)

    # ---- 画障碍物（黑色） ----
    for (ox, oy) in obstacles:
        rect = plt.Rectangle((ox - 0.5, oy - 0.5), 1, 1,
                             facecolor='black', edgecolor='black')
        ax.add_patch(rect)

    # ---- 起点（白点）和终点（黄星） ----
    ax.plot(start[0], start[1], 'wo', markersize=10, markeredgecolor='black')
    ax.plot(goal[0], goal[1], 'y*', markersize=15, markeredgecolor='black')

    # ---- 绘制路径（红色虚线） ----
    if len(path) > 1:
        ax.plot(path_x, path_y, 'r--', linewidth=2.5, label='行走路径')

    # ---- 绘制动作箭头（跳过障碍物格子） ----
    # 方向向量：上=(0,1)，下=(0,-1)，左=(-1,0)，右=(1,0)
    dirs = [(0, 1), (0, -1), (-1, 0), (1, 0)]
    arrow_len = 0.3

    for y in range(grid_y):
        for x in range(grid_x):
            if (x, y) in obstacles:
                continue
            act = best_actions[y, x]
            dx, dy = dirs[act]
            ax.arrow(x, y, dx * arrow_len, dy * arrow_len,
                     head_width=0.15, head_length=0.15,
                     fc='white', ec='black', linewidth=1,
                     alpha=0.8, length_includes_head=True)

    # ---- 坐标轴与网格 ----
    xticks = np.arange(0, grid_x, 5)
    yticks = np.arange(0, grid_y, 5)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.set_xticklabels(xticks)
    ax.set_yticklabels(yticks)
    ax.set_xlabel('X 坐标')
    ax.set_ylabel('Y 坐标')
    ax.set_title('PPO 策略决策地图 (最优动作 + 路径)', fontsize=16)

    # ---- 图例 ----
    patches = [mpatches.Patch(color=cmap(i), label=action_names[i]) for i in range(4)]
    patches.append(mpatches.Patch(color='none', label='___ 路径 (红色虚线)'))
    ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left')

    # ---- 网格线 ----
    ax.set_xticks(np.arange(-0.5, grid_x, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, grid_y, 1), minor=True)
    ax.grid(which='minor', color='w', linestyle='-', linewidth=0.5)

    plt.tight_layout()
    plt.savefig('policy_decision_map.png', dpi=150)
    plt.show()

    # =========================================================
    # 6. 子图：各动作概率热力图
    # =========================================================
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    for i, ax in enumerate(axes.flat):
        im = ax.imshow(action_probs[:, :, i], origin='lower',
                       cmap='viridis', vmin=0, vmax=1)
        ax.set_title(f'动作 "{action_names[i]}" 的概率')
        ax.set_xticks([])
        ax.set_yticks([])

        # 叠加障碍物（黑色，半透明）
        for (ox, oy) in obstacles:
            rect = plt.Rectangle((ox - 0.5, oy - 0.5), 1, 1,
                                 facecolor='black', edgecolor='black')
            ax.add_patch(rect)

        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    plt.suptitle('各动作概率空间分布', fontsize=16)
    plt.tight_layout()
    plt.savefig('policy_probability_maps.png', dpi=150)
    plt.show()


if __name__ == "__main__":
    visualize_policy()