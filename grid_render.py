# grid_render.py
import matplotlib.pyplot as plt
import numpy as np
from grid_obstacle_const import OBSTACLE_COORDS, GOAL_POS
import imageio

def render_grid(agent_pos=None, goal=None, trajectory=None, save_path=None):
    if goal is None:
        goal = GOAL_POS
    rows, cols = 21, 16
    grid = np.zeros((rows, cols))
    for r, c in OBSTACLE_COORDS:
        grid[r, c] = 1
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(grid, cmap='gray', origin='upper', interpolation='none')
    
    if trajectory:
        traj_arr = np.array(trajectory)
        ax.plot(traj_arr[:, 1], traj_arr[:, 0], 'b-', linewidth=2, alpha=0.7, label='轨迹')
    
    ax.plot(goal[1], goal[0], 'g*', markersize=15, label='目标')
    if agent_pos:
        ax.plot(agent_pos[1], agent_pos[0], 'ro', markersize=10, label='智能体')
    
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
    ax.tick_params(which='minor', size=0)
    ax.set_xlim(-0.5, cols-0.5)
    ax.set_ylim(rows-0.5, -0.5)
    ax.legend()
    ax.set_title('Grid World (21x16)')
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"图片保存至 {save_path}")
    else:
        plt.show()
    plt.close()

def save_trajectory_gif(trajectory, goal=None, gif_path='trajectory.gif', fps=2):
    if goal is None:
        goal = GOAL_POS
    frames = []
    rows, cols = 21, 16
    for i in range(1, len(trajectory)+1):
        fig, ax = plt.subplots(figsize=(8, 6))
        grid = np.zeros((rows, cols))
        for r, c in OBSTACLE_COORDS:
            grid[r, c] = 1
        ax.imshow(grid, cmap='gray', origin='upper', interpolation='none')
        traj_part = trajectory[:i]
        if traj_part:
            arr = np.array(traj_part)
            ax.plot(arr[:, 1], arr[:, 0], 'b-', linewidth=2, alpha=0.7)
        ax.plot(goal[1], goal[0], 'g*', markersize=15)
        cur = trajectory[i-1]
        ax.plot(cur[1], cur[0], 'ro', markersize=10)
        ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
        ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
        ax.set_xlim(-0.5, cols-0.5)
        ax.set_ylim(rows-0.5, -0.5)
        ax.tick_params(which='minor', size=0)
        plt.close(fig)
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames.append(image)
    imageio.mimsave(gif_path, frames, fps=fps)
    print(f"GIF已保存至 {gif_path}")

# 独立测试
if __name__ == "__main__":
    render_grid()
    traj = [(0,0), (1,0), (2,0), (3,1), (4,2), (5,3)]
    render_grid(agent_pos=(5,3), trajectory=traj, save_path='demo_map.png')
