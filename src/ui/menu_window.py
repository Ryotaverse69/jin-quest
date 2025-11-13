"""
JID×QUEST - メニューウィンドウシステム
"""

import pygame
from config import *


class MenuWindow:
    """メニューウィンドウクラス（ドラクエ風）"""

    def __init__(self, save_callback=None):
        """
        メニューウィンドウの初期化

        Args:
            save_callback: セーブ実行時のコールバック関数
        """
        self.font = pygame.font.Font(None, FONT_SIZE)

        # メニュー項目
        self.menu_items = ['つよさ', 'どうぐ', 'セーブ', 'とじる']
        self.selected_index = 0

        # 状態
        self.is_active = False
        self.current_submenu = None  # 'status', 'items', 'save', None
        self.save_selected_slot = 0  # セーブスロット選択
        self.save_message = ""  # セーブメッセージ
        self.save_message_timer = 0  # メッセージ表示タイマー

        # コールバック
        self.save_callback = save_callback

    def open(self):
        """メニューを開く"""
        self.is_active = True
        self.selected_index = 0
        self.current_submenu = None

    def close(self):
        """メニューを閉じる"""
        self.is_active = False
        self.current_submenu = None

    def update(self):
        """メニューウィンドウの更新"""
        if self.save_message_timer > 0:
            self.save_message_timer -= 1
            if self.save_message_timer == 0:
                self.save_message = ""

    def handle_input(self, events):
        """
        入力処理

        Args:
            events: pygameイベントリスト
        """
        if not self.is_active:
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                # サブメニュー表示中
                if self.current_submenu:
                    # セーブサブメニュー
                    if self.current_submenu == 'save':
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.save_selected_slot = (self.save_selected_slot - 1) % 3
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.save_selected_slot = (self.save_selected_slot + 1) % 3
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            # セーブ実行
                            if self.save_callback:
                                success = self.save_callback(self.save_selected_slot + 1)
                                if success:
                                    self.save_message = "セーブしました！"
                                else:
                                    self.save_message = "セーブに失敗しました"
                                self.save_message_timer = 90  # 1.5秒表示
                        elif event.key == pygame.K_ESCAPE or event.key == pygame.K_x:
                            self.current_submenu = None
                            self.save_message = ""
                    else:
                        # その他のサブメニュー
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_x:
                            self.current_submenu = None
                    return

                # メインメニュー操作
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_index = (self.selected_index - 1) % len(self.menu_items)

                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_index = (self.selected_index + 1) % len(self.menu_items)

                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.select_item()

                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_x:
                    self.close()

    def select_item(self):
        """選択中のメニュー項目を実行"""
        selected = self.menu_items[self.selected_index]

        if selected == 'つよさ':
            self.current_submenu = 'status'
        elif selected == 'どうぐ':
            self.current_submenu = 'items'
        elif selected == 'セーブ':
            self.current_submenu = 'save'
        elif selected == 'とじる':
            self.close()

    def draw(self, surface, player):
        """
        メニューウィンドウを描画

        Args:
            surface: 描画先サーフェス
            player: プレイヤーオブジェクト
        """
        if not self.is_active:
            return

        # 半透明の背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLORS['BLACK'])
        overlay.set_alpha(128)
        surface.blit(overlay, (0, 0))

        # サブメニュー表示
        if self.current_submenu == 'status':
            self.draw_status_submenu(surface, player)
        elif self.current_submenu == 'items':
            self.draw_items_submenu(surface)
        elif self.current_submenu == 'save':
            self.draw_save_submenu(surface)
        else:
            # メインメニュー表示
            self.draw_main_menu(surface, player)

    def draw_main_menu(self, surface, player):
        """メインメニューを描画"""
        # メニューウィンドウ
        menu_width = 100
        menu_height = 80
        menu_x = 20
        menu_y = 20

        # ウィンドウ背景
        menu_bg = pygame.Surface((menu_width, menu_height))
        menu_bg.fill(COLORS['DARK_BLUE'])
        pygame.draw.rect(menu_bg, COLORS['WINDOW_BLUE'], (0, 0, menu_width, menu_height), 2)
        surface.blit(menu_bg, (menu_x, menu_y))

        # メニュー項目
        for i, item in enumerate(self.menu_items):
            y_offset = menu_y + 10 + i * 18

            # カーソル
            if i == self.selected_index:
                cursor_surface = self.font.render("▶", True, COLORS['GOLD'])
                surface.blit(cursor_surface, (menu_x + 5, y_offset))

            # 項目名
            item_surface = self.font.render(item, True, COLORS['WHITE'])
            surface.blit(item_surface, (menu_x + 20, y_offset))

        # プレイヤー情報（右側）
        self.draw_player_info(surface, player, menu_x + menu_width + 10, menu_y)

    def draw_player_info(self, surface, player, x, y):
        """プレイヤー情報を描画"""
        info_width = 130
        info_height = 80

        # ウィンドウ背景
        info_bg = pygame.Surface((info_width, info_height))
        info_bg.fill(COLORS['DARK_BLUE'])
        pygame.draw.rect(info_bg, COLORS['WINDOW_BLUE'], (0, 0, info_width, info_height), 2)
        surface.blit(info_bg, (x, y))

        # プレイヤー情報
        info_lines = [
            f"{player.name}",
            f"Lv.{player.level} {player.get_rank()}",
            f"HP: {player.hp}/{player.max_hp}",
            f"MP: {player.mp}/{player.max_mp}",
        ]

        for i, line in enumerate(info_lines):
            text_surface = self.font.render(line, True, COLORS['WHITE'])
            surface.blit(text_surface, (x + 10, y + 10 + i * 15))

    def draw_status_submenu(self, surface, player):
        """ステータスサブメニューを描画"""
        # ウィンドウ
        status_width = SCREEN_WIDTH - 40
        status_height = SCREEN_HEIGHT - 40
        status_x = 20
        status_y = 20

        # 背景
        status_bg = pygame.Surface((status_width, status_height))
        status_bg.fill(COLORS['DARK_BLUE'])
        pygame.draw.rect(status_bg, COLORS['WINDOW_BLUE'], (0, 0, status_width, status_height), 2)
        surface.blit(status_bg, (status_x, status_y))

        # タイトル
        title_surface = self.font.render("つよさ", True, COLORS['GOLD'])
        surface.blit(title_surface, (status_x + 10, status_y + 10))

        # ステータス詳細
        status_lines = [
            f"なまえ: {player.name}",
            f"クラス: {player.player_class}",
            f"",
            f"レベル: {player.level}",
            f"役職: {player.get_rank()}",
            f"",
            f"HP: {player.hp} / {player.max_hp}",
            f"MP: {player.mp} / {player.max_mp}",
            f"",
            f"こうげきりょく: {player.atk}",
            f"ぼうぎょりょく: {player.defense}",
            f"すばやさ: {player.spd}",
            f"",
            f"経験値: {player.exp}",
            f"次のレベルまで: {player.next_level_exp - player.exp}",
        ]

        for i, line in enumerate(status_lines):
            text_surface = self.font.render(line, True, COLORS['WHITE'])
            surface.blit(text_surface, (status_x + 20, status_y + 40 + i * 15))

        # 操作説明
        help_text = "ESC: もどる"
        help_surface = self.font.render(help_text, True, COLORS['LIGHT_BLUE'])
        surface.blit(help_surface, (status_x + 10, status_y + status_height - 20))

    def draw_items_submenu(self, surface):
        """アイテムサブメニューを描画"""
        # ウィンドウ
        items_width = SCREEN_WIDTH - 40
        items_height = SCREEN_HEIGHT - 40
        items_x = 20
        items_y = 20

        # 背景
        items_bg = pygame.Surface((items_width, items_height))
        items_bg.fill(COLORS['DARK_BLUE'])
        pygame.draw.rect(items_bg, COLORS['WINDOW_BLUE'], (0, 0, items_width, items_height), 2)
        surface.blit(items_bg, (items_x, items_y))

        # タイトル
        title_surface = self.font.render("どうぐ", True, COLORS['GOLD'])
        surface.blit(title_surface, (items_x + 10, items_y + 10))

        # メッセージ
        message = "（アイテムシステムは未実装です）"
        message_surface = self.font.render(message, True, COLORS['WHITE'])
        surface.blit(message_surface, (items_x + 20, items_y + 50))

        # 操作説明
        help_text = "ESC: もどる"
        help_surface = self.font.render(help_text, True, COLORS['LIGHT_BLUE'])
        surface.blit(help_surface, (items_x + 10, items_y + items_height - 20))

    def draw_save_submenu(self, surface):
        """セーブサブメニューを描画"""
        # ウィンドウ
        save_width = 200
        save_height = 140
        save_x = (SCREEN_WIDTH - save_width) // 2
        save_y = (SCREEN_HEIGHT - save_height) // 2

        # 背景
        save_bg = pygame.Surface((save_width, save_height))
        save_bg.fill(COLORS['DARK_BLUE'])
        pygame.draw.rect(save_bg, COLORS['WINDOW_BLUE'], (0, 0, save_width, save_height), 2)
        surface.blit(save_bg, (save_x, save_y))

        # タイトル
        title_surface = self.font.render("セーブ", True, COLORS['GOLD'])
        surface.blit(title_surface, (save_x + 10, save_y + 10))

        # セーブスロット
        slot_names = ["セーブ1", "セーブ2", "セーブ3"]
        for i, slot_name in enumerate(slot_names):
            y_offset = save_y + 40 + i * 20

            # カーソル
            if i == self.save_selected_slot:
                cursor_surface = self.font.render("▶", True, COLORS['GOLD'])
                surface.blit(cursor_surface, (save_x + 10, y_offset))

            # スロット名
            slot_surface = self.font.render(slot_name, True, COLORS['WHITE'])
            surface.blit(slot_surface, (save_x + 30, y_offset))

        # セーブメッセージ
        if self.save_message:
            message_surface = self.font.render(self.save_message, True, COLORS['GOLD'])
            message_rect = message_surface.get_rect(center=(save_x + save_width // 2, save_y + 105))
            surface.blit(message_surface, message_rect)

        # 操作説明
        help_text = "Enter: セーブ  ESC: もどる"
        help_surface = self.font.render(help_text, True, COLORS['LIGHT_BLUE'])
        surface.blit(help_surface, (save_x + 10, save_y + save_height - 20))
