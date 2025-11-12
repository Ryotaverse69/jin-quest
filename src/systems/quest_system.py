"""
JID×QUEST - クエストシステム
"""

import json
import os


class QuestSystem:
    """クエストシステムクラス"""

    def __init__(self):
        """クエストシステムの初期化"""
        self.quests = {}  # 全クエストデータ
        self.active_quests = []  # 進行中のクエスト
        self.completed_quests = []  # 完了したクエスト
        self.quest_progress = {}  # クエスト進捗状況

    def load_quests(self, quest_file='data/quests/main_quests.json'):
        """
        クエストデータを読み込み

        Args:
            quest_file: クエストデータファイルのパス
        """
        try:
            if os.path.exists(quest_file):
                with open(quest_file, 'r', encoding='utf-8') as f:
                    self.quests = json.load(f)
                print(f"クエストデータ読み込み完了: {len(self.quests)}件")
            else:
                print(f"警告: クエストファイルが見つかりません: {quest_file}")
                self.quests = {}
        except Exception as e:
            print(f"クエスト読み込みエラー: {e}")
            self.quests = {}

    def can_accept_quest(self, quest_id, player_level=1, event_flags=None):
        """
        クエストを受注可能かチェック

        Args:
            quest_id: クエストID
            player_level: プレイヤーレベル
            event_flags: イベントフラグ辞書

        Returns:
            bool: 受注可能な場合True
        """
        if quest_id not in self.quests:
            return False

        # すでに完了済み
        if quest_id in self.completed_quests:
            return False

        # すでに進行中
        if quest_id in self.active_quests:
            return False

        quest_data = self.quests[quest_id]

        # レベル要件チェック
        required_level = quest_data.get('required_level', 1)
        if player_level < required_level:
            return False

        # 前提クエストチェック
        prerequisites = quest_data.get('prerequisites', [])
        for prereq_id in prerequisites:
            if prereq_id not in self.completed_quests:
                return False

        # イベントフラグチェック
        if event_flags:
            required_flags = quest_data.get('required_flags', [])
            for flag_name in required_flags:
                if not event_flags.get(flag_name, False):
                    return False

        return True

    def accept_quest(self, quest_id):
        """
        クエストを受注

        Args:
            quest_id: クエストID

        Returns:
            dict: クエストデータ、受注できない場合None
        """
        if quest_id not in self.quests:
            return None

        if quest_id in self.active_quests:
            print(f"すでに進行中のクエスト: {quest_id}")
            return None

        quest_data = self.quests[quest_id]

        # クエストを進行中リストに追加
        self.active_quests.append(quest_id)

        # 進捗を初期化
        self.quest_progress[quest_id] = {
            'objectives': {},
            'started': True,
            'completed': False
        }

        # 目標を初期化
        for objective in quest_data.get('objectives', []):
            objective_id = objective.get('id')
            self.quest_progress[quest_id]['objectives'][objective_id] = {
                'current': 0,
                'target': objective.get('target', 1),
                'completed': False
            }

        print(f"クエスト受注: {quest_data.get('name', quest_id)}")
        return quest_data

    def update_objective(self, quest_id, objective_id, increment=1):
        """
        クエスト目標を更新

        Args:
            quest_id: クエストID
            objective_id: 目標ID
            increment: 進捗増加量

        Returns:
            bool: 目標完了の場合True
        """
        if quest_id not in self.active_quests:
            return False

        if quest_id not in self.quest_progress:
            return False

        objectives = self.quest_progress[quest_id]['objectives']
        if objective_id not in objectives:
            return False

        objective = objectives[objective_id]

        # すでに完了している
        if objective['completed']:
            return True

        # 進捗を更新
        objective['current'] += increment

        # 目標達成チェック
        if objective['current'] >= objective['target']:
            objective['completed'] = True
            print(f"目標達成: {objective_id}")

            # クエスト全体の完了チェック
            if self.check_quest_completion(quest_id):
                self.complete_quest(quest_id)

            return True

        return False

    def check_quest_completion(self, quest_id):
        """
        クエストの全目標が完了しているかチェック

        Args:
            quest_id: クエストID

        Returns:
            bool: すべての目標が完了している場合True
        """
        if quest_id not in self.quest_progress:
            return False

        objectives = self.quest_progress[quest_id]['objectives']

        for objective in objectives.values():
            if not objective['completed']:
                return False

        return True

    def complete_quest(self, quest_id):
        """
        クエストを完了

        Args:
            quest_id: クエストID

        Returns:
            dict: 報酬データ
        """
        if quest_id not in self.active_quests:
            return None

        quest_data = self.quests[quest_id]

        # 進行中リストから削除
        self.active_quests.remove(quest_id)

        # 完了リストに追加
        self.completed_quests.append(quest_id)

        # 進捗を完了としてマーク
        if quest_id in self.quest_progress:
            self.quest_progress[quest_id]['completed'] = True

        print(f"クエスト完了: {quest_data.get('name', quest_id)}")

        # 報酬を返す
        return quest_data.get('rewards', {})

    def get_quest_info(self, quest_id):
        """
        クエスト情報を取得

        Args:
            quest_id: クエストID

        Returns:
            dict: クエスト情報
        """
        if quest_id not in self.quests:
            return None

        quest_data = self.quests[quest_id].copy()

        # 進捗情報を追加
        if quest_id in self.quest_progress:
            quest_data['progress'] = self.quest_progress[quest_id]

        # 状態を追加
        if quest_id in self.completed_quests:
            quest_data['status'] = 'completed'
        elif quest_id in self.active_quests:
            quest_data['status'] = 'active'
        else:
            quest_data['status'] = 'available'

        return quest_data

    def get_active_quests(self):
        """
        進行中のクエスト一覧を取得

        Returns:
            list: 進行中のクエスト情報リスト
        """
        return [self.get_quest_info(qid) for qid in self.active_quests]

    def get_completed_quests(self):
        """
        完了したクエスト一覧を取得

        Returns:
            list: 完了したクエスト情報リスト
        """
        return [self.get_quest_info(qid) for qid in self.completed_quests]

    def save_state(self):
        """
        クエスト状態を保存用辞書に変換

        Returns:
            dict: 保存用データ
        """
        return {
            'active_quests': self.active_quests.copy(),
            'completed_quests': self.completed_quests.copy(),
            'quest_progress': self.quest_progress.copy()
        }

    def load_state(self, state_data):
        """
        保存されたクエスト状態を読み込み

        Args:
            state_data: 保存データ
        """
        self.active_quests = state_data.get('active_quests', [])
        self.completed_quests = state_data.get('completed_quests', [])
        self.quest_progress = state_data.get('quest_progress', {})
