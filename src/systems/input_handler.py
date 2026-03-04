"""
输入处理器
处理两个玩家的键盘输入
"""

from typing import Dict, List, Tuple, Optional
import pygame

from src.config import PLAYER1_CONTROLS, PLAYER2_CONTROLS
from src.models.player import Player


class InputHandler:
    """输入处理器 - 管理双玩家输入"""

    def __init__(self, player1: Player, player2: Player):
        """
        初始化输入处理器

        Args:
            player1: 玩家1实例
            player2: 玩家2实例
        """
        self.player1 = player1
        self.player2 = player2

        # 构建按键到玩家的映射
        self._key_to_player: Dict[int, Player] = {}

        # 玩家1控制键
        for action, key in PLAYER1_CONTROLS.items():
            self._key_to_player[key] = player1

        # 玩家2控制键
        for action, key in PLAYER2_CONTROLS.items():
            self._key_to_player[key] = player2

        # 全局控制键
        self._global_keys = {
            pygame.K_ESCAPE: 'quit',
            pygame.K_p: 'pause',
            pygame.K_r: 'restart',
        }

        # 游戏状态回调
        self.on_quit: Optional[callable] = None
        self.on_pause: Optional[callable] = None
        self.on_restart: Optional[callable] = None

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        处理单个事件

        Args:
            event: Pygame 事件

        Returns:
            全局动作字符串或 None
        """
        if event.type == pygame.QUIT:
            return 'quit'

        if event.type == pygame.KEYDOWN:
            return self._handle_key_down(event.key)

        if event.type == pygame.KEYUP:
            self._handle_key_up(event.key)

        return None

    def _handle_key_down(self, key: int) -> Optional[str]:
        """
        处理按键按下

        Args:
            key: 按键代码

        Returns:
            全局动作字符串或 None
        """
        # 检查全局控制键
        if key in self._global_keys:
            action = self._global_keys[key]
            return action

        # 分发到对应玩家
        if key in self._key_to_player:
            player = self._key_to_player[key]
            player.handle_key_press(key)

        return None

    def _handle_key_up(self, key: int) -> None:
        """
        处理按键释放

        Args:
            key: 按键代码
        """
        if key in self._key_to_player:
            player = self._key_to_player[key]
            player.handle_key_release(key)

    def process_events(self) -> Tuple[bool, bool, bool]:
        """
        处理所有事件

        Returns:
            (quit_requested, pause_toggled, restart_requested)
        """
        quit_requested = False
        pause_toggled = False
        restart_requested = False

        for event in pygame.event.get():
            action = self.handle_event(event)

            if action == 'quit':
                quit_requested = True
            elif action == 'pause':
                pause_toggled = True
            elif action == 'restart':
                restart_requested = True

        return quit_requested, pause_toggled, restart_requested

    def get_all_pressed_keys(self) -> List[int]:
        """
        获取当前所有按下的键

        Returns:
            按键代码列表
        """
        all_keys = []
        all_keys.extend(self.player1.keys_pressed)
        all_keys.extend(self.player2.keys_pressed)
        return all_keys
