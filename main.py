"""
JID×QUEST - メインゲームファイル
スーパーファミコン風RPG
"""

import pygame
import sys
from config import *

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

    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                # タイトル画面でEnterキーでゲーム開始
                if self.state == GameState.TITLE:
                    if event.key == pygame.K_RETURN:
                        print("ゲーム開始！（未実装）")
                        # TODO: ゲーム開始処理

    def update(self):
        """ゲームロジックの更新"""
        if self.state == GameState.TITLE:
            self.update_title()

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

        # "PRESS ENTER" (点滅)
        if self.title_show_text:
            press_text = "PRESS ENTER"
            press_surface = self.font.render(press_text, True, COLORS['WHITE'])
            press_rect = press_surface.get_rect(center=(SCREEN_WIDTH // 2, 170))
            self.screen.blit(press_surface, press_rect)

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
