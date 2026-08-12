# grid_obstacle_const.py
# 坐标系：原始地图用 (x, y)，环境内部统一用 (row, col) = (y, x)
MAP_WIDTH = 16   # x 0~15
MAP_HEIGHT = 21  # y 0~20

OBSTACLE_COORDS = set()

# y=20
for x in [0,1,2,3,4,5,6,7,13,14,15]:
    OBSTACLE_COORDS.add((20, x))
# y=19
for x in [1,2,3,4,5,6,7,13,14,15]:
    OBSTACLE_COORDS.add((19, x))
# y=18
for x in [1,2,3,4,5,6,7,13,14,15]:
    OBSTACLE_COORDS.add((18, x))
# y=17
for x in [0,1,2,3,4,5,6,7,13,14,15]:
    OBSTACLE_COORDS.add((17, x))
# y=16
for x in [1,2,3,4,5,6,7,13,14,15]:
    OBSTACLE_COORDS.add((16, x))
# y=15
for x in [1,2,3,4,5,6,7,13,14,15]:
    OBSTACLE_COORDS.add((15, x))
# y=14
for x in [13,14,15]:
    OBSTACLE_COORDS.add((14, x))
# y=13
for x in [14,15]:
    OBSTACLE_COORDS.add((13, x))
# y=12
for x in [14,15]:
    OBSTACLE_COORDS.add((12, x))
# y=11
for x in [4,5,6]:
    OBSTACLE_COORDS.add((11, x))
# y=10
for x in [4,5,6]:
    OBSTACLE_COORDS.add((10, x))
# y=9
OBSTACLE_COORDS.add((9, 0))
OBSTACLE_COORDS.add((9, 14))
# y=8
OBSTACLE_COORDS.add((8, 0))
OBSTACLE_COORDS.add((8, 15))
# y=7
OBSTACLE_COORDS.add((7, 0))
OBSTACLE_COORDS.add((7, 15))
# y=6
OBSTACLE_COORDS.add((6, 0))
OBSTACLE_COORDS.add((6, 15))
# y=5
OBSTACLE_COORDS.add((5, 0))
OBSTACLE_COORDS.add((5, 14))
OBSTACLE_COORDS.add((5, 15))
# y=4
OBSTACLE_COORDS.add((4, 0))
OBSTACLE_COORDS.add((4, 15))
# y=3
OBSTACLE_COORDS.add((3, 0))
OBSTACLE_COORDS.add((3, 15))
# y=2
OBSTACLE_COORDS.add((2, 0))
OBSTACLE_COORDS.add((2, 15))
# y=1
for x in [5,6,7,14]:
    OBSTACLE_COORDS.add((1, x))
# y=0
for x in [0,1,2,3,4,5,6,7,8,9,10,11,13,14,15]:
    OBSTACLE_COORDS.add((0, x))

# 目标点
GOAL_POS = (1, 8)   # (row, col) = (y, x)

def get_obstacle_map():
    grid = [[0]*MAP_WIDTH for _ in range(MAP_HEIGHT)]
    for r, c in OBSTACLE_COORDS:
        grid[r][c] = 1
    return grid
