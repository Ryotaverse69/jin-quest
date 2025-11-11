"""
JID×QUEST - 敵エンティティ
"""

import pygame
import json
from config import *


class Enemy:
    """敵クラス"""

    def __init__(self, enemy_type, level=1):
        """
        敵の初期化

        Args:
            enemy_type: 敵タイプ（'不動産会社' or '滞納者'）
            level: 敵のレベル
        """
        self.enemy_type = enemy_type
        self.level = level

        # キャラクターデータから敵情報を読み込み
        self.load_enemy_data()

        # 現在のHP/MP
        self.hp = self.max_hp
        self.mp = self.max_mp

        # バトル用の状態
        self.is_alive = True
        self.action = None  # 次の行動

    def load_enemy_data(self):
        """キャラクターデータから敵情報を読み込む"""
        with open(CHARACTERS_DATA, 'r', encoding='utf-8') as f:
            data = json.load(f)

        enemies = data['enemies'].get(self.enemy_type, {})
        levels = enemies.get('levels', {})

        # レベルに最も近いデータを取得
        available_levels = sorted([int(k) for k in levels.keys()])
        closest_level = min(available_levels, key=lambda x: abs(x - self.level))

        enemy_data = levels[str(closest_level)]

        # ステータス設定
        self.name = enemy_data['name']
        self.max_hp = enemy_data['hp']
        self.max_mp = enemy_data['mp']
        self.atk = enemy_data['atk']
        self.defense = enemy_data['def']
        self.spd = enemy_data['spd']
        self.exp_reward = enemy_data['exp']
        self.gold_reward = enemy_data['gold']

        # 特殊ステータス（滞納者の場合）
        self.special_stat = enemy_data.get('special_stat', None)

    def take_damage(self, damage):
        """
        ダメージを受ける

        Args:
            damage: ダメージ量

        Returns:
            int: 実際に受けたダメージ
        """
        actual_damage = max(0, damage)
        self.hp -= actual_damage

        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

        return actual_damage

    def heal(self, amount):
        """
        HPを回復

        Args:
            amount: 回復量

        Returns:
            int: 実際に回復した量
        """
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def choose_action(self, player):
        """
        敵の行動を決定（簡易AI）

        Args:
            player: プレイヤーオブジェクト

        Returns:
            dict: 行動情報
        """
        import random

        # 80%の確率で通常攻撃、20%の確率で防御
        action_roll = random.random()

        if action_roll < 0.8:
            return {
                'type': 'attack',
                'name': '攻撃',
                'target': player
            }
        else:
            return {
                'type': 'defend',
                'name': '様子を見ている'
            }

    def get_status_text(self):
        """ステータス情報のテキストを取得"""
        status = f"{self.name} Lv.{self.level}\n"
        status += f"HP: {self.hp}/{self.max_hp}"

        if self.special_stat:
            status += f"\n{self.special_stat}"

        return status

    def create_sprite(self):
        """敵のスプライトを作成（仮：四角形）"""
        surface = pygame.Surface((32, 32))

        # 敵タイプで色を変える
        if self.enemy_type == '不動産会社':
            color = (200, 50, 50)  # 赤系
        elif self.enemy_type == '滞納者':
            color = (150, 150, 50)  # 黄土色系
        else:
            color = (100, 100, 100)  # 灰色

        surface.fill(color)

        # 枠線
        pygame.draw.rect(surface, COLORS['BLACK'], (0, 0, 32, 32), 2)

        return surface
