"""
JID×QUEST - バトル管理システム
"""

from config import *
from src.battle_system.damage_calc import *


class BattleManager:
    """バトル管理クラス"""

    def __init__(self, player, enemy):
        """
        バトルマネージャーの初期化

        Args:
            player: プレイヤーオブジェクト
            enemy: 敵オブジェクト
        """
        self.player = player
        self.enemy = enemy

        # バトルの状態
        self.battle_phase = 'player_turn'  # player_turn, enemy_turn, victory, defeat, escaped
        self.turn_count = 0

        # メッセージキュー
        self.message_queue = []
        self.current_message = ""

        # アクション処理用
        self.action_delay = 0  # アクション間のディレイ
        self.pending_actions = []  # 実行待ちアクション

        # 開始メッセージ
        self.add_message(f"{self.enemy.name}が現れた！")

    def add_message(self, message):
        """メッセージをキューに追加"""
        self.message_queue.append(message)

    def get_current_message(self):
        """現在表示中のメッセージを取得"""
        if self.message_queue:
            return self.message_queue[0]
        return ""

    def next_message(self):
        """次のメッセージに進む"""
        if self.message_queue:
            self.message_queue.pop(0)

    def has_messages(self):
        """表示待ちのメッセージがあるか"""
        return len(self.message_queue) > 0

    def execute_player_attack(self):
        """プレイヤーの通常攻撃を実行"""
        result = calculate_damage(self.player, self.enemy)
        damage = result['damage']
        is_critical = result['is_critical']

        self.enemy.take_damage(damage)

        if is_critical:
            self.add_message(f"{self.player.name}の攻撃！")
            self.add_message(f"会心の一撃！ {damage}のダメージ！")
        else:
            self.add_message(f"{self.player.name}の攻撃！ {damage}のダメージ！")

        # 敵を倒した場合
        if not self.enemy.is_alive:
            self.handle_victory()
        else:
            self.battle_phase = 'enemy_turn'

    def execute_player_defend(self):
        """プレイヤーの防御"""
        self.add_message(f"{self.player.name}は身構えた！")
        self.battle_phase = 'enemy_turn'

    def execute_player_escape(self):
        """プレイヤーの逃走"""
        success = check_escape_success(self.player.spd, self.enemy.spd)

        if success:
            self.add_message(f"{self.player.name}は逃げ出した！")
            self.battle_phase = 'escaped'
        else:
            self.add_message(f"逃げられなかった！")
            self.battle_phase = 'enemy_turn'

    def execute_enemy_turn(self):
        """敵のターンを実行"""
        if not self.enemy.is_alive:
            return

        # 敵の行動を決定
        action = self.enemy.choose_action(self.player)

        if action['type'] == 'attack':
            result = calculate_damage(self.enemy, self.player)
            damage = result['damage']

            self.player.hp -= damage
            if self.player.hp < 0:
                self.player.hp = 0

            self.add_message(f"{self.enemy.name}の攻撃！ {damage}のダメージ！")

            # プレイヤーが倒された場合
            if self.player.hp <= 0:
                self.handle_defeat()
            else:
                self.battle_phase = 'player_turn'
                self.turn_count += 1

        elif action['type'] == 'defend':
            self.add_message(f"{self.enemy.name}は{action['name']}！")
            self.battle_phase = 'player_turn'
            self.turn_count += 1

    def handle_victory(self):
        """勝利時の処理"""
        self.battle_phase = 'victory'

        # 経験値とゴールド獲得
        self.add_message(f"{self.enemy.name}を倒した！")
        self.add_message(f"経験値を{self.enemy.exp_reward}獲得！")
        self.add_message(f"{self.enemy.gold_reward}円を手に入れた！")

        # 経験値を加算
        self.player.exp += self.enemy.exp_reward

        # レベルアップチェック
        while can_level_up(self.player.exp, self.player.level):
            self.level_up_player()

    def level_up_player(self):
        """プレイヤーのレベルアップ処理"""
        old_level = self.player.level
        self.player.level += 1
        self.player.exp -= calculate_exp_for_level(old_level)

        # ステータス上昇
        stats_gain = calculate_level_up_stats(self.player, self.player.level)

        self.player.max_hp += stats_gain['max_hp']
        self.player.max_mp += stats_gain['max_mp']
        self.player.atk += stats_gain['atk']
        self.player.defense += stats_gain['defense']
        self.player.spd += stats_gain['spd']

        # HP/MP全回復
        self.player.hp = self.player.max_hp
        self.player.mp = self.player.max_mp

        # レベルアップメッセージ
        self.add_message(f"レベルが{self.player.level}に上がった！")
        self.add_message(f"役職: {self.player.get_rank()}")

        # ステータス上昇メッセージ
        self.add_message(
            f"HP+{stats_gain['max_hp']} MP+{stats_gain['max_mp']} " +
            f"攻+{stats_gain['atk']} 防+{stats_gain['defense']} 速+{stats_gain['spd']}"
        )

    def handle_defeat(self):
        """敗北時の処理"""
        self.battle_phase = 'defeat'
        self.add_message(f"{self.player.name}は力尽きた...")

    def is_battle_over(self):
        """バトルが終了したか"""
        return self.battle_phase in ['victory', 'defeat', 'escaped']

    def get_battle_result(self):
        """バトル結果を取得"""
        return {
            'phase': self.battle_phase,
            'exp_gained': self.enemy.exp_reward if self.battle_phase == 'victory' else 0,
            'gold_gained': self.enemy.gold_reward if self.battle_phase == 'victory' else 0,
            'turns': self.turn_count
        }
