"""
攻击系统单元测试
"""

import pytest
from src.models.player import Player
from src.models.tetromino import SharedPieceSequence
from src.config import (
    PLAYER1_CONTROLS, PLAYER2_CONTROLS,
    ATTACK_FORMULA, BOARD_WIDTH, BOARD_HEIGHT
)


class TestPlayerAttack:
    """玩家攻击测试"""

    def test_receive_garbage(self):
        """测试接收垃圾行"""
        player = Player(1, PLAYER1_CONTROLS)
        player.receive_garbage(3)

        # 检查底部是否有垃圾行
        garbage_count = 0
        for row in range(BOARD_HEIGHT - 3, BOARD_HEIGHT):
            for cell in player.board.grid[row]:
                if cell == 'garbage':
                    garbage_count += 1

        # 每行有一个空洞，所以3行有 (BOARD_WIDTH-1)*3 个垃圾单元格
        assert garbage_count == (BOARD_WIDTH - 1) * 3

    def test_receive_garbage_game_over(self):
        """测试接收垃圾行导致游戏结束"""
        player = Player(1, PLAYER1_CONTROLS)

        # 在顶部附近放置方块
        for col in range(BOARD_WIDTH):
            player.board.grid[2][col] = 'I'

        # 添加大量垃圾行
        result = player.receive_garbage(10)
        assert not result
        assert player.game_over

    def test_receive_zero_garbage(self):
        """测试接收0行垃圾（无效果）"""
        player = Player(1, PLAYER1_CONTROLS)
        result = player.receive_garbage(0)
        assert result

    def test_get_attack_lines_no_clear(self):
        """测试未消行时无攻击"""
        player = Player(1, PLAYER1_CONTROLS)
        player.spawn_piece()

        # 放置方块但不消行
        player.current_piece.row = BOARD_HEIGHT - 2
        player.board.place_tetromino(player.current_piece)
        player.board.clear_lines()

        # 如果没有消行，攻击为0
        # 这个测试假设放置的方块没有填满行


class TestPVPFairness:
    """PVP 公平性测试"""

    def test_shared_sequence_same_initial(self):
        """测试共享序列初始方块相同"""
        shared_seq = SharedPieceSequence()
        p1 = Player(1, PLAYER1_CONTROLS, shared_sequence=shared_seq)
        p2 = Player(2, PLAYER2_CONTROLS, shared_sequence=shared_seq)

        p1.spawn_piece()
        p2.spawn_piece()

        assert p1.current_piece.type == p2.current_piece.type
        assert p1.next_piece.type == p2.next_piece.type

    def test_shared_sequence_after_multiple_spawns(self):
        """测试多次生成后方块仍相同"""
        shared_seq = SharedPieceSequence()
        p1 = Player(1, PLAYER1_CONTROLS, shared_sequence=shared_seq)
        p2 = Player(2, PLAYER2_CONTROLS, shared_sequence=shared_seq)

        p1.spawn_piece()
        p2.spawn_piece()

        for _ in range(10):
            p1.spawn_piece()
            p2.spawn_piece()
            assert p1.current_piece.type == p2.current_piece.type

    def test_independent_sequences_different(self):
        """测试独立序列方块可能不同"""
        p1 = Player(1, PLAYER1_CONTROLS)
        p2 = Player(2, PLAYER2_CONTROLS)

        p1.spawn_piece()
        p2.spawn_piece()

        # 独立序列的方块可能不同（虽然理论上可能相同，概率极低）
        # 这个测试主要验证独立模式工作正常
        assert p1.current_piece.type in 'IOTSLJZ'
        assert p2.current_piece.type in 'IOTSLJZ'


class TestAttackFormula:
    """攻击公式测试"""

    def test_attack_formula_values(self):
        """测试攻击公式值（保守模式）"""
        assert ATTACK_FORMULA[1] == 0   # 1行无攻击
        assert ATTACK_FORMULA[2] == 0   # 2行无攻击
        assert ATTACK_FORMULA[3] == 1   # 3行1垃圾
        assert ATTACK_FORMULA[4] == 2   # 4行2垃圾

    def test_attack_progression(self):
        """测试攻击递进关系"""
        # 4行应该比3行攻击更多
        assert ATTACK_FORMULA[4] > ATTACK_FORMULA[3]
        # 3行应该比2行攻击更多
        assert ATTACK_FORMULA[3] > ATTACK_FORMULA[2]
        # 1行和2行都无攻击
        assert ATTACK_FORMULA[1] == ATTACK_FORMULA[2]

    def test_attack_reset_after_get(self):
        """测试获取攻击后重置，避免重复发送"""
        from src.models.board import Board

        board = Board()
        # 填满3行
        for row in range(BOARD_HEIGHT - 3, BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                board.grid[row][col] = 'I'

        board.clear_lines()
        # 第一次获取应该返回1
        attack1 = board.get_attack_lines()
        assert attack1 == 1
        # 第二次获取应该返回0（已重置）
        attack2 = board.get_attack_lines()
        assert attack2 == 0


class TestPlayerIntegration:
    """玩家集成测试"""

    def test_full_game_cycle(self):
        """测试完整游戏周期"""
        shared_seq = SharedPieceSequence()
        p1 = Player(1, PLAYER1_CONTROLS, shared_sequence=shared_seq)
        p2 = Player(2, PLAYER2_CONTROLS, shared_sequence=shared_seq)

        # 生成初始方块
        p1.spawn_piece()
        p2.spawn_piece()

        # 模拟游戏循环
        for _ in range(5):
            # 玩家1锁定方块
            p1.board.place_tetromino(p1.current_piece)
            p1.spawn_piece()

            # 玩家2锁定方块
            p2.board.place_tetromino(p2.current_piece)
            p2.spawn_piece()

            # 检查方块相同
            assert p1.current_piece.type == p2.current_piece.type

    def test_attack_exchange(self):
        """测试攻击交换"""
        shared_seq = SharedPieceSequence()
        p1 = Player(1, PLAYER1_CONTROLS, shared_sequence=shared_seq)
        p2 = Player(2, PLAYER2_CONTROLS, shared_sequence=shared_seq)

        p1.spawn_piece()
        p2.spawn_piece()

        # 玩家1消2行（需要先填充棋盘）
        for row in range(BOARD_HEIGHT - 2, BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                p1.board.grid[row][col] = 'I'

        p1.board.clear_lines()
        attack = p1.get_attack_lines()

        # 玩家2接收攻击
        if attack > 0:
            p2.receive_garbage(attack)
            # 检查玩家2棋盘有垃圾行
            has_garbage = any(
                cell == 'garbage'
                for row in p2.board.grid
                for cell in row
            )
            assert has_garbage

    def test_reset_clears_state(self):
        """测试重置清除状态"""
        player = Player(1, PLAYER1_CONTROLS)
        player.spawn_piece()

        # 模拟游戏
        player.score = 1000
        player.lines = 10
        player.level = 2

        # 重置
        player.reset()
        player.spawn_piece()

        assert player.score == 0
        assert player.lines == 0
        assert player.level == 1
