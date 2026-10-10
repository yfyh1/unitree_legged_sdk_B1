import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import matplotlib.pyplot as plt
except ImportError:
    install_package("matplotlib")
    import matplotlib.pyplot as plt

try:
    import numpy as np
except ImportError:
    install_package("numpy")
    import numpy as np

# 解决中文乱码
# plt.rcParams["font.family"] = ["SimHei", "Microsoft YaHei", "WenQuanYi Micro Hei"]
# plt.rcParams["axes.unicode_minus"] = False
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

# 原始障碍数据：这里元组实际上是 (x, y)
black_cells_origin = {
    # x=0
    (0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),(0,10),(0,11),(0,12),(0,13),(0,14),
    # x=1
    (1,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(1,10),(1,11),(1,12),(1,13),(1,14),
    # x=2
    (2,0),(2,4),(2,5),(2,6),(2,7),(2,8),(2,9),(2,10),(2,11),(2,12),(2,13),(2,14),
    # x=3
    (3,0),(3,4),(3,5),(3,6),(3,7),(3,8),(3,9),(3,10),(3,11),(3,18),(3,19),
    # x=4
    (4,0),(4,4),(4,5),(4,6),(4,7),(4,8),(4,9),(4,10),(4,11),(4,18),(4,19),
    # x=5
    (5,0),(5,4),(5,5),(5,6),(5,7),(5,8),(5,9),(5,10),(5,11),(5,15),(5,16),(5,17),(5,18),(5,19),
    # x=6
    (6,0),(6,4),(6,5),(6,6),(6,7),(6,8),(6,9),(6,10),(6,11),(6,15),(6,16),(6,17),(6,18),(6,19),
    # x=7
    (7,0),(7,1),(7,15),(7,16),(7,17),(7,18),(7,19),
    # x=8
    (8,0),(8,1),(8,15),(8,16),(8,17),(8,18),(8,19),
    # x=9
    (9,0),(9,1),(9,15),(9,16),(9,17),(9,18),(9,19),
    # x=10
    (10,0),(10,1),(10,2),(10,15),(10,16),(10,17),(10,18),(10,19),
    # x=11
    (11,0),(11,1),(11,2),(11,15),(11,16),(11,17),(11,18),(11,19),
    # x=12
    (12,0),(12,1),(12,2),(12,18),(12,19),
    # x=13
    (13,12),
    # x=14 无黑色
    # x=15
    (15,4),(15,5),(15,6),(15,7),(15,10),(15,18),(15,19)
}

# ===== 关键修正 =====
# 用户期望：x 轴 0~15 (宽16)，y 轴 0~20 (高21)
W = 25  # x 轴长度
H = 30  # y 轴长度

grid = np.ones((H, W))  # 注意：imshow 中第一维是行(y)，第二维是列(x)

for x, y in black_cells_origin:  # 这里的 x, y 对应原数据的第一个和第二个元素
    if 0 <= x < W and 0 <= y < H:
        x_mirror = 15 - x  # 水平镜像（左右翻转）
        # y_mirror = 20 - y  # 如果你想要垂直镜像（上下翻转），用这行替换上面
        grid[y, x_mirror] = 0

plt.figure(figsize=(8.5, 11))
# origin='lower' 表示 y=0 在底部，符合常规笛卡尔坐标系；如果想让 y=0 在顶部，改为 origin='upper'
plt.imshow(grid, cmap="gray", vmin=0, vmax=1, origin="lower")
plt.grid(lw=0.4, c="#777777")

# 刻度设置：x轴0~15，y轴0~20
plt.xticks(np.arange(W))
plt.yticks(np.arange(H))

plt.xlabel("x (0~15)")
plt.ylabel("y (0~20)")
plt.title("栅格地图 | 黑色为障碍，白色为通路")
plt.tight_layout()
plt.show()