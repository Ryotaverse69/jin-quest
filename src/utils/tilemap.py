"""
JID×QUEST - タイルマップシステム
"""

import pygame
import json
from config import *


class TileMap:
    """タイルマップクラス"""

    def __init__(self, map_data_path):
        """
        タイルマップの初期化

        Args:
            map_data_path: マップデータのJSONファイルパス
        """
        self.load_map(map_data_path)
        self.create_tile_surfaces()

    def load_map(self, map_data_path):
        """
        マップデータを読み込む

        Args:
            map_data_path: マップデータのJSONファイルパス
        """
        with open(map_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.name = data.get('name', 'Unnamed Map')
        self.width = data['width']
        self.height = data['height']
        self.tiles = data['tiles']  # 2次元配列
        self.collision = data.get('collision', [[0] * self.width for _ in range(self.height)])
        self.events = data.get('events', [])
        self.npcs = data.get('npcs', [])
        self.spawn_point = data.get('spawn_point', {'x': 0, 'y': 0})

    def create_tile_surfaces(self):
        """タイルの描画サーフェスを作成（仮：色分け）"""
        self.tile_colors = {
            0: COLORS['BLACK'],          # 壁（黒）
            1: (200, 200, 200),          # 床（灰色）
            2: (150, 100, 50),           # ドア（茶色）
            3: (100, 100, 100),          # 階段（濃い灰色）
            4: (50, 50, 150),            # カーペット（紺色）
            5: (180, 150, 100),          # デスク（薄茶色）
        }

    def get_tile_color(self, tile_id):
        """タイルIDから色を取得"""
        return self.tile_colors.get(tile_id, COLORS['WHITE'])

    def draw(self, surface, camera_x=0, camera_y=0):
        """
        マップを描画

        Args:
            surface: 描画先サーフェス
            camera_x: カメラX座標
            camera_y: カメラY座標
        """
        # 描画範囲を計算（最適化のため画面内のタイルのみ描画）
        start_col = max(0, camera_x // TILE_SIZE)
        end_col = min(self.width, (camera_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        start_row = max(0, camera_y // TILE_SIZE)
        end_row = min(self.height, (camera_y + SCREEN_HEIGHT) // TILE_SIZE + 1)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile_id = self.tiles[row][col]
                color = self.get_tile_color(tile_id)

                # タイルの描画位置を計算
                x = col * TILE_SIZE - camera_x
                y = row * TILE_SIZE - camera_y

                pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))

                # グリッド線（デバッグ用）
                pygame.draw.rect(surface, (100, 100, 100), (x, y, TILE_SIZE, TILE_SIZE), 1)

    def is_walkable(self, tile_x, tile_y):
        """
        指定座標が歩行可能かチェック

        Args:
            tile_x: X座標（タイル単位）
            tile_y: Y座標（タイル単位）

        Returns:
            bool: 歩行可能ならTrue
        """
        # 範囲外チェック
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return False

        # 衝突判定
        return self.collision[tile_y][tile_x] == 0

    def get_event_at(self, tile_x, tile_y):
        """
        指定座標のイベントを取得

        Args:
            tile_x: X座標（タイル単位）
            tile_y: Y座標（タイル単位）

        Returns:
            dict or None: イベントデータ
        """
        for event in self.events:
            if event['x'] == tile_x and event['y'] == tile_y:
                return event
        return None

    def get_npc_at(self, tile_x, tile_y):
        """
        指定座標のNPCを取得

        Args:
            tile_x: X座標（タイル単位）
            tile_y: Y座標（タイル単位）

        Returns:
            dict or None: NPCデータ
        """
        for npc in self.npcs:
            if npc['x'] == tile_x and npc['y'] == tile_y:
                return npc
        return None
