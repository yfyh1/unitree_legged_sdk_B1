# env_test_demo.py
from GridEnv import GridNavEnv
import numpy as np
from grid_render import render_grid, save_trajectory_gif
from grid_obstacle_const import GOAL_POS

def test_env():

    env = GridNavEnv(goal=(20,15))  
    obs = env.reset()
    print(f"初始观测: {obs}  (格式: [row, col, goal_r, goal_c])")
    
    trajectory = [tuple(obs[:2])]
    done = False
    total_reward = 0
    step_count = 0
    
    while not done:
        action = np.random.randint(0, 4)
        obs, reward, done, info = env.step(action)
        trajectory.append(tuple(obs[:2]))
        total_reward += reward
        step_count += 1
        print(f"Step {step_count}: action={action}, obs={obs}, reward={reward:.2f}, done={done}")
        if step_count > 300:
            break
    
    print(f"总步数: {step_count}, 总奖励: {total_reward:.2f}, 成功: {info['is_success']}")
    
    # 渲染
    render_grid(agent_pos=tuple(obs[:2]), goal=env.goal, trajectory=trajectory, save_path='final_state.png')
    save_trajectory_gif(trajectory, env.goal, gif_path='trajectory.gif')
    
    # 测试边界碰撞
    env.reset(start=(0,0))
    obs, _, _, _ = env.step(0)
    assert tuple(obs[:2]) == (0,0), "边界碰撞测试失败"
    print("边界碰撞测试通过")
    
    # 测试障碍碰撞（需要已知障碍，例如 (20,0) 是障碍）
    env.reset(start=(20,1))
    obs, _, _, info = env.step(3)  # 向右撞 (20,0)
    if (20,0) in env.obstacles:
        assert tuple(obs[:2]) == (20,1), "障碍碰撞测试失败"
        assert info['collision'] == True
        print("障碍碰撞测试通过")
    else:
        print("注意：障碍 (20,0) 不存在，请检查常量")

if __name__ == "__main__":
    test_env()
