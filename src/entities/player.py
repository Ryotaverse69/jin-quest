"""
JID×QUEST - プレイヤーエンティティ
"""

import pygame
from config import *


class Player(pygame.sprite.Sprite):
    """プレイヤークラス"""

    def __init__(self, x, y, player_class='男性営業'):
        """
        プレイヤーの初期化

        Args:
            x: X座標（タイル単位）
            y: Y座標（タイル単位）
            player_class: プレイヤークラス（'男性営業' or '女性営業'）
        """
        super().__init__()

        # 位置情報（タイル単位）
        self.tile_x = x
        self.tile_y = y

        # 実際のピクセル座標
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE

        # 移動関連
        self.speed = PLAYER_SPEED
        self.direction = 'down'  # 向き: up, down, left, right
        self.moving = False
        self.move_progress = 0  # 移動アニメーション進捗

        # プレイヤー情報
        self.player_class = player_class
        self.name = "主人公"
        self.level = 1
        self.exp = 0
        self.next_level_exp = 30

        # ステータス（仮の初期値）
        self.max_hp = 30
        self.hp = 30
        self.max_mp = 10
        self.mp = 10
        self.atk = 8
        self.defense = 6
        self.spd = 5

        # 描画用サーフェス（仮：16x16の四角）
        self.image = self.create_placeholder_sprite()
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    def create_placeholder_sprite(self):
        """仮のスプライトを作成（後でドット絵に差し替え）"""
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))

        # プレイヤークラスで色を変える
        if self.player_class == '男性営業':
            color = (100, 150, 255)  # 水色
        else:
            color = (255, 150, 200)  # ピンク

        surface.fill(color)

        # 向きを示す矢印
        arrow_color = COLORS['WHITE']
        if self.direction == 'down':
            pygame.draw.polygon(surface, arrow_color, [(8, 12), (5, 8), (11, 8)])
        elif self.direction == 'up':
            pygame.draw.polygon(surface, arrow_color, [(8, 4), (5, 8), (11, 8)])
        elif self.direction == 'left':
            pygame.draw.polygon(surface, arrow_color, [(4, 8), (8, 5), (8, 11)])
        elif self.direction == 'right':
            pygame.draw.polygon(surface, arrow_color, [(12, 8), (8, 5), (8, 11)])

        return surface

    def handle_input(self, keys):
        """
        キー入力処理

        Args:
            keys: pygame.key.get_pressed()の結果
        """
        if self.moving:
            return  # 移動中は入力を受け付けない

        # 移動入力
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.start_move('up')
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.start_move('down')
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.start_move('left')
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.start_move('right')

    def start_move(self, direction):
        """
        移動を開始

        Args:
            direction: 移動方向
        """
        self.direction = direction
        self.moving = True
        self.move_progress = 0

        # 目標タイル座標を計算
        self.target_tile_x = self.tile_x
        self.target_tile_y = self.tile_y

        if direction == 'up':
            self.target_tile_y -= 1
        elif direction == 'down':
            self.target_tile_y += 1
        elif direction == 'left':
            self.target_tile_x -= 1
        elif direction == 'right':
            self.target_tile_x += 1

    def update(self, collision_map=None):
        """
        プレイヤーの更新

        Args:
            collision_map: 衝突判定用のマップ（2次元リスト）
        """
        if self.moving:
            self.move_progress += self.speed

            # 移動完了
            if self.move_progress >= TILE_SIZE:
                self.tile_x = self.target_tile_x
                self.tile_y = self.target_tile_y
                self.x = self.tile_x * TILE_SIZE
                self.y = self.tile_y * TILE_SIZE
                self.moving = False
                self.move_progress = 0
            else:
                # 移動アニメーション
                if self.direction == 'up':
                    self.y = self.tile_y * TILE_SIZE - self.move_progress
                elif self.direction == 'down':
                    self.y = self.tile_y * TILE_SIZE + self.move_progress
                elif self.direction == 'left':
                    self.x = self.tile_x * TILE_SIZE - self.move_progress
                elif self.direction == 'right':
                    self.x = self.tile_x * TILE_SIZE + self.move_progress

        # スプライトを更新
        self.image = self.create_placeholder_sprite()
        self.rect.topleft = (self.x, self.y)

    def can_move(self, collision_map):
        """
        移動可能かチェック

        Args:
            collision_map: 衝突判定用のマップ

        Returns:
            bool: 移動可能ならTrue
        """
        if collision_map is None:
            return True

        # マップの範囲外チェック
        if (self.target_tile_y < 0 or
            self.target_tile_y >= len(collision_map) or
            self.target_tile_x < 0 or
            self.target_tile_x >= len(collision_map[0])):
            return False

        # 衝突判定
        return collision_map[self.target_tile_y][self.target_tile_x] == 0

    def get_rank(self):
        """現在の役職を取得"""
        return get_rank_name(self.level)

    def draw(self, surface, camera_x=0, camera_y=0):
        """
        プレイヤーを描画

        Args:
            surface: 描画先サーフェス
            camera_x: カメラX座標
            camera_y: カメラY座標
        """
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        surface.blit(self.image, (draw_x, draw_y))
