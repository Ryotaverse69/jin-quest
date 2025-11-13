"""
JID×QUEST - キャラクター描画システム
HD-2D風のキャラクター表現
"""

import pygame
from config import *


class CharacterRenderer:
    """キャラクター描画クラス"""

    @staticmethod
    def draw_player(surface, x, y, direction='down'):
        """
        プレイヤーを描画（HD-2D風）

        Args:
            surface: 描画先サーフェス
            x: X座標
            y: Y座標
            direction: 向き ('up', 'down', 'left', 'right')
        """
        # キャラクターサイズ
        char_width = TILE_SIZE
        char_height = TILE_SIZE

        # 影を描画
        shadow = pygame.Surface((char_width, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), (0, 0, char_width, 8))
        surface.blit(shadow, (x, y + char_height - 8))

        # 本体を描画（スーツ姿の営業マン風）
        # 顔
        pygame.draw.ellipse(surface, (255, 220, 180),
                           (x + 18, y + 12, 28, 28))  # 肌色の顔

        # 髪
        pygame.draw.ellipse(surface, (40, 30, 20),
                           (x + 16, y + 8, 32, 20))  # 黒髪

        # 目
        if direction == 'down':
            pygame.draw.circle(surface, (20, 20, 20), (x + 26, y + 22), 3)
            pygame.draw.circle(surface, (20, 20, 20), (x + 38, y + 22), 3)
        elif direction == 'left':
            pygame.draw.circle(surface, (20, 20, 20), (x + 22, y + 22), 3)
            pygame.draw.circle(surface, (20, 20, 20), (x + 34, y + 22), 3)
        elif direction == 'right':
            pygame.draw.circle(surface, (20, 20, 20), (x + 30, y + 22), 3)
            pygame.draw.circle(surface, (20, 20, 20), (x + 42, y + 22), 3)
        else:  # up
            pygame.draw.line(surface, (20, 20, 20), (x + 24, y + 22), (x + 28, y + 22), 2)
            pygame.draw.line(surface, (20, 20, 20), (x + 36, y + 22), (x + 40, y + 22), 2)

        # スーツ（紺色）
        pygame.draw.rect(surface, (30, 40, 80),
                        (x + 16, y + 36, 32, 24))  # 胴体

        # ネクタイ（赤）
        pygame.draw.rect(surface, (200, 30, 30),
                        (x + 30, y + 38, 4, 18))

        # 腕
        pygame.draw.rect(surface, (30, 40, 80),
                        (x + 10, y + 38, 8, 20))  # 左腕
        pygame.draw.rect(surface, (30, 40, 80),
                        (x + 46, y + 38, 8, 20))  # 右腕

        # 手
        pygame.draw.circle(surface, (255, 220, 180), (x + 14, y + 54), 4)
        pygame.draw.circle(surface, (255, 220, 180), (x + 50, y + 54), 4)

        # 脚（スーツのズボン）
        pygame.draw.rect(surface, (20, 30, 60),
                        (x + 20, y + 56, 10, 8))  # 左脚
        pygame.draw.rect(surface, (20, 30, 60),
                        (x + 34, y + 56, 10, 8))  # 右脚

    @staticmethod
    def draw_npc(surface, x, y, npc_type='staff'):
        """
        NPCを描画（HD-2D風）

        Args:
            surface: 描画先サーフェス
            x: X座標
            y: Y座標
            npc_type: NPCタイプ ('chairman', 'president', 'staff', 'dog')
        """
        char_width = TILE_SIZE
        char_height = TILE_SIZE

        # 影を描画
        shadow = pygame.Surface((char_width, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), (0, 0, char_width, 8))
        surface.blit(shadow, (x, y + char_height - 8))

        if npc_type == 'chairman':
            # 井坂会長（貫禄のある男性）
            # 顔
            pygame.draw.ellipse(surface, (255, 210, 170),
                               (x + 16, y + 10, 32, 32))

            # 白髪
            pygame.draw.ellipse(surface, (200, 200, 200),
                               (x + 14, y + 6, 36, 22))

            # メガネ
            pygame.draw.circle(surface, (100, 100, 100), (x + 24, y + 22), 6, 2)
            pygame.draw.circle(surface, (100, 100, 100), (x + 40, y + 22), 6, 2)
            pygame.draw.line(surface, (100, 100, 100), (x + 30, y + 22), (x + 34, y + 22), 2)

            # スーツ（高級感のある黒）
            pygame.draw.rect(surface, (20, 20, 30),
                            (x + 14, y + 38, 36, 26))

            # 金色のネクタイ
            pygame.draw.rect(surface, COLORS['GOLD'],
                            (x + 30, y + 40, 4, 20))

        elif npc_type == 'president':
            # 梅田社長（女性）
            # 顔
            pygame.draw.ellipse(surface, (255, 225, 195),
                               (x + 18, y + 12, 28, 28))

            # 髪（茶色のロングヘア）
            pygame.draw.ellipse(surface, (120, 80, 40),
                               (x + 12, y + 8, 40, 28))
            pygame.draw.rect(surface, (120, 80, 40),
                            (x + 14, y + 32, 16, 12))  # 左の髪
            pygame.draw.rect(surface, (120, 80, 40),
                            (x + 34, y + 32, 16, 12))  # 右の髪

            # 目（大きめ）
            pygame.draw.circle(surface, (50, 30, 20), (x + 26, y + 22), 4)
            pygame.draw.circle(surface, (50, 30, 20), (x + 38, y + 22), 4)
            pygame.draw.circle(surface, COLORS['WHITE'], (x + 27, y + 21), 2)
            pygame.draw.circle(surface, COLORS['WHITE'], (x + 39, y + 21), 2)

            # スーツ（紺色）
            pygame.draw.rect(surface, (40, 50, 100),
                            (x + 18, y + 38, 28, 22))

            # ブラウス（白）
            pygame.draw.polygon(surface, (240, 240, 250), [
                (x + 26, y + 38),
                (x + 38, y + 38),
                (x + 32, y + 50)
            ])

        elif npc_type == 'dog':
            # ポメ吉（ポメラニアン風）
            # 体（ふわふわの茶色）
            pygame.draw.ellipse(surface, (200, 150, 80),
                               (x + 18, y + 30, 28, 24))

            # 頭
            pygame.draw.ellipse(surface, (200, 150, 80),
                               (x + 20, y + 20, 24, 20))

            # 耳（三角形）
            pygame.draw.polygon(surface, (200, 150, 80), [
                (x + 18, y + 20),
                (x + 22, y + 16),
                (x + 24, y + 22)
            ])
            pygame.draw.polygon(surface, (200, 150, 80), [
                (x + 40, y + 22),
                (x + 42, y + 16),
                (x + 46, y + 20)
            ])

            # 目
            pygame.draw.circle(surface, (20, 20, 20), (x + 26, y + 26), 3)
            pygame.draw.circle(surface, (20, 20, 20), (x + 38, y + 26), 3)
            pygame.draw.circle(surface, COLORS['WHITE'], (x + 27, y + 25), 1)
            pygame.draw.circle(surface, COLORS['WHITE'], (x + 39, y + 25), 1)

            # 鼻
            pygame.draw.circle(surface, (50, 30, 20), (x + 32, y + 32), 3)

            # 尻尾
            pygame.draw.circle(surface, (200, 150, 80), (x + 48, y + 38), 6)

        else:  # staff (一般社員)
            # 顔
            pygame.draw.ellipse(surface, (255, 215, 180),
                               (x + 18, y + 14, 28, 26))

            # 髪
            pygame.draw.ellipse(surface, (60, 50, 40),
                               (x + 16, y + 10, 32, 18))

            # 目
            pygame.draw.circle(surface, (20, 20, 20), (x + 26, y + 24), 2)
            pygame.draw.circle(surface, (20, 20, 20), (x + 38, y + 24), 2)

            # スーツ（グレー）
            pygame.draw.rect(surface, (80, 80, 90),
                            (x + 16, y + 38, 32, 22))

            # ネクタイ（青）
            pygame.draw.rect(surface, (30, 80, 150),
                            (x + 30, y + 40, 4, 16))

    @staticmethod
    def draw_enemy(surface, x, y, enemy_type):
        """
        敵を描画（HD-2D風）

        Args:
            surface: 描画先サーフェス
            x: X座標
            y: Y座標
            enemy_type: 敵タイプ ('不動産会社', '滞納者')
        """
        char_width = TILE_SIZE * 1.5
        char_height = TILE_SIZE * 1.5

        # 影
        shadow = pygame.Surface((int(char_width), 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 120), (0, 0, int(char_width), 10))
        surface.blit(shadow, (x, y + char_height - 10))

        if enemy_type == '不動産会社':
            # ビジネスマン風（やや威圧的）
            # 顔（大きめ）
            pygame.draw.ellipse(surface, (255, 210, 170),
                               (x + 20, y + 16, 56, 48))

            # 髪（黒）
            pygame.draw.ellipse(surface, (30, 30, 30),
                               (x + 18, y + 12, 60, 32))

            # サングラス
            pygame.draw.rect(surface, (20, 20, 20),
                            (x + 28, y + 32, 52, 12))
            pygame.draw.rect(surface, (40, 40, 40),
                            (x + 30, y + 34, 22, 8))
            pygame.draw.rect(surface, (40, 40, 40),
                            (x + 56, y + 34, 22, 8))

            # スーツ（黒）
            pygame.draw.rect(surface, (20, 20, 30),
                            (x + 16, y + 60, 64, 36))

            # 札束のアイコン（手に持っている）
            pygame.draw.rect(surface, (100, 180, 100),
                            (x + 10, y + 68, 12, 20))

        else:  # 滞納者
            # 困った様子の人
            # 顔
            pygame.draw.ellipse(surface, (255, 220, 190),
                               (x + 22, y + 18, 52, 44))

            # 髪（茶色、ボサボサ風）
            pygame.draw.ellipse(surface, (100, 70, 40),
                               (x + 18, y + 14, 60, 28))
            # ボサボサ感
            for i in range(5):
                pygame.draw.line(surface, (100, 70, 40),
                               (x + 20 + i*12, y + 14),
                               (x + 22 + i*12, y + 8), 2)

            # 目（困った表情）
            pygame.draw.circle(surface, (40, 40, 40), (x + 36, y + 34), 5)
            pygame.draw.circle(surface, (40, 40, 40), (x + 60, y + 34), 5)
            pygame.draw.line(surface, (40, 40, 40),
                           (x + 30, y + 28), (x + 38, y + 30), 2)
            pygame.draw.line(surface, (40, 40, 40),
                           (x + 58, y + 30), (x + 66, y + 28), 2)

            # 服（よれよれ）
            pygame.draw.rect(surface, (120, 100, 80),
                            (x + 18, y + 58, 60, 34))

            # 汗マーク
            pygame.draw.circle(surface, (100, 150, 255), (x + 78, y + 24), 6)
            pygame.draw.circle(surface, (100, 150, 255), (x + 80, y + 32), 4)
