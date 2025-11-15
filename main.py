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

        # 画面設定 (HD-2D)
        # 実際の描画サーフェス = 表示サーフェス (スケーリングなし)
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        # 表示用ウィンドウ (HD解像度)
        self.display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("JID×QUEST - HD-2D Edition")

        # クロック設定
        self.clock = pygame.time.Clock()

        # ゲーム状態
        self.state = GameState.TITLE
        self.running = True

        # フォント設定 (HD対応)
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.title_font = pygame.font.Font(None, 120)  # タイトル専用の大きなフォント

        # タイトル画面用の変数
        self.title_flash_timer = 0
        self.title_show_text = True
        self.title_menu_items = ['はじめから', 'つづきから', 'おわる']
        self.title_selected_index = 0

        # タイトルアニメーション用
        self.title_wave_offset = 0
        self.cursor_pulse = 0
        self.title_glow_alpha = 0
        self.title_glow_direction = 1

        # パーティクルエフェクト
        self.particles = []
        self.particle_timer = 0

        # タイトル背景画像の読み込み（ドット絵版）
        try:
            self.title_background = pygame.image.load('assets/ui/jid_headquarters_pixel_art.png')
            print("タイトル背景画像を読み込みました（ドット絵版）")
        except Exception as e:
            print(f"Warning: タイトル背景画像の読み込みに失敗しました: {e}")
            self.title_background = None

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

        # タイトルの波打ちアニメーション
        self.title_wave_offset += 0.05

        # カーソルの脈動アニメーション
        self.cursor_pulse += 0.1

        # タイトルのグロー効果
        self.title_glow_alpha += 3 * self.title_glow_direction
        if self.title_glow_alpha >= 100:
            self.title_glow_direction = -1
        elif self.title_glow_alpha <= 0:
            self.title_glow_direction = 1

        # パーティクルの生成
        self.particle_timer += 1
        if self.particle_timer >= 10:  # 10フレームごとに新しいパーティクル
            import random
            particle = {
                'x': random.randint(0, SCREEN_WIDTH),
                'y': SCREEN_HEIGHT,
                'speed': random.uniform(1, 3),
                'size': random.randint(2, 4),
                'alpha': random.randint(100, 255),
                'twinkle_speed': random.uniform(0.05, 0.15),
                'twinkle_offset': random.uniform(0, 6.28)
            }
            self.particles.append(particle)
            self.particle_timer = 0

        # パーティクルの更新
        for particle in self.particles[:]:
            particle['y'] -= particle['speed']
            particle['twinkle_offset'] += particle['twinkle_speed']
            if particle['y'] < -10:
                self.particles.remove(particle)

        # パーティクルの数を制限
        if len(self.particles) > 50:
            self.particles = self.particles[-50:]

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
        import math

        # 背景画像を描画
        if self.title_background:
            self.screen.blit(self.title_background, (0, 0))

            # テキストを見やすくするためのオーバーレイ（半透明の黒）
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(100)  # 透明度（0-255）- ドット絵がよく見えるように薄めに
            overlay.fill(COLORS['BLACK'])
            self.screen.blit(overlay, (0, 0))
        else:
            # 背景画像がない場合は従来の濃い青
            self.screen.fill(COLORS['DARK_BLUE'])

        # パーティクルエフェクト（星の粒子）を描画
        for particle in self.particles:
            # 点滅効果
            twinkle = abs(math.sin(particle['twinkle_offset']))
            alpha = int(particle['alpha'] * twinkle)
            color = (255, 255, 200, alpha)  # 黄色っぽい白

            # 半透明のサーフェスを作成
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (particle['size'], particle['size']), particle['size'])
            self.screen.blit(particle_surface, (int(particle['x']), int(particle['y'])))

        # タイトルロゴ "JID×QUEST" - 画面中央上部に大きく表示
        title_text = "JID×QUEST"
        title_y = SCREEN_HEIGHT // 3

        # 多重影効果（深みを出す）
        for i in range(6, 0, -1):
            shadow_alpha = 255 - (i * 30)
            shadow_color = (0, 0, 0)
            shadow_surface = self.title_font.render(title_text, True, shadow_color)
            shadow_rect = shadow_surface.get_rect(center=(SCREEN_WIDTH // 2 + i, title_y + i))
            shadow_surface.set_alpha(shadow_alpha)
            self.screen.blit(shadow_surface, shadow_rect)

        # グロー効果（外側の光）
        glow_surface = self.title_font.render(title_text, True, (255, 220, 100))
        glow_surface.set_alpha(int(self.title_glow_alpha))
        for offset_x, offset_y in [(-2, -2), (2, -2), (-2, 2), (2, 2), (-3, 0), (3, 0), (0, -3), (0, 3)]:
            glow_rect = glow_surface.get_rect(center=(SCREEN_WIDTH // 2 + offset_x, title_y + offset_y))
            self.screen.blit(glow_surface, glow_rect)

        # アウトライン（輪郭線）
        outline_surface = self.title_font.render(title_text, True, (100, 50, 0))  # 暗い茶色
        for offset_x, offset_y in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            outline_rect = outline_surface.get_rect(center=(SCREEN_WIDTH // 2 + offset_x, title_y + offset_y))
            self.screen.blit(outline_surface, outline_rect)

        # メインタイトル
        title_surface = self.title_font.render(title_text, True, COLORS['GOLD'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        self.screen.blit(title_surface, title_rect)

        # サブタイトル
        subtitle = "Super Famicom Style RPG"
        subtitle_surface = self.font.render(subtitle, True, COLORS['WHITE'])
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 80))
        self.screen.blit(subtitle_surface, subtitle_rect)

        # キャッチコピー - タイトル上部
        catchphrase_font = pygame.font.Font(None, 48)
        catchphrase = "〜 保証の力で、新たな世界へ 〜"

        # キャッチコピーの影
        catch_shadow = catchphrase_font.render(catchphrase, True, (0, 0, 0))
        catch_shadow_rect = catch_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, title_y - 100 + 2))
        catch_shadow.set_alpha(150)
        self.screen.blit(catch_shadow, catch_shadow_rect)

        # キャッチコピー本体
        catch_surface = catchphrase_font.render(catchphrase, True, (200, 220, 255))
        catch_rect = catch_surface.get_rect(center=(SCREEN_WIDTH // 2, title_y - 100))
        self.screen.blit(catch_surface, catch_rect)

        # フレーバーテキスト（世界観の説明）- タイトルとメニューの間
        flavor_font = pygame.font.Font(None, 38)
        flavor_y_start = SCREEN_HEIGHT // 3 + 140
        flavor_texts = [
            "あなたは日本賃貸保証の新人アドバイザー。",
            "保証契約を通じて、人々の新生活を支える冒険が始まる。",
            "様々な顧客との出会い、困難な審査、そして成長の物語――"
        ]

        for i, flavor_line in enumerate(flavor_texts):
            # 各行を少し透明にして雰囲気を出す
            flavor_surface = flavor_font.render(flavor_line, True, (220, 230, 255))
            flavor_surface.set_alpha(200)
            flavor_rect = flavor_surface.get_rect(center=(SCREEN_WIDTH // 2, flavor_y_start + i * 45))

            # 影
            flavor_shadow = flavor_font.render(flavor_line, True, (0, 0, 0))
            flavor_shadow_rect = flavor_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 1, flavor_y_start + i * 45 + 1))
            flavor_shadow.set_alpha(100)
            self.screen.blit(flavor_shadow, flavor_shadow_rect)

            self.screen.blit(flavor_surface, flavor_rect)

        # メニュー項目 - 画面中央下部に大きく表示
        menu_font = pygame.font.Font(None, 60)  # メニュー用フォント
        menu_start_y = SCREEN_HEIGHT // 2 + 120
        menu_spacing = 80  # メニュー項目の間隔

        # メニュー背景パネル
        panel_width = 600
        panel_height = len(self.title_menu_items) * menu_spacing + 40
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = menu_start_y - 40

        # パネルの影
        shadow_panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_panel, (0, 0, 0, 80), (0, 0, panel_width, panel_height), border_radius=15)
        self.screen.blit(shadow_panel, (panel_x + 5, panel_y + 5))

        # パネル本体
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 40, 90, 200), (0, 0, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(panel, (100, 150, 255, 150), (0, 0, panel_width, panel_height), 3, border_radius=15)
        self.screen.blit(panel, (panel_x, panel_y))

        for i, item in enumerate(self.title_menu_items):
            y_offset = menu_start_y + i * menu_spacing

            # カーソル - 脈動アニメーション
            if i == self.title_selected_index:
                pulse = abs(math.sin(self.cursor_pulse))
                cursor_x_offset = int(pulse * 10)  # 左右に動く
                cursor_alpha = int(150 + pulse * 105)  # 明るさが変わる

                cursor_surface = menu_font.render("▶", True, COLORS['GOLD'])
                cursor_surface.set_alpha(cursor_alpha)
                cursor_rect = cursor_surface.get_rect(center=(SCREEN_WIDTH // 2 - 120 + cursor_x_offset, y_offset))
                self.screen.blit(cursor_surface, cursor_rect)

                # 選択されたアイテムは明るく、少し大きく
                item_color = COLORS['GOLD']
                item_scale = 1.1

                # 選択アイテムの背景ハイライト
                highlight = pygame.Surface((panel_width - 40, menu_spacing - 10), pygame.SRCALPHA)
                pygame.draw.rect(highlight, (255, 200, 50, 50), (0, 0, panel_width - 40, menu_spacing - 10), border_radius=10)
                self.screen.blit(highlight, (panel_x + 20, y_offset - menu_spacing // 2 + 5))
            else:
                item_color = COLORS['WHITE']
                item_scale = 1.0

            # メニュー項目の影
            shadow_surface = menu_font.render(item, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(SCREEN_WIDTH // 2 + 2, y_offset + 2))
            shadow_surface.set_alpha(150)
            self.screen.blit(shadow_surface, shadow_rect)

            # メニュー項目
            item_surface = menu_font.render(item, True, item_color)
            if item_scale != 1.0:
                new_width = int(item_surface.get_width() * item_scale)
                new_height = int(item_surface.get_height() * item_scale)
                item_surface = pygame.transform.scale(item_surface, (new_width, new_height))
            item_rect = item_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(item_surface, item_rect)

        # "PRESS ENTER TO START" プロンプト - メニュー上部に点滅表示
        if self.title_show_text:
            prompt_font = pygame.font.Font(None, 44)
            prompt_text = "▼ メニューから選択してください ▼"

            # プロンプトの影
            prompt_shadow = prompt_font.render(prompt_text, True, (0, 0, 0))
            prompt_shadow_rect = prompt_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, menu_start_y - 80 + 2))
            prompt_shadow.set_alpha(120)
            self.screen.blit(prompt_shadow, prompt_shadow_rect)

            # プロンプト本体
            prompt_surface = prompt_font.render(prompt_text, True, (255, 255, 150))
            prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, menu_start_y - 80))
            self.screen.blit(prompt_surface, prompt_rect)

        # コピーライト - 画面下部（装飾付き）
        copyright_text = "(C) 2024 JID Corporation"

        # コピーライトの装飾線
        line_y = SCREEN_HEIGHT - 100
        line_width = 400
        line_x = (SCREEN_WIDTH - line_width) // 2
        pygame.draw.line(self.screen, (100, 150, 255, 100), (line_x, line_y), (line_x + line_width, line_y), 2)

        # 操作方法ヘルプ - 右上
        help_font = pygame.font.Font(None, 32)
        help_y = 30
        help_texts = [
            "【操作方法】",
            "↑↓ / W S : 選択",
            "Enter : 決定",
            "ESC : 終了"
        ]

        for i, help_line in enumerate(help_texts):
            help_color = (180, 200, 255) if i == 0 else (200, 210, 230)
            help_surface = help_font.render(help_line, True, help_color)
            help_surface.set_alpha(220)
            help_rect = help_surface.get_rect(topright=(SCREEN_WIDTH - 30, help_y + i * 38))
            self.screen.blit(help_surface, help_rect)

        # バージョン情報 - 左下
        version_text = "Ver 1.0.0 - HD-2D Edition"
        version_surface = pygame.font.Font(None, 28).render(version_text, True, (150, 150, 150))
        version_rect = version_surface.get_rect(topleft=(30, SCREEN_HEIGHT - 35))
        self.screen.blit(version_surface, version_rect)

        # コピーライトの影
        copyright_shadow = self.font.render(copyright_text, True, (0, 0, 0))
        copyright_shadow_rect = copyright_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 1, SCREEN_HEIGHT - 50 + 1))
        copyright_shadow.set_alpha(100)
        self.screen.blit(copyright_shadow, copyright_shadow_rect)

        # コピーライト本体
        copyright_surface = self.font.render(copyright_text, True, COLORS['LIGHT_BLUE'])
        copyright_rect = copyright_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
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
