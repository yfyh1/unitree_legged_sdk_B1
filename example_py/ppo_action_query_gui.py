"""
PPO 动作查询工具（GUI 版）
功能：弹窗输入坐标 (x, y) → 调用 model_interface.get_action_from_position
      → 弹窗输出 PPO 选择的动作（上/下/左/右）
用途：调试、演示、真机部署前的人工验证

使用方法：
    双击运行，或在命令行执行：
    python ppo_action_query_gui.py
"""
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox
from pathlib import Path
import tkinter.messagebox
tkinter.messagebox = lambda *args, **kwargs: print("Error:", args, kwargs) # 临时重定向，或者干脆注释掉弹窗代码
# ========== 将项目根目录加入路径，确保能 import rl_ppo_module ==========
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# ========== 导入 PPO 模型接口 ==========
from rl_ppo_module.model_interface import get_action_from_position

# ========== 动作映射 ==========
ACTION_NAMES = {0: "↑ 上 (forward)", 1: "↓ 下 (down)", 2: "← 左 (left)", 3: "→ 右 (right)"}
ACTION_SHORT = {0: "↑上", 1: "↓下", 2: "←左", 3: "→右"}

# ========== 坐标范围（与 GridEnv 保持一致） ==========
X_MIN, X_MAX = 0, 15
Y_MIN, Y_MAX = 0, 20


def query_action_gui():
    """
    主交互逻辑：
    1. 弹窗输入 X
    2. 弹窗输入 Y
    3. 弹窗输出 PPO 动作
    4. 询问是否继续
    """
    # ---- 隐藏 tkinter 主窗口 ----
    root = tk.Tk()
    root.withdraw()

    # ---- 欢迎 ----
    messagebox.showinfo(
        "PPO 动作查询工具",
        "欢迎使用 PPO 导航策略查询工具\n\n"
        "请输入当前栅格坐标 (x, y)\n"
        f"x 范围: {X_MIN}~{X_MAX}\n"
        f"y 范围: {Y_MIN}~{Y_MAX}\n\n"
        "程序将调用训练好的 PPO 模型\n"
        "返回建议的下一步动作方向",
    )

    while True:
        try:
            # ---- 弹窗 1：输入 X ----
            x_str = simpledialog.askstring(
                "输入 X 坐标",
                f"请输入 X（列号，范围 {X_MIN}~{X_MAX}）：\n\n"
                "提示：X 越大越靠右",
                initialvalue="12",
            )
            if x_str is None:  # 用户点取消
                break
            x = int(x_str.strip())

            # ---- 弹窗 2：输入 Y ----
            y_str = simpledialog.askstring(
                "输入 Y 坐标",
                f"请输入 Y（行号，范围 {Y_MIN}~{Y_MAX}）：\n\n"
                "提示：Y 越大越靠上",
                initialvalue="1",
            )
            if y_str is None:
                break
            y = int(y_str.strip())

            # ---- 合法性校验 ----
            if not (X_MIN <= x <= X_MAX):
                messagebox.showerror("输入错误", f"X 超出范围！应为 {X_MIN}~{X_MAX}")
                continue
            if not (Y_MIN <= y <= Y_MAX):
                messagebox.showerror("输入错误", f"Y 超出范围！应为 {Y_MIN}~{Y_MAX}")
                continue

            # ---- 调用 PPO 模型 ----
            action_id = get_action_from_position(x, y)
            action_name = ACTION_NAMES.get(action_id, f"未知动作({action_id})")
            action_short = ACTION_SHORT.get(action_id, "?")

            # ---- 弹窗 3：输出结果 ----
            result = (
                f"📍 当前位置: ({x}, {y})\n"
                f"🤖 PPO 选择动作: {action_name}\n\n"
                f"  动作 ID = {action_id}\n\n"
                f"下一步将向 {action_short} 移动一格"
            )
            messagebox.showinfo("PPO 动作决策结果", result)

            # ---- 弹窗 4：是否继续 ----
            again = messagebox.askyesno("继续查询？", "是否再查询另一个位置？")
            if not again:
                break

        except ValueError:
            messagebox.showerror("输入错误", "请输入整数！")
        except Exception as e:
            messagebox.showerror("运行错误", f"调用 PPO 模型时出错：\n{type(e).__name__}: {e}")
            break

    # ---- 结束 ----
    messagebox.showinfo("结束", "PPO 动作查询工具已退出\n\n感谢使用！")
    root.destroy()


# ========== 命令行批量测试模式（无 GUI 时） ==========
def batch_test(coords):
    """
    批量测试模式：不弹窗，直接打印结果
    用法：python ppo_action_query_gui.py --batch 12,1 5,5 1,18
    """
    print("=" * 55)
    print("  PPO 动作查询工具 - 批量测试模式")
    print("=" * 55)
    print(f"  {'位置(x,y)':<14} {'动作ID':<8} {'方向'}")
    print("-" * 55)

    for x, y in coords:
        action_id = get_action_from_position(x, y)
        direction = ACTION_SHORT.get(action_id, "?")
        print(f"  ({x:2d},{y:2d})           {action_id:<8} {direction}")

    print("=" * 55)


if __name__ == "__main__":
    # ---- 检查是否有命令行参数 ----
    if len(sys.argv) > 2 and sys.argv[1] == "--batch":
        # 批量模式：python ppo_action_query_gui.py --batch 12,1 5,5
        coords = []
        for arg in sys.argv[2:]:
            parts = arg.split(",")
            coords.append((int(parts[0]), int(parts[1])))
        batch_test(coords)
    else:
        # GUI 模式（默认）
        query_action_gui()
