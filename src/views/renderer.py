"""
游戏渲染器
使用 Pygame 绘制游戏画面
"""

import pygame
from typing import Optional

from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, FPS,
    BOARD_WIDTH, BOARD_HEIGHT, CELL_SIZE,
    PLAYER1_BOARD_X, PLAYER2_BOARD_X, BOARD_MARGIN_Y,
    COLORS, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM
)


class Renderer:
    """游戏渲染器类"""

    def __init__(self):
        """初始化渲染器"""
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.fps = FPS

        # 加载字体
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)

    def clear(self) -> None:
        """清空屏幕"""
        self.screen.fill(COLORS['background'])

    def draw_board(self, board_x: int, board_y: int, grid: list) -> None:
        """
        绘制棋盘

        Args:
            board_x: 棋盘左上角 X 坐标
            board_y: 棋盘左上角 Y 坐标
            grid: 棋盘网格数据
        """
        # 绘制棋盘背景
        board_rect = pygame.Rect(
            board_x, board_y,
            BOARD_WIDTH * CELL_SIZE,
            BOARD_HEIGHT * CELL_SIZE
        )
        pygame.draw.rect(self.screen, COLORS['board_bg'], board_rect)

        # 绘制网格线
        for row in range(BOARD_HEIGHT + 1):
            y = board_y + row * CELL_SIZE
            pygame.draw.line(
                self.screen, COLORS['grid'],
                (board_x, y), (board_x + BOARD_WIDTH * CELL_SIZE, y)
            )

        for col in range(BOARD_WIDTH + 1):
            x = board_x + col * CELL_SIZE
            pygame.draw.line(
                self.screen, COLORS['grid'],
                (x, board_y), (x, board_y + BOARD_HEIGHT * CELL_SIZE)
            )

        # 绘制已放置的方块
        for row in range(BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                cell = grid[row][col]
                if cell is not None:
                    self.draw_cell(board_x, board_y, row, col, cell)

    def draw_cell(self, board_x: int, board_y: int,
                  row: int, col: int, cell_type: str) -> None:
        """
        绘制单个单元格

        Args:
            board_x: 棋盘左上角 X 坐标
            board_y: 棋盘左上角 Y 坐标
            row: 行号
            col: 列号
            cell_type: 方块类型
        """
        x = board_x + col * CELL_SIZE
        y = board_y + row * CELL_SIZE

        # 获取颜色
        color = COLORS.get(cell_type, COLORS['garbage'])

        # 绘制填充矩形
        rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(self.screen, color, rect)

        # 绘制高光效果（左上边缘）
        highlight = tuple(min(c + 50, 255) for c in color)
        pygame.draw.line(self.screen, highlight, (x + 1, y + 1), (x + CELL_SIZE - 2, y + 1), 2)
        pygame.draw.line(self.screen, highlight, (x + 1, y + 1), (x + 1, y + CELL_SIZE - 2), 2)

        # 绘制阴影效果（右下边缘）
        shadow = tuple(max(c - 50, 0) for c in color)
        pygame.draw.line(self.screen, shadow, (x + CELL_SIZE - 1, y + 2), (x + CELL_SIZE - 1, y + CELL_SIZE - 1), 2)
        pygame.draw.line(self.screen, shadow, (x + 2, y + CELL_SIZE - 1), (x + CELL_SIZE - 1, y + CELL_SIZE - 1), 2)

    def draw_tetromino(self, board_x: int, board_y: int,
                       tetromino, is_ghost: bool = False) -> None:
        """
        绘制活动方块

        Args:
            board_x: 棋盘左上角 X 坐标
            board_y: 棋盘左上角 Y 坐标
            tetromino: Tetromino 对象
            is_ghost: 是否绘制幽灵方块
        """
        for row, col in tetromino.absolute_cells:
            if row >= 0:  # 只绘制可见部分
                x = board_x + col * CELL_SIZE
                y = board_y + row * CELL_SIZE

                if is_ghost:
                    # 幽灵方块：半透明边框
                    rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
                    pygame.draw.rect(self.screen, COLORS['ghost'], rect, 2)
                else:
                    # 正常方块
                    self.draw_cell(board_x, board_y, row, col, tetromino.type)

    def draw_border(self, board_x: int, board_y: int) -> None:
        """
        绘制棋盘边框

        Args:
            board_x: 棋盘左上角 X 坐标
            board_y: 棋盘左上角 Y 坐标
        """
        border_rect = pygame.Rect(
            board_x - 2, board_y - 2,
            BOARD_WIDTH * CELL_SIZE + 4,
            BOARD_HEIGHT * CELL_SIZE + 4
        )
        pygame.draw.rect(self.screen, COLORS['border'], border_rect, 3)

    def draw_text(self, text: str, x: int, y: int,
                  font_size: str = 'medium', center: bool = False) -> None:
        """
        绘制文本

        Args:
            text: 要绘制的文本
            x: X 坐标
            y: Y 坐标
            font_size: 字体大小 ('large' 或 'medium')
            center: 是否居中对齐
        """
        font = self.font_large if font_size == 'large' else self.font_medium
        text_surface = font.render(text, True, COLORS['text'])

        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, (x, y))

    def draw_player_info(self, player_num: int, board_x: int,
                         score: int, lines: int) -> None:
        """
        绘制玩家信息

        Args:
            player_num: 玩家编号
            board_x: 棋盘 X 坐标
            score: 分数
            lines: 消行数
        """
        # 玩家标签
        self.draw_text(f"Player {player_num}", board_x, 20, 'large')

        # 分数和消行
        info_y = BOARD_MARGIN_Y + BOARD_HEIGHT * CELL_SIZE + 20
        self.draw_text(f"Score: {score}", board_x, info_y)
        self.draw_text(f"Lines: {lines}", board_x, info_y + 25)

    def update(self) -> None:
        """更新显示"""
        pygame.display.flip()
        self.clock.tick(self.fps)

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
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def quit(self) -> None:
        """退出渲染器"""
        pygame.quit()
