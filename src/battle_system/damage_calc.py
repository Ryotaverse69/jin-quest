"""
JID×QUEST - ダメージ計算システム
"""

import random
from config import *


def calculate_damage(attacker, defender, skill_power=1.0, is_critical=False):
    """
    ダメージを計算

    Args:
        attacker: 攻撃者（PlayerまたはEnemy）
        defender: 防御者（PlayerまたはEnemy）
        skill_power: スキル倍率（通常攻撃は1.0）
        is_critical: クリティカルヒットかどうか

    Returns:
        dict: ダメージ情報 {'damage': int, 'is_critical': bool, 'variance': float}
    """
    # 基本ダメージ計算: (攻撃力 * 2 - 防御力) * スキル倍率
    base_damage = (attacker.atk * 2 - defender.defense) * skill_power

    # 最低ダメージは1
    base_damage = max(1, base_damage)

    # クリティカル判定（5%の確率）
    if not is_critical:
        is_critical = random.random() < 0.05

    # クリティカルの場合は1.5倍
    if is_critical:
        base_damage *= 1.5

    # ダメージの乱数（±10%）
    variance = random.uniform(1.0 - DAMAGE_VARIANCE, 1.0 + DAMAGE_VARIANCE)
    final_damage = int(base_damage * variance)

    return {
        'damage': final_damage,
        'is_critical': is_critical,
        'variance': variance
    }


def calculate_exp_for_level(level):
    """
    次のレベルに必要な経験値を計算

    Args:
        level: 現在のレベル

    Returns:
        int: 必要経験値
    """
    # 基本: レベル * 30
    return level * 30


def can_level_up(current_exp, current_level):
    """
    レベルアップ可能かチェック

    Args:
        current_exp: 現在の経験値
        current_level: 現在のレベル

    Returns:
        bool: レベルアップ可能ならTrue
    """
    return current_exp >= calculate_exp_for_level(current_level)


def calculate_level_up_stats(player, new_level):
    """
    レベルアップ時のステータス上昇を計算

    Args:
        player: プレイヤーオブジェクト
        new_level: 新しいレベル

    Returns:
        dict: 上昇したステータス
    """
    # クラスに応じた成長率
    if player.player_class == '男性営業':
        hp_growth = 5
        mp_growth = 2
        atk_growth = 2
        def_growth = 1
        spd_growth = 1
    else:  # 女性営業
        hp_growth = 4
        mp_growth = 3
        atk_growth = 1
        def_growth = 1
        spd_growth = 2

    # レベル5ごとにボーナス
    if new_level % 5 == 0:
        hp_growth += 3
        mp_growth += 2

    return {
        'max_hp': hp_growth,
        'max_mp': mp_growth,
        'atk': atk_growth,
        'defense': def_growth,
        'spd': spd_growth
    }


def check_escape_success(player_speed, enemy_speed):
    """
    逃走成功判定

    Args:
        player_speed: プレイヤーの素早さ
        enemy_speed: 敵の素早さ

    Returns:
        bool: 逃走成功ならTrue
    """
    # 素早さの差に応じて成功率を変動
    # 基本成功率50% + (プレイヤー素早さ - 敵素早さ) * 5%
    base_rate = 0.5
    speed_diff = (player_speed - enemy_speed) * 0.05
    success_rate = max(0.1, min(0.9, base_rate + speed_diff))  # 10%～90%に制限

    return random.random() < success_rate


def get_enemy_for_area(area_level):
    """
    エリアレベルに応じた敵を生成

    Args:
        area_level: エリアのレベル（1～10）

    Returns:
        dict: 敵情報 {'type': str, 'level': int}
    """
    # 敵タイプをランダムに選択
    enemy_types = ['不動産会社', '滞納者']
    enemy_type = random.choice(enemy_types)

    # レベルはエリアレベル±1
    enemy_level = area_level + random.randint(-1, 1)
    enemy_level = max(1, min(10, enemy_level))  # 1～10に制限

    return {
        'type': enemy_type,
        'level': enemy_level
    }
