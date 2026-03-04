"""
UI 组件
游戏菜单、按钮、提示等界面元素
"""

import pygame
from typing import List, Tuple, Optional, Callable

from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLORS, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,
    PLAYER1_CONTROLS, PLAYER2_CONTROLS
)


class Button:
    """按钮组件"""

    def __init__(self, text: str, x: int, y: int,
                 width: int = 200, height: int = 50,
                 callback: Optional[Callable] = None):
        """
        初始化按钮

        Args:
            text: 按钮文本
            x: 中心 X 坐标
            y: 中心 Y 坐标
            width: 按钮宽度
            height: 按钮高度
            callback: 点击回调函数
        """
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.callback = callback
        self.hovered = False

        # 按钮颜色
        self.color_normal = COLORS['border']
        self.color_hover = (150, 150, 180)
        self.color_text = COLORS['text']

    @property
    def rect(self) -> pygame.Rect:
        """获取按钮矩形区域"""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )

    def contains_point(self, pos: Tuple[int, int]) -> bool:
        """检查点是否在按钮内"""
        return self.rect.collidepoint(pos)

    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """更新按钮状态"""
        self.hovered = self.contains_point(mouse_pos)

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """绘制按钮"""
        color = self.color_hover if self.hovered else self.color_normal

        # 绘制按钮背景
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLORS['text'], self.rect, 2, border_radius=8)

        # 绘制文本
        text_surface = font.render(self.text, True, self.color_text)
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)

    def click(self) -> Optional[str]:
        """处理点击，返回按钮文本"""
        if self.hovered and self.callback:
            return self.callback()
        return self.text if self.hovered else None


