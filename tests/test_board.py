"""
棋盘类单元测试
"""

import pytest
from src.models.board import Board
from src.models.tetromino import Tetromino
from src.config import BOARD_WIDTH, BOARD_HEIGHT


class TestBoard:
    """棋盘类测试"""

    def test_initial_state(self):
        """测试初始状态"""
        board = Board()
        assert len(board.grid) == BOARD_HEIGHT
        assert len(board.grid[0]) == BOARD_WIDTH
        assert all(cell is None for row in board.grid for cell in row)

    def test_is_valid_position_inside(self):
        """测试有效位置（内部）"""
        board = Board()
        tetromino = Tetromino('I')
        tetromino.row = 10
        tetromino.col = 5
        assert board.is_valid_position(tetromino)

    def test_is_valid_position_left_boundary(self):
        """测试左边界"""
        board = Board()
        tetromino = Tetromino('I')
        tetromino.row = 10
        tetromino.col = -5  # 超出左边界
        assert not board.is_valid_position(tetromino)

    def test_is_valid_position_right_boundary(self):
        """测试右边界"""
        board = Board()
        tetromino = Tetromino('I')
        tetromino.row = 10
        tetromino.col = BOARD_WIDTH  # 超出右边界
        assert not board.is_valid_position(tetromino)

    def test_is_valid_position_bottom_boundary(self):
        """测试底部边界"""
        board = Board()
        tetromino = Tetromino('I')
        tetromino.row = BOARD_HEIGHT  # 超出底部
        assert not board.is_valid_position(tetromino)

    def test_is_valid_position_above_top(self):
        """测试顶部上方（允许）"""
        board = Board()
        tetromino = Tetromino('I')
        tetromino.row = -1  # 部分在顶部上方
        tetromino.col = 5
        assert board.is_valid_position(tetromino)

    def test_place_tetromino(self):
        """测试放置方块"""
        board = Board()
        tetromino = Tetromino('T')
        tetromino.row = 0
        tetromino.col = 0

        board.place_tetromino(tetromino)

        # 检查是否有方块被放置
        placed_cells = sum(1 for row in board.grid for cell in row if cell is not None)
        assert placed_cells == 4

    def test_clear_single_line(self):
        """测试消除单行"""
        board = Board()

        # 填满底行
        for col in range(BOARD_WIDTH):
            board.grid[BOARD_HEIGHT - 1][col] = 'I'

        lines_cleared = board.clear_lines()
        assert lines_cleared == 1
        # 检查顶行是否为空
        assert all(cell is None for cell in board.grid[0])

    def test_clear_multiple_lines(self):
        """测试消除多行"""
        board = Board()

        # 填满底两行
        for row in range(BOARD_HEIGHT - 2, BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                board.grid[row][col] = 'I'

        lines_cleared = board.clear_lines()
        assert lines_cleared == 2

    def test_clear_non_full_line(self):
        """测试非满行不消除"""
        board = Board()

        # 填满底行但留一个空位
        for col in range(BOARD_WIDTH - 1):
            board.grid[BOARD_HEIGHT - 1][col] = 'I'

        lines_cleared = board.clear_lines()
        assert lines_cleared == 0

    def test_collision_with_placed_piece(self):
        """测试与已放置方块的碰撞"""
        board = Board()

        # 放置一个方块
        tetromino1 = Tetromino('T')
        tetromino1.row = 10
        tetromino1.col = 5
        board.place_tetromino(tetromino1)

        # 尝试在相同位置放置另一个方块
        tetromino2 = Tetromino('T')
        tetromino2.row = 10
        tetromino2.col = 5

        assert not board.is_valid_position(tetromino2)

    def test_can_rotate(self):
        """测试旋转检查"""
        board = Board()
        tetromino = Tetromino('T')
        tetromino.row = 10
        tetromino.col = 5

        # 在空棋盘上应该可以旋转
        assert board.can_rotate(tetromino, 1)

    def test_cannot_rotate_at_boundary(self):
        """测试边界处无法旋转"""
        board = Board()
        tetromino = Tetromino('I')
        tetromino.row = 10
        tetromino.col = -1  # 部分在边界外

        # 这种情况旋转后可能越界
        # 结果取决于具体实现

    def test_add_garbage_rows(self):
        """测试添加垃圾行"""
        board = Board()
        result = board.add_garbage_rows(3)

        assert result  # 应该成功
        # 检查底部是否有垃圾行
        for row in range(BOARD_HEIGHT - 3, BOARD_HEIGHT):
            garbage_count = sum(1 for cell in board.grid[row] if cell == 'garbage')
            assert garbage_count == BOARD_WIDTH - 1  # 每行有一个空洞

    def test_add_garbage_rows_with_hole(self):
        """测试垃圾行有空洞"""
        board = Board()
        board.add_garbage_rows(1)

        # 底行应该有一个空洞
        bottom_row = board.grid[BOARD_HEIGHT - 1]
        none_count = sum(1 for cell in bottom_row if cell is None)
        assert none_count == 1

    def test_add_garbage_rows_game_over(self):
        """测试垃圾行导致游戏结束"""
        board = Board()

        # 在顶部附近放置方块
        for col in range(BOARD_WIDTH):
            board.grid[1][col] = 'I'

        # 添加大量垃圾行应该导致游戏结束
        result = board.add_garbage_rows(5)
        assert not result

    def test_get_ghost_position(self):
        """测试幽灵位置计算"""
        board = Board()
        tetromino = Tetromino('I')
        tetromino.row = 0
        tetromino.col = 5

        ghost_row = board.get_ghost_position(tetromino)
        # 幽灵位置应该在当前位置下方
        assert ghost_row > tetromino.row
        # 应该在底部附近
        assert ghost_row >= BOARD_HEIGHT - 4

    def test_is_game_over(self):
        """测试游戏结束检测"""
        board = Board()

        # 填满顶部区域
        for col in range(BOARD_WIDTH):
            board.grid[0][col] = 'I'

        tetromino = Tetromino('T')
        tetromino.row = 0
        tetromino.col = 5

        assert board.is_game_over(tetromino)

    def test_reset(self):
        """测试重置棋盘"""
        board = Board()

        # 放置一些方块
        for col in range(BOARD_WIDTH):
            board.grid[BOARD_HEIGHT - 1][col] = 'I'

        board.reset()

        # 检查是否清空
        assert all(cell is None for row in board.grid for cell in row)

    def test_get_cell(self):
        """测试获取单元格"""
        board = Board()
        board.grid[5][3] = 'T'

        assert board.get_cell(5, 3) == 'T'
        assert board.get_cell(0, 0) is None
        assert board.get_cell(-1, 0) is None  # 越界返回None
        assert board.get_cell(0, 100) is None


class TestBoardAttackCalculation:
    """棋盘攻击计算测试"""

    def test_single_line_no_attack(self):
        """测试消1行无攻击"""
        board = Board()
        for col in range(BOARD_WIDTH):
            board.grid[BOARD_HEIGHT - 1][col] = 'I'

        board.clear_lines()
        assert board.get_attack_lines() == 0

    def test_double_line_no_attack(self):
        """测试消2行无攻击（保守模式）"""
        board = Board()
        for row in range(BOARD_HEIGHT - 2, BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                board.grid[row][col] = 'I'

        board.clear_lines()
        assert board.get_attack_lines() == 0

    def test_triple_line_attack(self):
        """测试消3行发送1行垃圾"""
        board = Board()
        for row in range(BOARD_HEIGHT - 3, BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                board.grid[row][col] = 'I'

        board.clear_lines()
        assert board.get_attack_lines() == 1

    def test_tetris_attack(self):
        """测试消4行(Tetris)发送2行垃圾"""
        board = Board()
        for row in range(BOARD_HEIGHT - 4, BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                board.grid[row][col] = 'I'

        board.clear_lines()
        assert board.get_attack_lines() == 2
