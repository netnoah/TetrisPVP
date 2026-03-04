"""
俄罗斯方块主程序
支持单机和双人对战模式，带完整菜单系统
"""

import pygame
import sys
from typing import Optional

from src.config import (
    BOARD_WIDTH, BOARD_HEIGHT,
    PLAYER1_BOARD_X, PLAYER2_BOARD_X, BOARD_MARGIN_Y,
    PLAYER1_CONTROLS, PLAYER2_CONTROLS,
    DEFAULT_DIFFICULTY,
)
from src.models.player import Player
from src.models.board import Board
from src.models.tetromino import Tetromino, TetrominoBag, SharedPieceSequence
from src.systems.input_handler import InputHandler
from src.views.renderer import Renderer
from src.views.ui import UI


class GameState:
    """游戏状态枚举"""
    MENU = 'menu'
    COUNTDOWN = 'countdown'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'


class Game:
    """游戏主类 - 支持双人对战"""

    def __init__(self):
        """初始化游戏"""
        self.renderer = Renderer()
        self.ui = UI(self.renderer.screen)

        # 游戏模式
        self.pvp_mode = True
        self.difficulty = DEFAULT_DIFFICULTY

        # 玩家
        self.player1: Optional[Player] = None
        self.player2: Optional[Player] = None
        self.input_handler: Optional[InputHandler] = None

        # 游戏状态
        self.state = GameState.MENU
        self.winner: Optional[int] = None

        # 初始化玩家
        self._init_players()

    def _init_players(self) -> None:
        """初始化玩家"""
        if self.pvp_mode:
            # PVP 模式：共享方块序列，确保公平
            self._shared_sequence = SharedPieceSequence()
            self.player1 = Player(1, PLAYER1_CONTROLS, self.difficulty,
                                  shared_sequence=self._shared_sequence)
            self.player2 = Player(2, PLAYER2_CONTROLS, self.difficulty,
                                  shared_sequence=self._shared_sequence)
            self.input_handler = InputHandler(self.player1, self.player2)
            # 生成初始方块
            self.player1.spawn_piece()
            self.player2.spawn_piece()
        else:
            # 单人模式：独立方块序列
            self._shared_sequence = None
            self.player1 = Player(1, PLAYER1_CONTROLS, self.difficulty)
            self.player1.spawn_piece()
            self.player2 = None
            self.input_handler = None

    def handle_events(self) -> bool:
        """
        处理事件

        Returns:
            True 如果游戏继续，False 如果退出
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if not self._handle_key_down(event.key):
                    return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event.pos)

        return True

    def _handle_key_down(self, key: int) -> bool:
        """
        处理按键按下

        Args:
            key: 按键代码

        Returns:
            True 如果游戏继续
        """
        # ESC 键处理
        if key == pygame.K_ESCAPE:
            if self.state == GameState.MENU:
                return False
            elif self.state in (GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER):
                self.state = GameState.MENU
                self._init_players()
                return True

        # R 键重新开始
        if key == pygame.K_r:
            if self.state == GameState.GAME_OVER:
                self.restart()
                return True

        # P 键暂停
        if key == pygame.K_p:
            if self.state == GameState.PLAYING:
                self.state = GameState.PAUSED
            elif self.state == GameState.PAUSED:
                self.state = GameState.PLAYING

        # 菜单状态下的按键
        if self.state == GameState.MENU:
            if key == pygame.K_1:
                self._start_game(pvp=True)
            elif key == pygame.K_2:
                self._start_game(pvp=False)
            elif key == pygame.K_3:
                return False

        # 游戏中的按键处理
        if self.state == GameState.PLAYING:
            if self.pvp_mode and self.input_handler:
                # 检查道具使用键
                if key == self.player1.controls.get('use_item'):
                    self._use_item(self.player1, self.player2)
                elif key == self.player2.controls.get('use_item'):
                    self._use_item(self.player2, self.player1)
                # 普通按键分发
                elif key in self.input_handler._key_to_player:
                    player = self.input_handler._key_to_player[key]
                    player.handle_key_press(key)
            elif not self.pvp_mode:
                self.player1.handle_key_press(key)

        return True

    def _handle_mouse_click(self, pos: tuple) -> None:
        """处理鼠标点击"""
        if self.state == GameState.MENU:
            action = self.ui.check_menu_click(pos)
            if action == "PVP Mode":
                self._start_game(pvp=True)
            elif action == "Single Player":
                self._start_game(pvp=False)
            elif action == "Quit":
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _start_game(self, pvp: bool) -> None:
        """开始游戏"""
        self.pvp_mode = pvp
        self._init_players()
        self.state = GameState.COUNTDOWN
        self.ui.start_countdown()

    def restart(self) -> None:
        """重新开始游戏"""
        if self.pvp_mode:
            # PVP 模式：创建新的共享序列
            self._shared_sequence = SharedPieceSequence()
            self.player1.reset(reset_sequence=False)
            self.player1._shared_sequence = self._shared_sequence
            self.player2.reset(reset_sequence=False)
            self.player2._shared_sequence = self._shared_sequence
            # 生成初始方块
            self.player1.spawn_piece()
            self.player2.spawn_piece()
        else:
            self.player1.reset(reset_sequence=True)
            self.player1.spawn_piece()

        self.winner = None
        self.state = GameState.COUNTDOWN
        self.ui.start_countdown()

    def update(self, dt: int) -> None:
        """
        更新游戏状态

        Args:
            dt: 距离上一帧的时间（毫秒）
        """
        if self.state == GameState.COUNTDOWN:
            result = self.ui.update_countdown()
            if result == 0:
                self.state = GameState.PLAYING

        elif self.state == GameState.PLAYING:
            current_time = pygame.time.get_ticks()

            # 更新玩家
            self.player1.update(dt, current_time)
            if self.pvp_mode and self.player2:
                self.player2.update(dt, current_time)

            # 检查游戏结束
            self._check_game_over()

    def _handle_held_keys(self) -> None:
        """处理持续按住的键"""
        pass  # 按键状态已在 Player 中维护

    def _use_item(self, attacker: Player, target: Player) -> None:
        """
        使用道具攻击对手

        Args:
            attacker: 使用道具的玩家
            target: 被攻击的玩家
        """
        garbage_count = attacker.use_item()
        if garbage_count > 0:
            target.receive_garbage(garbage_count)

    def _check_game_over(self) -> None:
        """检查游戏结束"""
        if self.pvp_mode and self.player2:
            p1_dead = self.player1.game_over
            p2_dead = self.player2.game_over

            if p1_dead and p2_dead:
                # 同时死亡，比较分数
                self.state = GameState.GAME_OVER
                if self.player1.score > self.player2.score:
                    self.winner = 1
                elif self.player2.score > self.player1.score:
                    self.winner = 2
                else:
                    self.winner = None  # 平局
            elif p1_dead:
                self.state = GameState.GAME_OVER
                self.winner = 2
            elif p2_dead:
                self.state = GameState.GAME_OVER
                self.winner = 1
        else:
            # 单人模式
            if self.player1.game_over:
                self.state = GameState.GAME_OVER

    def render(self) -> None:
        """渲染游戏画面"""
        if self.state == GameState.MENU:
            mouse_pos = pygame.mouse.get_pos()
            self.ui.draw_main_menu(mouse_pos)

        elif self.state == GameState.COUNTDOWN:
            self._render_game()
            self.ui.draw_countdown()

        elif self.state == GameState.PLAYING:
            self._render_game()

        elif self.state == GameState.PAUSED:
            self._render_game()
            self.ui.draw_pause_screen()

        elif self.state == GameState.GAME_OVER:
            self._render_game()
            if self.pvp_mode and self.player2:
                scores = (self.player1.score, self.player2.score)
                self.ui.draw_game_over(self.winner, scores)
            else:
                self.ui.draw_single_game_over(self.player1.score, self.player1.lines)

        self.renderer.update()

    def _render_game(self) -> None:
        """渲染游戏画面"""
        self.renderer.clear()

        if self.pvp_mode and self.player2:
            # 对战模式
            self.renderer.draw_vs_divider()
            self.renderer.draw_player_board(self.player1, PLAYER1_BOARD_X)
            self.renderer.draw_player_board(self.player2, PLAYER2_BOARD_X)
        else:
            # 单人模式
            self.renderer.draw_player_board(self.player1, PLAYER1_BOARD_X)

    def run(self) -> None:
        """运行游戏主循环"""
        clock = pygame.time.Clock()
        running = True

        while running:
            # 处理输入
            running = self.handle_events()

            # 处理按键释放
            self._handle_key_releases()

            # 更新游戏状态
            dt = clock.tick(60)  # 60 FPS
            self.update(dt)

            # 渲染
            self.render()

        self.renderer.quit()

    def _handle_key_releases(self) -> None:
        """处理按键释放"""
        if self.state != GameState.PLAYING:
            return

        keys = pygame.key.get_pressed()

        # 检查玩家控制键是否释放
        for key in list(self.player1.keys_pressed):
            if not keys[key]:
                self.player1.handle_key_release(key)

        if self.pvp_mode and self.player2:
            for key in list(self.player2.keys_pressed):
                if not keys[key]:
                    self.player2.handle_key_release(key)


def main():
    """程序入口"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