class UI:
    """UI 管理器"""

    def __init__(self, screen: pygame.Surface):
        """
        初始化 UI

        Args:
            screen: Pygame 显示表面
        """
        self.screen = screen

        # 加载字体
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)

        # 菜单按钮
        self.menu_buttons: List[Button] = []
        self._create_menu_buttons()

        # 倒计时状态
        self.countdown_active = False
        self.countdown_value = 3
        self.countdown_timer = 0

    def _create_menu_buttons(self) -> None:
        """创建主菜单按钮"""
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2

        self.menu_buttons = [
            Button("PVP Mode", center_x, center_y - 30, 220, 50),
            Button("Single Player", center_x, center_y + 40, 220, 50),
            Button("Quit", center_x, center_y + 110, 220, 50),
        ]

    def draw_background(self) -> None:
        """绘制背景"""
        self.screen.fill(COLORS['background'])

    def draw_title(self, text: str, y_offset: int = 0) -> None:
        """
        绘制标题

        Args:
            text: 标题文本
            y_offset: Y 偏移量
        """
        title_surface = self.font_large.render(text, True, COLORS['text'])
        title_rect = title_surface.get_rect(
            center=(WINDOW_WIDTH // 2, 100 + y_offset)
        )
        self.screen.blit(title_surface, title_rect)

    def draw_subtitle(self, text: str, y: int) -> None:
        """绘制副标题"""
        surface = self.font_medium.render(text, True, COLORS['text'])
        rect = surface.get_rect(center=(WINDOW_WIDTH // 2, y))
        self.screen.blit(surface, rect)

    def draw_text(self, text: str, x: int, y: int,
                  center: bool = False, size: str = 'medium') -> None:
        """绘制文本"""
        font = {
            'large': self.font_large,
            'medium': self.font_medium,
            'small': self.font_small
        }.get(size, self.font_medium)

        surface = font.render(text, True, COLORS['text'])
        if center:
            rect = surface.get_rect(center=(x, y))
            self.screen.blit(surface, rect)
        else:
            self.screen.blit(surface, (x, y))

    def draw_main_menu(self, mouse_pos: Tuple[int, int]) -> None:
        """
        绘制主菜单

        Args:
            mouse_pos: 鼠标位置
        """
        self.draw_background()
        self.draw_title("TETRIS PVP")

        # 绘制副标题
        self.draw_subtitle("Local Multiplayer Tetris", 150)

        # 更新和绘制按钮
        for button in self.menu_buttons:
            button.update(mouse_pos)
            button.draw(self.screen, self.font_medium)

        # 绘制控制说明
        self._draw_controls_help()

    def _draw_controls_help(self) -> None:
        """绘制控制说明"""
        y_start = WINDOW_HEIGHT - 180
        col1_x = WINDOW_WIDTH // 4
        col2_x = WINDOW_WIDTH * 3 // 4

        # 玩家1控制
        self.draw_text("Player 1", col1_x, y_start, center=True, size='small')
        self.draw_text("Move: A / D", col1_x, y_start + 25, center=True, size='small')
        self.draw_text("Soft Drop: S", col1_x, y_start + 45, center=True, size='small')
        self.draw_text("Hard Drop: Space", col1_x, y_start + 65, center=True, size='small')
        self.draw_text("Rotate: W", col1_x, y_start + 85, center=True, size='small')
        self.draw_text("Use Item: E", col1_x, y_start + 105, center=True, size='small')

        # 玩家2控制
        self.draw_text("Player 2", col2_x, y_start, center=True, size='small')
        self.draw_text("Move: ← / →", col2_x, y_start + 25, center=True, size='small')
        self.draw_text("Soft Drop: ↓", col2_x, y_start + 45, center=True, size='small')
        self.draw_text("Hard Drop: RCtrl", col2_x, y_start + 65, center=True, size='small')
        self.draw_text("Rotate: ↑", col2_x, y_start + 85, center=True, size='small')
        self.draw_text("Use Item: .", col2_x, y_start + 105, center=True, size='small')

        # 通用控制
        self.draw_text("Pause: P  |  Restart: R  |  Quit: ESC",
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30,
                       center=True, size='small')

    def check_menu_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """
        检查菜单点击

        Args:
            mouse_pos: 鼠标位置

        Returns:
            被点击的按钮文本，或 None
        """
        for button in self.menu_buttons:
            if button.contains_point(mouse_pos):
                return button.text
        return None

    def start_countdown(self) -> None:
        """开始倒计时"""
        self.countdown_active = True
        self.countdown_value = 3
        self.countdown_timer = pygame.time.get_ticks()

    def update_countdown(self) -> Optional[int]:
        """
        更新倒计时

        Returns:
            当前倒计时值，倒计时结束时返回 0
        """
        if not self.countdown_active:
            return None

        elapsed = pygame.time.get_ticks() - self.countdown_timer
        current = 3 - (elapsed // 1000)

        if current <= 0:
            self.countdown_active = False
            return 0

        self.countdown_value = current
        return current

    def draw_countdown(self) -> None:
        """绘制倒计时"""
        if not self.countdown_active:
            return

        # 半透明背景
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(COLORS['background'])
        self.screen.blit(overlay, (0, 0))

        # 倒计时数字
        if self.countdown_value > 0:
            text = str(self.countdown_value)
        else:
            text = "GO!"

        # 大字体显示
        font = pygame.font.Font(None, 120)
        surface = font.render(text, True, COLORS['text'])
        rect = surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(surface, rect)

    def draw_game_over(self, winner_id: Optional[int] = None,
                       scores: Tuple[int, int] = (0, 0)) -> None:
        """
        绘制游戏结束画面

        Args:
            winner_id: 获胜玩家编号
            scores: (玩家1分数, 玩家2分数)
        """
        # 半透明背景
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(COLORS['background'])
        self.screen.blit(overlay, (0, 0))

        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2 - 50

        if winner_id is not None:
            self.draw_text(f"PLAYER {winner_id} WINS!", center_x, center_y,
                           center=True, size='large')
        else:
            self.draw_text("DRAW!", center_x, center_y, center=True, size='large')

        # 显示分数
        self.draw_text(f"P1: {scores[0]}  |  P2: {scores[1]}",
                       center_x, center_y + 60, center=True, size='medium')

        # 提示
        self.draw_text("Press R to Restart", center_x, center_y + 120,
                       center=True, size='medium')
        self.draw_text("Press ESC for Menu", center_x, center_y + 150,
                       center=True, size='small')

    def draw_pause_screen(self) -> None:
        """绘制暂停画面"""
        # 半透明背景
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(COLORS['background'])
        self.screen.blit(overlay, (0, 0))

        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2

        self.draw_text("PAUSED", center_x, center_y - 30,
                       center=True, size='large')
        self.draw_text("Press P to Continue", center_x, center_y + 30,
                       center=True, size='medium')
        self.draw_text("Press ESC for Menu", center_x, center_y + 60,
                       center=True, size='small')

    def draw_single_game_over(self, score: int, lines: int) -> None:
        """
        绘制单人模式游戏结束画面

        Args:
            score: 最终分数
            lines: 消除行数
        """
        # 半透明背景
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(COLORS['background'])
        self.screen.blit(overlay, (0, 0))

        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2 - 50

        self.draw_text("GAME OVER", center_x, center_y,
                       center=True, size='large')

        # 显示分数
        self.draw_text(f"Score: {score}", center_x, center_y + 60,
                       center=True, size='medium')
        self.draw_text(f"Lines: {lines}", center_x, center_y + 90,
                       center=True, size='medium')

        # 提示
        self.draw_text("Press R to Restart", center_x, center_y + 140,
                       center=True, size='medium')
        self.draw_text("Press ESC for Menu", center_x, center_y + 170,
                       center=True, size='small')
