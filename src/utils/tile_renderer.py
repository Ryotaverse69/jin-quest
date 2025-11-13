"""
JID×QUEST - HD-2D風タイル描画システム
"""

import pygame
from config import TILE_SIZE, COLORS


class TileRenderer:
    """HD-2D風タイル描画クラス"""

    @staticmethod
    def draw_wall(surface, x, y):
        """
        壁タイルを描画（HD-2D風）

        Args:
            surface: 描画先サーフェス
            x: X座標
            y: Y座標
        """
        # ベース色（ダークグレー）
        base_color = (30, 30, 40)
        pygame.draw.rect(surface, base_color, (x, y, TILE_SIZE, TILE_SIZE))

        # 微細なタイルパターン
        tile_dark = (20, 20, 30)
        tile_light = (40, 40, 50)

        # 4x4のタイルパターン
        sub_size = TILE_SIZE // 4
        for i in range(4):
            for j in range(4):
                color = tile_dark if (i + j) % 2 == 0 else tile_light
                pygame.draw.rect(surface, color,
                               (x + i * sub_size, y + j * sub_size, sub_size, sub_size))

        # 影（下と右）
        pygame.draw.line(surface, (10, 10, 15),
                        (x, y + TILE_SIZE - 1), (x + TILE_SIZE - 1, y + TILE_SIZE - 1), 2)
        pygame.draw.line(surface, (10, 10, 15),
                        (x + TILE_SIZE - 1, y), (x + TILE_SIZE - 1, y + TILE_SIZE - 1), 2)

    @staticmethod
    def draw_floor(surface, x, y):
        """
        床タイルを描画（HD-2D風）

        Args:
            surface: 描画先サーフェス
            x: X座標
            y: Y座標
        """
        # ベース色（明るいグレー）
        base_color = (220, 220, 230)
        pygame.draw.rect(surface, base_color, (x, y, TILE_SIZE, TILE_SIZE))

        # タイル模様
        tile_color1 = (200, 200, 210)
        tile_color2 = (210, 210, 220)

        # チェッカーパターン
        half = TILE_SIZE // 2
        pygame.draw.rect(surface, tile_color1, (x, y, half, half))
        pygame.draw.rect(surface, tile_color2, (x + half, y, half, half))
        pygame.draw.rect(surface, tile_color2, (x, y + half, half, half))
        pygame.draw.rect(surface, tile_color1, (x + half, y + half, half, half))

        # タイルの目地
        grout_color = (180, 180, 190)
        pygame.draw.line(surface, grout_color, (x, y + half), (x + TILE_SIZE, y + half), 1)
        pygame.draw.line(surface, grout_color, (x + half, y), (x + half, y + TILE_SIZE), 1)

        # ハイライト（左上）
        pygame.draw.line(surface, (240, 240, 250), (x, y), (x + TILE_SIZE, y), 1)
        pygame.draw.line(surface, (240, 240, 250), (x, y), (x, y + TILE_SIZE), 1)

    @staticmethod
    def draw_door(surface, x, y):
        """
        ドアタイルを描画（HD-2D風）

        Args:
            surface: 描画先サーフェス
            x: X座標
            y: Y座標
        """
        # ベース色（木の色）
        base_color = (120, 80, 40)
        pygame.draw.rect(surface, base_color, (x, y, TILE_SIZE, TILE_SIZE))

        # ドアパネル
        panel_color = (140, 90, 45)
        panel_dark = (100, 70, 35)

        # 2つのパネル
        margin = TILE_SIZE // 8
        panel_width = (TILE_SIZE - margin * 3) // 2

        # 左パネル
        pygame.draw.rect(surface, panel_color,
                        (x + margin, y + margin, panel_width, TILE_SIZE - margin * 2))
        pygame.draw.rect(surface, panel_dark,
                        (x + margin, y + margin, panel_width, TILE_SIZE - margin * 2), 2)

        # 右パネル
        pygame.draw.rect(surface, panel_color,
                        (x + margin * 2 + panel_width, y + margin, panel_width, TILE_SIZE - margin * 2))
        pygame.draw.rect(surface, panel_dark,
                        (x + margin * 2 + panel_width, y + margin, panel_width, TILE_SIZE - margin * 2), 2)

        # ドアノブ
        knob_x = x + TILE_SIZE - margin * 2
        knob_y = y + TILE_SIZE // 2
        pygame.draw.circle(surface, COLORS['GOLD'], (knob_x, knob_y), 4)
        pygame.draw.circle(surface, (180, 140, 20), (knob_x, knob_y), 4, 1)

    @staticmethod
    def draw_stairs(surface, x, y):
        """
        階段タイルを描画（HD-2D風）

        Args:
            surface: 描画先サーフェス
            x: X座標
            y: Y座標
        """
        # ベース色（グレー）
        base_color = (100, 100, 110)
        pygame.draw.rect(surface, base_color, (x, y, TILE_SIZE, TILE_SIZE))

        # 階段のステップ
        num_steps = 5
        step_height = TILE_SIZE // num_steps

        for i in range(num_steps):
            step_y = y + i * step_height
            # ステップ面（明るめ）
            step_color = (120 + i * 5, 120 + i * 5, 130 + i * 5)
            pygame.draw.rect(surface, step_color,
                           (x, step_y, TILE_SIZE, step_height // 2))

            # ステップ側面（暗め）
            side_color = (80 + i * 5, 80 + i * 5, 90 + i * 5)
            pygame.draw.rect(surface, side_color,
                           (x, step_y + step_height // 2, TILE_SIZE, step_height // 2))

        # 矢印（上向き）
        arrow_color = COLORS['GOLD']
        center_x = x + TILE_SIZE // 2
        center_y = y + TILE_SIZE // 2
        arrow_size = TILE_SIZE // 4

        # 上向き三角形
        points = [
            (center_x, center_y - arrow_size),
            (center_x - arrow_size, center_y + arrow_size),
            (center_x + arrow_size, center_y + arrow_size)
        ]
        pygame.draw.polygon(surface, arrow_color, points)

    @staticmethod
    def draw_carpet(surface, x, y):
        """
        カーペットタイルを描画（HD-2D風）

        Args:
            surface: 描画先サーフェス
            x: X座標
            y: Y座標
        """
        # ベース色（紺色）
        base_color = (40, 40, 120)
        pygame.draw.rect(surface, base_color, (x, y, TILE_SIZE, TILE_SIZE))

        # カーペットパターン
        pattern_color1 = (50, 50, 140)
        pattern_color2 = (30, 30, 100)

        # ダイヤモンドパターン
        quarter = TILE_SIZE // 4
        for i in range(4):
            for j in range(4):
                color = pattern_color1 if (i + j) % 2 == 0 else pattern_color2
                diamond_x = x + i * quarter
                diamond_y = y + j * quarter
                pygame.draw.rect(surface, color, (diamond_x, diamond_y, quarter, quarter))

        # 縁取り
        border_color = (60, 60, 80)
        pygame.draw.rect(surface, border_color, (x, y, TILE_SIZE, TILE_SIZE), 2)

    @staticmethod
    def draw_desk(surface, x, y):
        """
        デスクタイルを描画（HD-2D風）

        Args:
            surface: 描画先サーフェス
            x: X座標
            y: Y座標
        """
        # ベース色（床）
        base_color = (220, 220, 230)
        pygame.draw.rect(surface, base_color, (x, y, TILE_SIZE, TILE_SIZE))

        # デスク本体（木の色）
        desk_color = (160, 120, 80)
        desk_dark = (140, 100, 60)
        desk_light = (180, 140, 100)

        # デスク天板
        margin = TILE_SIZE // 8
        desk_rect = pygame.Rect(x + margin, y + margin, TILE_SIZE - margin * 2, TILE_SIZE - margin * 2)
        pygame.draw.rect(surface, desk_color, desk_rect)

        # 立体感（影とハイライト）
        pygame.draw.line(surface, desk_light,
                        (desk_rect.left, desk_rect.top),
                        (desk_rect.right, desk_rect.top), 2)
        pygame.draw.line(surface, desk_light,
                        (desk_rect.left, desk_rect.top),
                        (desk_rect.left, desk_rect.bottom), 2)
        pygame.draw.line(surface, desk_dark,
                        (desk_rect.left, desk_rect.bottom),
                        (desk_rect.right, desk_rect.bottom), 2)
        pygame.draw.line(surface, desk_dark,
                        (desk_rect.right, desk_rect.top),
                        (desk_rect.right, desk_rect.bottom), 2)

        # デスク上のアイテム（書類）
        paper_color = (250, 250, 255)
        paper_x = x + TILE_SIZE // 3
        paper_y = y + TILE_SIZE // 3
        paper_w = TILE_SIZE // 4
        paper_h = TILE_SIZE // 3
        pygame.draw.rect(surface, paper_color, (paper_x, paper_y, paper_w, paper_h))
        pygame.draw.rect(surface, (200, 200, 210), (paper_x, paper_y, paper_w, paper_h), 1)

        # ペン
        pen_color = (50, 50, 200)
        pen_x = paper_x + paper_w + 4
        pen_y = paper_y + paper_h // 2
        pygame.draw.line(surface, pen_color,
                        (pen_x, pen_y), (pen_x + paper_w // 2, pen_y), 3)

    @staticmethod
    def draw_tile(surface, x, y, tile_id):
        """
        タイルIDに応じて適切なタイルを描画

        Args:
            surface: 描画先サーフェス
            x: X座標
            y: Y座標
            tile_id: タイルID
        """
        if tile_id == 0:
            TileRenderer.draw_wall(surface, x, y)
        elif tile_id == 1:
            TileRenderer.draw_floor(surface, x, y)
        elif tile_id == 2:
            TileRenderer.draw_door(surface, x, y)
        elif tile_id == 3:
            TileRenderer.draw_stairs(surface, x, y)
        elif tile_id == 4:
            TileRenderer.draw_carpet(surface, x, y)
        elif tile_id == 5:
            TileRenderer.draw_desk(surface, x, y)
        else:
            # デフォルト（白）
            pygame.draw.rect(surface, COLORS['WHITE'], (x, y, TILE_SIZE, TILE_SIZE))
