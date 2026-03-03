"""
俄罗斯方块主程序
单机版游戏循环
"""

import pygame
import sys

from src.config import (
    BOARD_WIDTH, BOARD_HEIGHT,
    PLAYER1_BOARD_X, BOARD_MARGIN_Y,
    FALL_SPEED_INITIAL, SOFT_DROP_SPEED, LOCK_DELAY,
    PLAYER1_CONTROLS, SCORE_PER_LINE
)
from src.models.board import Board
from src.models.tetromino import Tetromino, TetrominoBag
from src.views.renderer import Renderer


class Game:
    """游戏主类"""

    def __init__(self):
        """初始化游戏"""
        self.renderer = Renderer()
        self.board = Board()
        self.bag = TetrominoBag()

        # 当前和下一个方块
        self.current_piece: Tetromino = None
        self.next_piece: Tetromino = None
        self.spawn_piece()

        # 游戏状态
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.paused = False

        # 计时器
        self.last_fall_time = 0
        self.fall_speed = FALL_SPEED_INITIAL
        self.lock_timer = 0
        self.is_locking = False

        # 输入状态（用于处理按住按键）
        self.keys_pressed = set()

    def spawn_piece(self) -> None:
        """生成新方块"""
        if self.next_piece is None:
            self.next_piece = Tetromino(self.bag.next())

        self.current_piece = self.next_piece
        self.next_piece = Tetromino(self.bag.next())

        # 设置初始位置（棋盘顶部中央）
        self.current_piece.row = 0
        self.current_piece.col = BOARD_WIDTH // 2 - 1

        # 检查游戏结束
        if self.board.is_game_over(self.current_piece):
            self.game_over = True

    def handle_input(self) -> bool:
        """
        处理输入

        Returns:
            True 如果游戏继续，False 如果退出
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over:
                    if event.key == pygame.K_r:
                        self.restart()
                    continue

                if event.key == pygame.K_p:
                    self.paused = not self.paused

                if not self.paused:
                    self.keys_pressed.add(event.key)
                    self.handle_key_press(event.key)

            if event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)

        return True

    def handle_key_press(self, key: int) -> None:
        """处理按键按下"""
        if key == PLAYER1_CONTROLS['left']:
            self.move_piece(0, -1)
        elif key == PLAYER1_CONTROLS['right']:
            self.move_piece(0, 1)
        elif key == PLAYER1_CONTROLS['soft_drop']:
            pass  # 在 update 中处理软降
        elif key == PLAYER1_CONTROLS['hard_drop']:
            self.hard_drop()
        elif key == PLAYER1_CONTROLS['rotate_cw']:
            self.rotate_piece(1)
        elif key == PLAYER1_CONTROLS['rotate_ccw']:
            self.rotate_piece(-1)

    def move_piece(self, dr: int, dc: int) -> bool:
        """
        移动方块

        Args:
            dr: 行方向移动量
            dc: 列方向移动量

        Returns:
            True 如果移动成功
        """
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
        旋转方块

        Args:
            direction: 1 为顺时针，-1 为逆时针

        Returns:
            True 如果旋转成功
        """
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
        while self.move_piece(1, 0):
            self.score += 2  # 硬降每格加2分
        self.lock_piece()

    def update(self, dt: int) -> None:
        """
        更新游戏状态

        Args:
            dt: 距离上一帧的时间（毫秒）
        """
        if self.game_over or self.paused:
            return

        current_time = pygame.time.get_ticks()

        # 处理软降（按住下键）
        if PLAYER1_CONTROLS['soft_drop'] in self.keys_pressed:
            fall_speed = SOFT_DROP_SPEED
        else:
            fall_speed = self.fall_speed

        # 检查是否需要下落
        if current_time - self.last_fall_time >= fall_speed:
            self.last_fall_time = current_time

            # 尝试下落
            if self.move_piece(1, 0):
                # 下落成功
                if PLAYER1_CONTROLS['soft_drop'] in self.keys_pressed:
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

    def lock_piece(self) -> None:
        """锁定当前方块"""
        self.board.place_tetromino(self.current_piece)

        # 消行
        lines_cleared = self.board.clear_lines()
        if lines_cleared > 0:
            self.lines += lines_cleared
            self.score += SCORE_PER_LINE.get(lines_cleared, 0) * self.level

            # 升级（每10行升一级）
            self.level = self.lines // 10 + 1
            # 加快下落速度
            self.fall_speed = max(
                FALL_SPEED_INITIAL - (self.level - 1) * 50,
                100
            )

        # 生成新方块
        self.spawn_piece()
        self.is_locking = False
        self.lock_timer = 0

    def restart(self) -> None:
        """重新开始游戏"""
        self.board.reset()
        self.bag = TetrominoBag()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.fall_speed = FALL_SPEED_INITIAL
        self.current_piece = None
        self.next_piece = None
        self.spawn_piece()

    def render(self) -> None:
        """渲染游戏画面"""
        self.renderer.clear()

        # 绘制棋盘
        self.renderer.draw_board(
            PLAYER1_BOARD_X, BOARD_MARGIN_Y,
            self.board.grid
        )
        self.renderer.draw_border(PLAYER1_BOARD_X, BOARD_MARGIN_Y)

        # 绘制当前方块
        if self.current_piece and not self.game_over:
            # 绘制幽灵方块
            ghost_row = self.board.get_ghost_position(self.current_piece)
            ghost = self.current_piece.copy()
            ghost.row = ghost_row
            self.renderer.draw_tetromino(
                PLAYER1_BOARD_X, BOARD_MARGIN_Y,
                ghost, is_ghost=True
            )
            # 绘制当前方块
            self.renderer.draw_tetromino(
                PLAYER1_BOARD_X, BOARD_MARGIN_Y,
                self.current_piece
            )

        # 绘制玩家信息
        self.renderer.draw_player_info(
            1, PLAYER1_BOARD_X,
            self.score, self.lines
        )

        # 绘制等级
        self.renderer.draw_text(
            f"Level: {self.level}",
            PLAYER1_BOARD_X,
            BOARD_MARGIN_Y + BOARD_HEIGHT * 30 + 70
        )

        # 绘制下一个方块预览
        if self.next_piece:
            self.renderer.draw_text(
                "Next:",
                PLAYER1_BOARD_X + 200,
                BOARD_MARGIN_Y
            )
            # 简单预览：在右侧显示下一个方块
            preview_x = PLAYER1_BOARD_X + 200
            preview_y = BOARD_MARGIN_Y + 30
            for row, col in self.next_piece.cells:
                x = preview_x + col * 20
                y = preview_y + row * 20
                rect = pygame.Rect(x, y, 18, 18)
                pygame.draw.rect(self.renderer.screen, self.next_piece.color, rect)

        # 游戏结束画面
        if self.game_over:
            self.renderer.draw_text(
                "GAME OVER",
                PLAYER1_BOARD_X + 150,
                BOARD_MARGIN_Y + 250,
                'large',
                center=True
            )
            self.renderer.draw_text(
                "Press R to Restart",
                PLAYER1_BOARD_X + 150,
                BOARD_MARGIN_Y + 300,
                center=True
            )

        # 暂停画面
        if self.paused and not self.game_over:
            self.renderer.draw_text(
                "PAUSED",
                PLAYER1_BOARD_X + 150,
                BOARD_MARGIN_Y + 250,
                'large',
                center=True
            )
            self.renderer.draw_text(
                "Press P to Continue",
                PLAYER1_BOARD_X + 150,
                BOARD_MARGIN_Y + 300,
                center=True
            )

        self.renderer.update()

    def run(self) -> None:
        """运行游戏主循环"""
        clock = pygame.time.Clock()
        running = True

        while running:
            # 处理输入
            running = self.handle_input()

            # 更新游戏状态
            dt = clock.tick(60)  # 60 FPS
            self.update(dt)

            # 渲染
            self.render()

        self.renderer.quit()


def main():
    """程序入口"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
