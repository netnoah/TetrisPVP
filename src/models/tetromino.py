"""
俄罗斯方块类
定义方块的形状、旋转和移动
"""

import random
from typing import List, Tuple

from src.config import TETROMINOES, TETROMINO_TYPES, COLORS


class Tetromino:
    """俄罗斯方块类"""

    def __init__(self, shape_type: str = None):
        """
        初始化方块

        Args:
            shape_type: 方块类型 ('I', 'O', 'T', 'S', 'Z', 'J', 'L')
                        如果为 None，则随机生成
        """
        if shape_type is None:
            shape_type = random.choice(TETROMINO_TYPES)

        self.type = shape_type
        self.rotation = 0  # 当前旋转状态 (0-3)
        self.shapes = TETROMINOES[shape_type]  # 四种旋转状态
        self.color = COLORS[shape_type]

        # 方块在棋盘上的位置（左上角）
        # 初始位置在棋盘顶部中央
        self.row = 0
        self.col = 0

    @property
    def cells(self) -> List[Tuple[int, int]]:
        """
        获取当前旋转状态下，方块的四个单元格坐标

        Returns:
            包含4个 (row, col) 元组的列表
        """
        return self.shapes[self.rotation]

    @property
    def absolute_cells(self) -> List[Tuple[int, int]]:
        """
        获取方块在棋盘上的绝对坐标

        Returns:
            包含4个 (row, col) 元组的列表，表示在棋盘上的实际位置
        """
        return [(self.row + r, self.col + c) for r, c in self.cells]

    def rotate_cw(self) -> None:
        """顺时针旋转"""
        self.rotation = (self.rotation + 1) % 4

    def rotate_ccw(self) -> None:
        """逆时针旋转"""
        self.rotation = (self.rotation - 1) % 4

    def move(self, dr: int, dc: int) -> None:
        """
        移动方块

        Args:
            dr: 行方向的移动量（正数向下）
            dc: 列方向的移动量（正数向右）
        """
        self.row += dr
        self.col += dc

    def move_left(self) -> None:
        """向左移动"""
        self.move(0, -1)

    def move_right(self) -> None:
        """向右移动"""
        self.move(0, 1)

    def move_down(self) -> None:
        """向下移动"""
        self.move(1, 0)

    def get_rotated_cells(self, direction: int = 1) -> List[Tuple[int, int]]:
        """
        获取旋转后的单元格坐标（不实际旋转）

        Args:
            direction: 1 为顺时针，-1 为逆时针

        Returns:
            旋转后的单元格相对坐标列表
        """
        new_rotation = (self.rotation + direction) % 4
        return self.shapes[new_rotation]

    def copy(self) -> 'Tetromino':
        """
        创建方块的副本

        Returns:
            新的 Tetromino 对象
        """
        new_tetromino = Tetromino(self.type)
        new_tetromino.rotation = self.rotation
        new_tetromino.row = self.row
        new_tetromino.col = self.col
        return new_tetromino

    def __repr__(self) -> str:
        return f"Tetromino({self.type}, pos=({self.row}, {self.col}), rot={self.rotation})"


class TetrominoBag:
    """
    方块袋 - 实现7-bag随机系统
    确保每7个方块中包含所有7种类型各一个
    """

    def __init__(self):
        self.bag: List[str] = []
        self._refill_bag()

    def _refill_bag(self) -> None:
        """重新填充方块袋"""
        self.bag = TETROMINO_TYPES.copy()
        random.shuffle(self.bag)

    def next(self) -> str:
        """
        获取下一个方块类型

        Returns:
            方块类型字符串
        """
        if not self.bag:
            self._refill_bag()
        return self.bag.pop()

    def peek(self, count: int = 1) -> List[str]:
        """
        预览接下来的几个方块类型

        Args:
            count: 要预览的数量

        Returns:
            方块类型列表
        """
        result = []
        temp_bag = self.bag.copy()

        for i in range(count):
            if not temp_bag:
                temp_bag = TETROMINO_TYPES.copy()
                random.shuffle(temp_bag)
            result.append(temp_bag.pop())

        return result
