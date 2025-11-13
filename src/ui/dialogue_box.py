"""
JID×QUEST - 会話ウィンドウシステム
"""

import pygame
from config import *


class DialogueBox:
    """会話ウィンドウクラス（ドラクエ風）"""

    def __init__(self):
        """会話ウィンドウの初期化"""
        self.font = pygame.font.Font(None, FONT_SIZE)

        # ウィンドウサイズと位置 (フルHD対応)
        self.window_width = SCREEN_WIDTH - 100
        self.window_height = 250
        self.window_x = 50
        self.window_y = SCREEN_HEIGHT - self.window_height - 50

        # 会話テキスト
        self.messages = []  # メッセージリスト
        self.current_message_index = 0
        self.current_char_index = 0  # 現在表示中の文字位置

        # アニメーション
        self.text_speed = MESSAGE_SPEED  # 文字表示速度
        self.frame_counter = 0
        self.is_animating = True  # テキストアニメーション中か

        # 話者情報
        self.speaker_name = ""

        # 状態
        self.is_active = False
        self.auto_close = False  # 会話終了後に自動で閉じるか

    def start_dialogue(self, messages, speaker_name="", auto_close=False):
        """
        会話を開始

        Args:
            messages: メッセージリスト（文字列のリスト）
            speaker_name: 話者の名前
            auto_close: 会話終了後に自動で閉じるか
        """
        if isinstance(messages, str):
            messages = [messages]

        self.messages = messages
        self.speaker_name = speaker_name
        self.auto_close = auto_close
        self.current_message_index = 0
        self.current_char_index = 0
        self.is_animating = True
        self.is_active = True
        self.frame_counter = 0

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
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if self.is_animating:
                        # アニメーション中は全文表示
                        self.current_char_index = len(self.get_current_message())
                        self.is_animating = False
                    else:
                        # 次のメッセージへ
                        self.next_message()

    def next_message(self):
        """次のメッセージに進む"""
        if self.current_message_index < len(self.messages) - 1:
            self.current_message_index += 1
            self.current_char_index = 0
            self.is_animating = True
            self.frame_counter = 0
        else:
            # 会話終了
            if self.auto_close:
                self.close()
            else:
                # 最後のメッセージを表示し続ける
                pass

    def close(self):
        """会話ウィンドウを閉じる"""
        self.is_active = False
        self.messages = []
        self.current_message_index = 0
        self.current_char_index = 0

    def update(self):
        """会話ウィンドウの更新"""
        if not self.is_active:
            return

        if self.is_animating:
            self.frame_counter += 1

            if self.frame_counter >= self.text_speed:
                self.frame_counter = 0
                self.current_char_index += 1

                # メッセージ全体を表示し終えた
                if self.current_char_index >= len(self.get_current_message()):
                    self.is_animating = False

    def get_current_message(self):
        """現在のメッセージを取得"""
        if 0 <= self.current_message_index < len(self.messages):
            return self.messages[self.current_message_index]
        return ""

    def get_displayed_text(self):
        """現在表示中のテキストを取得"""
        message = self.get_current_message()
        return message[:self.current_char_index]

    def is_finished(self):
        """会話が終了したか"""
        return (not self.is_active or
                (self.current_message_index >= len(self.messages) - 1 and
                 not self.is_animating))

    def draw(self, surface):
        """
        会話ウィンドウを描画

        Args:
            surface: 描画先サーフェス
        """
        if not self.is_active:
            return

        # ウィンドウ背景
        window_bg = pygame.Surface((self.window_width, self.window_height))
        window_bg.fill(COLORS['DARK_BLUE'])

        # 枠線（青）
        pygame.draw.rect(window_bg, COLORS['WINDOW_BLUE'],
                        (0, 0, self.window_width, self.window_height), 2)

        # 角の装飾（SFC風）
        corner_size = 4
        pygame.draw.rect(window_bg, COLORS['WINDOW_BLUE'],
                        (0, 0, corner_size, corner_size))
        pygame.draw.rect(window_bg, COLORS['WINDOW_BLUE'],
                        (self.window_width - corner_size, 0, corner_size, corner_size))
        pygame.draw.rect(window_bg, COLORS['WINDOW_BLUE'],
                        (0, self.window_height - corner_size, corner_size, corner_size))
        pygame.draw.rect(window_bg, COLORS['WINDOW_BLUE'],
                        (self.window_width - corner_size, self.window_height - corner_size,
                         corner_size, corner_size))

        surface.blit(window_bg, (self.window_x, self.window_y))

        # 話者名
        if self.speaker_name:
            name_surface = self.font.render(self.speaker_name, True, COLORS['GOLD'])
            surface.blit(name_surface, (self.window_x + 10, self.window_y + 5))

        # メッセージテキスト（複数行対応）
        displayed_text = self.get_displayed_text()
        text_y_offset = 25 if self.speaker_name else 10

        # 改行を考慮して描画
        lines = self.wrap_text(displayed_text, self.window_width - 20)
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, COLORS['WHITE'])
            surface.blit(text_surface,
                        (self.window_x + 10, self.window_y + text_y_offset + i * 15))

        # "▼"マーク（メッセージ送りアイコン）
        if not self.is_animating:
            if self.current_message_index < len(self.messages) - 1:
                # まだメッセージがある
                arrow_surface = self.font.render("▼", True, COLORS['WHITE'])
                surface.blit(arrow_surface,
                           (self.window_x + self.window_width - 20,
                            self.window_y + self.window_height - 18))
            else:
                # 最後のメッセージ
                if not self.auto_close:
                    arrow_surface = self.font.render("■", True, COLORS['WHITE'])
                    surface.blit(arrow_surface,
                               (self.window_x + self.window_width - 20,
                                self.window_y + self.window_height - 18))

    def wrap_text(self, text, max_width):
        """
        テキストを指定幅で折り返す

        Args:
            text: テキスト
            max_width: 最大幅（ピクセル）

        Returns:
            list: 行のリスト
        """
        words = text
        lines = []
        current_line = ""

        for char in words:
            test_line = current_line + char
            text_width = self.font.size(test_line)[0]

            if text_width > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = char
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

        return lines
