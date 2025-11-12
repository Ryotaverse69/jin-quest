"""
JID×QUEST - イベント管理システム
"""

import json
import os


class EventManager:
    """イベント管理クラス"""

    def __init__(self):
        """イベントマネージャーの初期化"""
        self.events = {}  # イベントデータ
        self.event_flags = {}  # イベントフラグ
        self.current_event = None  # 現在実行中のイベント
        self.event_step = 0  # イベントの進行ステップ

    def load_events(self, event_file='data/events/story_events.json'):
        """
        イベントデータを読み込み

        Args:
            event_file: イベントデータファイルのパス
        """
        try:
            if os.path.exists(event_file):
                with open(event_file, 'r', encoding='utf-8') as f:
                    self.events = json.load(f)
                print(f"イベントデータ読み込み完了: {len(self.events)}件")
            else:
                print(f"警告: イベントファイルが見つかりません: {event_file}")
                self.events = {}
        except Exception as e:
            print(f"イベント読み込みエラー: {e}")
            self.events = {}

    def set_flag(self, flag_name, value=True):
        """
        イベントフラグを設定

        Args:
            flag_name: フラグ名
            value: フラグの値（デフォルト: True）
        """
        self.event_flags[flag_name] = value
        print(f"イベントフラグ設定: {flag_name} = {value}")

    def get_flag(self, flag_name, default=False):
        """
        イベントフラグを取得

        Args:
            flag_name: フラグ名
            default: デフォルト値

        Returns:
            フラグの値
        """
        return self.event_flags.get(flag_name, default)

    def check_conditions(self, conditions):
        """
        イベント発生条件をチェック

        Args:
            conditions: 条件のリスト

        Returns:
            bool: すべての条件を満たす場合True
        """
        if not conditions:
            return True

        for condition in conditions:
            condition_type = condition.get('type')

            if condition_type == 'flag':
                # フラグ条件
                flag_name = condition.get('flag')
                required_value = condition.get('value', True)
                if self.get_flag(flag_name) != required_value:
                    return False

            elif condition_type == 'level':
                # レベル条件（プレイヤーオブジェクトが必要）
                # ここでは省略、必要に応じて実装
                pass

            elif condition_type == 'position':
                # 位置条件
                # ここでは省略、必要に応じて実装
                pass

        return True

    def can_trigger_event(self, event_id):
        """
        イベントが発動可能かチェック

        Args:
            event_id: イベントID

        Returns:
            bool: 発動可能な場合True
        """
        if event_id not in self.events:
            return False

        event_data = self.events[event_id]

        # すでに完了しているイベントは発動しない
        if self.get_flag(f"event_{event_id}_completed"):
            return False

        # 条件チェック
        conditions = event_data.get('conditions', [])
        return self.check_conditions(conditions)

    def start_event(self, event_id):
        """
        イベントを開始

        Args:
            event_id: イベントID

        Returns:
            dict: イベントデータ、イベントが存在しない場合None
        """
        if not self.can_trigger_event(event_id):
            return None

        self.current_event = event_id
        self.event_step = 0

        event_data = self.events[event_id]
        print(f"イベント開始: {event_data.get('name', event_id)}")

        # イベント開始フラグを設定
        self.set_flag(f"event_{event_id}_started", True)

        return event_data

    def get_current_step(self):
        """
        現在のイベントステップデータを取得

        Returns:
            dict: ステップデータ、イベントが実行中でない場合None
        """
        if not self.current_event:
            return None

        event_data = self.events.get(self.current_event)
        if not event_data:
            return None

        steps = event_data.get('steps', [])
        if self.event_step >= len(steps):
            return None

        return steps[self.event_step]

    def advance_step(self):
        """
        イベントを次のステップに進める

        Returns:
            bool: 次のステップがある場合True、イベント終了の場合False
        """
        if not self.current_event:
            return False

        event_data = self.events.get(self.current_event)
        if not event_data:
            return False

        steps = event_data.get('steps', [])
        self.event_step += 1

        if self.event_step >= len(steps):
            # イベント終了
            self.complete_event()
            return False

        return True

    def complete_event(self):
        """現在のイベントを完了としてマーク"""
        if not self.current_event:
            return

        event_id = self.current_event
        event_data = self.events.get(event_id)

        if event_data:
            print(f"イベント完了: {event_data.get('name', event_id)}")

        # 完了フラグを設定
        self.set_flag(f"event_{event_id}_completed", True)

        # 報酬フラグを設定
        rewards = event_data.get('rewards', {})
        for flag_name in rewards.get('flags', []):
            self.set_flag(flag_name, True)

        self.current_event = None
        self.event_step = 0

    def cancel_event(self):
        """現在のイベントをキャンセル"""
        if self.current_event:
            print(f"イベントキャンセル: {self.current_event}")
            self.current_event = None
            self.event_step = 0

    def is_event_active(self):
        """
        イベントが実行中かチェック

        Returns:
            bool: イベント実行中の場合True
        """
        return self.current_event is not None

    def get_event_data(self, event_id):
        """
        イベントデータを取得

        Args:
            event_id: イベントID

        Returns:
            dict: イベントデータ
        """
        return self.events.get(event_id)

    def save_state(self):
        """
        イベント状態を保存用辞書に変換

        Returns:
            dict: 保存用データ
        """
        return {
            'flags': self.event_flags.copy(),
            'current_event': self.current_event,
            'event_step': self.event_step
        }

    def load_state(self, state_data):
        """
        保存されたイベント状態を読み込み

        Args:
            state_data: 保存データ
        """
        self.event_flags = state_data.get('flags', {})
        self.current_event = state_data.get('current_event')
        self.event_step = state_data.get('event_step', 0)
