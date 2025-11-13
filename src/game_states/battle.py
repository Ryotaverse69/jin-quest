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
        self.commands = ['たたかう', 'スキル', 'アイテム', 'ぼうぎょ', 'にげる']
        self.message_wait_timer = 0  # メッセージ表示待機時間
        self.message_display_time = 90  # メッセージ表示時間（1.5秒）

        # サブメニュー状態
        self.menu_mode = 'main'  # 'main', 'skill', 'item'
        self.submenu_index = 0  # サブメニューの選択インデックス

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
                        if self.menu_mode == 'main':
                            self.command_index = (self.command_index - 1) % len(self.commands)
                        else:
                            # サブメニュー
                            if self.menu_mode == 'skill':
                                max_index = len(self.player.skills)
                            elif self.menu_mode == 'item':
                                max_index = len(self.player.items)
                            self.submenu_index = (self.submenu_index - 1) % max_index

                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if self.menu_mode == 'main':
                            self.command_index = (self.command_index + 1) % len(self.commands)
                        else:
                            # サブメニュー
                            if self.menu_mode == 'skill':
                                max_index = len(self.player.skills)
                            elif self.menu_mode == 'item':
                                max_index = len(self.player.items)
                            self.submenu_index = (self.submenu_index + 1) % max_index

                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.execute_command()

                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_x:
                        # サブメニューから戻る
                        if self.menu_mode != 'main':
                            self.menu_mode = 'main'
                            self.submenu_index = 0

    def execute_command(self):
        """選択されたコマンドを実行"""
        if self.menu_mode == 'main':
            command = self.commands[self.command_index]

            if command == 'たたかう':
                self.battle_manager.execute_player_attack()
            elif command == 'スキル':
                # スキルメニューを開く
                if len(self.player.skills) > 0:
                    self.menu_mode = 'skill'
                    self.submenu_index = 0
                else:
                    self.battle_manager.add_message("使えるスキルがない！")
            elif command == 'アイテム':
                # アイテムメニューを開く
                if len(self.player.items) > 0 and any(item['count'] > 0 for item in self.player.items):
                    self.menu_mode = 'item'
                    self.submenu_index = 0
                else:
                    self.battle_manager.add_message("使えるアイテムがない！")
            elif command == 'ぼうぎょ':
                self.battle_manager.execute_player_defend()
            elif command == 'にげる':
                self.battle_manager.execute_player_escape()

        elif self.menu_mode == 'skill':
            # スキル使用
            skill = self.player.skills[self.submenu_index]
            if self.player.mp >= skill['mp_cost']:
                self.player.mp -= skill['mp_cost']
                self.execute_skill(skill)
                self.menu_mode = 'main'
            else:
                self.battle_manager.add_message("MPが足りない！")

        elif self.menu_mode == 'item':
            # アイテム使用
            item = self.player.items[self.submenu_index]
            if item['count'] > 0:
                item['count'] -= 1
                self.execute_item(item)
                self.menu_mode = 'main'
            else:
                self.battle_manager.add_message("アイテムがない！")

    def execute_skill(self, skill):
        """スキルを実行"""
        if 'heal' in skill:
            # 回復スキル
            heal_amount = skill['heal']
            self.player.hp = min(self.player.max_hp, self.player.hp + heal_amount)
            self.battle_manager.add_message(f"{skill['name']}を使った！")
            self.battle_manager.add_message(f"HPが{heal_amount}回復した！")
            self.battle_manager.battle_phase = 'enemy_turn'
            self.battle_manager.execute_enemy_turn()
        else:
            # 攻撃スキル
            damage = int(self.player.atk * skill['power'])
            actual_damage = self.enemy.take_damage(damage)
            self.battle_manager.add_message(f"{skill['name']}！")
            self.battle_manager.add_message(f"{self.enemy.name}に{actual_damage}のダメージ！")

            if not self.enemy.is_alive:
                self.battle_manager.battle_phase = 'victory'
                self.battle_manager.calculate_rewards()
            else:
                self.battle_manager.battle_phase = 'enemy_turn'
                self.battle_manager.execute_enemy_turn()

    def execute_item(self, item):
        """アイテムを使用"""
        effect = item['effect']
        value = item['value']

        self.battle_manager.add_message(f"{item['name']}を使った！")

        if effect == 'heal_hp':
            self.player.hp = min(self.player.max_hp, self.player.hp + value)
            self.battle_manager.add_message(f"HPが{value}回復した！")
        elif effect == 'heal_mp':
            self.player.mp = min(self.player.max_mp, self.player.mp + value)
            self.battle_manager.add_message(f"MPが{value}回復した！")

        self.battle_manager.battle_phase = 'enemy_turn'
        self.battle_manager.execute_enemy_turn()

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

        # 敵の描画（HD-2D風）
        if self.enemy.is_alive:
            from src.entities.character_renderer import CharacterRenderer

            # 敵を中央やや上に大きく描画
            enemy_x = SCREEN_WIDTH // 2 - TILE_SIZE
            enemy_y = 150

            # 敵キャラクターを描画
            CharacterRenderer.draw_enemy(surface, enemy_x, enemy_y, self.enemy.name)

            # 敵の名前（影付き）
            name_shadow = self.font.render(self.enemy.name, True, (0, 0, 0))
            name_surface = self.font.render(self.enemy.name, True, COLORS['WHITE'])
            name_rect = name_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
            surface.blit(name_shadow, (name_rect.x + 3, name_rect.y + 3))
            surface.blit(name_surface, name_rect)

            # 敵のHP（ゲージ風）
            hp_text = f"HP: {self.enemy.hp}/{self.enemy.max_hp}"
            hp_surface = self.font.render(hp_text, True, COLORS['GOLD'])
            hp_rect = hp_surface.get_rect(center=(SCREEN_WIDTH // 2, 400))
            surface.blit(hp_surface, hp_rect)

            # HPゲージ
            gauge_width = 300
            gauge_height = 20
            gauge_x = SCREEN_WIDTH // 2 - gauge_width // 2
            gauge_y = 430
            hp_ratio = self.enemy.hp / self.enemy.max_hp

            # ゲージ背景
            pygame.draw.rect(surface, COLORS['DARK_BLUE'],
                           (gauge_x, gauge_y, gauge_width, gauge_height))
            # ゲージ（HP）
            if hp_ratio > 0.5:
                gauge_color = (50, 200, 50)
            elif hp_ratio > 0.25:
                gauge_color = (255, 200, 0)
            else:
                gauge_color = (255, 50, 50)
            pygame.draw.rect(surface, gauge_color,
                           (gauge_x, gauge_y, int(gauge_width * hp_ratio), gauge_height))
            # ゲージ枠
            pygame.draw.rect(surface, COLORS['WHITE'],
                           (gauge_x, gauge_y, gauge_width, gauge_height), 2)

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
        if self.menu_mode == 'main':
            # メインコマンドウィンドウ
            window_x = SCREEN_WIDTH - 400
            window_y = SCREEN_HEIGHT - 250
            window_width = 350
            window_height = 200

            window_bg = pygame.Surface((window_width, window_height))
            window_bg.fill(COLORS['DARK_BLUE'])
            pygame.draw.rect(window_bg, COLORS['WINDOW_BLUE'], (0, 0, window_width, window_height), 3)
            surface.blit(window_bg, (window_x, window_y))

            # コマンドリストを2列で表示
            cols = 2
            for i, command in enumerate(self.commands):
                col = i % cols
                row = i // cols
                x_offset = window_x + 20 + col * 150
                y_offset = window_y + 20 + row * 50

                # 選択中のコマンドにカーソル
                if i == self.command_index:
                    cursor_surface = self.font.render("▶", True, COLORS['GOLD'])
                    surface.blit(cursor_surface, (x_offset - 5, y_offset))

                command_surface = self.font.render(command, True, COLORS['WHITE'])
                surface.blit(command_surface, (x_offset + 30, y_offset))

        elif self.menu_mode == 'skill':
            # スキルウィンドウ
            self.draw_skill_window(surface)

        elif self.menu_mode == 'item':
            # アイテムウィンドウ
            self.draw_item_window(surface)

    def draw_skill_window(self, surface):
        """スキルウィンドウの描画"""
        window_x = SCREEN_WIDTH - 700
        window_y = SCREEN_HEIGHT - 350
        window_width = 650
        window_height = 300

        window_bg = pygame.Surface((window_width, window_height))
        window_bg.fill(COLORS['DARK_BLUE'])
        pygame.draw.rect(window_bg, COLORS['WINDOW_BLUE'], (0, 0, window_width, window_height), 3)
        surface.blit(window_bg, (window_x, window_y))

        # タイトル
        title_surface = self.font.render("スキル選択", True, COLORS['GOLD'])
        surface.blit(title_surface, (window_x + 20, window_y + 15))

        # スキルリスト
        for i, skill in enumerate(self.player.skills):
            y_offset = window_y + 60 + i * 70

            # 選択中のスキルにカーソル
            if i == self.submenu_index:
                cursor_surface = self.font.render("▶", True, COLORS['GOLD'])
                surface.blit(cursor_surface, (window_x + 15, y_offset))

            # スキル名
            skill_surface = self.font.render(skill['name'], True, COLORS['WHITE'])
            surface.blit(skill_surface, (window_x + 50, y_offset))

            # MP消費
            mp_text = f"MP:{skill['mp_cost']}"
            mp_color = COLORS['WHITE'] if self.player.mp >= skill['mp_cost'] else COLORS['RED']
            mp_surface = self.font.render(mp_text, True, mp_color)
            surface.blit(mp_surface, (window_x + 350, y_offset))

            # 説明
            desc_surface = self.font.render(skill['description'], True, COLORS['WINDOW_BLUE'])
            surface.blit(desc_surface, (window_x + 50, y_offset + 30))

        # 操作説明
        help_surface = self.font.render("Enter:決定  X:キャンセル", True, COLORS['GOLD'])
        surface.blit(help_surface, (window_x + 20, window_y + window_height - 40))

    def draw_item_window(self, surface):
        """アイテムウィンドウの描画"""
        window_x = SCREEN_WIDTH - 700
        window_y = SCREEN_HEIGHT - 350
        window_width = 650
        window_height = 300

        window_bg = pygame.Surface((window_width, window_height))
        window_bg.fill(COLORS['DARK_BLUE'])
        pygame.draw.rect(window_bg, COLORS['WINDOW_BLUE'], (0, 0, window_width, window_height), 3)
        surface.blit(window_bg, (window_x, window_y))

        # タイトル
        title_surface = self.font.render("アイテム選択", True, COLORS['GOLD'])
        surface.blit(title_surface, (window_x + 20, window_y + 15))

        # アイテムリスト
        for i, item in enumerate(self.player.items):
            y_offset = window_y + 60 + i * 60

            # 選択中のアイテムにカーソル
            if i == self.submenu_index:
                cursor_surface = self.font.render("▶", True, COLORS['GOLD'])
                surface.blit(cursor_surface, (window_x + 15, y_offset))

            # アイテム名
            item_color = COLORS['WHITE'] if item['count'] > 0 else COLORS['WINDOW_BLUE']
            item_surface = self.font.render(item['name'], True, item_color)
            surface.blit(item_surface, (window_x + 50, y_offset))

            # 所持数
            count_text = f"×{item['count']}"
            count_surface = self.font.render(count_text, True, item_color)
            surface.blit(count_surface, (window_x + 400, y_offset))

        # 操作説明
        help_surface = self.font.render("Enter:決定  X:キャンセル", True, COLORS['GOLD'])
        surface.blit(help_surface, (window_x + 20, window_y + window_height - 40))
