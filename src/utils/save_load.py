"""
JID×QUEST - セーブ/ロードシステム
"""

import json
import os
from datetime import datetime


class SaveLoadManager:
    """セーブ/ロード管理クラス"""

    def __init__(self, save_dir='data/saves'):
        """
        セーブ/ロードマネージャーの初期化

        Args:
            save_dir: セーブデータの保存ディレクトリ
        """
        self.save_dir = save_dir

        # セーブディレクトリが存在しない場合は作成
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    def save_game(self, player, map_path, slot=1):
        """
        ゲームをセーブ

        Args:
            player: プレイヤーオブジェクト
            map_path: 現在のマップパス
            slot: セーブスロット番号 (1-3)

        Returns:
            bool: セーブ成功時True
        """
        try:
            save_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'player': {
                    'name': player.name,
                    'level': player.level,
                    'exp': player.exp,
                    'hp': player.hp,
                    'max_hp': player.max_hp,
                    'mp': player.mp,
                    'max_mp': player.max_mp,
                    'atk': player.atk,
                    'defense': player.defense,
                    'spd': player.spd,
                    'tile_x': player.tile_x,
                    'tile_y': player.tile_y,
                    'direction': player.direction
                },
                'map': {
                    'path': map_path
                },
                'flags': {},  # 今後のイベントフラグ用
                'inventory': []  # 今後のアイテム用
            }

            save_path = os.path.join(self.save_dir, f'save_{slot}.json')

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            print(f"セーブ完了: スロット{slot}")
            return True

        except Exception as e:
            print(f"セーブエラー: {e}")
            return False

    def load_game(self, slot=1):
        """
        ゲームをロード

        Args:
            slot: セーブスロット番号 (1-3)

        Returns:
            dict: セーブデータ、失敗時はNone
        """
        try:
            save_path = os.path.join(self.save_dir, f'save_{slot}.json')

            if not os.path.exists(save_path):
                print(f"セーブデータが見つかりません: スロット{slot}")
                return None

            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            print(f"ロード完了: スロット{slot}")
            return save_data

        except Exception as e:
            print(f"ロードエラー: {e}")
            return None

    def get_save_info(self, slot=1):
        """
        セーブスロットの情報を取得

        Args:
            slot: セーブスロット番号 (1-3)

        Returns:
            dict: セーブ情報、データがない場合はNone
        """
        try:
            save_path = os.path.join(self.save_dir, f'save_{slot}.json')

            if not os.path.exists(save_path):
                return None

            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            # 表示用の情報を返す
            player_data = save_data['player']
            timestamp = datetime.fromisoformat(save_data['timestamp'])

            return {
                'slot': slot,
                'name': player_data['name'],
                'level': player_data['level'],
                'timestamp': timestamp.strftime('%Y/%m/%d %H:%M'),
                'exists': True
            }

        except Exception as e:
            print(f"セーブ情報取得エラー: {e}")
            return None

    def delete_save(self, slot=1):
        """
        セーブデータを削除

        Args:
            slot: セーブスロット番号 (1-3)

        Returns:
            bool: 削除成功時True
        """
        try:
            save_path = os.path.join(self.save_dir, f'save_{slot}.json')

            if os.path.exists(save_path):
                os.remove(save_path)
                print(f"セーブデータ削除: スロット{slot}")
                return True

            return False

        except Exception as e:
            print(f"削除エラー: {e}")
            return False

    def apply_save_data(self, player, save_data):
        """
        セーブデータをプレイヤーに適用

        Args:
            player: プレイヤーオブジェクト
            save_data: セーブデータ
        """
        player_data = save_data['player']

        player.name = player_data['name']
        player.level = player_data['level']
        player.exp = player_data['exp']
        player.hp = player_data['hp']
        player.max_hp = player_data['max_hp']
        player.mp = player_data['mp']
        player.max_mp = player_data['max_mp']
        player.atk = player_data['atk']
        player.defense = player_data['defense']
        player.spd = player_data['spd']
        player.tile_x = player_data['tile_x']
        player.tile_y = player_data['tile_y']
        player.direction = player_data['direction']

        # ピクセル座標も更新
        from config import TILE_SIZE
        player.x = player.tile_x * TILE_SIZE
        player.y = player.tile_y * TILE_SIZE
        player.target_tile_x = player.tile_x
        player.target_tile_y = player.tile_y
