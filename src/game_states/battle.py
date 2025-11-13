"""
JID×QUEST - バトル画面
"""

import pygame
from config import *
from src.entities.enemy import Enemy
from src.battle_system.battle_manager import BattleManager


class BattleState:
    """バトル状態クラス"""

    def __init__(self, game, player, enemy_type, enemy_level):
        """
        バトル画面の初期化

        Args:
            game: メインゲームオブジェクト
            player: プレイヤーオブジェクト
            enemy_type: 敵のタイプ
            enemy_level: 敵のレベル
        """
        self.game = game
        self.player = player
        self.font = pygame.font.Font(None, FONT_SIZE)

        # 敵を生成
        self.enemy = Enemy(enemy_type, enemy_level)

        # バトルマネージャー
        self.battle_manager = BattleManager(player, self.enemy)

        # UI状態
        self.command_index = 0  # 選択中のコマンド
        self.commands = ['たたかう', 'ぼうぎょ', 'にげる']
        self.message_wait_timer = 0  # メッセージ表示待機時間
        self.message_display_time = 90  # メッセージ表示時間（1.5秒）

        # トランジション
        self.transition_timer = 0
        self.transition_phase = 'fade_in'  # fade_in, battle, fade_out

    def handle_events(self, events):
        """
        イベント処理

        Args:
            events: pygameイベントリスト
        """
        # トランジション中は入力を受け付けない
        if self.transition_phase == 'fade_in':
            return

        # メッセージ表示中
        if self.battle_manager.has_messages():
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.battle_manager.next_message()
                        self.message_wait_timer = 0

                        # メッセージがなくなったら敵のターン実行
                        if not self.battle_manager.has_messages():
                            if self.battle_manager.battle_phase == 'enemy_turn':
                                self.battle_manager.execute_enemy_turn()
            return

        # バトル終了時
        if self.battle_manager.is_battle_over():
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.end_battle()
            return

        # プレイヤーのターン - コマンド選択
        if self.battle_manager.battle_phase == 'player_turn':
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.command_index = (self.command_index - 1) % len(self.commands)

                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.command_index = (self.command_index + 1) % len(self.commands)

                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.execute_command()

    def execute_command(self):
        """選択されたコマンドを実行"""
        command = self.commands[self.command_index]

        if command == 'たたかう':
            self.battle_manager.execute_player_attack()
        elif command == 'ぼうぎょ':
            self.battle_manager.execute_player_defend()
        elif command == 'にげる':
            self.battle_manager.execute_player_escape()

    def update(self):
        """バトル状態の更新"""
        # トランジション処理
        if self.transition_phase == 'fade_in':
            self.transition_timer += 1
            if self.transition_timer >= BATTLE_TRANSITION_FRAMES:
                self.transition_phase = 'battle'
                self.transition_timer = 0

        # メッセージ自動送り
        if self.battle_manager.has_messages():
            self.message_wait_timer += 1
            if self.message_wait_timer >= self.message_display_time:
                self.battle_manager.next_message()
                self.message_wait_timer = 0

                # 敵のターン実行
                if not self.battle_manager.has_messages():
                    if self.battle_manager.battle_phase == 'enemy_turn':
                        self.battle_manager.execute_enemy_turn()

    def end_battle(self):
        """バトルを終了してフィールドに戻る"""
        result = self.battle_manager.get_battle_result()

        # 敗北時はHP回復
        if result['phase'] == 'defeat':
            self.player.hp = self.player.max_hp // 2

        # フィールドに戻る
        self.game.state = GameState.FIELD

    def draw(self, surface):
        """
        描画処理

        Args:
            surface: 描画先サーフェス
        """
        # 背景（黒）
        surface.fill(COLORS['BLACK'])

        # フェードイン効果
        if self.transition_phase == 'fade_in':
            alpha = int(255 * (1 - self.transition_timer / BATTLE_TRANSITION_FRAMES))
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill(COLORS['WHITE'])
            fade_surface.set_alpha(alpha)
            surface.blit(fade_surface, (0, 0))
            return

        # 敵の描画
        if self.enemy.is_alive:
            enemy_sprite = self.enemy.create_sprite()
            enemy_x = SCREEN_WIDTH // 2 - 16
            enemy_y = 50
            surface.blit(enemy_sprite, (enemy_x, enemy_y))

            # 敵の名前
            name_surface = self.font.render(self.enemy.name, True, COLORS['WHITE'])
            name_rect = name_surface.get_rect(center=(SCREEN_WIDTH // 2, 30))
            surface.blit(name_surface, name_rect)

            # 敵のHP
            hp_text = f"HP: {self.enemy.hp}/{self.enemy.max_hp}"
            hp_surface = self.font.render(hp_text, True, COLORS['GOLD'])
            hp_rect = hp_surface.get_rect(center=(SCREEN_WIDTH // 2, 90))
            surface.blit(hp_surface, hp_rect)

        # プレイヤー情報（下部）
        self.draw_player_status(surface)

        # メッセージウィンドウ
        self.draw_message_window(surface)

        # コマンドウィンドウ
        if self.battle_manager.battle_phase == 'player_turn' and not self.battle_manager.has_messages():
            self.draw_command_window(surface)

        # バトル終了時のメッセージ
        if self.battle_manager.is_battle_over() and not self.battle_manager.has_messages():
            result_text = ""
            if self.battle_manager.battle_phase == 'victory':
                result_text = "【勝利】 Enterキーで続ける"
            elif self.battle_manager.battle_phase == 'defeat':
                result_text = "【敗北】 Enterキーで続ける"
            elif self.battle_manager.battle_phase == 'escaped':
                result_text = "【逃走成功】 Enterキーで続ける"

            result_surface = self.font.render(result_text, True, COLORS['GOLD'])
            result_rect = result_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
            surface.blit(result_surface, result_rect)

    def draw_player_status(self, surface):
        """プレイヤーのステータス表示"""
        # 背景
        status_bg = pygame.Surface((SCREEN_WIDTH - 20, 30))
        status_bg.fill(COLORS['DARK_BLUE'])
        surface.blit(status_bg, (10, 115))

        # ステータステキスト
        status_text = f"{self.player.name} Lv.{self.player.level} {self.player.get_rank()}"
        status_surface = self.font.render(status_text, True, COLORS['WHITE'])
        surface.blit(status_surface, (15, 120))

        hp_text = f"HP: {self.player.hp}/{self.player.max_hp}"
        hp_surface = self.font.render(hp_text, True, COLORS['WHITE'])
        surface.blit(hp_surface, (15, 133))

        mp_text = f"MP: {self.player.mp}/{self.player.max_mp}"
        mp_surface = self.font.render(mp_text, True, COLORS['WHITE'])
        surface.blit(mp_surface, (120, 133))

    def draw_message_window(self, surface):
        """メッセージウィンドウの描画"""
        # ウィンドウ背景
        window_bg = pygame.Surface((SCREEN_WIDTH - 20, 50))
        window_bg.fill(COLORS['DARK_BLUE'])
        pygame.draw.rect(window_bg, COLORS['WINDOW_BLUE'], (0, 0, SCREEN_WIDTH - 20, 50), 2)
        surface.blit(window_bg, (10, 155))

        # メッセージテキスト
        message = self.battle_manager.get_current_message()
        if message:
            message_surface = self.font.render(message, True, COLORS['WHITE'])
            surface.blit(message_surface, (20, 170))

            # "▼"マーク
            if self.battle_manager.has_messages():
                arrow_surface = self.font.render("▼", True, COLORS['WHITE'])
                surface.blit(arrow_surface, (SCREEN_WIDTH - 30, 188))

    def draw_command_window(self, surface):
        """コマンドウィンドウの描画"""
        # ウィンドウ背景
        window_x = 150
        window_y = 155
        window_width = 90
        window_height = 50

        window_bg = pygame.Surface((window_width, window_height))
        window_bg.fill(COLORS['DARK_BLUE'])
        pygame.draw.rect(window_bg, COLORS['WINDOW_BLUE'], (0, 0, window_width, window_height), 2)
        surface.blit(window_bg, (window_x, window_y))

        # コマンドリスト
        for i, command in enumerate(self.commands):
            y_offset = window_y + 10 + i * 15

            # 選択中のコマンドにカーソル
            if i == self.command_index:
                cursor_surface = self.font.render("▶", True, COLORS['GOLD'])
                surface.blit(cursor_surface, (window_x + 5, y_offset))

            command_surface = self.font.render(command, True, COLORS['WHITE'])
            surface.blit(command_surface, (window_x + 20, y_offset))
