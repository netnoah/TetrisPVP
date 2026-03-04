"""
游戏棋盘类
管理棋盘状态、碰撞检测、消行等核心逻辑
"""

from typing import List, Tuple, Optional

from src.config import (
    BOARD_WIDTH, BOARD_HEIGHT, COLORS,
    ATTACK_FORMULA
)
from src.models.tetromino import Tetromino


class Board:
    """游戏棋盘类"""

    def __init__(self):
        """初始化空棋盘"""
        # 棋盘网格：None 表示空，字符串表示方块类型（用于获取颜色）
        self.grid: List[List[Optional[str]]] = [
            [None for _ in range(BOARD_WIDTH)]
            for _ in range(BOARD_HEIGHT)
        ]
        self.lines_cleared = 0  # 本次消行数（用于计算攻击）

    def is_valid_position(self, tetromino: Tetromino) -> bool:
        """
        检查方块位置是否有效（不越界、不碰撞）

        Args:
            tetromino: 要检查的方块

        Returns:
            True 如果位置有效
        """
        for row, col in tetromino.absolute_cells:
            # 检查边界
            if col < 0 or col >= BOARD_WIDTH:
                return False
            if row >= BOARD_HEIGHT:
                return False
            # 检查与已有方块的碰撞（允许在顶部上方）
            if row >= 0 and self.grid[row][col] is not None:
                return False
        return True

    def can_rotate(self, tetromino: Tetromino, direction: int = 1) -> bool:
        """
        检查方块是否可以旋转

        Args:
            tetromino: 要旋转的方块
            direction: 1 为顺时针，-1 为逆时针

        Returns:
            True 如果可以旋转
        """
        # 创建临时方块进行测试
        test_tetromino = tetromino.copy()
        test_tetromino.rotation = (test_tetromino.rotation + direction) % 4
        return self.is_valid_position(test_tetromino)

    def place_tetromino(self, tetromino: Tetromino) -> None:
        """
        将方块放置到棋盘上

        Args:
            tetromino: 要放置的方块
        """
        for row, col in tetromino.absolute_cells:
            if 0 <= row < BOARD_HEIGHT and 0 <= col < BOARD_WIDTH:
                self.grid[row][col] = tetromino.type

    def clear_lines(self) -> int:
        """
        清除已填满的行

        Returns:
            清除的行数
        """
        lines_to_clear = []

        # 找出所有满行
        for row in range(BOARD_HEIGHT):
            if all(cell is not None for cell in self.grid[row]):
                lines_to_clear.append(row)

        # 删除满行，在顶部添加空行
        for row in lines_to_clear:
            del self.grid[row]
            self.grid.insert(0, [None for _ in range(BOARD_WIDTH)])

        self.lines_cleared = len(lines_to_clear)
        return self.lines_cleared

    def get_attack_lines(self) -> int:
        """
        根据消行数计算应该发送给对手的垃圾行数
        获取后重置消行数，避免重复发送

        Returns:
            垃圾行数量
        """
        attack = ATTACK_FORMULA.get(self.lines_cleared, 0)
        self.lines_cleared = 0  # 重置，避免重复发送
        return attack

    def add_garbage_rows(self, count: int) -> bool:
        """
        在底部添加垃圾行

        Args:
            count: 要添加的垃圾行数量

        Returns:
            True 如果游戏未结束，False 如果垃圾行导致游戏结束
        """
        if count <= 0:
            return True

        import random

        # 检查顶部是否有方块会被推出（游戏结束）
        for row in range(count):
            for col in range(BOARD_WIDTH):
                if self.grid[row][col] is not None:
                    return False  # 游戏结束

        # 删除顶部的行
        for _ in range(count):
            self.grid.pop(0)

        # 在底部添加垃圾行
        for _ in range(count):
            # 垃圾行有一个随机空洞
            hole_position = random.randint(0, BOARD_WIDTH - 1)
            garbage_row = ['garbage' for _ in range(BOARD_WIDTH)]
            garbage_row[hole_position] = None
            self.grid.append(garbage_row)

        return True

    def get_cell(self, row: int, col: int) -> Optional[str]:
        """
        获取指定位置的单元格内容

        Args:
            row: 行号
            col: 列号

        Returns:
            方块类型或 None
        """
        if 0 <= row < BOARD_HEIGHT and 0 <= col < BOARD_WIDTH:
            return self.grid[row][col]
        return None

    def get_ghost_position(self, tetromino: Tetromino) -> int:
        """
        计算方块的幽灵位置（硬降后的行号）

        Args:
            tetromino: 当前方块

        Returns:
            幽灵方块的顶部行号
        """
        ghost = tetromino.copy()
        while self.is_valid_position(ghost):
            ghost.move_down()
        # 回退一步（因为最后一步无效）
        ghost.move(-1, 0)
        return ghost.row

    def is_game_over(self, tetromino: Tetromino) -> bool:
        """
        检查游戏是否结束

        Args:
            tetromino: 新生成的方块

        Returns:
            True 如果游戏结束
        """
        # 如果新方块无法放置在任何有效位置，游戏结束
        return not self.is_valid_position(tetromino)

    def reset(self) -> None:
        """重置棋盘"""
        self.grid = [
            [None for _ in range(BOARD_WIDTH)]
            for _ in range(BOARD_HEIGHT)
        ]
        self.lines_cleared = 0

    def __repr__(self) -> str:
        """打印棋盘状态（用于调试）"""
        result = []
        for row in self.grid:
            line = ''.join(['#' if cell else '.' for cell in row])
            result.append(line)
        return '\n'.join(result)
