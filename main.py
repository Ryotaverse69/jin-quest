"""
JID×QUEST - メインゲームファイル
スーパーファミコン風RPG
"""

import pygame
import sys
from config import *
from src.game_states.field_map import FieldMapState

class Game:
    """メインゲームクラス"""

    def __init__(self):
        """ゲームの初期化"""
        pygame.init()

        # 画面設定
        # 実際の描画サーフェス (256x224 - SFC標準)
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        # 表示用ウィンドウ (3倍拡大)
        self.display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("JID×QUEST")

        # クロック設定
        self.clock = pygame.time.Clock()

        # ゲーム状態
        self.state = GameState.TITLE
        self.running = True

        # フォント設定
        self.font = pygame.font.Font(None, 16)  # とりあえずデフォルトフォント

        # タイトル画面用の変数
        self.title_flash_timer = 0
        self.title_show_text = True
        self.title_menu_items = ['はじめから', 'つづきから', 'おわる']
        self.title_selected_index = 0

        # ゲーム状態オブジェクト
        self.field_state = None
        self.battle_state = None

        # セーブ/ロードマネージャー
        from src.utils.save_load import SaveLoadManager
        self.save_manager = SaveLoadManager()

    def handle_events(self):
        """イベント処理"""
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.FIELD:
                        # フィールドからタイトルに戻る
                        self.state = GameState.TITLE
                    else:
                        # タイトル画面から終了
                        self.running = False

                # タイトル画面でのメニュー操作
                if self.state == GameState.TITLE:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.title_selected_index = (self.title_selected_index - 1) % len(self.title_menu_items)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.title_selected_index = (self.title_selected_index + 1) % len(self.title_menu_items)
                    elif event.key == pygame.K_RETURN:
                        self.select_title_menu()

        # フィールド状態のイベント処理
        if self.state == GameState.FIELD and self.field_state:
            self.field_state.handle_events(events)

        # バトル状態のイベント処理
        if self.state == GameState.BATTLE and self.battle_state:
            self.battle_state.handle_events(events)

    def select_title_menu(self):
        """タイトルメニューの選択処理"""
        selected = self.title_menu_items[self.title_selected_index]

        if selected == 'はじめから':
            self.start_new_game()
        elif selected == 'つづきから':
            self.show_load_menu()
        elif selected == 'おわる':
            self.running = False

    def start_new_game(self):
        """新しいゲームを開始"""
        print("ゲーム開始！")
        self.field_state = FieldMapState(self)
        self.state = GameState.FIELD

    def start_game(self):
        """ゲームを開始（後方互換性のため残す）"""
        self.start_new_game()

    def show_load_menu(self):
        """ロードメニューを表示（簡易版）"""
        # スロット1からロードを試みる
        save_data = self.save_manager.load_game(slot=1)
        if save_data:
            self.load_game(save_data)
        else:
            print("セーブデータがありません")

    def load_game(self, save_data):
        """
        セーブデータからゲームをロード

        Args:
            save_data: ロードしたセーブデータ
        """
        print("ゲームをロード中...")

        # マップパスを取得
        map_path = save_data['map']['path']

        # フィールド状態を作成
        self.field_state = FieldMapState(self, map_path)

        # プレイヤーデータを適用
        self.save_manager.apply_save_data(self.field_state.player, save_data)

        # ゲーム状態をフィールドに
        self.state = GameState.FIELD

        print(f"ロード完了: {self.field_state.player.name} Lv.{self.field_state.player.level}")

    def update(self):
        """ゲームロジックの更新"""
        if self.state == GameState.TITLE:
            self.update_title()
        elif self.state == GameState.FIELD:
            if self.field_state:
                self.field_state.update()
        elif self.state == GameState.BATTLE:
            if self.battle_state:
                self.battle_state.update()

    def update_title(self):
        """タイトル画面の更新"""
        # "PRESS ENTER" のフラッシュ効果
        self.title_flash_timer += 1
        if self.title_flash_timer >= 30:  # 0.5秒ごとに点滅
            self.title_show_text = not self.title_show_text
            self.title_flash_timer = 0

    def draw(self):
        """描画処理"""
        self.screen.fill(COLORS['BLACK'])

        if self.state == GameState.TITLE:
            self.draw_title()
        elif self.state == GameState.FIELD:
            if self.field_state:
                self.field_state.draw(self.screen)
        elif self.state == GameState.BATTLE:
            if self.battle_state:
                self.battle_state.draw(self.screen)

        # 3倍拡大して表示
        scaled_screen = pygame.transform.scale(self.screen,
                                              (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.display.blit(scaled_screen, (0, 0))
        pygame.display.flip()

    def draw_title(self):
        """タイトル画面の描画"""
        # 背景（濃い青）
        self.screen.fill(COLORS['DARK_BLUE'])

        # タイトルロゴ "JID×QUEST"
        title_text = "JID×QUEST"
        title_surface = self.font.render(title_text, True, COLORS['GOLD'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 70))

        # 影効果
        shadow_surface = self.font.render(title_text, True, COLORS['BLACK'])
        shadow_rect = shadow_surface.get_rect(center=(SCREEN_WIDTH // 2 + 2, 72))
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(title_surface, title_rect)

        # サブタイトル
        subtitle = "Super Famicom Style RPG"
        subtitle_surface = self.font.render(subtitle, True, COLORS['WHITE'])
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 95))
        self.screen.blit(subtitle_surface, subtitle_rect)

        # メニュー項目
        menu_start_y = 140
        for i, item in enumerate(self.title_menu_items):
            y_offset = menu_start_y + i * 20

            # カーソル
            if i == self.title_selected_index:
                cursor_surface = self.font.render("▶", True, COLORS['GOLD'])
                cursor_rect = cursor_surface.get_rect(center=(SCREEN_WIDTH // 2 - 40, y_offset))
                self.screen.blit(cursor_surface, cursor_rect)

            # メニュー項目
            item_surface = self.font.render(item, True, COLORS['WHITE'])
            item_rect = item_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(item_surface, item_rect)

        # コピーライト
        copyright_text = "(C) 2024 JID Corporation"
        copyright_surface = self.font.render(copyright_text, True, COLORS['LIGHT_BLUE'])
        copyright_rect = copyright_surface.get_rect(center=(SCREEN_WIDTH // 2, 210))
        self.screen.blit(copyright_surface, copyright_rect)

    def run(self):
        """メインゲームループ"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    """ゲームのエントリーポイント"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
