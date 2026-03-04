"""
玩家类
封装单个玩家的游戏状态和操作
"""

from typing import Optional, Dict, Set

from src.config import (
    BOARD_WIDTH,
    FALL_SPEED_INITIAL,
    SOFT_DROP_SPEED,
    LOCK_DELAY,
    SCORE_PER_LINE,
    DIFFICULTY_SETTINGS,
    DEFAULT_DIFFICULTY,
)
from src.models.tetromino import Tetromino, TetrominoBag, SharedPieceSequence
from src.models.board import Board
from src.models.tetromino import Tetromino, TetrominoBag


class Player:
    """玩家类 - 封装单个玩家的所有游戏状态"""

    def __init__(self, player_id: int, controls: Dict[str, int],
                 difficulty: str = DEFAULT_DIFFICULTY,
                 shared_sequence: Optional[SharedPieceSequence] = None):
        """
        初始化玩家

        Args:
            player_id: 玩家编号 (1 或 2)
            controls: 控制键映射字典
            difficulty: 难度设置 ('easy', 'normal', 'hard')
            shared_sequence: 共享的方块序列（PVP模式下使用，确保公平）
        """
        self.player_id = player_id
        self.controls = controls
        self.difficulty = difficulty

        # 获取难度设置
        diff_settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS[DEFAULT_DIFFICULTY])
        self.initial_fall_speed = diff_settings['fall_speed']
        self.speed_decrease = diff_settings['speed_decrease']

        # 游戏组件
        self.board = Board()

        # 方块序列：共享或独立
        self._shared_sequence = shared_sequence
        self._piece_index = 0  # 当前方块在序列中的索引

        # 独立模式的 bag
        self._bag = TetrominoBag() if shared_sequence is None else None

        # 当前方块
        self.current_piece: Optional[Tetromino] = None
        self.next_piece: Optional[Tetromino] = None

        # 游戏状态
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False

        # 计时器
        self.last_fall_time = 0
        self.fall_speed = self.initial_fall_speed
        self.lock_timer = 0
        self.is_locking = False

        # 输入状态
        self.keys_pressed: Set[int] = set()

        # 道具系统
        self.garbage_item = 0  # 存储的垃圾行道具数量

    def add_item(self, count: int) -> None:
        """
        添加道具

        Args:
            count: 道具数量（垃圾行数）
        """
        if count > 0:
            self.garbage_item += count

    def use_item(self) -> int:
        """
        使用道具，返回要发送的垃圾行数

        Returns:
            要发送的垃圾行数，如果没有道具返回0
        """
        if self.garbage_item > 0:
            item = self.garbage_item
            self.garbage_item = 0
            return item
        return 0

    def _get_piece_type(self, index: int) -> str:
        """
        获取指定索引的方块类型

        Args:
            index: 方块索引

        Returns:
            方块类型字符串
        """
        if self._shared_sequence is not None:
            return self._shared_sequence.get(index)
        else:
            return self._bag.next()

    def spawn_piece(self) -> None:
        """生成新方块"""
        # 获取当前方块
        current_type = self._get_piece_type(self._piece_index)
        self._piece_index += 1

        # 获取下一个方块
        next_type = self._get_piece_type(self._piece_index)

        if self.next_piece is None:
            # 首次生成
            self.current_piece = Tetromino(current_type)
            self.next_piece = Tetromino(next_type)
        else:
            # 后续生成
            self.current_piece = self.next_piece
            self.next_piece = Tetromino(next_type)

        # 设置初始位置
        self.current_piece.row = 0
        self.current_piece.col = BOARD_WIDTH // 2 - 1

        # 检查游戏结束
        if self.board.is_game_over(self.current_piece):
            self.game_over = True

    def move_piece(self, dr: int, dc: int) -> bool:
        """
        移动当前方块

        Args:
            dr: 行方向移动量（正数向下）
            dc: 列方向移动量（正数向右）

        Returns:
            True 如果移动成功
        """
        if self.game_over or self.current_piece is None:
            return False

        self.current_piece.move(dr, dc)
        if self.board.is_valid_position(self.current_piece):
            # 移动成功，重置锁定计时器
            if self.is_locking:
                self.lock_timer = 0
            return True
        else:
            # 移动失败，撤销
            self.current_piece.move(-dr, -dc)
            return False

    def rotate_piece(self, direction: int) -> bool:
        """
        旋转当前方块

        Args:
            direction: 1 为顺时针，-1 为逆时针

        Returns:
            True 如果旋转成功
        """
        if self.game_over or self.current_piece is None:
            return False

        if self.board.can_rotate(self.current_piece, direction):
            if direction == 1:
                self.current_piece.rotate_cw()
            else:
                self.current_piece.rotate_ccw()
            # 旋转成功，重置锁定计时器
            if self.is_locking:
                self.lock_timer = 0
            return True
        return False

    def hard_drop(self) -> None:
        """硬降 - 直接落到底部"""
        if self.game_over or self.current_piece is None:
            return

        while self.move_piece(1, 0):
            self.score += 2  # 硬降每格加2分
        self.lock_piece()

    def lock_piece(self) -> int:
        """
        锁定当前方块

        Returns:
            消除的行数
        """
        if self.current_piece is None:
            return 0

        self.board.place_tetromino(self.current_piece)

        # 消行
        lines_cleared = self.board.clear_lines()
        if lines_cleared > 0:
            self.lines += lines_cleared
            self.score += SCORE_PER_LINE.get(lines_cleared, 0) * self.level

            # 升级（每10行升一级）
            self.level = self.lines // 10 + 1
            # 加快下落速度（使用难度相关的递减值）
            self.fall_speed = max(
                self.initial_fall_speed - (self.level - 1) * self.speed_decrease,
                100
            )

            # 获得道具（而不是直接攻击）
            item_count = self.board.get_attack_lines()
            if item_count > 0:
                self.add_item(item_count)

        # 生成新方块
        self.spawn_piece()
        self.is_locking = False
        self.lock_timer = 0

        return lines_cleared

    def update(self, dt: int, current_time: int) -> None:
        """
        更新玩家状态

        Args:
            dt: 距离上一帧的时间（毫秒）
            current_time: 当前时间戳（毫秒）
        """
        if self.game_over:
            return

        # 处理软降（按住下键）
        if self.controls['soft_drop'] in self.keys_pressed:
            fall_speed = SOFT_DROP_SPEED
        else:
            fall_speed = self.fall_speed

        # 检查是否需要下落
        if current_time - self.last_fall_time >= fall_speed:
            self.last_fall_time = current_time

            # 尝试下落
            if self.move_piece(1, 0):
                # 下落成功
                if self.controls['soft_drop'] in self.keys_pressed:
                    self.score += 1  # 软降每格加1分
                self.is_locking = False
            else:
                # 无法下落，开始或继续锁定计时
                if not self.is_locking:
                    self.is_locking = True
                    self.lock_timer = 0
                else:
                    self.lock_timer += fall_speed

        # 检查锁定
        if self.is_locking and self.lock_timer >= LOCK_DELAY:
            self.lock_piece()

    def handle_key_press(self, key: int) -> None:
        """
        处理按键按下

        Args:
            key: 按键代码
        """
        if self.game_over:
            return

        self.keys_pressed.add(key)

        if key == self.controls['left']:
            self.move_piece(0, -1)
        elif key == self.controls['right']:
            self.move_piece(0, 1)
        elif key == self.controls['hard_drop']:
            self.hard_drop()
        elif key == self.controls['rotate_cw']:
            self.rotate_piece(1)
        elif key == self.controls['rotate_ccw']:
            self.rotate_piece(-1)

    def handle_key_release(self, key: int) -> None:
        """
        处理按键释放

        Args:
            key: 按键代码
        """
        self.keys_pressed.discard(key)

    def receive_garbage(self, count: int) -> bool:
        """
        接收垃圾行

        Args:
            count: 垃圾行数量

        Returns:
            True 如果游戏未结束，False 如果游戏结束
        """
        if count <= 0:
            return True

        result = self.board.add_garbage_rows(count)
        if not result:
            self.game_over = True
        return result

    def get_attack_lines(self) -> int:
        """
        获取要发送给对手的垃圾行数

        Returns:
            垃圾行数量
        """
        return self.board.get_attack_lines()

    def reset(self, reset_sequence: bool = True) -> None:
        """
        重置玩家状态

        Args:
            reset_sequence: 是否重置方块序列（共享模式下应为 False）
        """
        self.board.reset()
        self._piece_index = 0

        if reset_sequence and self._shared_sequence is None:
            # 独立模式：重置 bag
            self._bag = TetrominoBag()

        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.fall_speed = self.initial_fall_speed
        self.is_locking = False
        self.lock_timer = 0
        self.keys_pressed.clear()
        self.pending_garbage = 0

    def __repr__(self) -> str:
        return f"Player({self.player_id}, score={self.score}, lines={self.lines})"
