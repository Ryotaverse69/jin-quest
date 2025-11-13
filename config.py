"""
JID×QUEST - ゲーム設定定数
スーパーファミコン風RPGの基本設定
"""

# 画面設定 (HD-2D風 - フルHD)
SCREEN_WIDTH = 1920  # フルHD解像度 (16:9)
SCREEN_HEIGHT = 1080
SCALE_FACTOR = 1  # スケーリングなし（ネイティブフルHD）
DISPLAY_WIDTH = SCREEN_WIDTH
DISPLAY_HEIGHT = SCREEN_HEIGHT

# ゲーム設定
FPS = 60
TILE_SIZE = 64  # フルHDに最適化された大きなタイル
LANGUAGE = 'ja'  # 日本語固定

# サーバー設定
SERVER_PORT = 4000  # ローカルサーバーポート
SERVER_HOST = 'localhost'

# カラーパレット (HD-2D風 - より洗練された色)
COLORS = {
    'BLACK': (10, 10, 15),  # 完全な黒ではなく、わずかに青みがかった黒
    'WHITE': (255, 255, 255),
    'BLUE': (45, 120, 255),  # より鮮やかなブルー
    'DARK_BLUE': (15, 25, 80),  # 深みのあるダークブルー
    'LIGHT_BLUE': (140, 190, 255),  # 明るく柔らかいブルー
    'TEXT_WHITE': (250, 250, 250),
    'WINDOW_BLUE': (30, 140, 255),  # 現代的なブルー
    'WINDOW_DARK': (20, 40, 90),  # より深いウィンドウ背景
    'GOLD': (255, 200, 50),  # より鮮やかなゴールド
    'SILVER': (200, 200, 220),  # シルバー
    'SHADOW': (0, 0, 0, 128),  # 半透明の影
    'OVERLAY': (0, 0, 0, 180),  # オーバーレイ用
}

# フォント設定 (フルHD対応)
FONT_SIZE = 36  # フルHDに最適化された読みやすいフォント
MESSAGE_SPEED = 2  # 文字表示速度（フレーム数）

# プレイヤー設定
PLAYER_SPEED = 2

# バトル設定
BATTLE_TRANSITION_FRAMES = 30
DAMAGE_VARIANCE = 0.1  # ダメージの乱数幅 (±10%)

# ゲームパス
SAVE_FILE = 'data/save_data.json'
CHARACTERS_DATA = 'data/game_data/characters.json'
MAPS_DIR = 'data/maps/'
DIALOGUES_DIR = 'data/dialogues/'

# ゲーム状態
class GameState:
    TITLE = 'title'
    FIELD = 'field'
    BATTLE = 'battle'
    MENU = 'menu'
    DIALOGUE = 'dialogue'
    EVENT = 'event'

# 役職レベル定義
RANK_LEVELS = {
    1: "アドバイザー",
    11: "スーパーバイザー",
    21: "チーフアドバイザー",
    31: "サブリーダー",
    41: "リーダー",
    51: "マネージャー",
    66: "部長",
    81: "役員",
}

def get_rank_name(level):
    """レベルから役職名を取得"""
    rank = "アドバイザー"
    for req_level, rank_name in sorted(RANK_LEVELS.items(), reverse=True):
        if level >= req_level:
            rank = rank_name
            break
    return rank
