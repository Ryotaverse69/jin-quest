"""
JID×QUEST - フィールドマップ画面
"""

import pygame
import random
import json
from config import *
from src.entities.player import Player
from src.utils.tilemap import TileMap
from src.battle_system.damage_calc import get_enemy_for_area
from src.ui.dialogue_box import DialogueBox
from src.ui.menu_window import MenuWindow
from src.utils.save_load import SaveLoadManager
from src.utils.event_manager import EventManager
from src.systems.quest_system import QuestSystem


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
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.map_path = map_path  # マップパスを保存

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

        # 会話システム
        self.dialogue_box = DialogueBox()
        self.load_dialogue_data()

        # セーブ/ロードシステム
        self.save_manager = SaveLoadManager()

        # イベントシステム
        self.event_manager = EventManager()
        self.event_manager.load_events()

        # クエストシステム
        self.quest_system = QuestSystem()
        self.quest_system.load_quests()

        # メニューシステム
        self.menu_window = MenuWindow(save_callback=self.save_game)

        # 初回起動フラグ
        self.initial_event_triggered = False

    def load_dialogue_data(self):
        """会話データを読み込み"""
        try:
            with open('data/dialogues/npcs.json', 'r', encoding='utf-8') as f:
                self.dialogue_data = json.load(f)
        except FileNotFoundError:
            print("警告: 会話データが見つかりません")
            self.dialogue_data = {}

    def save_game(self, slot):
        """
        ゲームをセーブ

        Args:
            slot: セーブスロット番号

        Returns:
            bool: セーブ成功時True
        """
        return self.save_manager.save_game(self.player, self.map_path, slot)

    def handle_events(self, events):
        """
        イベント処理

        Args:
            events: pygameイベントリスト
        """
        # メニュー表示中はメニューに入力を渡す
        if self.menu_window.is_active:
            self.menu_window.handle_input(events)
            return

        # 会話中は会話ウィンドウに入力を渡す
        if self.dialogue_box.is_active:
            self.dialogue_box.handle_input(events)
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # メニューを開く
                    self.menu_window.open()

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
            self.talk_to_npc(npc)
            return

        # イベントチェック
        event = self.tilemap.get_event_at(target_x, target_y)
        if event:
            print(f"イベント発生: {event}")
            # TODO: イベント処理

    def talk_to_npc(self, npc):
        """
        NPCと会話

        Args:
            npc: NPCデータ
        """
        npc_name = npc['name']

        # 会話データから適切なメッセージを取得
        if npc_name in self.dialogue_data:
            npc_dialogues = self.dialogue_data[npc_name]

            # レベルに応じたメッセージを選択
            if f"レベル{self.player.level}" in npc_dialogues:
                messages = npc_dialogues[f"レベル{self.player.level}"]
            elif "通常" in npc_dialogues:
                messages = npc_dialogues["通常"]
            elif "初回" in npc_dialogues:
                messages = npc_dialogues["初回"]
            else:
                # デフォルトメッセージ
                messages = list(npc_dialogues.values())[0]

            # 会話開始
            self.dialogue_box.start_dialogue(messages, npc_name, auto_close=False)
        else:
            # 会話データがない場合はデフォルトメッセージ
            default_message = npc.get('dialogue', '...')
            self.dialogue_box.start_dialogue([default_message], npc_name, auto_close=False)

    def trigger_story_event(self, event_id):
        """
        ストーリーイベントを発生させる

        Args:
            event_id: イベントID
        """
        event_data = self.event_manager.start_event(event_id)
        if not event_data:
            return

        # イベントの最初のステップを処理
        self.process_event_step()

    def process_event_step(self):
        """現在のイベントステップを処理"""
        step_data = self.event_manager.get_current_step()
        if not step_data:
            return

        step_type = step_data.get('type')

        if step_type == 'dialogue':
            # 会話ステップ
            speaker = step_data.get('speaker', 'システム')
            messages = step_data.get('messages', [])
            self.dialogue_box.start_dialogue(messages, speaker, auto_close=False)
            # 会話終了後に次のステップへ進める
            self.event_manager.advance_step()
            # 次のステップがあれば処理
            if self.event_manager.is_event_active():
                # 会話が終わったら次のステップを処理（連続会話の場合）
                next_step = self.event_manager.get_current_step()
                if next_step and next_step.get('type') == 'dialogue':
                    # 現在の会話が終わるまで待つ必要があるので、ここでは処理しない
                    pass

        elif step_type == 'set_flag':
            # フラグ設定ステップ
            flag_name = step_data.get('flag')
            if flag_name:
                self.event_manager.set_flag(flag_name, True)
            # 次のステップへ
            if not self.event_manager.advance_step():
                # イベント終了
                pass

        elif step_type == 'objective':
            # 目標表示ステップ
            objective_text = step_data.get('text', '')
            self.dialogue_box.start_dialogue([f"【目標】", objective_text], "システム", auto_close=False)
            self.event_manager.advance_step()

    def update(self):
        """状態の更新"""
        # 初回イベントの発生
        if not self.initial_event_triggered and not self.dialogue_box.is_active:
            self.initial_event_triggered = True
            # 入社式イベントが未完了なら開始
            if self.event_manager.can_trigger_event('welcome_ceremony'):
                welcome_messages = [
                    "ようこそ、JID Corporationへ。",
                    "私は井坂、この会社の創設者だ。",
                    "今日から君も我が社の一員だ。",
                    "営業として、多くの契約を",
                    "取ってきてほしい。",
                    "",
                    "入社おめでとうございます！",
                    "私は梅田、社長をしています。",
                    "一緒に最強の会社を作りましょう。",
                    "困ったことがあれば、",
                    "いつでも相談してください。"
                ]
                self.dialogue_box.start_dialogue(welcome_messages, "JID Corporation", auto_close=False)
                self.event_manager.set_flag('welcome_ceremony_done', True)

        # 会話ウィンドウの更新
        self.dialogue_box.update()

        # メニューウィンドウの更新
        self.menu_window.update()

        # メニュー表示中または会話中は移動できない
        if self.menu_window.is_active or self.dialogue_box.is_active:
            return

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

        # 会話ウィンドウ描画
        self.dialogue_box.draw(surface)

        # メニューウィンドウ描画
        self.menu_window.draw(surface, self.player)

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
