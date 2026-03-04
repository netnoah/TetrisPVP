"""
方块类单元测试
"""

import pytest
from src.models.tetromino import Tetromino, TetrominoBag, SharedPieceSequence
from src.config import TETROMINO_TYPES


class TestTetromino:
    """方块类测试"""

    def test_create_all_types(self):
        """测试创建所有类型的方块"""
        for t_type in TETROMINO_TYPES:
            tetromino = Tetromino(t_type)
            assert tetromino.type == t_type
            assert tetromino.rotation == 0
            assert len(tetromino.cells) == 4

    def test_random_creation(self):
        """测试随机创建方块"""
        tetromino = Tetromino()
        assert tetromino.type in TETROMINO_TYPES

    def test_initial_position(self):
        """测试初始位置"""
        tetromino = Tetromino('I')
        assert tetromino.row == 0
        assert tetromino.col == 0

    def test_move(self):
        """测试移动"""
        tetromino = Tetromino('T')
        tetromino.move(5, 3)
        assert tetromino.row == 5
        assert tetromino.col == 3

    def test_move_left(self):
        """测试左移"""
        tetromino = Tetromino('T')
        tetromino.col = 5
        tetromino.move_left()
        assert tetromino.col == 4

    def test_move_right(self):
        """测试右移"""
        tetromino = Tetromino('T')
        tetromino.col = 5
        tetromino.move_right()
        assert tetromino.col == 6

    def test_move_down(self):
        """测试下移"""
        tetromino = Tetromino('T')
        tetromino.row = 5
        tetromino.move_down()
        assert tetromino.row == 6

    def test_rotate_cw(self):
        """测试顺时针旋转"""
        tetromino = Tetromino('T')
        initial_rotation = tetromino.rotation
        tetromino.rotate_cw()
        assert tetromino.rotation == (initial_rotation + 1) % 4

    def test_rotate_ccw(self):
        """测试逆时针旋转"""
        tetromino = Tetromino('T')
        initial_rotation = tetromino.rotation
        tetromino.rotate_ccw()
        assert tetromino.rotation == (initial_rotation - 1) % 4

    def test_full_rotation_cycle(self):
        """测试完整旋转周期"""
        tetromino = Tetromino('T')
        initial_cells = tetromino.cells
        for _ in range(4):
            tetromino.rotate_cw()
        assert tetromino.cells == initial_cells

    def test_absolute_cells(self):
        """测试绝对坐标计算"""
        tetromino = Tetromino('I')
        tetromino.row = 5
        tetromino.col = 3
        abs_cells = tetromino.absolute_cells
        for r, c in abs_cells:
            assert r >= 5
            assert c >= 3

    def test_copy(self):
        """测试复制方块"""
        tetromino = Tetromino('T')
        tetromino.row = 5
        tetromino.col = 3
        tetromino.rotate_cw()

        copy = tetromino.copy()
        assert copy.type == tetromino.type
        assert copy.row == tetromino.row
        assert copy.col == tetromino.col
        assert copy.rotation == tetromino.rotation

        # 确保是深拷贝
        copy.rotate_cw()
        assert copy.rotation != tetromino.rotation

    def test_o_shape_single_state(self):
        """测试O形只有一个状态"""
        tetromino = Tetromino('O')
        initial_cells = tetromino.cells
        tetromino.rotate_cw()
        assert tetromino.cells == initial_cells


class TestTetrominoBag:
    """方块袋测试"""

    def test_bag_contains_all_types(self):
        """测试每袋包含所有7种方块"""
        bag = TetrominoBag()
        pieces = []
        for _ in range(7):
            pieces.append(bag.next())

        # 每种类型各一个
        assert sorted(pieces) == sorted(TETROMINO_TYPES)

    def test_multiple_bags(self):
        """测试多袋连续获取"""
        bag = TetrominoBag()
        pieces = []
        for _ in range(14):  # 两袋
            pieces.append(bag.next())

        # 每袋都是完整的7种
        first_7 = sorted(pieces[:7])
        second_7 = sorted(pieces[7:])
        assert first_7 == sorted(TETROMINO_TYPES)
        assert second_7 == sorted(TETROMINO_TYPES)

    def test_peek(self):
        """测试预览功能"""
        bag = TetrominoBag()
        preview = bag.peek(3)
        assert len(preview) == 3

        # 预览不应影响实际获取
        actual = bag.next()
        assert actual == preview[0]

    def test_bag_randomness(self):
        """测试袋的随机性（不同袋应该不同顺序）"""
        bag1 = TetrominoBag()
        bag2 = TetrominoBag()

        seq1 = [bag1.next() for _ in range(7)]
        seq2 = [bag2.next() for _ in range(7)]

        # 虽然可能相同，但概率极低
        # 这里只测试它们是有效的序列
        assert sorted(seq1) == sorted(TETROMINO_TYPES)
        assert sorted(seq2) == sorted(TETROMINO_TYPES)


class TestSharedPieceSequence:
    """共享方块序列测试"""

    def test_initial_size(self):
        """测试初始序列大小"""
        seq = SharedPieceSequence(50)
        assert len(seq.sequence) == 50

    def test_get_piece(self):
        """测试获取方块"""
        seq = SharedPieceSequence(100)
        piece = seq.get(0)
        assert piece in TETROMINO_TYPES

    def test_same_index_same_piece(self):
        """测试相同索引返回相同方块"""
        seq = SharedPieceSequence(100)
        piece1 = seq.get(10)
        piece2 = seq.get(10)
        assert piece1 == piece2

    def test_auto_extend(self):
        """测试自动扩展"""
        seq = SharedPieceSequence(10)
        # 获取超出初始大小的索引
        piece = seq.get(100)
        assert piece in TETROMINO_TYPES
        assert len(seq.sequence) > 10

    def test_different_indices(self):
        """测试不同索引可能返回不同方块"""
        seq = SharedPieceSequence(100)
        pieces = [seq.get(i) for i in range(20)]
        # 至少应该有多种方块类型
        unique_types = set(pieces)
        assert len(unique_types) > 1

    def test_7bag_distribution(self):
        """测试7-bag分布（每7个应该包含所有类型）"""
        seq = SharedPieceSequence(100)
        for i in range(0, 70, 7):
            batch = [seq.get(j) for j in range(i, i + 7)]
            assert sorted(batch) == sorted(TETROMINO_TYPES)
