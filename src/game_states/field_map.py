"""
JID×QUEST - フィールドマップ画面
"""

import pygame
import random
from config import *
from src.entities.player import Player
from src.utils.tilemap import TileMap
from src.battle_system.damage_calc import get_enemy_for_area


class FieldMapState:
    """フィールドマップ状態クラス"""

    def __init__(self, game, map_path='data/maps/jid_hq_2f.json'):
        """
        フィールドマップの初期化

        Args:
            game: メインゲームオブジェクト
            map_path: マップデータのパス
        """
        self.game = game
        self.font = pygame.font.Font(None, 16)

        # マップ読み込み
        self.tilemap = TileMap(map_path)

        # プレイヤー作成
        spawn = self.tilemap.spawn_point
        self.player = Player(spawn['x'], spawn['y'])

        # カメラ座標
        self.camera_x = 0
        self.camera_y = 0

        # UI表示
        self.show_info = True

        # エンカウントシステム
        self.encounter_rate = 0.05  # 1歩ごとの遭遇率（5%）
        self.encounter_enabled = True  # エンカウント有効フラグ
        self.area_level = 2  # 現在エリアのレベル（2F営業部）

    def handle_events(self, events):
        """
        イベント処理

        Args:
            events: pygameイベントリスト
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # メニューを開く（未実装）
                    print("メニューを開く（未実装）")

                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    # 目の前のNPCに話しかける
                    self.interact()

                if event.key == pygame.K_i:
                    # 情報表示の切り替え
                    self.show_info = not self.show_info

    def interact(self):
        """目の前のタイルとインタラクション"""
        # プレイヤーの向いている方向のタイル座標を取得
        target_x = self.player.tile_x
        target_y = self.player.tile_y

        if self.player.direction == 'up':
            target_y -= 1
        elif self.player.direction == 'down':
            target_y += 1
        elif self.player.direction == 'left':
            target_x -= 1
        elif self.player.direction == 'right':
            target_x += 1

        # NPCチェック
        npc = self.tilemap.get_npc_at(target_x, target_y)
        if npc:
            print(f"{npc['name']}に話しかけた: {npc.get('dialogue', '...')}")
            # TODO: 会話ウィンドウを表示

        # イベントチェック
        event = self.tilemap.get_event_at(target_x, target_y)
        if event:
            print(f"イベント発生: {event}")
            # TODO: イベント処理

    def update(self):
        """状態の更新"""
        # キー入力処理
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        # プレイヤーが移動を開始する時に衝突判定
        if self.player.moving and self.player.move_progress == 0:
            if not self.tilemap.is_walkable(self.player.target_tile_x, self.player.target_tile_y):
                # 移動キャンセル
                self.player.moving = False

        # プレイヤー更新
        was_moving = self.player.moving
        self.player.update()

        # 移動完了時にエンカウント判定
        if was_moving and not self.player.moving and self.encounter_enabled:
            self.check_encounter()

        # カメラをプレイヤーに追従
        self.update_camera()

    def check_encounter(self):
        """エンカウント判定"""
        if random.random() < self.encounter_rate:
            # エンカウント発生！
            enemy_data = get_enemy_for_area(self.area_level)
            self.start_battle(enemy_data['type'], enemy_data['level'])

    def start_battle(self, enemy_type, enemy_level):
        """
        バトルを開始

        Args:
            enemy_type: 敵のタイプ
            enemy_level: 敵のレベル
        """
        from src.game_states.battle import BattleState

        print(f"バトル開始！ {enemy_type} Lv.{enemy_level}")

        # バトル状態に遷移
        self.game.battle_state = BattleState(self.game, self.player, enemy_type, enemy_level)
        self.game.state = GameState.BATTLE

    def update_camera(self):
        """カメラをプレイヤーに追従させる"""
        # プレイヤーを画面中央に配置
        target_camera_x = self.player.x - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        target_camera_y = self.player.y - SCREEN_HEIGHT // 2 + TILE_SIZE // 2

        # マップの境界内に制限
        max_camera_x = self.tilemap.width * TILE_SIZE - SCREEN_WIDTH
        max_camera_y = self.tilemap.height * TILE_SIZE - SCREEN_HEIGHT

        self.camera_x = max(0, min(target_camera_x, max_camera_x))
        self.camera_y = max(0, min(target_camera_y, max_camera_y))

    def draw(self, surface):
        """
        描画処理

        Args:
            surface: 描画先サーフェス
        """
        # 背景
        surface.fill(COLORS['BLACK'])

        # マップ描画
        self.tilemap.draw(surface, self.camera_x, self.camera_y)

        # NPCを描画（仮）
        self.draw_npcs(surface)

        # プレイヤー描画
        self.player.draw(surface, self.camera_x, self.camera_y)

        # UI描画
        if self.show_info:
            self.draw_ui(surface)

    def draw_npcs(self, surface):
        """NPCを描画"""
        for npc_data in self.tilemap.npcs:
            npc_x = npc_data['x'] * TILE_SIZE - self.camera_x
            npc_y = npc_data['y'] * TILE_SIZE - self.camera_y

            # 仮：NPCを黄色い四角で表示
            pygame.draw.rect(surface, COLORS['GOLD'],
                           (npc_x, npc_y, TILE_SIZE, TILE_SIZE))

            # 名前を表示
            name_surface = self.font.render(npc_data['name'], True, COLORS['WHITE'])
            name_rect = name_surface.get_rect(center=(npc_x + TILE_SIZE // 2, npc_y - 5))
            surface.blit(name_surface, name_rect)

    def draw_ui(self, surface):
        """UI情報を描画"""
        # 上部に情報パネル
        info_bg = pygame.Surface((SCREEN_WIDTH, 30))
        info_bg.fill(COLORS['DARK_BLUE'])
        info_bg.set_alpha(200)
        surface.blit(info_bg, (0, 0))

        # プレイヤー情報
        info_text = f"{self.player.name} Lv.{self.player.level} {self.player.get_rank()} | HP:{self.player.hp}/{self.player.max_hp} MP:{self.player.mp}/{self.player.max_mp}"
        info_surface = self.font.render(info_text, True, COLORS['WHITE'])
        surface.blit(info_surface, (5, 8))

        # マップ名
        map_text = self.tilemap.name
        map_surface = self.font.render(map_text, True, COLORS['GOLD'])
        map_rect = map_surface.get_rect(right=SCREEN_WIDTH - 5, centery=15)
        surface.blit(map_surface, map_rect)

        # デバッグ情報
        debug_text = f"座標: ({self.player.tile_x}, {self.player.tile_y}) 向き: {self.player.direction}"
        debug_surface = self.font.render(debug_text, True, COLORS['LIGHT_BLUE'])
        surface.blit(debug_surface, (5, SCREEN_HEIGHT - 15))
